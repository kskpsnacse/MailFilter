import time
from typing import Optional, Callable
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.http import BatchHttpRequest

__SCOPES: list[str] = [
    "https://mail.google.com/", "https://www.googleapis.com/auth/userinfo.profile"
]

def __get_credentials(user_id: int) -> Optional[Credentials]:
    creds: Optional[Credentials] = None
    if os.path.exists(f"user_creds/{user_id}_token.json"):
        creds = Credentials.from_authorized_user_file(f"user_creds/{user_id}_token.json", __SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(
                f"user_creds/credentials.json", __SCOPES
            )
            creds = flow.run_local_server(port=8990)
        if creds:
            with open(f"user_creds/{user_id}_token.json", "w") as token_file:
                token_file.write(creds.to_json())
    return creds

def get_gmail_api_service(user_id: int) -> Resource:
    creds: Optional[Credentials] = __get_credentials(user_id)
    service: Resource = build("gmail", "v1", credentials=creds)
    return service

def execute_in_batch(
    __batch_callback: Callable[[str, dict, Optional[Exception]], None], req_id_to_request: dict[str, Request],
    batch_size: int, per_batch_ack: Callable[[],None]
) -> None:
    req_ids = list(req_id_to_request.keys())
    for i in range(0, len(req_ids), batch_size):
        batch: BatchHttpRequest = BatchHttpRequest(
            batch_uri='https://www.googleapis.com/batch/gmail/v1', callback=__batch_callback
        )
        start_time: float = time.time()
        for req_id in req_ids[i:i + batch_size]:
            batch.add(request = req_id_to_request[req_id], request_id = req_id)
        batch.execute()
        per_batch_ack()
        end_time: float = time.time()
        elapsed_time: float = end_time - start_time
        if elapsed_time < 1.5:
            time.sleep(1.5 - elapsed_time)