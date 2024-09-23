from datetime import datetime
from typing import List, Optional
from user import UserDTO, UserSyncStatus, UserAuthStatus, User, UserStats

from user.dao import get_users as get_users_from_db
from user.dao import get_last_sync_time as get_last_sync_time_from_db
from user.dao import update_sync_status as update_sync_status_from_db
from user.dao import get_users_to_sync as get_users_to_sync_from_db
from user.dao import update_last_sync_time as update_last_sync_time_from_db
from user.dao import mark_auth_error as mark_auth_error_in_db


def get_last_sync_time(user_id : int) -> Optional[datetime]:
    return get_last_sync_time_from_db(user_id)

def update_last_sync_time(user_id : int, last_sync_time: datetime) -> None:
    return update_last_sync_time_from_db(user_id, last_sync_time)

def update_sync_status(user_id : int, status : UserSyncStatus) -> None:
    return update_sync_status_from_db(user_id, status)

def get_users_to_sync() -> list[UserDTO]:
    return get_users_to_sync_from_db()

def get_users(ids: list[int]) -> List[UserDTO]:
    return get_users_from_db(ids)

def mark_auth_error(user_id: int) -> None:
    return mark_auth_error_in_db(user_id)
