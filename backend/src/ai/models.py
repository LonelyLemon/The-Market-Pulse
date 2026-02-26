"""Chat conversation model for persisting AI conversations."""

import uuid
from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, TIMESTAMP, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import Base


class ChatConversation(Base):
    """A chat conversation/session belonging to a user."""
    __tablename__ = 'chat_conversations'

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, default="New Chat")

    # Relationships
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", order_by="ChatMessage.created_at"
    )


class ChatMessage(Base):
    """Individual message in a chat conversation."""
    __tablename__ = 'chat_messages'

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user | assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    conversation: Mapped["ChatConversation"] = relationship(back_populates="messages")
