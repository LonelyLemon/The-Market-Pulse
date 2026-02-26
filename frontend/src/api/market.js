import { api } from './client';

export const marketApi = {
    /** List tracked assets */
    listAssets: (assetType) =>
        api.get('/market/assets', { params: assetType ? { asset_type: assetType } : {} }),

    /** Get OHLCV candle data */
    getCandles: (symbol, { timeframe = '1d', period = '6mo' } = {}) =>
        api.get(`/market/candles/${encodeURIComponent(symbol)}`, {
            params: { timeframe, period },
        }),

    /** Get live quote */
    getQuote: (symbol) =>
        api.get(`/market/quote/${encodeURIComponent(symbol)}`),
};
