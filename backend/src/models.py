"""Central model imports — all models must be imported here for Alembic autogenerate."""

from src.auth.models import User  # noqa: F401
from src.blog.models import (  # noqa: F401
    Category,
    Comment,
    Like,
    Post,
    PostTag,
    Share,
    Tag,
)
from src.market.models import Asset, Candle  # noqa: F401
from src.ai.models import ChatConversation, ChatMessage  # noqa: F401