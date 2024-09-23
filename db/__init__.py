import sqlite3
from sqlalchemy import Any, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session as SqlAlchemySession

MAIL_FILTER_SQLITE_DB_NAME='mail_filter.db'
# Connect to the SQLite database (it will create the database file if it doesn't exist)
__connection = sqlite3.connect(MAIL_FILTER_SQLITE_DB_NAME)

# Create a cursor object to execute SQL commands
__cursor =  __connection.cursor()
print("running init.py")

# SQL commands to create tables
__create_users_table = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    mail_server_type TEXT NOT NULL,
    UNIQUE (email)
);
'''

__create_mails_table = '''
CREATE TABLE IF NOT EXISTS mails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject TEXT,
    body TEXT NOT NULL,
    from_address TEXT NOT NULL,
    to_address TEXT,
    cc TEXT,
    bcc TEXT,
    message_id TEXT NOT NULL,
    thread_id TEXT NOT NULL,
    mail_sent_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE (user_id, thread_id, message_id)
);
'''

__create_filtered_mails_table = '''
CREATE TABLE IF NOT EXISTS filtered_mails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mail_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mail_id) REFERENCES mails (id),
    UNIQUE (mail_id)
);
'''

__create_filter_scheduler_table = '''
CREATE TABLE IF NOT EXISTS filter_scheduler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    last_run_at DATETIME NOT NULL
);
'''

__create_user_stats_table = '''
CREATE TABLE IF NOT EXISTS user_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    auth_status TEXT,
    sync_last_run_at DATETIME,
    sync_status TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE (user_id)
);
'''

__create_actions_table = '''
CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mail_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    config TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mail_id) REFERENCES mails (id)
);
'''

__create_completed_actions_table = '''
CREATE TABLE IF NOT EXISTS completed_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (action_id) REFERENCES actions (id),
    UNIQUE (action_id)
);
'''

__create_action_scheduler_table = '''
CREATE TABLE IF NOT EXISTS action_scheduler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    last_run_at DATETIME NOT NULL
);
'''

__cursor.execute(__create_users_table)
__cursor.execute(__create_mails_table)
__cursor.execute(__create_filtered_mails_table)
__cursor.execute(__create_filter_scheduler_table)
__cursor.execute(__create_user_stats_table)
__cursor.execute(__create_actions_table)
__cursor.execute(__create_completed_actions_table)
__cursor.execute(__create_action_scheduler_table)

__create_indexes = [
    "CREATE INDEX IF NOT EXISTS idx_mails_userid_messageid ON mails (user_id, message_id);",
    "CREATE INDEX IF NOT EXISTS idx_mails_userid_mail_sent_at ON mails (user_id, mail_sent_at);",
    "CREATE INDEX IF NOT EXISTS idx_filtered_mails_mailid_created_at ON filtered_mails (mail_id, created_at);",
    "CREATE INDEX IF NOT EXISTS idx_actions_created_at ON actions (created_at);",
    "CREATE INDEX IF NOT EXISTS idx_completed_actions_actionid_created_at ON completed_actions (action_id, created_at);"
]

for index_query in __create_indexes:
    __cursor.execute(index_query)
try:
    __cursor.execute('insert into users(email, mail_server_type) values("kskpsnacse@gmail.com", "GMAIL")');
    __cursor.execute('insert into user_stats(user_id, auth_status, sync_status) values(1, "SUCCESS", "READY_TO_FULL_SYNC")');
except Exception as e:
    print(e)

__connection.commit()
__connection.close()

print("Tables and indexes created successfully!")

Base: Any = declarative_base()

class SessionManager:
    def __init__(self, database_url: str) -> None:
        self.engine = create_engine(database_url, echo=False, pool_size=5)
        self.session_factory = sessionmaker(bind=self.engine)

    def get_session(self) -> SqlAlchemySession:
        return self.session_factory()

session_manager: SessionManager = SessionManager('sqlite:///' + MAIL_FILTER_SQLITE_DB_NAME)
