"""Market data API router — assets, candles, quotes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.auth.dependencies import get_current_user
from src.core.database import SessionDep
from src.core.dependencies import require_admin
from src.market import service
from src.market.schemas import (
    AssetCreate,
    AssetResponse,
    AssetQuote,
    CandlesResponse,
    CandleResponse,
)

market_route = APIRouter(prefix="/market", tags=["Market Data"])


# ═══════════════════════════════════════════════════════════
#  ASSETS
# ═══════════════════════════════════════════════════════════

@market_route.get("/assets", response_model=list[AssetResponse])
async def list_assets(
    db: SessionDep,
    asset_type: str | None = Query(None, description="Filter by type: stock, crypto, forex, etc."),
):
    """List all tracked assets."""
    return await service.list_assets(db, asset_type)


@market_route.post(
    "/assets",
    response_model=AssetResponse,
    status_code=201,
    dependencies=[Depends(require_admin)],
)
async def create_asset(payload: AssetCreate, db: SessionDep):
    """Register a new tracked asset. Admin only."""
    return await service.create_asset(db, payload.symbol, payload.asset_name, payload.asset_type)


@market_route.delete("/assets/{asset_id}", status_code=204, dependencies=[Depends(require_admin)])
async def delete_asset(asset_id: UUID, db: SessionDep):
    """Delete a tracked asset. Admin only."""
    await service.delete_asset(db, asset_id)


# ═══════════════════════════════════════════════════════════
#  CANDLES (OHLCV chart data)
# ═══════════════════════════════════════════════════════════

@market_route.get("/candles/{symbol}", response_model=CandlesResponse)
async def get_candles(
    symbol: str,
    db: SessionDep,
    timeframe: str = Query("1d", description="1d, 1h, 5m, etc."),
    period: str = Query("6mo", description="1d, 5d, 1mo, 3mo, 6mo, 1y, 5y, max"),
):
    """Get OHLCV candle data for a symbol. Uses DB cache when available."""
    resolved_symbol, candles = await service.get_candles(db, symbol, timeframe, period)
    return CandlesResponse(
        symbol=resolved_symbol,
        timeframe=timeframe,
        count=len(candles),
        candles=[CandleResponse(**c) for c in candles],
    )


# ═══════════════════════════════════════════════════════════
#  QUOTES (live prices)
# ═══════════════════════════════════════════════════════════

@market_route.get("/quote/{symbol}", response_model=AssetQuote)
async def get_quote(symbol: str):
    """Get latest live quote for a symbol."""
    quote = await service.get_quote(symbol)
    return AssetQuote(**quote)