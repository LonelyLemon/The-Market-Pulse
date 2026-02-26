"""Blog full-text search utilities using PostgreSQL tsvector/tsquery."""

from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.blog.models import Post


async def search_posts(
    db: AsyncSession,
    query: str,
    *,
    limit: int = 20,
    offset: int = 0,
    status_filter: str = "published",
):
    """Search posts using PostgreSQL full-text search.
    
    Uses plainto_tsquery for natural language queries and
    ts_rank_cd for relevance ranking.
    """
    ts_query = func.plainto_tsquery("english", query)

    stmt = (
        select(Post)
        .where(Post.search_vector.op("@@")(ts_query))
        .where(Post.status == status_filter)
        .order_by(func.ts_rank_cd(Post.search_vector, ts_query).desc())
        .offset(offset)
        .limit(limit)
    )

    count_stmt = (
        select(func.count())
        .select_from(Post)
        .where(Post.search_vector.op("@@")(ts_query))
        .where(Post.status == status_filter)
    )

    result = await db.execute(stmt)
    count_result = await db.execute(count_stmt)

    return result.scalars().all(), count_result.scalar_one()
