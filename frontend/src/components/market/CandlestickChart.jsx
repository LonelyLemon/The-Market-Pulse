import { useEffect, useRef } from 'react';
import { createChart, ColorType, CandlestickSeries, HistogramSeries } from 'lightweight-charts';

/**
 * TradingView Lightweight Charts wrapper (v5 API).
 *
 * Props:
 *   candles — array of { time, open, high, low, close, volume }
 *   height — optional chart height (default: 450)
 */
export default function CandlestickChart({ candles = [], height = 450 }) {
    const containerRef = useRef(null);
    const chartRef = useRef(null);

    useEffect(() => {
        if (!containerRef.current) return;

        const chart = createChart(containerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: 'transparent' },
                textColor: 'rgba(255,255,255,0.6)',
                fontFamily: "'Inter', sans-serif",
            },
            grid: {
                vertLines: { color: 'rgba(255,255,255,0.04)' },
                horzLines: { color: 'rgba(255,255,255,0.04)' },
            },
            crosshair: {
                mode: 0,
                vertLine: { labelBackgroundColor: '#3b82f6' },
                horzLine: { labelBackgroundColor: '#3b82f6' },
            },
            rightPriceScale: {
                borderColor: 'rgba(255,255,255,0.08)',
            },
            timeScale: {
                borderColor: 'rgba(255,255,255,0.08)',
                timeVisible: true,
            },
            height,
            width: containerRef.current.clientWidth,
        });

        const candleSeries = chart.addSeries(CandlestickSeries, {
            upColor: '#10b981',
            downColor: '#ef4444',
            borderDownColor: '#ef4444',
            borderUpColor: '#10b981',
            wickDownColor: '#ef4444',
            wickUpColor: '#10b981',
        });

        const volumeSeries = chart.addSeries(HistogramSeries, {
            priceFormat: { type: 'volume' },
            priceScaleId: 'volume',
        });

        chart.priceScale('volume').applyOptions({
            scaleMargins: { top: 0.8, bottom: 0 },
        });

        chartRef.current = { chart, candleSeries, volumeSeries };

        // Handle resize
        const observer = new ResizeObserver((entries) => {
            for (const entry of entries) {
                chart.applyOptions({ width: entry.contentRect.width });
            }
        });
        observer.observe(containerRef.current);

        return () => {
            observer.disconnect();
            chart.remove();
        };
    }, [height]);

    // Update data when candles change
    useEffect(() => {
        if (!chartRef.current || candles.length === 0) return;
        const { candleSeries, volumeSeries, chart } = chartRef.current;

        candleSeries.setData(
            candles.map((c) => ({
                time: c.time,
                open: c.open,
                high: c.high,
                low: c.low,
                close: c.close,
            })),
        );

        volumeSeries.setData(
            candles.map((c) => ({
                time: c.time,
                value: c.volume,
                color: c.close >= c.open ? 'rgba(16,185,129,0.25)' : 'rgba(239,68,68,0.25)',
            })),
        );

        chart.timeScale().fitContent();
    }, [candles]);

    return <div ref={containerRef} className="chart-container" />;
}
