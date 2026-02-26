import uuid
from datetime import datetime

from sqlalchemy import String, Enum, Float, Integer, ForeignKey, UniqueConstraint, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import Base
from src.market.constants import AssetType


class Asset(Base):
    __tablename__ = 'assets'

    symbol: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    asset_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    asset_type: Mapped[str] = mapped_column(
        String(50),
        Enum(AssetType, name="asset_type_enum"),
        nullable=False,
    )

    # Relationships
    candles: Mapped[list["Candle"]] = relationship(back_populates="asset", cascade="all, delete-orphan")


class Candle(Base):
    """OHLCV candlestick data for a given asset and timeframe."""
    __tablename__ = 'candles'
    __table_args__ = (
        UniqueConstraint("asset_id", "timeframe", "timestamp", name="uq_candle_asset_tf_ts"),
    )

    asset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), nullable=False
    )
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False)  # 1d, 1h, 5m, etc.
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, index=True)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    asset: Mapped["Asset"] = relationship(back_populates="candles")