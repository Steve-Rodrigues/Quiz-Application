from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from datetime import datetime, timezone

#user storage: id, email(this is login method), pwd hash, display_name, created_at
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    password_hash: Mapped[str] 
    display_name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
