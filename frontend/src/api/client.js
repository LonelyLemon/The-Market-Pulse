import axios from 'axios';

const api = axios.create({
    baseURL: '/api/v1',
    headers: { 'Content-Type': 'application/json' },
});

const authApi = axios.create({
    baseURL: '/auth',
    headers: { 'Content-Type': 'application/json' },
});

// ── JWT interceptor ──────────────────────────────────────────
function attachToken(config) {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}

api.interceptors.request.use(attachToken);
authApi.interceptors.request.use(attachToken);

// ── Response error handler ───────────────────────────────────
function handleError(error) {
    if (error.response?.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
    }
    return Promise.reject(error);
}

api.interceptors.response.use((r) => r, handleError);
authApi.interceptors.response.use((r) => r, handleError);

export { api, authApi };
