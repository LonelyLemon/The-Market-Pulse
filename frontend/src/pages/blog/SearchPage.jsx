import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { HiOutlineSearch, HiOutlineEye, HiOutlineHeart } from 'react-icons/hi';
import { postApi } from '../../api/blog';
import { format } from 'date-fns';
import '../Pages.css';

export default function SearchPage() {
    const [searchParams, setSearchParams] = useSearchParams();
    const [query, setQuery] = useState(searchParams.get('q') || '');
    const [posts, setPosts] = useState([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(false);
    const [searched, setSearched] = useState(false);

    const q = searchParams.get('q') || '';

    useEffect(() => {
        if (!q) return;
        setLoading(true);
        setSearched(true);
        postApi.search(q, { per_page: 20 })
            .then(({ data }) => {
                setPosts(data.items);
                setTotal(data.total);
            })
            .catch(() => { })
            .finally(() => setLoading(false));
    }, [q]);

    function handleSearch(e) {
        e.preventDefault();
        if (query.trim()) {
            setSearchParams({ q: query.trim() });
        }
    }

    return (
        <div className="search-page">
            <div className="search-header">
                <h1>Search</h1>
                <form className="search-form" onSubmit={handleSearch} style={{ marginTop: 'var(--space-lg)' }}>
                    <input
                        className="input"
                        placeholder="Search posts, topics, ideas…"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                    />
                    <button type="submit" className="btn btn-primary">
                        <HiOutlineSearch /> Search
                    </button>
                </form>
                {searched && !loading && (
                    <p className="search-results-count">
                        {total} result{total !== 1 ? 's' : ''} for &ldquo;{q}&rdquo;
                    </p>
                )}
            </div>

            {loading ? (
                <div className="loading-center"><div className="spinner" /></div>
            ) : searched && posts.length === 0 ? (
                <div className="empty-state">
                    <h3>No results found</h3>
                    <p>Try different keywords</p>
                </div>
            ) : (
                <div className="posts-grid">
                    {posts.map((post) => (
                        <article key={post.id} className="post-card">
                            {post.cover_image_url ? (
                                <img src={post.cover_image_url} alt="" className="post-card-cover" />
                            ) : (
                                <div className="post-card-cover-placeholder">📈</div>
                            )}
                            <div className="post-card-body">
                                <div className="post-card-meta">
                                    {post.category && <span className="badge badge-accent">{post.category.name}</span>}
                                    <span>{format(new Date(post.created_at), 'MMM d, yyyy')}</span>
                                </div>
                                <h3 className="post-card-title">
                                    <Link to={`/posts/${post.slug}`}>{post.title}</Link>
                                </h3>
                                <p className="post-card-excerpt">{post.excerpt}</p>
                                <div className="post-card-footer">
                                    <span>{post.author?.display_name || post.author?.username}</span>
                                    <div className="post-card-stats">
                                        <span><HiOutlineEye /> {post.view_count}</span>
                                        <span><HiOutlineHeart /> {post.like_count || 0}</span>
                                    </div>
                                </div>
                            </div>
                        </article>
                    ))}
                </div>
            )}
        </div>
    );
}
