from typing import Callable
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from db import session_manager

def execute_in_tx(callable: Callable[[Session], None]) -> None:
    session: Session = session_manager.get_session()
    try:
        with session.begin():
            callable(session)
    except SQLAlchemyError as e:
        print(f"Transaction failed: {e}")
    finally:
        session.close()