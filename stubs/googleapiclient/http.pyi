from typing import Callable, Any


class BatchHttpRequest:
    def __init__(self, batch_uri: str, callback: Callable[[Any, Any, Any], None]) -> None:
        ...
    
    def add(self, request: Any, request_id: str) -> None:
        ...
    
    def execute(self) -> None:
        ...