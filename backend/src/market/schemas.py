"""Market data Pydantic schemas."""

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


# ─── Asset ────────────────────────────────────────────────
class AssetCreate(BaseModel):
    symbol: str = Field(..., max_length=50, description="Ticker symbol (e.g. AAPL, BTC-USD)")
    asset_name: str = Field(..., max_length=100, description="Human-readable name")
    asset_type: str = Field(..., description="stock | crypto | forex | commodity | index")


class AssetResponse(BaseModel):
    id: UUID
    symbol: str
    asset_name: str
    asset_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Candle ───────────────────────────────────────────────
class CandleResponse(BaseModel):
    """Single OHLCV candle for chart rendering."""
    time: float  # Unix timestamp (seconds) — TradingView lightweight-charts format
    open: float
    high: float
    low: float
    close: float
    volume: int


class CandlesRequest(BaseModel):
    """Query parameters for candle data."""
    symbol: str
    timeframe: str = Field("1d", description="1d, 1h, 5m, etc.")
    period: str = Field("6mo", description="yfinance period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 5y, max")


class CandlesResponse(BaseModel):
    symbol: str
    timeframe: str
    count: int
    candles: list[CandleResponse]


class AssetQuote(BaseModel):
    """Real-time or latest price quote."""
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: float | None = None
    timestamp: datetime
