import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { HiOutlineArrowRight, HiOutlineEye, HiOutlineHeart, HiOutlineChatAlt } from 'react-icons/hi';
import { postApi } from '../../api/blog';
import { format } from 'date-fns';
import '../Pages.css';

export default function HomePage() {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        postApi.list({ per_page: 6 })
            .then(({ data }) => setPosts(data.items))
            .catch(() => { })
            .finally(() => setLoading(false));
    }, []);

    return (
        <>
            {/* Hero */}
            <section className="home-hero">
                <h1>
                    Financial insights for the<br />
                    <span className="brand-highlight">modern investor</span>
                </h1>
                <p className="hero-desc">
                    Market analysis, trading ideas, and investment strategies — delivered with clarity and depth.
                </p>
                <div className="hero-actions">
                    <Link to="/posts" className="btn btn-primary">
                        Explore Blog <HiOutlineArrowRight />
                    </Link>
                    <Link to="/register" className="btn btn-secondary">
                        Join Community
                    </Link>
                </div>
            </section>

            {/* Latest Posts */}
            <section className="home-section">
                <div className="home-section-header">
                    <h2>Latest Posts</h2>
                    <Link to="/posts" className="btn btn-ghost btn-sm">
                        View all <HiOutlineArrowRight />
                    </Link>
                </div>

                {loading ? (
                    <div className="loading-center"><div className="spinner" /></div>
                ) : posts.length === 0 ? (
                    <div className="empty-state">
                        <h3>No posts yet</h3>
                        <p>Check back soon for fresh market insights</p>
                    </div>
                ) : (
                    <div className="posts-grid">
                        {posts.map((post) => (
                            <PostCard key={post.id} post={post} />
                        ))}
                    </div>
                )}
            </section>
        </>
    );
}

function PostCard({ post }) {
    return (
        <article className="post-card">
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
    );
}
