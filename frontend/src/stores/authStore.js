/** Zustand auth store — manages user state + tokens */
import { create } from 'zustand';
import { authApiCalls } from '../api/auth';

const useAuthStore = create((set, get) => ({
    user: null,
    isAuthenticated: false,
    isLoading: true,

    /** Call on app mount to restore session from stored token */
    init: async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            set({ isLoading: false });
            return;
        }
        try {
            const { data } = await authApiCalls.me();
            set({ user: data, isAuthenticated: true, isLoading: false });
        } catch {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            set({ user: null, isAuthenticated: false, isLoading: false });
        }
    },

    login: async (email, password) => {
        const { data } = await authApiCalls.login({ email, password });
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        const { data: user } = await authApiCalls.me();
        set({ user, isAuthenticated: true });
        return user;
    },

    register: async (username, email, password) => {
        const { data } = await authApiCalls.register({ username, email, password });
        return data;
    },

    logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ user: null, isAuthenticated: false });
    },

    updateProfile: async (updates) => {
        const { data } = await authApiCalls.updateProfile(updates);
        set({ user: data });
        return data;
    },

    /** Helper getters */
    isAdmin: () => get().user?.role === 'admin',
    isAuthor: () => ['admin', 'author'].includes(get().user?.role),
}));

export default useAuthStore;
