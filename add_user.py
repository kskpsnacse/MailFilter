from google.auth.credentials import Credentials
from mail.gmail import get_cred_by_login
from user import service as user_service

def add_user() -> None:
    email: str
    creds: Credentials
    email, creds = get_cred_by_login()
    user_service.add_user(email, creds)
    print(f"User {email} added")

if __name__ == '__main__':
    add_user()