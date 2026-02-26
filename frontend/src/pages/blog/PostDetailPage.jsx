import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { HiOutlineHeart, HiHeart, HiOutlineShare, HiOutlineEye, HiOutlineClock } from 'react-icons/hi';
import { FaXTwitter, FaFacebook, FaLinkedin } from 'react-icons/fa6';
import { postApi, likeApi, commentApi, shareApi } from '../../api/blog';
import useAuthStore from '../../stores/authStore';
import { format } from 'date-fns';
import '../Pages.css';

export default function PostDetailPage() {
    const { slug } = useParams();
    const { user, isAuthenticated } = useAuthStore();
    const [post, setPost] = useState(null);
    const [loading, setLoading] = useState(true);
    const [liked, setLiked] = useState(false);
    const [likeCount, setLikeCount] = useState(0);
    const [comments, setComments] = useState([]);
    const [commentText, setCommentText] = useState('');
    const [submittingComment, setSubmittingComment] = useState(false);

    useEffect(() => {
        setLoading(true);
        postApi.getBySlug(slug)
            .then(({ data }) => {
                setPost(data);
                setLikeCount(data.like_count || 0);
                // Load comments
                commentApi.list(data.id).then(({ data: d }) => setComments(d.items || [])).catch(() => { });
            })
            .catch(() => { })
            .finally(() => setLoading(false));
    }, [slug]);

    async function handleLike() {
        if (!isAuthenticated) return;
        try {
            const { data } = await likeApi.toggle(post.id);
            setLiked(data.liked);
            setLikeCount(data.total_likes);
        } catch { /* noop */ }
    }

    async function handleComment(e) {
        e.preventDefault();
        if (!commentText.trim()) return;
        setSubmittingComment(true);
        try {
            const { data } = await commentApi.create(post.id, { body: commentText });
            setComments((prev) => [data, ...prev]);
            setCommentText('');
        } catch { /* noop */ }
        setSubmittingComment(false);
    }

    async function handleShare(platform) {
        if (post?.share_urls?.[platform]) {
            window.open(post.share_urls[platform], '_blank', 'width=600,height=400');
            if (isAuthenticated) {
                shareApi.record(post.id, platform).catch(() => { });
            }
        }
    }

    if (loading) {
        return <div className="loading-center" style={{ minHeight: '80vh' }}><div className="spinner" /></div>;
    }

    if (!post) {
        return (
            <div className="post-detail" style={{ textAlign: 'center' }}>
                <h1>Post not found</h1>
                <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-lg)' }}>
                    This post doesn&apos;t exist or has been removed.
                </p>
                <Link to="/posts" className="btn btn-primary">Back to Blog</Link>
            </div>
        );
    }

    return (
        <article className="post-detail">
            {post.cover_image_url && (
                <img src={post.cover_image_url} alt="" className="post-detail-cover" />
            )}

            <h1>{post.title}</h1>

            <div className="post-detail-meta">
                <div className="post-detail-author">
                    <span className="avatar" style={{ width: 36, height: 36, fontSize: '0.875rem' }}>
                        {(post.author?.display_name || post.author?.username)?.[0]}
                    </span>
                    <span style={{ fontWeight: 600 }}>{post.author?.display_name || post.author?.username}</span>
                </div>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <HiOutlineClock /> {format(new Date(post.created_at), 'MMM d, yyyy')}
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <HiOutlineEye /> {post.view_count} views
                </span>
                {post.category && (
                    <Link to={`/posts?category=${post.category.slug}`} className="badge badge-accent">
                        {post.category.name}
                    </Link>
                )}
            </div>

            {/* Post content */}
            <div
                className="post-detail-content"
                dangerouslySetInnerHTML={{ __html: post.content_html }}
            />

            {/* Tags */}
            {post.tags?.length > 0 && (
                <div style={{ display: 'flex', gap: 'var(--space-sm)', flexWrap: 'wrap', margin: 'var(--space-lg) 0' }}>
                    {post.tags.map((tag) => (
                        <span key={tag.id} className="badge badge-accent">#{tag.name}</span>
                    ))}
                </div>
            )}

            {/* Social bar */}
            <div className="social-bar">
                <button
                    className={`btn btn-ghost btn-sm like-btn${liked ? ' liked' : ''}`}
                    onClick={handleLike}
                    disabled={!isAuthenticated}
                >
                    {liked ? <HiHeart /> : <HiOutlineHeart />} {likeCount}
                </button>

                <div style={{ marginLeft: 'auto', display: 'flex', gap: 'var(--space-sm)' }}>
                    <button className="btn btn-ghost btn-sm" onClick={() => handleShare('x')} title="Share on X">
                        <FaXTwitter />
                    </button>
                    <button className="btn btn-ghost btn-sm" onClick={() => handleShare('facebook')} title="Share on Facebook">
                        <FaFacebook />
                    </button>
                    <button className="btn btn-ghost btn-sm" onClick={() => handleShare('linkedin')} title="Share on LinkedIn">
                        <FaLinkedin />
                    </button>
                </div>
            </div>

            {/* Comments */}
            <section className="comments-section">
                <h3>Comments ({comments.length})</h3>

                {isAuthenticated && (
                    <form className="comment-form" onSubmit={handleComment}>
                        <textarea
                            className="textarea"
                            placeholder="Write a comment…"
                            value={commentText}
                            onChange={(e) => setCommentText(e.target.value)}
                        />
                        <button type="submit" className="btn btn-primary btn-sm" disabled={submittingComment}>
                            {submittingComment ? 'Posting…' : 'Post'}
                        </button>
                    </form>
                )}

                {comments.length === 0 ? (
                    <div className="empty-state" style={{ padding: 'var(--space-xl)' }}>
                        <p>No comments yet. Be the first to share your thoughts!</p>
                    </div>
                ) : (
                    comments.map((c) => (
                        <div key={c.id} className="comment">
                            <div className="comment-header">
                                <div className="comment-author">
                                    <span className="avatar" style={{ width: 28, height: 28, fontSize: '0.7rem' }}>
                                        {(c.author?.display_name || c.author?.username)?.[0]}
                                    </span>
                                    {c.author?.display_name || c.author?.username}
                                </div>
                                <span className="comment-time">{format(new Date(c.created_at), 'MMM d, yyyy')}</span>
                            </div>
                            <div className="comment-body">{c.body}</div>
                        </div>
                    ))
                )}
            </section>
        </article>
    );
}
