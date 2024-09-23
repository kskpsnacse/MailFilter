from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import Request
from exceptions import MailServerAuthError
from mail import AbstractMailFetcher, MailDTO
from datetime import datetime
from googleapiclient.discovery import Resource
from typing import Optional, Callable, List, Set
from mail.gmail import get_gmail_api_service, execute_in_batch
from mail.gmail.processor import get_list_from_thread

class GmailFetcher(AbstractMailFetcher):
    __THREAD_ID_MAX_RESULTS: int = 700
    __THREAD_MAX_RESULTS: int = 18
    __MESSAGE_LIST_MAX_RESULTS: int = 500

    def do_full_sync(self, user_id: int, msg_list_saver: Callable[[list[MailDTO]], None]) -> None:
        try:
            next_page_token: Optional[str] = None
            service: Resource = get_gmail_api_service(user_id)
            while True:
                response: dict = service.users().threads().list(
                    userId='me', maxResults=self.__THREAD_ID_MAX_RESULTS, pageToken=next_page_token
                ).execute()
                thread_ids: List[str] = [thread['id'] for thread in response.get('threads', [])]
                next_page_token = response.get('nextPageToken', None)
                if not thread_ids:
                    break
                self.__process_thread_ids(msg_list_saver, service, thread_ids, user_id)
                if not next_page_token:
                    break
        except GoogleAuthError as auth_error:
            raise MailServerAuthError(auth_error, user_id)
    
    def sync_live_emails(
        self, user_id: int, last_sync_time: datetime,
        msg_list_saver: Callable[[list[MailDTO]], None]
    ) -> None:
        try:
            service: Resource = get_gmail_api_service(user_id)
            next_page_token: Optional[str] = None
            thread_ids: Set[str] = set()
            while True:
                response: dict = service.users().messages().list(
                    userId='me',
                    q=f'after:{int(last_sync_time.timestamp())}',
                    maxResults=self.__MESSAGE_LIST_MAX_RESULTS,
                    pageToken=next_page_token
                ).execute()
                for message in response.get('messages', []):
                    thread_id = message['threadId']
                    thread_ids.add(thread_id)
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            if thread_ids:
                self.__process_thread_ids(msg_list_saver, service, list(thread_ids), user_id)
        except GoogleAuthError as auth_error:
            raise MailServerAuthError(auth_error, user_id)
    
    
    def __process_thread_ids(
        self, msg_list_saver: Callable[[list[MailDTO]], None], service: Resource,
        thread_ids: list[str], user_id: int
    ) -> None:
        thread_id_to_req: dict[str, Request] = {
            thread_id : service.users().threads().get(userId='me', id=thread_id, format="full")
            for thread_id in thread_ids
        }
        self.__execute_batches(user_id, thread_id_to_req, self.__THREAD_MAX_RESULTS, msg_list_saver)
    
    def __execute_batches(
        self, user_id: int, thread_id_to_req : dict[str, Request], batch_size: int,
        ack: Callable[[list[MailDTO]], None]
    ) -> None:
        full_thread_details: list[MailDTO] = []
        def __batch_callback(request_id: str, response: dict, exception: Optional[Exception]):
            if exception is None:
                full_thread_details.extend(get_list_from_thread(user_id, response))
            else:
                print(f"An error occurred while fetching thread {request_id}: {exception}")
        def on_per_batch_complete():
            if full_thread_details:
                ack(full_thread_details)
                full_thread_details.clear()
        execute_in_batch(__batch_callback, thread_id_to_req, batch_size, on_per_batch_complete)

        