"""Tests for AI agent and schemas."""

import pytest
from unittest.mock import patch, MagicMock

from src.ai.schemas import ChatInput, ChatMessageSchema, ConversationSchema
from datetime import datetime, timezone
from uuid import uuid4


class TestChatSchemas:
    def test_chat_input_valid(self):
        ci = ChatInput(message="What is AAPL price?")
        assert ci.message == "What is AAPL price?"
        assert ci.conversation_id is None

    def test_chat_input_with_conversation(self):
        cid = uuid4()
        ci = ChatInput(message="Follow up", conversation_id=cid)
        assert ci.conversation_id == cid

    def test_chat_input_too_short(self):
        with pytest.raises(Exception):
            ChatInput(message="")

    def test_message_schema(self):
        msg = ChatMessageSchema(
            id=uuid4(),
            role="user",
            content="Hello",
            created_at=datetime.now(timezone.utc),
        )
        assert msg.role == "user"

    def test_conversation_schema(self):
        conv = ConversationSchema(
            id=uuid4(),
            title="Test Chat",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        assert conv.title == "Test Chat"


class TestAgentCreation:
    @patch("src.ai.agent.settings")
    def test_no_api_key_returns_none(self, mock_settings):
        mock_settings.OPENAI_API_KEY = ""
        mock_settings.OPENAI_MODEL = "gpt-4o-mini"
        from src.ai.agent import create_agent
        result = create_agent()
        assert result is None

    @patch("src.ai.agent.settings")
    def test_with_api_key_returns_config(self, mock_settings):
        mock_settings.OPENAI_API_KEY = "sk-test-key-123"
        mock_settings.OPENAI_MODEL = "gpt-4o-mini"
        from src.ai.agent import create_agent
        result = create_agent()
        assert result is not None
        assert "llm" in result
        assert "prompt" in result
        assert "tools" in result
        assert len(result["tools"]) == 3
