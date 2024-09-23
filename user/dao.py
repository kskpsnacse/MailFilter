from datetime import datetime
from typing import Optional

from sqlalchemy import Row, and_, or_
from sqlalchemy.orm import Session
from db import session_manager
from mail import MailServerType
from user import UserStats, UserSyncStatus, UserDTO, User, UserAuthStatus
from user.util import get_as_dto, covert_model_to_dto
import os


def get_last_sync_time(user_id : int) -> Optional[datetime]:
    session: Session = session_manager.get_session()
    try:
        user_stats: Optional[UserStats] = session.query(UserStats).filter(UserStats.user_id == user_id).first()
        if user_stats:
            return user_stats.sync_last_run_at
        return None
    finally:
        session.close()

def update_last_sync_time(user_id : int, last_sync_time: datetime) -> None:
    session: Session = session_manager.get_session()
    try:
        user_stats: Optional[UserStats] = session.query(UserStats).filter(UserStats.user_id == user_id).first()
        if user_stats:
            user_stats.sync_last_run_at = last_sync_time
            session.commit()
    finally:
        session.close()

def update_sync_status(user_id : int, status : UserSyncStatus) -> None:
    session: Session = session_manager.get_session()
    try:
        user_stats: Optional[UserStats] = session.query(UserStats).filter(UserStats.user_id == user_id).first()
        if user_stats:
            user_stats.sync_status = status
            session.commit()
    finally:
        session.close()

def get_users_to_sync() -> list[UserDTO]:
    session: Session = session_manager.get_session()
    try:
        users: list[Row[tuple[int, MailServerType, Optional[UserSyncStatus]]]] = (
            session
            .query(User.id, User.mail_server_type, UserStats.sync_status)
            .join(UserStats)
            .filter(
                and_(UserStats.auth_status == UserAuthStatus.SUCCESS)
            ).filter(
                or_(
                    UserStats.sync_status == UserSyncStatus.READY_TO_FULL_SYNC,
                    UserStats.sync_status == UserSyncStatus.FULL_SYNC_DONE
                )
            ).all()
        )
        return [get_as_dto(user) for user in users]
    finally:
        session.close()

def get_users(ids: list[int]) -> list[UserDTO]:
    session: Session = session_manager.get_session()
    try:
        users: list[User] = (
            session
            .query(User)
            .filter(
                and_(User.id.in_(ids))
            ).all()
        )
        return [covert_model_to_dto(user) for user in users]
    finally:
        session.close()


def mark_auth_error(user_id: int) -> None:
    session: Session = session_manager.get_session()
    try:
        user_stats: Optional[UserStats] = session.query(UserStats).filter(UserStats.user_id == user_id).first()
        if user_stats:
            user_stats.auth_status = UserAuthStatus.ERROR
            session.commit()
            os.remove("user_creds/1_token.json");
    finally:
        session.close()