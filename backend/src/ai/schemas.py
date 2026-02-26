"""Pydantic schemas for the chat module."""

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class ChatMessageSchema(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationSchema(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetailSchema(ConversationSchema):
    messages: list[ChatMessageSchema] = []


class ChatInput(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: UUID | None = None
