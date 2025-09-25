from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, JSON, UniqueConstraint


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_name: Mapped[str] = mapped_column(String(100), nullable=False)

    user_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    __table_args__ = (
        UniqueConstraint("user_email", name="uq_users_user_email"),
    )

    age: Mapped[int | None] = mapped_column(Integer, nullable=True)

    recommendations: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    ZIP: Mapped[str | None] = mapped_column(String(20), nullable=True)
