import { useState } from 'react';
import useAuthStore from '../../stores/authStore';
import '../Pages.css';

export default function ProfilePage() {
    const { user, updateProfile } = useAuthStore();
    const [form, setForm] = useState({
        display_name: user?.display_name || '',
        bio: user?.bio || '',
        avatar_url: user?.avatar_url || '',
    });
    const [loading, setLoading] = useState(false);
    const [saved, setSaved] = useState(false);
    const [error, setError] = useState('');

    function update(field) {
        return (e) => {
            setForm((prev) => ({ ...prev, [field]: e.target.value }));
            setSaved(false);
        };
    }

    async function handleSubmit(e) {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            await updateProfile(form);
            setSaved(true);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to update profile');
        } finally {
            setLoading(false);
        }
    }

    return (
        <div style={{ maxWidth: 600, margin: '0 auto', padding: `calc(var(--navbar-height) + var(--space-2xl)) var(--space-lg) var(--space-2xl)` }}>
            <h1 style={{ marginBottom: 'var(--space-xl)' }}>Profile</h1>

            <div className="card" style={{ padding: 'var(--space-xl)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-lg)', marginBottom: 'var(--space-xl)' }}>
                    {user?.avatar_url ? (
                        <img src={user.avatar_url} alt="" className="avatar" style={{ width: 64, height: 64 }} />
                    ) : (
                        <span className="avatar" style={{ width: 64, height: 64, fontSize: 'var(--text-xl)' }}>
                            {(user?.display_name || user?.username)?.[0]}
                        </span>
                    )}
                    <div>
                        <div style={{ fontWeight: 700, fontSize: 'var(--text-lg)' }}>{user?.display_name || user?.username}</div>
                        <div style={{ color: 'var(--text-muted)', fontSize: 'var(--text-sm)' }}>{user?.email}</div>
                        <span className="badge badge-accent" style={{ marginTop: 'var(--space-xs)' }}>{user?.role}</span>
                    </div>
                </div>

                {error && <div className="auth-error" style={{ marginBottom: 'var(--space-md)' }}>{error}</div>}
                {saved && (
                    <div style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)', color: 'var(--success)', padding: 'var(--space-sm) var(--space-md)', borderRadius: 'var(--radius-md)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-md)' }}>
                        Profile updated successfully
                    </div>
                )}

                <form style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }} onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label" htmlFor="prof-display">Display Name</label>
                        <input id="prof-display" className="input" value={form.display_name} onChange={update('display_name')} placeholder="Your display name" />
                    </div>

                    <div className="form-group">
                        <label className="form-label" htmlFor="prof-avatar">Avatar URL</label>
                        <input id="prof-avatar" className="input" value={form.avatar_url} onChange={update('avatar_url')} placeholder="https://example.com/photo.jpg" />
                    </div>

                    <div className="form-group">
                        <label className="form-label" htmlFor="prof-bio">Bio</label>
                        <textarea id="prof-bio" className="textarea" value={form.bio} onChange={update('bio')} placeholder="Tell us about yourself" style={{ minHeight: 100 }} />
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={loading} style={{ alignSelf: 'flex-end' }}>
                        {loading ? 'Saving…' : 'Save Changes'}
                    </button>
                </form>
            </div>
        </div>
    );
}
