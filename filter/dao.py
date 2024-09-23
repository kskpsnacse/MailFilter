from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from db import session_manager
from filter import FilterScheduler

def get_last_run_time() -> Optional[datetime]:
    session: Session = session_manager.get_session()
    try:
        scheduler: Optional[FilterScheduler] = session.query(FilterScheduler).first()
        if scheduler:
            return scheduler.last_run_at
        return None
    finally:
        session.close()
        
def add_or_update_last_run_time(last_run_at: datetime) -> None:
    session: Session = session_manager.get_session()
    try:
        scheduler: Optional[FilterScheduler] = session.query(FilterScheduler).first()
        if scheduler:
            scheduler.last_run_at = last_run_at
        else:
            session.add(FilterScheduler(last_run_at=last_run_at))
        session.commit()
    finally:
        session.close()