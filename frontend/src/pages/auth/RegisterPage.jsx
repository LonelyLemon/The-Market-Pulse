import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../../stores/authStore';
import './Auth.css';

export default function RegisterPage() {
    const navigate = useNavigate();
    const register = useAuthStore((s) => s.register);
    const [form, setForm] = useState({ username: '', email: '', password: '' });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);

    function update(field) {
        return (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));
    }

    async function handleSubmit(e) {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await register(form.username, form.email, form.password);
            setSuccess(true);
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed.');
        } finally {
            setLoading(false);
        }
    }

    if (success) {
        return (
            <div className="auth-page">
                <div className="auth-card" style={{ textAlign: 'center' }}>
                    <h1>Check your email ✉️</h1>
                    <p className="auth-subtitle" style={{ marginBottom: 'var(--space-md)' }}>
                        We&apos;ve sent a verification link to <strong>{form.email}</strong>.
                    </p>
                    <Link to="/login" className="btn btn-primary" style={{ width: '100%' }}>
                        Go to Sign In
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="auth-page">
            <div className="auth-card">
                <h1>Create account</h1>
                <p className="auth-subtitle">Join The Market Pulse community</p>

                {error && <div className="auth-error">{error}</div>}

                <form className="auth-form" onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label" htmlFor="reg-username">Username</label>
                        <input
                            id="reg-username"
                            className="input"
                            placeholder="johndoe"
                            value={form.username}
                            onChange={update('username')}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label" htmlFor="reg-email">Email</label>
                        <input
                            id="reg-email"
                            className="input"
                            type="email"
                            placeholder="you@example.com"
                            value={form.email}
                            onChange={update('email')}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label" htmlFor="reg-password">Password</label>
                        <input
                            id="reg-password"
                            className="input"
                            type="password"
                            placeholder="Min 8 characters"
                            value={form.password}
                            onChange={update('password')}
                            minLength={8}
                            required
                        />
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? 'Creating account…' : 'Create Account'}
                    </button>
                </form>

                <div className="auth-footer">
                    Already have an account? <Link to="/login">Sign in</Link>
                </div>
            </div>
        </div>
    );
}
