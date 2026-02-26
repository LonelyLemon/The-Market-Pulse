"""Yahoo Finance data provider using yfinance library."""

from __future__ import annotations

from datetime import datetime, timezone

from loguru import logger


def _yf():
    """Lazy import yfinance to avoid slow pandas startup at module load time."""
    import yfinance as yf
    return yf


VALID_TIMEFRAMES = {"1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"}
VALID_PERIODS = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"}


def fetch_candles(
    symbol: str,
    timeframe: str = "1d",
    period: str = "6mo",
) -> list[dict]:
    """
    Fetch OHLCV candle data from Yahoo Finance.

    Returns a list of dicts with keys:
        time (float), open, high, low, close, volume
    """
    if timeframe not in VALID_TIMEFRAMES:
        raise ValueError(f"Invalid timeframe: {timeframe}")
    if period not in VALID_PERIODS:
        raise ValueError(f"Invalid period: {period}")

    try:
        ticker = _yf().Ticker(symbol)
        df = ticker.history(period=period, interval=timeframe)

        if df.empty:
            logger.warning(f"No data returned for {symbol} ({timeframe}, {period})")
            return []

        candles = []
        for ts, row in df.iterrows():
            # Convert pandas Timestamp to Unix seconds
            unix_ts = ts.timestamp()
            candles.append({
                "time": unix_ts,
                "timestamp": ts.to_pydatetime().replace(tzinfo=timezone.utc),
                "open": round(row["Open"], 4),
                "high": round(row["High"], 4),
                "low": round(row["Low"], 4),
                "close": round(row["Close"], 4),
                "volume": int(row.get("Volume", 0)),
            })

        logger.info(f"Fetched {len(candles)} candles for {symbol} ({timeframe}, {period})")
        return candles

    except Exception as e:
        logger.error(f"yfinance error for {symbol}: {e}")
        raise


def fetch_quote(symbol: str) -> dict | None:
    """Fetch latest quote info for a symbol."""
    try:
        ticker = _yf().Ticker(symbol)
        info = ticker.fast_info

        return {
            "symbol": symbol.upper(),
            "name": getattr(ticker, "info", {}).get("shortName", symbol),
            "price": round(info.get("lastPrice", 0), 4),
            "change": round(info.get("lastPrice", 0) - info.get("previousClose", 0), 4),
            "change_percent": round(
                ((info.get("lastPrice", 0) - info.get("previousClose", 1)) / info.get("previousClose", 1)) * 100,
                2,
            ),
            "volume": int(info.get("lastVolume", 0)),
            "market_cap": info.get("marketCap"),
            "timestamp": datetime.now(timezone.utc),
        }
    except Exception as e:
        logger.error(f"Quote error for {symbol}: {e}")
        return None
