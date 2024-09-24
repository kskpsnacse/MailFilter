from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional
from mail import AbstractMailFetcher, FilteredMail, MailServerType, AbstractMailOperations, MailDTO
from mail.gmail.fetcher import GmailFetcher
from mail.gmail.operations import GmailOperations
from user import UserDTO, UserSyncStatus
from user.service import get_last_sync_time, update_sync_status
from user.service import get_users_to_sync, update_last_sync_time
from mail.dao import save, get_user_id_to_mail_ids as get_user_id_to_mail_ids_from_db
from mail.dao import get_unfiltered_mails as get_unfiltered_mails_from_db

__gmail_fetcher: GmailFetcher = GmailFetcher()
__gmail_operations: GmailOperations = GmailOperations()

def get_mail_fetcher(mail_server_type: MailServerType) -> Optional[AbstractMailFetcher] :
    if mail_server_type == MailServerType.GMAIL:
        return __gmail_fetcher
    return None

def get_mail_operations(mail_server_type: MailServerType) -> Optional[AbstractMailOperations]:
    if mail_server_type == MailServerType.GMAIL:
        return __gmail_operations
    return None

def start_sync() -> None:
    users: list[UserDTO] = get_users_to_sync()
    for user in users:
        mail_fetcher: Optional[AbstractMailFetcher] = get_mail_fetcher(user.mail_server_type)
        if not mail_fetcher:
            continue
        current_time: datetime = datetime.now()
        if user.sync_status == UserSyncStatus.READY_TO_FULL_SYNC:
            mail_fetcher.do_full_sync(user.id, lambda x: save(user.id, x))
            update_sync_status(user.id, UserSyncStatus.FULL_SYNC_DONE)
            update_last_sync_time(user.id, current_time)
            print("full sync completed")
        elif user.sync_status == UserSyncStatus.FULL_SYNC_DONE:
            last_sync_time: Optional[datetime] = get_last_sync_time(user.id)
            if last_sync_time:
                mail_fetcher.sync_live_emails(
                    user.id, last_sync_time - timedelta(minutes = 2), lambda x: save(user.id, x)
                )
                update_last_sync_time(user.id, current_time)

def mark_as_filtered(ids: list[int], session: Session) -> None:
    print(f"adding {len(ids)} filtered_mails to db")
    session.add_all([FilteredMail(mail_id= id) for id in ids])

def get_user_id_to_mail_ids(ids: list[int]) -> dict[int, list[int]]:
    return get_user_id_to_mail_ids_from_db(ids)

def get_unfiltered_mails(created_after: datetime, page_size: int, page_number: int = 1) -> list[MailDTO]:
    return get_unfiltered_mails_from_db(created_after, page_size, page_number)
