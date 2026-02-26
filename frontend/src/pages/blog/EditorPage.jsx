import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { postApi, categoryApi } from '../../api/blog';
import '../Pages.css';

export default function EditorPage() {
    const navigate = useNavigate();
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const [form, setForm] = useState({
        title: '',
        content_markdown: '',
        excerpt: '',
        cover_image_url: '',
        category_id: '',
        tag_names: '',
        status: 'draft',
    });

    useEffect(() => {
        categoryApi.list().then(({ data }) => setCategories(data)).catch(() => { });
    }, []);

    function update(field) {
        return (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));
    }

    async function handleSubmit(e) {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            const payload = {
                title: form.title,
                content_markdown: form.content_markdown,
                excerpt: form.excerpt || undefined,
                cover_image_url: form.cover_image_url || undefined,
                category_id: form.category_id || undefined,
                tag_names: form.tag_names ? form.tag_names.split(',').map((t) => t.trim()).filter(Boolean) : [],
                status: form.status,
            };
            const { data } = await postApi.create(payload);
            navigate(`/posts/${data.slug}`);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to create post');
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="editor-page">
            <h1>Write a Post</h1>

            {error && <div className="auth-error" style={{ marginBottom: 'var(--space-lg)' }}>{error}</div>}

            <form className="editor-form" onSubmit={handleSubmit}>
                <div className="form-group">
                    <label className="form-label" htmlFor="ed-title">Title</label>
                    <input
                        id="ed-title"
                        className="input"
                        placeholder="Your post title"
                        value={form.title}
                        onChange={update('title')}
                        required
                    />
                </div>

                <div className="form-group">
                    <label className="form-label" htmlFor="ed-excerpt">Excerpt</label>
                    <input
                        id="ed-excerpt"
                        className="input"
                        placeholder="A brief summary (optional)"
                        value={form.excerpt}
                        onChange={update('excerpt')}
                    />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
                    <div className="form-group">
                        <label className="form-label" htmlFor="ed-category">Category</label>
                        <select id="ed-category" className="select" value={form.category_id} onChange={update('category_id')}>
                            <option value="">None</option>
                            {categories.map((c) => (
                                <option key={c.id} value={c.id}>{c.name}</option>
                            ))}
                        </select>
                    </div>

                    <div className="form-group">
                        <label className="form-label" htmlFor="ed-status">Status</label>
                        <select id="ed-status" className="select" value={form.status} onChange={update('status')}>
                            <option value="draft">Draft</option>
                            <option value="published">Published</option>
                        </select>
                    </div>
                </div>

                <div className="form-group">
                    <label className="form-label" htmlFor="ed-tags">Tags</label>
                    <input
                        id="ed-tags"
                        className="input"
                        placeholder="Comma-separated: stocks, crypto, analysis"
                        value={form.tag_names}
                        onChange={update('tag_names')}
                    />
                </div>

                <div className="form-group">
                    <label className="form-label" htmlFor="ed-cover">Cover Image URL</label>
                    <input
                        id="ed-cover"
                        className="input"
                        placeholder="https://example.com/image.jpg"
                        value={form.cover_image_url}
                        onChange={update('cover_image_url')}
                    />
                </div>

                <div className="form-group">
                    <label className="form-label" htmlFor="ed-content">Content (Markdown)</label>
                    <textarea
                        id="ed-content"
                        className="textarea"
                        placeholder="Write your post in Markdown..."
                        value={form.content_markdown}
                        onChange={update('content_markdown')}
                        required
                    />
                </div>

                <div className="editor-actions">
                    <button type="button" className="btn btn-secondary" onClick={() => navigate(-1)}>Cancel</button>
                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? 'Publishing…' : form.status === 'published' ? 'Publish' : 'Save Draft'}
                    </button>
                </div>
            </form>
        </div>
    );
}
