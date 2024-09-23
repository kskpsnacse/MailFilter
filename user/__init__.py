from datetime import datetime
from enum import Enum
from typing import Optional
from db import Base
from mail import MailServerType
from sqlalchemy import Integer, String, DateTime, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column


class UserSyncStatus(Enum):
    READY_TO_FULL_SYNC = "READY_TO_FULL_SYNC"
    FULL_SYNC_DONE = "FULL_SYNC_DONE"
    ERROR = "ERROR"

class UserAuthStatus(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"

class User(Base):
    __tablename__: str = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    mail_server_type: Mapped[MailServerType] = mapped_column(SqlEnum(MailServerType), nullable=False)

class UserStats(Base):
    __tablename__: str = 'user_stats'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    auth_status: Mapped[Optional[UserAuthStatus]] = mapped_column(SqlEnum(UserAuthStatus), nullable=True)
    sync_last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    sync_status: Mapped[Optional[UserSyncStatus]] = mapped_column(SqlEnum(UserSyncStatus), nullable=True)

class UserDTO:
    def __init__(
        self, id: int, email: Optional[str], mail_server_type: MailServerType,
        sync_status : Optional[UserSyncStatus],
    ) -> None:
        self.id: int = id
        self.email: Optional[str] = email
        self.mail_server_type: MailServerType = mail_server_type
        self.sync_status: Optional[UserSyncStatus] = sync_status
    
    def __str__(self) -> str:
        return (
            f"UserDTO(id={self.id}, "
            f"mail_server_type={self.mail_server_type}, "
            f"email={self.email}, "
            f"sync_status={self.sync_status})"
        )