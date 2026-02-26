"""Chat router — REST + WebSocket endpoints for AI assistant."""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth.dependencies import get_current_user
from src.core.database import SessionDep, get_session
from src.ai.models import ChatConversation, ChatMessage
from src.ai.schemas import ConversationSchema, ConversationDetailSchema, ChatInput
from src.ai.agent import create_agent, run_agent
from src.auth.models import User

chat_route = APIRouter(prefix="/chat", tags=["AI Chat"])


# ═══════════════════════════════════════════════════════════
#  REST — Conversation management
# ═══════════════════════════════════════════════════════════

@chat_route.get("/conversations", response_model=list[ConversationSchema])
async def list_conversations(db: SessionDep, user: User = Depends(get_current_user)):
    """List all conversations for the current user."""
    result = await db.execute(
        select(ChatConversation)
        .where(ChatConversation.user_id == user.id)
        .order_by(ChatConversation.updated_at.desc())
    )
    return list(result.scalars().all())


@chat_route.get("/conversations/{conversation_id}", response_model=ConversationDetailSchema)
async def get_conversation(conversation_id: uuid.UUID, db: SessionDep, user: User = Depends(get_current_user)):
    """Get a conversation with all messages."""
    result = await db.execute(
        select(ChatConversation)
        .options(selectinload(ChatConversation.messages))
        .where(ChatConversation.id == conversation_id, ChatConversation.user_id == user.id)
    )
    conv = result.scalar_one_or_none()
    if not conv:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@chat_route.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: uuid.UUID, db: SessionDep, user: User = Depends(get_current_user)):
    """Delete a conversation."""
    result = await db.execute(
        select(ChatConversation)
        .where(ChatConversation.id == conversation_id, ChatConversation.user_id == user.id)
    )
    conv = result.scalar_one_or_none()
    if conv:
        await db.delete(conv)
        await db.commit()


# ═══════════════════════════════════════════════════════════
#  REST — Synchronous chat (non-streaming fallback)
# ═══════════════════════════════════════════════════════════

@chat_route.post("/send")
async def send_message(payload: ChatInput, db: SessionDep, user: User = Depends(get_current_user)):
    """Send a chat message and get a complete response (non-streaming)."""
    agent = create_agent()

    # Get or create conversation
    conv = None
    if payload.conversation_id:
        result = await db.execute(
            select(ChatConversation).options(selectinload(ChatConversation.messages))
            .where(ChatConversation.id == payload.conversation_id, ChatConversation.user_id == user.id)
        )
        conv = result.scalar_one_or_none()

    if not conv:
        conv = ChatConversation(user_id=user.id, title=payload.message[:100])
        db.add(conv)
        await db.flush()

    # Save user message
    user_msg = ChatMessage(conversation_id=conv.id, role="user", content=payload.message)
    db.add(user_msg)

    # Build history
    history = [{"role": m.role, "content": m.content} for m in (conv.messages or [])]

    # Run agent
    full_response = ""
    async for chunk in run_agent(agent, payload.message, history):
        full_response += chunk

    # Save assistant message
    ai_msg = ChatMessage(conversation_id=conv.id, role="assistant", content=full_response)
    db.add(ai_msg)
    await db.commit()

    return {
        "conversation_id": str(conv.id),
        "message": full_response,
    }


# ═══════════════════════════════════════════════════════════
#  WEBSOCKET — Streaming chat
# ═══════════════════════════════════════════════════════════

@chat_route.websocket("/ws")
async def chat_websocket(
    websocket: WebSocket,
    token: str = Query(...),
):
    """
    WebSocket endpoint for streaming AI chat.
    
    Connect: ws://host/api/v1/chat/ws?token=<JWT>
    
    Client sends: {"message": "...", "conversation_id": "..."}
    Server streams: {"type": "chunk", "content": "..."} 
                    {"type": "done", "conversation_id": "..."}
                    {"type": "error", "content": "..."}
    """
    await websocket.accept()

    # Authenticate via token
    from src.auth.dependencies import get_user_from_token
    try:
        async for session in get_session():
            user = await get_user_from_token(token, session)
            if not user:
                await websocket.send_json({"type": "error", "content": "Authentication failed"})
                await websocket.close()
                return
            break
    except Exception:
        await websocket.send_json({"type": "error", "content": "Authentication failed"})
        await websocket.close()
        return

    agent = create_agent()

    try:
        while True:
            data = await websocket.receive_json()
            user_message = data.get("message", "").strip()
            conv_id = data.get("conversation_id")

            if not user_message:
                await websocket.send_json({"type": "error", "content": "Empty message"})
                continue

            async for session in get_session():
                # Get or create conversation
                conv = None
                if conv_id:
                    result = await session.execute(
                        select(ChatConversation).options(selectinload(ChatConversation.messages))
                        .where(ChatConversation.id == uuid.UUID(conv_id), ChatConversation.user_id == user.id)
                    )
                    conv = result.scalar_one_or_none()

                if not conv:
                    conv = ChatConversation(user_id=user.id, title=user_message[:100])
                    session.add(conv)
                    await session.flush()

                # Save user message
                session.add(ChatMessage(conversation_id=conv.id, role="user", content=user_message))

                # Build history from previous messages
                history = [{"role": m.role, "content": m.content} for m in (conv.messages or [])]

                # Stream response
                full_response = ""
                async for chunk in run_agent(agent, user_message, history):
                    full_response += chunk
                    await websocket.send_json({"type": "chunk", "content": chunk})

                # Save assistant message
                session.add(ChatMessage(conversation_id=conv.id, role="assistant", content=full_response))
                await session.commit()

                await websocket.send_json({
                    "type": "done",
                    "conversation_id": str(conv.id),
                })
                break  # Break from session generator

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "content": str(e)})
        except Exception:
            pass
