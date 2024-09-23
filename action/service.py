from collections import defaultdict
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from action import ActionDTO, ActionType
from action import Action
from mail import AbstractMailOperations, MailActionResourceDTO
from mail.service import get_user_id_to_mail_ids
from mail.service import get_mail_operations
from user import UserDTO
from user.service import get_users
from action.dao import get_last_run_time
from action.dao import get_actions_to_be_done, add_or_update_last_run_time, mark_as_done

def __get_model(action : ActionDTO) -> Action:
    return Action(
        mail_id=action.mail_id,type=action.type, config=action.config
    )

def save(action_list: list[ActionDTO], session: Session) -> None:
    if action_list:
        actions: list[Action] = [__get_model(action) for action in action_list]
        print(f"adding {len(action_list)} actions to db")
        session.add_all(actions)

def start_action() -> None:
    last_run_at: Optional[datetime] = get_last_run_time()
    if not last_run_at:
        last_run_at = datetime(1970, 1, 1)
    page: int = 1
    page_size: int = 100
    now = datetime.now()
    while True:
        src_action_list: list[ActionDTO] = get_actions_to_be_done(last_run_at, page_size, page)
        if not src_action_list:
            break
        mail_id_to_action_list: dict[int, list[ActionDTO]] = defaultdict(list)
        for action in src_action_list:
            mail_id_to_action_list[action.mail_id].append(action)
        user_id_to_mail_ids: dict[int, list[int]] = get_user_id_to_mail_ids(list(mail_id_to_action_list.keys()))
        id_to_user: dict[int, UserDTO] = {user.id : user for user in get_users(list(user_id_to_mail_ids.keys()))}
        for user_id in user_id_to_mail_ids:
            __do_action_for_a_user(id_to_user, mail_id_to_action_list, user_id, user_id_to_mail_ids)
    add_or_update_last_run_time(now)


def __do_action_for_a_user(
    id_to_user: dict[int, UserDTO], mail_id_to_action_list: dict[int, list[ActionDTO]],
    user_id: int, user_id_to_mail_ids: dict[int, list[int]]
) -> None:
    action_list: list[ActionDTO] = [
        action
        for mail_id in user_id_to_mail_ids[user_id]
        for action in mail_id_to_action_list[mail_id]
    ]
    mail_ops: Optional[AbstractMailOperations] = get_mail_operations(id_to_user[user_id].mail_server_type)
    if not mail_ops:
        return None
    grouped_actions_type: dict[ActionType, list[ActionDTO]] = defaultdict(list)
    for action in action_list:
        grouped_actions_type[action.type].append(action)
    __handle_move_to(grouped_actions_type, mail_ops, user_id)
    __handle_mark_as_read(grouped_actions_type, mail_ops, user_id)
    __handle_mark_as_unread(grouped_actions_type, mail_ops, user_id)

def __get_mail_action_resources(actions: list[ActionDTO]) -> list[MailActionResourceDTO]:
    return [
        MailActionResourceDTO(action.msg_id, action.id)
        for action in actions
        if action.msg_id and action.id
    ]

def __handle_mark_as_read(
    grouped_actions_type: dict[ActionType, list[ActionDTO]],
    mail_ops: AbstractMailOperations, user_id: int
) -> None:
    if ActionType.MARK_AS_READ not in grouped_actions_type:
        return None
    mail_ops.mark_as_read(
        user_id, __get_mail_action_resources(grouped_actions_type[ActionType.MARK_AS_READ]),
        mark_as_done
    )
    
def __handle_mark_as_unread(
        grouped_actions_type: dict[ActionType, list[ActionDTO]],
        mail_ops: AbstractMailOperations, user_id: int
) -> None:
    if ActionType.MARK_AS_UNREAD not in grouped_actions_type:
        return None
    mail_ops.mark_as_unread(
        user_id, __get_mail_action_resources(grouped_actions_type[ActionType.MARK_AS_UNREAD]),
        mark_as_done
    )

def __handle_move_to(
    grouped_actions_type: dict[ActionType, list[ActionDTO]],
    mail_ops: AbstractMailOperations, user_id: int
) -> None:
    if ActionType.MOVE_TO not in grouped_actions_type:
        return None
    grouped_actions_config = defaultdict(list)
    for action in grouped_actions_type[ActionType.MOVE_TO]:
        if action.config:
            grouped_actions_config[action.config].append(action)
    for config in grouped_actions_config:
        mail_ops.move_to(
            user_id, __get_mail_action_resources(grouped_actions_config[config]),
            config, mark_as_done
        )