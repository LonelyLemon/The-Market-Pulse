import { Link } from 'react-router-dom';
import './Footer.css';

export default function Footer() {
    return (
        <footer className="footer">
            <div className="footer-inner">
                <div className="footer-brand">
                    <Link to="/" className="navbar-brand" style={{ fontSize: 'var(--text-lg)' }}>
                        <span>The<span className="brand-highlight">Market</span>Pulse</span>
                    </Link>
                    <p>Financial insights, market analysis, and trading ideas for the modern investor.</p>
                </div>

                <div className="footer-col">
                    <h4>Navigate</h4>
                    <Link to="/">Home</Link>
                    <Link to="/posts">Blog</Link>
                    <Link to="/search">Search</Link>
                </div>

                <div className="footer-col">
                    <h4>Connect</h4>
                    <a href="https://twitter.com" target="_blank" rel="noopener noreferrer">X (Twitter)</a>
                    <a href="https://github.com" target="_blank" rel="noopener noreferrer">GitHub</a>
                    <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer">LinkedIn</a>
                </div>
            </div>

            <div className="footer-bottom">
                <span>&copy; {new Date().getFullYear()} The Market Pulse. All rights reserved.</span>
            </div>
        </footer>
    );
}
