import { api } from './client';

export const chatApi = {
    /** List conversations */
    listConversations: () => api.get('/chat/conversations'),

    /** Get conversation with messages */
    getConversation: (id) => api.get(`/chat/conversations/${id}`),

    /** Delete conversation */
    deleteConversation: (id) => api.delete(`/chat/conversations/${id}`),

    /** Send message (non-streaming fallback) */
    sendMessage: (message, conversationId) =>
        api.post('/chat/send', { message, conversation_id: conversationId }),

    /** Create WebSocket connection for streaming */
    createWs: () => {
        const token = localStorage.getItem('access_token');
        const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
        return new WebSocket(`${proto}://${window.location.host}/api/v1/chat/ws?token=${token}`);
    },
};
