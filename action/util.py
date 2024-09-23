from sqlalchemy import Row
from action import Action, ActionDTO

def get_as_dto(row : Row[tuple[Action, str]]) -> ActionDTO:
    action: Action = row[0]
    return ActionDTO(
        id = action.id, mail_id=action.mail_id, type=action.type,
        config=action.config, created_at= action.created_at, msg_id= row[1]
    )