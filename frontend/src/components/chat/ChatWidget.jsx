import { useState, useRef, useEffect, useCallback } from 'react';
import { HiOutlineChat, HiOutlineX } from 'react-icons/hi';
import { IoSend } from 'react-icons/io5';
import useAuthStore from '../../stores/authStore';
import { chatApi } from '../../api/chat';
import './Chat.css';

export default function ChatWidget() {
    const { isAuthenticated } = useAuthStore();
    const [open, setOpen] = useState(false);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [conversationId, setConversationId] = useState(null);
    const messagesEndRef = useRef(null);
    const wsRef = useRef(null);

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Cleanup WS on unmount
    useEffect(() => {
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
                wsRef.current = null;
            }
        };
    }, []);

    const connectWs = useCallback(() => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;

        const ws = chatApi.createWs();
        wsRef.current = ws;

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'chunk') {
                setMessages((prev) => {
                    const last = prev[prev.length - 1];
                    if (last && last.role === 'assistant' && last.streaming) {
                        return [
                            ...prev.slice(0, -1),
                            { ...last, content: last.content + data.content },
                        ];
                    } else {
                        return [...prev, { role: 'assistant', content: data.content, streaming: true }];
                    }
                });
            } else if (data.type === 'done') {
                setConversationId(data.conversation_id);
                setMessages((prev) =>
                    prev.map((m) => (m.streaming ? { ...m, streaming: false } : m))
                );
                setLoading(false);
            } else if (data.type === 'error') {
                setMessages((prev) => [
                    ...prev,
                    { role: 'assistant', content: `Error: ${data.content}` },
                ]);
                setLoading(false);
            }
        };

        ws.onerror = () => {
            setLoading(false);
        };

        ws.onclose = () => {
            wsRef.current = null;
        };

        return ws;
    }, []);

    async function handleSend(e) {
        e.preventDefault();
        const text = input.trim();
        if (!text || loading) return;

        setInput('');
        setMessages((prev) => [...prev, { role: 'user', content: text }]);
        setLoading(true);

        // Try WebSocket first
        try {
            let ws = wsRef.current;
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                ws = connectWs();
                // Wait for connection
                await new Promise((resolve, reject) => {
                    ws.onopen = resolve;
                    ws.onerror = reject;
                    setTimeout(reject, 3000);
                });
            }

            ws.send(JSON.stringify({
                message: text,
                conversation_id: conversationId,
            }));
        } catch {
            // Fallback to REST
            try {
                const { data } = await chatApi.sendMessage(text, conversationId);
                setConversationId(data.conversation_id);
                setMessages((prev) => [...prev, { role: 'assistant', content: data.message }]);
            } catch (err) {
                setMessages((prev) => [
                    ...prev,
                    { role: 'assistant', content: 'Sorry, I couldn\'t process your request. Please try again.' },
                ]);
            }
            setLoading(false);
        }
    }

    function handleNewChat() {
        setMessages([]);
        setConversationId(null);
    }

    if (!isAuthenticated) return null;

    return (
        <>
            {/* FAB */}
            <button className="chat-fab" onClick={() => setOpen(!open)} title="AI Assistant">
                {open ? <HiOutlineX /> : <HiOutlineChat />}
            </button>

            {/* Panel */}
            {open && (
                <div className="chat-panel">
                    <div className="chat-header">
                        <h3>
                            <span className="status-dot" /> PulseAI
                        </h3>
                        <button onClick={handleNewChat} title="New chat">⟳</button>
                    </div>

                    <div className="chat-messages">
                        {messages.length === 0 && (
                            <div className="chat-welcome">
                                <h4>👋 Hi! I&apos;m PulseAI</h4>
                                <p>Ask me about stock prices, market trends, or financial concepts.</p>
                                <p style={{ fontSize: 'var(--text-xs)', marginTop: 'var(--space-sm)' }}>
                                    Try: &quot;What&apos;s the price of AAPL?&quot;
                                </p>
                            </div>
                        )}
                        {messages.map((msg, i) => (
                            <div
                                key={i}
                                className={`chat-msg ${msg.role}${msg.streaming ? ' typing' : ''}`}
                            >
                                {msg.content}
                            </div>
                        ))}
                        {loading && messages[messages.length - 1]?.role !== 'assistant' && (
                            <div className="chat-msg typing">Thinking…</div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    <form className="chat-input-area" onSubmit={handleSend}>
                        <input
                            placeholder="Ask about stocks, crypto…"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            disabled={loading}
                        />
                        <button type="submit" disabled={loading || !input.trim()}>
                            <IoSend />
                        </button>
                    </form>
                </div>
            )}
        </>
    );
}
