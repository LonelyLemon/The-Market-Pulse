"""Market data service — asset CRUD + candle ingestion/retrieval."""

from __future__ import annotations

import uuid

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.market.models import Asset, Candle
from src.market.provider import fetch_candles, fetch_quote
from src.market.exceptions import AssetNotFound, AssetAlreadyExists, MarketDataUnavailable, InvalidTimeframe
from src.market.provider import VALID_TIMEFRAMES


# ─── Assets ───────────────────────────────────────────────
async def create_asset(db: AsyncSession, symbol: str, asset_name: str, asset_type: str) -> Asset:
    existing = await db.execute(select(Asset).where(Asset.symbol == symbol.upper()))
    if existing.scalar_one_or_none():
        raise AssetAlreadyExists()

    asset = Asset(symbol=symbol.upper(), asset_name=asset_name, asset_type=asset_type)
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset


async def get_asset_by_symbol(db: AsyncSession, symbol: str) -> Asset | None:
    result = await db.execute(select(Asset).where(Asset.symbol == symbol.upper()))
    return result.scalar_one_or_none()


async def list_assets(db: AsyncSession, asset_type: str | None = None) -> list[Asset]:
    query = select(Asset).order_by(Asset.symbol)
    if asset_type:
        query = query.where(Asset.asset_type == asset_type)
    result = await db.execute(query)
    return list(result.scalars().all())


async def delete_asset(db: AsyncSession, asset_id: uuid.UUID) -> None:
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise AssetNotFound()
    await db.delete(asset)
    await db.commit()


# ─── Candles ──────────────────────────────────────────────
async def get_candles(
    db: AsyncSession,
    symbol: str,
    timeframe: str = "1d",
    period: str = "6mo",
) -> tuple[str, list[dict]]:
    """
    Get candle data for a symbol. First checks DB cache,
    falls back to yfinance fetch + cache.
    """
    if timeframe not in VALID_TIMEFRAMES:
        raise InvalidTimeframe()

    asset = await get_asset_by_symbol(db, symbol)

    # Try DB cache first if asset is registered
    if asset:
        result = await db.execute(
            select(Candle)
            .where(Candle.asset_id == asset.id, Candle.timeframe == timeframe)
            .order_by(Candle.timestamp)
        )
        cached = list(result.scalars().all())
        if cached:
            return symbol.upper(), [
                {
                    "time": c.timestamp.timestamp(),
                    "open": c.open,
                    "high": c.high,
                    "low": c.low,
                    "close": c.close,
                    "volume": c.volume,
                }
                for c in cached
            ]

    # Fetch from provider
    try:
        candles = fetch_candles(symbol, timeframe, period)
    except Exception:
        raise MarketDataUnavailable(f"Could not fetch data for {symbol}")

    if not candles:
        raise MarketDataUnavailable(f"No data available for {symbol}")

    # Cache if asset is registered
    if asset:
        # Clear old candles for this timeframe
        await db.execute(
            delete(Candle).where(Candle.asset_id == asset.id, Candle.timeframe == timeframe)
        )
        for c in candles:
            db.add(Candle(
                asset_id=asset.id,
                timeframe=timeframe,
                timestamp=c["timestamp"],
                open=c["open"],
                high=c["high"],
                low=c["low"],
                close=c["close"],
                volume=c["volume"],
            ))
        await db.commit()

    # Return chart-ready data (without the timestamp datetime object)
    chart_data = [
        {"time": c["time"], "open": c["open"], "high": c["high"], "low": c["low"], "close": c["close"], "volume": c["volume"]}
        for c in candles
    ]
    return symbol.upper(), chart_data


async def get_quote(symbol: str) -> dict:
    """Get latest quote (always live, never cached)."""
    quote = fetch_quote(symbol)
    if not quote:
        raise MarketDataUnavailable(f"Quote unavailable for {symbol}")
    return quote
