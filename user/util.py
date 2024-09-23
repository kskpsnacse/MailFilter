from typing import Optional

from sqlalchemy import Row
from mail import MailServerType
from user import UserSyncStatus, UserDTO, User

def get_as_dto(user: Row[tuple[int, MailServerType, Optional[UserSyncStatus]]]) -> UserDTO:
    return UserDTO(
        user.id, None, user.mail_server_type, user.sync_status
    )

def covert_model_to_dto(user: User) -> UserDTO:
    return UserDTO(
        user.id, user.email, user.mail_server_type, None
    )
