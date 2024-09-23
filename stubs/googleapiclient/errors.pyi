from typing import Any

class HttpError(Exception):
    """Exception raised for errors in the HTTP request."""
    
    def __init__(self, message: str, *args: Any) -> None:
        ...
    
    def __str__(self) -> str:
        ...
