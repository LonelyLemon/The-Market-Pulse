import { useEffect, useState, useCallback } from 'react';
import { HiOutlineSearch } from 'react-icons/hi';
import { marketApi } from '../../api/market';
import CandlestickChart from '../../components/market/CandlestickChart';
import './Market.css';

const DEFAULT_SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'BTC-USD', 'ETH-USD'];
const TIMEFRAMES = [
    { label: '5m', value: '5m', period: '1d' },
    { label: '15m', value: '15m', period: '5d' },
    { label: '1H', value: '1h', period: '1mo' },
    { label: '1D', value: '1d', period: '6mo' },
    { label: '1W', value: '1wk', period: '2y' },
    { label: '1M', value: '1mo', period: '5y' },
];

export default function MarketDashboard() {
    const [activeSymbol, setActiveSymbol] = useState('AAPL');
    const [activeTf, setActiveTf] = useState(TIMEFRAMES[3]); // 1D
    const [candles, setCandles] = useState([]);
    const [quotes, setQuotes] = useState({});
    const [chartLoading, setChartLoading] = useState(false);
    const [searchInput, setSearchInput] = useState('');

    // Fetch chart data
    const loadCandles = useCallback(async () => {
        setChartLoading(true);
        try {
            const { data } = await marketApi.getCandles(activeSymbol, {
                timeframe: activeTf.value,
                period: activeTf.period,
            });
            setCandles(data.candles);
        } catch {
            setCandles([]);
        }
        setChartLoading(false);
    }, [activeSymbol, activeTf]);

    useEffect(() => { loadCandles(); }, [loadCandles]);

    // Load quotes for default symbols
    useEffect(() => {
        DEFAULT_SYMBOLS.forEach(async (sym) => {
            try {
                const { data } = await marketApi.getQuote(sym);
                setQuotes((prev) => ({ ...prev, [sym]: data }));
            } catch { /* skip */ }
        });
    }, []);

    function handleSearch(e) {
        e.preventDefault();
        const sym = searchInput.trim().toUpperCase();
        if (sym) {
            setActiveSymbol(sym);
            setSearchInput('');
        }
    }

    return (
        <div className="market-dashboard">
            <h1>Market Data</h1>

            {/* Quote cards */}
            <div className="quote-row">
                {DEFAULT_SYMBOLS.map((sym) => {
                    const q = quotes[sym];
                    return (
                        <div
                            key={sym}
                            className={`quote-card${activeSymbol === sym ? ' selected' : ''}`}
                            onClick={() => setActiveSymbol(sym)}
                        >
                            <div className="quote-symbol">{sym}</div>
                            {q ? (
                                <>
                                    <div className="quote-name">{q.name}</div>
                                    <div className="quote-price">${q.price?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</div>
                                    <div className={`quote-change ${q.change >= 0 ? 'positive' : 'negative'}`}>
                                        {q.change >= 0 ? '+' : ''}{q.change?.toFixed(2)} ({q.change_percent?.toFixed(2)}%)
                                    </div>
                                </>
                            ) : (
                                <div style={{ height: 60 }}>
                                    <div className="skeleton" style={{ width: '60%', height: 14, marginBottom: 8 }} />
                                    <div className="skeleton" style={{ width: '80%', height: 24 }} />
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Toolbar */}
            <div className="market-toolbar">
                <form onSubmit={handleSearch} style={{ display: 'contents' }}>
                    <input
                        className="input"
                        placeholder="Search symbol…"
                        value={searchInput}
                        onChange={(e) => setSearchInput(e.target.value)}
                    />
                    <button type="submit" className="btn btn-primary btn-sm"><HiOutlineSearch /></button>
                </form>

                <div style={{ flex: 1 }} />

                <div className="tf-buttons">
                    {TIMEFRAMES.map((tf) => (
                        <button
                            key={tf.value}
                            className={`tf-btn${activeTf.value === tf.value ? ' active' : ''}`}
                            onClick={() => setActiveTf(tf)}
                        >
                            {tf.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Chart */}
            <div style={{ marginBottom: 'var(--space-lg)', position: 'relative' }}>
                <div style={{ fontSize: 'var(--text-lg)', fontWeight: 700, marginBottom: 'var(--space-sm)' }}>
                    {activeSymbol} · {activeTf.label}
                </div>
                {chartLoading ? (
                    <div className="loading-center" style={{ minHeight: 450 }}><div className="spinner" /></div>
                ) : candles.length === 0 ? (
                    <div className="empty-state" style={{ minHeight: 450 }}>
                        <h3>No data available</h3>
                        <p>Could not load chart data for {activeSymbol}</p>
                    </div>
                ) : (
                    <CandlestickChart candles={candles} height={450} />
                )}
            </div>
        </div>
    );
}
