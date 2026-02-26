"""Custom LangChain tools for the MarketPulse AI assistant."""

from __future__ import annotations

from langchain_core.tools import tool

from src.market.provider import fetch_candles, fetch_quote, VALID_TIMEFRAMES


@tool
def get_stock_quote(symbol: str) -> str:
    """Get the latest price quote for a stock or crypto symbol (e.g. AAPL, BTC-USD, TSLA).
    Returns current price, price change, percentage change, and volume."""
    try:
        q = fetch_quote(symbol)
        if not q:
            return f"Could not retrieve quote for {symbol}."
        direction = "📈" if q["change"] >= 0 else "📉"
        return (
            f"{direction} **{q['symbol']}** ({q['name']})\n"
            f"Price: ${q['price']:,.2f}\n"
            f"Change: {'+' if q['change'] >= 0 else ''}{q['change']:.2f} "
            f"({'+' if q['change_percent'] >= 0 else ''}{q['change_percent']:.2f}%)\n"
            f"Volume: {q['volume']:,}"
        )
    except Exception as e:
        return f"Error fetching quote for {symbol}: {e}"


@tool
def get_price_history(symbol: str, timeframe: str = "1d", period: str = "1mo") -> str:
    """Get historical OHLCV price data for a symbol. 
    Timeframes: 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo.
    Periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max.
    Returns a summary with recent candles and basic statistics."""
    try:
        candles = fetch_candles(symbol, timeframe, period)
        if not candles:
            return f"No price history found for {symbol}."
        
        closes = [c["close"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        
        latest = candles[-1]
        first = candles[0]
        change = latest["close"] - first["close"]
        change_pct = (change / first["close"]) * 100
        
        return (
            f"**{symbol.upper()}** — {len(candles)} candles ({timeframe}, {period})\n"
            f"Current: ${latest['close']:,.2f}\n"
            f"Period High: ${max(highs):,.2f} | Period Low: ${min(lows):,.2f}\n"
            f"Period Change: {'+' if change >= 0 else ''}{change:.2f} ({change_pct:+.2f}%)\n"
            f"Avg Close: ${sum(closes)/len(closes):,.2f}\n"
            f"Last 5 closes: {', '.join(f'${c:.2f}' for c in closes[-5:])}"
        )
    except Exception as e:
        return f"Error fetching price history for {symbol}: {e}"


@tool
def compare_stocks(symbols: str) -> str:
    """Compare multiple stocks/crypto by their current prices.
    Pass comma-separated symbols like 'AAPL,MSFT,GOOGL'."""
    try:
        syms = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        if not syms:
            return "Please provide at least one symbol."
        
        results = []
        for sym in syms[:5]:  # Max 5
            q = fetch_quote(sym)
            if q:
                direction = "🟢" if q["change"] >= 0 else "🔴"
                results.append(
                    f"{direction} **{q['symbol']}**: ${q['price']:,.2f} "
                    f"({'+' if q['change_percent'] >= 0 else ''}{q['change_percent']:.2f}%)"
                )
            else:
                results.append(f"⚪ **{sym}**: data unavailable")
        
        return "**Stock Comparison**\n" + "\n".join(results)
    except Exception as e:
        return f"Error comparing stocks: {e}"


# All tools to register with the agent
ALL_TOOLS = [get_stock_quote, get_price_history, compare_stocks]
