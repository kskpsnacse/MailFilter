from datetime import datetime
from operator import and_
from typing import Optional
from sqlalchemy import Row
from sqlalchemy.orm import Session

from action import Action, CompletedAction, ActionScheduler, ActionDTO
from mail import Mail, MailActionResourceDTO
from user import UserAuthStatus, UserStats
from db import session_manager
from action.util import get_as_dto as get_action_as_dto

def get_last_run_time() -> Optional[datetime]:
    session: Session = session_manager.get_session()
    try:
        scheduler: Optional[ActionScheduler] = session.query(ActionScheduler).first()
        if scheduler:
            return scheduler.last_run_at
        return None
    finally:
        session.close()
        
def add_or_update_last_run_time(last_run_at: datetime) -> None:
    session: Session = session_manager.get_session()
    try:
        scheduler: Optional[ActionScheduler] = session.query(ActionScheduler).first()
        if scheduler:
            scheduler.last_run_at = last_run_at
        else:
            session.add(ActionScheduler(last_run_at=last_run_at))
        session.commit()
    finally:
        session.close()

def get_actions_to_be_done(created_after: datetime, page_size: int, page_number: int = 1) -> list[ActionDTO]:
    session: Session = session_manager.get_session()
    try:
        offset = (page_number - 1) * page_size
        action_list: list[Row[tuple[Action, str]]] = (
            session
                .query(Action, Mail.message_id)
                .outerjoin(CompletedAction, CompletedAction.action_id == Action.id)
                .join(Mail)
                .join(UserStats, Mail.user_id == UserStats.user_id)
                .filter(
                    and_(
                        Action.created_at > created_after,
                        CompletedAction.id == None,
                    )
                ).filter(UserStats.auth_status == UserAuthStatus.SUCCESS)
                .order_by(Action.id.desc()).limit(page_size).offset(offset)
                .all()
        )
        return [get_action_as_dto(action) for action in action_list]
    except Exception as e:
        print(e)
        return []
    finally:
        session.close()


def mark_as_done(resources: list[MailActionResourceDTO]) -> None:
    completed_actions: list[CompletedAction] = [
        CompletedAction(action_id = resource.action_id)
        for resource in resources
    ]
    session: Session = session_manager.get_session()
    try:
        session.add_all(completed_actions)
        print(f"adding {len(completed_actions)} completed_actions to db")
        session.commit()
    finally:
        session.close()