import { useState, useRef, useEffect } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { HiOutlineSearch, HiOutlinePencilAlt, HiOutlineUser, HiOutlineLogout, HiMenu } from 'react-icons/hi';
import useAuthStore from '../../stores/authStore';
import './Navbar.css';

export default function Navbar() {
    const { user, isAuthenticated, logout, isAuthor } = useAuthStore();
    const navigate = useNavigate();
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const dropdownRef = useRef(null);

    // Close dropdown when clicking outside
    useEffect(() => {
        function handleClick(e) {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
                setDropdownOpen(false);
            }
        }
        document.addEventListener('mousedown', handleClick);
        return () => document.removeEventListener('mousedown', handleClick);
    }, []);

    function handleSearch(e) {
        e.preventDefault();
        if (searchQuery.trim()) {
            navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
            setSearchQuery('');
        }
    }

    function handleLogout() {
        logout();
        setDropdownOpen(false);
        navigate('/');
    }

    const initials = user?.display_name?.[0] || user?.username?.[0] || '?';

    return (
        <nav className="navbar" role="navigation">
            <div className="navbar-inner">
                {/* Brand */}
                <Link to="/" className="navbar-brand">
                    <svg viewBox="0 0 28 28" fill="none"><path d="M4 20L10 10L16 16L24 4" stroke="url(#g)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" /><defs><linearGradient id="g" x1="4" y1="12" x2="24" y2="12" gradientUnits="userSpaceOnUse"><stop stopColor="#3b82f6" /><stop offset="1" stopColor="#8b5cf6" /></linearGradient></defs></svg>
                    <span>The<span className="brand-highlight">Market</span>Pulse</span>
                </Link>

                {/* Nav Links */}
                <ul className="navbar-links">
                    <li><NavLink to="/" end className={({ isActive }) => `navbar-link${isActive ? ' active' : ''}`}>Home</NavLink></li>
                    <li><NavLink to="/posts" className={({ isActive }) => `navbar-link${isActive ? ' active' : ''}`}>Blog</NavLink></li>
                    <li><NavLink to="/market" className={({ isActive }) => `navbar-link${isActive ? ' active' : ''}`}>Market</NavLink></li>
                </ul>

                {/* Search */}
                <form className="navbar-search" onSubmit={handleSearch}>
                    <HiOutlineSearch className="navbar-search-icon" />
                    <input
                        className="input"
                        placeholder="Search posts..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </form>

                {/* Actions */}
                <div className="navbar-actions">
                    {isAuthenticated ? (
                        <>
                            {isAuthor() && (
                                <Link to="/editor" className="btn btn-primary btn-sm">
                                    <HiOutlinePencilAlt /> Write
                                </Link>
                            )}

                            <div className="navbar-user-menu" ref={dropdownRef}>
                                <button className="navbar-user-btn" onClick={() => setDropdownOpen(!dropdownOpen)}>
                                    {user?.avatar_url ? (
                                        <img src={user.avatar_url} alt="" className="avatar" style={{ width: 32, height: 32 }} />
                                    ) : (
                                        <span className="avatar" style={{ width: 32, height: 32, fontSize: '0.75rem' }}>{initials}</span>
                                    )}
                                </button>

                                {dropdownOpen && (
                                    <div className="navbar-dropdown">
                                        <div style={{ padding: '0.5rem 0.75rem', borderBottom: '1px solid var(--border)' }}>
                                            <div style={{ fontWeight: 600, fontSize: 'var(--text-sm)' }}>{user?.display_name || user?.username}</div>
                                            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>{user?.email}</div>
                                        </div>
                                        <Link to="/profile" onClick={() => setDropdownOpen(false)}>
                                            <HiOutlineUser /> Profile
                                        </Link>
                                        <div className="divider" />
                                        <button onClick={handleLogout}>
                                            <HiOutlineLogout /> Sign Out
                                        </button>
                                    </div>
                                )}
                            </div>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="btn btn-ghost btn-sm">Sign In</Link>
                            <Link to="/register" className="btn btn-primary btn-sm">Get Started</Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
}
