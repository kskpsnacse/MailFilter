class MailServerAuthError(Exception):
    def __init__(self, exception: Exception, user_id: int):
        self.exception: Exception = exception
        self.user_id: int = user_id
        super().__init__(f"Auth error for {user_id} - {exception}")

    def __str__(self) -> str:
        return f"MailServerAuthError: Auth error for user {self.user_id} - {self.exception}"

    def __repr__(self) -> str:
        return f"MailServerAuthError(user_id={self.user_id}, exception={repr(self.exception)})"