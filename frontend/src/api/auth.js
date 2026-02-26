/** Auth API calls */
import { authApi } from './client';

export const authApiCalls = {
    register: (data) => authApi.post('/register', data),
    login: (data) => {
        const formData = new URLSearchParams();
        formData.append('username', data.email);
        formData.append('password', data.password);
        return authApi.post('/login', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });
    },
    me: () => authApi.get('/me'),
    updateProfile: (data) => authApi.patch('/me', data),
    forgotPassword: (email) => authApi.post('/forget-password', { email }),
    verifyEmail: (token) => authApi.get('/verify-email', { params: { token } }),
    resendVerification: (email) => authApi.post('/resend-verification', { email }),
};
