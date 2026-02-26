"""Tests for the market data provider and tools."""

import pytest
from unittest.mock import patch, MagicMock


# ═══════════════════════════════════════════════════════════
#  Provider validation tests
# ═══════════════════════════════════════════════════════════

from src.market.provider import VALID_TIMEFRAMES, VALID_PERIODS, fetch_candles


class TestProviderValidation:
    def test_valid_timeframes(self):
        expected = {"1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"}
        assert VALID_TIMEFRAMES == expected

    def test_valid_periods(self):
        expected = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"}
        assert VALID_PERIODS == expected

    def test_invalid_timeframe_raises(self):
        with pytest.raises(ValueError, match="Invalid timeframe"):
            fetch_candles("AAPL", timeframe="2h")

    def test_invalid_period_raises(self):
        with pytest.raises(ValueError, match="Invalid period"):
            fetch_candles("AAPL", period="2mo")


# ═══════════════════════════════════════════════════════════
#  Market schemas tests
# ═══════════════════════════════════════════════════════════

from src.market.schemas import AssetCreate, CandlesRequest, AssetQuote
from datetime import datetime, timezone


class TestMarketSchemas:
    def test_asset_create(self):
        a = AssetCreate(symbol="AAPL", asset_name="Apple Inc", asset_type="stock")
        assert a.symbol == "AAPL"
        assert a.asset_type == "stock"

    def test_candles_request(self):
        r = CandlesRequest(symbol="MSFT", timeframe="1d", period="6mo")
        assert r.symbol == "MSFT"

    def test_asset_quote(self):
        q = AssetQuote(
            symbol="AAPL",
            name="Apple",
            price=150.0,
            change=2.5,
            change_percent=1.7,
            volume=1000000,
            market_cap=2500000000000,
            timestamp=datetime.now(timezone.utc),
        )
        assert q.price == 150.0
        assert q.change_percent == 1.7


# ═══════════════════════════════════════════════════════════
#  Market exceptions tests
# ═══════════════════════════════════════════════════════════

from src.market.exceptions import AssetNotFound, AssetAlreadyExists, MarketDataUnavailable


class TestMarketExceptions:
    def test_asset_not_found(self):
        exc = AssetNotFound()
        assert exc.status_code == 404

    def test_asset_already_exists(self):
        exc = AssetAlreadyExists()
        assert exc.status_code == 409

    def test_market_data_unavailable(self):
        exc = MarketDataUnavailable()
        assert exc.status_code == 503


# ═══════════════════════════════════════════════════════════
#  AI Tools tests
# ═══════════════════════════════════════════════════════════

from src.ai.tools import get_stock_quote, get_price_history, compare_stocks


class TestAITools:
    @patch("src.ai.tools.fetch_quote")
    def test_get_stock_quote_success(self, mock_quote):
        mock_quote.return_value = {
            "symbol": "AAPL",
            "name": "Apple Inc",
            "price": 150.00,
            "change": 2.50,
            "change_percent": 1.70,
            "volume": 50000000,
        }
        result = get_stock_quote.invoke({"symbol": "AAPL"})
        assert "AAPL" in result
        assert "$150.00" in result
        assert "📈" in result

    @patch("src.ai.tools.fetch_quote")
    def test_get_stock_quote_not_found(self, mock_quote):
        mock_quote.return_value = None
        result = get_stock_quote.invoke({"symbol": "FAKE"})
        assert "Could not retrieve" in result

    @patch("src.ai.tools.fetch_candles")
    def test_get_price_history_success(self, mock_candles):
        mock_candles.return_value = [
            {"close": 100, "high": 105, "low": 95, "open": 98, "volume": 1000, "time": 1},
            {"close": 110, "high": 115, "low": 100, "open": 100, "volume": 1200, "time": 2},
        ]
        result = get_price_history.invoke({"symbol": "AAPL"})
        assert "AAPL" in result
        assert "2 candles" in result

    @patch("src.ai.tools.fetch_candles")
    def test_get_price_history_empty(self, mock_candles):
        mock_candles.return_value = []
        result = get_price_history.invoke({"symbol": "FAKE"})
        assert "No price history" in result

    @patch("src.ai.tools.fetch_quote")
    def test_compare_stocks(self, mock_quote):
        mock_quote.side_effect = [
            {"symbol": "AAPL", "price": 150, "change": 2, "change_percent": 1.5},
            {"symbol": "MSFT", "price": 400, "change": -3, "change_percent": -0.8},
        ]
        result = compare_stocks.invoke({"symbols": "AAPL,MSFT"})
        assert "AAPL" in result
        assert "MSFT" in result
        assert "🟢" in result
        assert "🔴" in result

    def test_compare_stocks_empty(self):
        result = compare_stocks.invoke({"symbols": ""})
        assert "at least one" in result
