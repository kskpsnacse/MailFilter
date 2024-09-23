from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Integer, Text, DateTime, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column
from db import Base

class ActionType(Enum):
    MOVE_TO = "MOVE_TO"
    MARK_AS_READ = "MARK_AS_READ"
    MARK_AS_UNREAD = "MARK_AS_UNREAD"

class Action(Base):
    __tablename__: str = 'actions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mail_id: Mapped[int] = mapped_column(Integer, ForeignKey('mails.id'), nullable=False)
    type: Mapped[ActionType] = mapped_column(SqlEnum(ActionType), nullable=False)
    config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

class CompletedAction(Base):
    __tablename__: str = 'completed_actions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action_id: Mapped[int] = mapped_column(Integer, ForeignKey('actions.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

class ActionScheduler(Base):
    __tablename__: str = 'action_scheduler'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    last_run_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

class ActionDTO:
    def __init__(
        self, id: Optional[int], mail_id: int, type: ActionType, config: Optional[str],
        created_at: Optional[datetime] = None, user_id: Optional[int] = None,
        msg_id: Optional[str] = None
    ) -> None:
        self.id: Optional[int] = id
        self.mail_id: int = mail_id
        self.type: ActionType = type
        self.config: Optional[str] = config
        self.created_at: Optional[datetime] = created_at
        self.user_id: Optional[int] = user_id
        self.msg_id: Optional[str] = msg_id
