from collections import defaultdict
from datetime import datetime
from sqlalchemy import Row
from sqlalchemy.orm import Session
from sqlalchemy.sql.operators import and_
from db import session_manager
from mail import MailDTO, Mail, FilteredMail
from mail.util import get_model, get_as_dto

def save(user_id:int, mail_list: list[MailDTO]) -> None:
    mails: list[Mail] = get_model(mail_list)
    session: Session = session_manager.get_session()
    try :
        message_ids: list[str] = [mail.message_id for mail in mails]
        message_ids_in_db = __get_message_ids_from_db(message_ids, session, user_id)
        mails = [mail for mail in mails if mail.message_id not in message_ids_in_db]
        if mails:
            print(f"saving {len(mails)} mails to db")
            session.add_all(mails)
            session.commit()
        else:
            print("All mails are already present")
    except Exception as e:
        print(e)
    finally:
        session.close()
        
def __get_message_ids_from_db(message_ids: list[str], session: Session, user_id: int) -> list[str]:
    message_ids_in_db: list[str] = [
        row.message_id
        for row in (
            session
            .query(Mail.message_id)
            .filter(
                and_(Mail.user_id == user_id, Mail.message_id.in_(message_ids))
            ).all()
        )
    ]
    return message_ids_in_db

def get_unfiltered_mails(created_after: datetime, page_size: int, page_number: int = 1) -> list[MailDTO]:
    session: Session = session_manager.get_session()
    try:
        offset: int = (page_number - 1) * page_size
        mail_list: list[Mail] = (
            session
                .query(Mail)
                .outerjoin(FilteredMail)
                .filter(
                    and_(
                        Mail.created_at > created_after,
                        FilteredMail.id == None
                    )
                ).order_by(Mail.id.desc()).limit(page_size).offset(offset)
                .all()
        )
        return [get_as_dto(mail) for mail in mail_list]
    except Exception as e:
        print(e)
        return []
    finally:
        session.close()

def get_user_id_to_mail_ids(ids: list[int]) -> dict[int, list[int]]:
    session: Session = session_manager.get_session()
    try:
        result: list[Row[tuple[int, int]]] = (
            session
            .query(Mail.user_id, Mail.id)
            .filter(Mail.id.in_(ids))
            .all()
        )
        mail_map: dict[int, list[int]] = defaultdict(list)
        for user_id, mail_id in result:
            mail_map[user_id].append(mail_id)
        return dict(mail_map)
    finally:
        session.close()