import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { HiOutlineEye, HiOutlineHeart, HiOutlineChatAlt } from 'react-icons/hi';
import { postApi, categoryApi } from '../../api/blog';
import { format } from 'date-fns';
import '../Pages.css';

export default function PostListPage() {
    const [searchParams, setSearchParams] = useSearchParams();
    const [posts, setPosts] = useState([]);
    const [categories, setCategories] = useState([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);

    const page = parseInt(searchParams.get('page') || '1');
    const activeCategory = searchParams.get('category') || '';
    const perPage = 9;

    useEffect(() => {
        categoryApi.list().then(({ data }) => setCategories(data)).catch(() => { });
    }, []);

    useEffect(() => {
        setLoading(true);
        const params = { page, per_page: perPage };
        if (activeCategory) params.category = activeCategory;

        postApi.list(params)
            .then(({ data }) => {
                setPosts(data.items);
                setTotal(data.total);
            })
            .catch(() => { })
            .finally(() => setLoading(false));
    }, [page, activeCategory]);

    function setPage(p) {
        const params = new URLSearchParams(searchParams);
        params.set('page', p);
        setSearchParams(params);
    }

    function filterCategory(slug) {
        const params = new URLSearchParams(searchParams);
        if (slug) {
            params.set('category', slug);
        } else {
            params.delete('category');
        }
        params.set('page', '1');
        setSearchParams(params);
    }

    const totalPages = Math.ceil(total / perPage);

    return (
        <div style={{ maxWidth: 'var(--max-content)', margin: '0 auto', padding: `calc(var(--navbar-height) + var(--space-2xl)) var(--space-lg) var(--space-2xl)` }}>
            <h1 style={{ marginBottom: 'var(--space-lg)' }}>Blog</h1>

            {/* Category filter */}
            {categories.length > 0 && (
                <div style={{ display: 'flex', gap: 'var(--space-sm)', marginBottom: 'var(--space-xl)', flexWrap: 'wrap' }}>
                    <button
                        className={`btn btn-sm ${!activeCategory ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => filterCategory('')}
                    >All</button>
                    {categories.map((cat) => (
                        <button
                            key={cat.id}
                            className={`btn btn-sm ${activeCategory === cat.slug ? 'btn-primary' : 'btn-secondary'}`}
                            onClick={() => filterCategory(cat.slug)}
                        >{cat.name}</button>
                    ))}
                </div>
            )}

            {/* Posts grid */}
            {loading ? (
                <div className="loading-center"><div className="spinner" /></div>
            ) : posts.length === 0 ? (
                <div className="empty-state">
                    <h3>No posts found</h3>
                    <p>Try a different category or check back later</p>
                </div>
            ) : (
                <>
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
                                            <span><HiOutlineChatAlt /> {post.comment_count || 0}</span>
                                        </div>
                                    </div>
                                </div>
                            </article>
                        ))}
                    </div>

                    {/* Pagination */}
                    {totalPages > 1 && (
                        <div className="pagination">
                            <button className="btn btn-secondary btn-sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
                                Previous
                            </button>
                            <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>
                                Page {page} of {totalPages}
                            </span>
                            <button className="btn btn-secondary btn-sm" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
                                Next
                            </button>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
