from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from action import ActionDTO
from filter import FILTER_LIST, ActionJSONDTO
from filter.evaluator import evaluate
from mail.service import get_unfiltered_mails, mark_as_filtered
from mail import MailDTO
from action.service import save as save_action
from util.util import execute_in_tx
from filter.dao import get_last_run_time, add_or_update_last_run_time

def __get_actions(json_actions: list[ActionJSONDTO], mail: MailDTO) -> list[ActionDTO]:
    def get_action_dto(json_action: ActionJSONDTO) -> ActionDTO:
        if not mail.id:
            raise ValueError
        return ActionDTO(
            id = None, mail_id = mail.id, type = json_action.action_type, config= json_action.config
        )
    return [
        get_action_dto(action)
        for action in json_actions
    ]

def start_filter() -> None:
    last_run_at: Optional[datetime] = get_last_run_time()
    if not last_run_at:
        last_run_at = datetime(1970, 1, 1)
    page: int = 1
    page_size: int = 100
    now = datetime.now()
    while True:
        mail_list: list[MailDTO] = get_unfiltered_mails(last_run_at, page_size, page)
        if not mail_list:
            break
        action_list: list[ActionDTO] = []
        for filter in FILTER_LIST:
            for mail in mail_list:
                if evaluate(filter, mail):
                    action_list.extend(__get_actions(filter.actions, mail))
        def save_action_and_mark_mail_as_filtered(session: Session):
            save_action(action_list, session)
            mark_as_filtered([mail.id for mail in mail_list if mail.id], session)
        execute_in_tx(save_action_and_mark_mail_as_filtered)
    add_or_update_last_run_time(now)