from sqlalchemy import String, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base_model import Base
from src.market.constants import AssetType

class Asset(Base):
    __tablename__ = 'assets'

    symbol: Mapped[str] = mapped_column(String(50), 
                                        nullable=False, 
                                        unique=True)
    asset_name: Mapped[str] = mapped_column(String(100), 
                                            nullable=False, 
                                            unique=True)
    asset_type: Mapped[str] = mapped_column(String(50), 
                                            Enum(AssetType, name="asset_type_enum"),
                                            nullable=False, 
                                            unique=False)