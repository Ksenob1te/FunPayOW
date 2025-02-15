from sqlalchemy import ForeignKey, DateTime, func
from uuid import uuid4, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base
from datetime import datetime



class User(Base):
    __tablename__ = "user_table"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    chat_id: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)

    is_admin: Mapped[bool] = mapped_column(default=False)

    balance: Mapped[int] = mapped_column(default=0)

    def __repr__(self) -> str:
        return (f"User(id={self.id}, chat_id={self.chat_id}, username={self.username},"
                f" first_name={self.first_name}, last_name={self.last_name})")


class Codes(Base):
    __tablename__ = "codes_table"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(nullable=False, unique=True)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user_table.id"))
    user: Mapped[User] = relationship(lazy="selectin")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    status: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return f"Code(id={self.id}, status={self.status})"


class Static(Base):
    __tablename__ = "static_table"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(nullable=False, unique=True)
    value: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return f"Static(id={self.id}, code={self.code}, value={self.code})"



