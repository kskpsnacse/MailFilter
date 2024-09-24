from typing import Callable, Optional, Any

from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import Request
from googleapiclient.discovery import Resource

from exceptions import MailServerAuthError
from mail import AbstractMailOperations, MailActionResourceDTO
from mail.gmail import get_gmail_api_service, execute_in_batch


class GmailOperations(AbstractMailOperations):
    __MESSAGE_MODIFY_API_BATCH_SIZE: int = 15
    
    def mark_as_read(
        self, user_id: int, resources: list[MailActionResourceDTO],
        ack: Callable[[list[MailActionResourceDTO]], None]
    ) -> None:
        self.__modify_msg(user_id, resources, ack, {'removeLabelIds': ['UNREAD']})

    def mark_as_unread(
        self, user_id: int, resources: list[MailActionResourceDTO],
        ack: Callable[[list[MailActionResourceDTO]], None]
    ) -> None:
        self.__modify_msg(user_id, resources, ack, {'addLabelIds': ['UNREAD']})
    
    def move_to(
        self, user_id: int, resources: list[MailActionResourceDTO], location: str,
        ack: Callable[[list[MailActionResourceDTO]], None]
    ) -> None:
        label_id: Optional[str] = self.__get_label_id(user_id, location)
        if not label_id:
            ack(resources)
            return
        self.__modify_msg(user_id, resources, ack, {'addLabelIds': [label_id]})
    
    def __get_label_id(self, user_id: int, location: str) -> Optional[str]:
        try :
            service: Resource = get_gmail_api_service(user_id)
            label_list: list[dict] = service.users().labels().list(userId="me").execute().get('labels', [])
            label_id: Optional[str] = None
            for label in label_list:
                if label['name'] == location:
                    label_id = label['id']
                    break
            return label_id
        except GoogleAuthError as auth_error:
            raise MailServerAuthError(auth_error, user_id)
    
    def __modify_msg(
        self, user_id: int, resources: list[MailActionResourceDTO],
        ack: Callable[[list[MailActionResourceDTO]], None], body: dict[str, Any]
    ) -> None:
        try :
            service: Resource = get_gmail_api_service(user_id)
            action_id_to_request: dict[int, Request] = {
                resource.action_id : service.users().messages().modify(
                    userId="me", id=resource.msg_id, body=body
                )
                for resource in resources
            }
            self.__execute_batches(
                action_id_to_request, batch_size=self.__MESSAGE_MODIFY_API_BATCH_SIZE, ack=ack
            )
        except GoogleAuthError as auth_error:
            raise MailServerAuthError(auth_error, user_id)

    def __execute_batches(
        self, action_id_to_request : dict[int, Request], batch_size: int,
        ack: Callable[[list[MailActionResourceDTO]], None]
    ) -> None:
        resources: list[MailActionResourceDTO] = []
        def __batch_callback(request_id, response, exception):
            if exception:
                print(f"An error occurred while batch operation {request_id}: {exception}")
            else:
                resources.append(MailActionResourceDTO(response.get('id'), int(request_id)))
        def on_per_batch_complete():
            if resources:
                ack(resources)
                resources.clear()
        request_id_to_request = {str(k) : action_id_to_request[k] for k in action_id_to_request.keys()}
        execute_in_batch(__batch_callback, request_id_to_request, batch_size, on_per_batch_complete)
        
