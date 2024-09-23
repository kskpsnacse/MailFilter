from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Optional
from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from db import Base

class MailServerType(Enum):
    GMAIL = "GMAIL"

class Mail(Base):
    __tablename__: str = 'mails'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    from_address: Mapped[str] = mapped_column(String, nullable=False)
    to_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cc: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    bcc: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    message_id: Mapped[str] = mapped_column(String, nullable=False)
    thread_id: Mapped[str] = mapped_column(String, nullable=False)
    mail_sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

class FilteredMail(Base):
    __tablename__: str = 'filtered_mails'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mail_id: Mapped[int] = mapped_column(Integer, ForeignKey('mails.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

class MailDTO:
    def __init__(
        self, id: Optional[int], user_id: int, subject: Optional[str], body: str, from_address: str,
        to_address: Optional[str], cc: Optional[str] = None, bcc: Optional[str] = None,
        message_id: Optional[str] = None, thread_id: Optional[str] = None,
        mail_sent_at: Optional[datetime] = None, created_at: Optional[datetime] = None
    ) -> None:
        self.id: Optional[int] = id
        self.user_id: int = user_id
        self.subject: Optional[str] = subject
        self.body: str = body
        self.from_address: str = from_address
        self.to_address: Optional[str] = to_address
        self.cc: Optional[str] = cc
        self.bcc: Optional[str] = bcc
        self.message_id: Optional[str] = message_id
        self.thread_id: Optional[str] = thread_id
        self.mail_sent_at: Optional[datetime] = mail_sent_at
        self.created_at: Optional[datetime] = created_at

    def __str__(self) -> str:
        return (
            f"MailDTO(id={self.id}, user_id={self.user_id}, subject='{self.subject}', "
            f"from_address='{self.from_address}', to_address='{self.to_address}', "
            f"cc='{self.cc}', bcc='{self.bcc}', "
            f"message_id='{self.message_id}', thread_id='{self.thread_id}', "
            f"mail_sent_at={self.mail_sent_at}, created_at={self.created_at})"
        )
    
    def __repr__(self) -> str:
        return (
            f"MailDTO(id={self.id}, user_id={self.user_id}, subject='{self.subject}', "
            f"from_address='{self.from_address}', to_address='{self.to_address}', "
            f"cc='{self.cc}', bcc='{self.bcc}', "
            f"message_id='{self.message_id}', thread_id='{self.thread_id}', "
            f"mail_sent_at={self.mail_sent_at}, created_at={self.created_at})"
        )

class MailActionResourceDTO:
    def __init__(self, msg_id: str, action_id: int) -> None:
        self.msg_id: str = msg_id
        self.action_id: int = action_id

class AbstractMailFetcher(ABC) :
    @abstractmethod
    def do_full_sync(self, user_id: int, msg_list_saver: Callable[[list[MailDTO]], None]) -> None:
        ...
    
    @abstractmethod
    def sync_live_emails(
        self, user_id: int, last_sync_time: datetime, msg_list_saver: Callable[[list[MailDTO]], None]
    ) -> None:
        ...

class AbstractMailOperations(ABC):
    @abstractmethod
    def mark_as_read(
        self, user_id: int, resources: list[MailActionResourceDTO], ack: Callable[[list[MailActionResourceDTO]], None]
    ) -> None:
        ...
    
    @abstractmethod
    def mark_as_unread(
        self, user_id: int, resources: list[MailActionResourceDTO], ack: Callable[[list[MailActionResourceDTO]], None]
    ) -> None:
        ...
    
    @abstractmethod
    def move_to(
        self, user_id: int, resources: list[MailActionResourceDTO], location: str,
        ack: Callable[[list[MailActionResourceDTO]], None]
    ) -> None:
        ...