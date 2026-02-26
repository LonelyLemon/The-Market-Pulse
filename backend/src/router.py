from fastapi import APIRouter

from src.blog.router import blog_route, category_route, tag_route
from src.market.router import market_route
from src.ai.router import chat_route


api_router = APIRouter(
    prefix="/api/v1"
)

api_router.include_router(blog_route)
api_router.include_router(category_route)
api_router.include_router(tag_route)
api_router.include_router(market_route)
api_router.include_router(chat_route)

