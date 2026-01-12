from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base_model import Base


class User(Base):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
