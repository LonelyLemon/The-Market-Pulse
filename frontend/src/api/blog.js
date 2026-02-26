/** Blog-related API calls */
import { api } from './client';

export const postApi = {
    list: (params = {}) => api.get('/posts/', { params }),
    search: (q, params = {}) => api.get('/posts/search', { params: { q, ...params } }),
    getBySlug: (slug) => api.get(`/posts/${slug}`),
    create: (data) => api.post('/posts/', data),
    update: (id, data) => api.patch(`/posts/${id}`, data),
    remove: (id) => api.delete(`/posts/${id}`),
};

export const commentApi = {
    list: (postId, params = {}) => api.get(`/posts/${postId}/comments`, { params }),
    create: (postId, data) => api.post(`/posts/${postId}/comments`, data),
    update: (commentId, data) => api.patch(`/posts/comments/${commentId}`, data),
    remove: (commentId) => api.delete(`/posts/comments/${commentId}`),
};

export const likeApi = {
    toggle: (postId) => api.post(`/posts/${postId}/likes`),
    count: (postId) => api.get(`/posts/${postId}/likes`),
};

export const shareApi = {
    record: (postId, platform) => api.post(`/posts/${postId}/shares`, { platform }),
    count: (postId) => api.get(`/posts/${postId}/shares`),
};

export const categoryApi = {
    list: () => api.get('/categories/'),
    create: (data) => api.post('/categories/', data),
    update: (id, data) => api.patch(`/categories/${id}`, data),
    remove: (id) => api.delete(`/categories/${id}`),
};

export const tagApi = {
    list: () => api.get('/tags/'),
};
