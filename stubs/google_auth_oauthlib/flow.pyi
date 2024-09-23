from typing import List, Any

class InstalledAppFlow:
    @classmethod
    def from_client_secrets_file(
        cls, client_secrets_file: str, scopes: List[str]
    ) -> 'InstalledAppFlow':
        ...

    def run_local_server(self, port: int = 0) -> Any:
        ...