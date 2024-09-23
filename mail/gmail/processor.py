from datetime import datetime
from typing import Optional
import base64

from mail import MailDTO

def __get_message_body(message: dict) -> str:
    payload: dict = message['payload']
    message_body: list[str] = []
    if 'parts' in payload:  # Check if parts is empty
        for part in payload['parts']:
            message_body.append(__get_message_body_from_part(part))
    elif 'data' in payload['body']:
        message_body.append(__decode_body(payload['body']['data']))
    return ''.join(message_body)

def __get_message_body_from_part(part: dict) -> str:
    message_body: list[str] = []
    mime_type: str = part['mimeType']
    if mime_type == "text/html" and 'data' in part['body']:
        message_body.append(__decode_body(part['body']['data']))
    elif mime_type.startswith("multipart/alternative"):
        for sub_part in part['parts']:
            if sub_part['mimeType'].lower() == "text/html" and 'data' in sub_part['body']:
                message_body.append(__decode_body(sub_part['body']['data']))
                return ''.join(message_body)
    elif mime_type.startswith("multipart/") and part['parts']:
        for sub_part in part['parts']:
            message_body.append(__get_message_body_from_part(sub_part))
    return ''.join(message_body)

def __get_headers(header_list: list[dict[str,str]]) -> dict[str,str]:
    to_include: set[str] = {'from', 'subject', 'to', 'cc', 'bcc'}
    return {
        header['name'].lower(): header['value']
        for header in header_list
        if header['name'].lower() in to_include
    }

def __get_as_dto(user_id: int, message: dict) -> MailDTO:
    body: str = __get_message_body(message)
    message_id: str = message['id']
    thread_id: str = message['threadId']
    sent_at: datetime = datetime.fromtimestamp(int(message['internalDate']) / 1000)
    headers: dict[str,str] = __get_headers(message['payload']['headers'])
    subject: Optional[str] = headers.get('subject', None)
    from_address: str = headers['from']
    to_address: Optional[str] = headers.get('to', None)
    cc: Optional[str] = headers.get('cc', None)
    bcc: Optional[str] = headers.get('bcc', None)
    return MailDTO(
        None, user_id, subject, body, from_address, to_address,
        cc, bcc, message_id, thread_id, sent_at, None
    )

def get_list_from_thread(user_id: int, thread: dict) -> list[MailDTO]:
    dtos: list[MailDTO] = []
    for msg in thread.get('messages', []):
        try:
            dto: MailDTO = __get_as_dto(user_id, msg)
            dtos.append(dto)
        except Exception as e:
            print(f'unable to convert to dto {msg} - {e}')
    return dtos


def __decode_body(encoded_data: Optional[str]) -> str:
    if encoded_data:
        decoded_bytes: bytes = base64.urlsafe_b64decode(encoded_data.encode('utf-8'))
        return decoded_bytes.decode('utf-8', errors='ignore')
    return ""