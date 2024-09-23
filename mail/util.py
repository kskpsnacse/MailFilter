from mail import Mail, MailDTO

def get_model(mail_list) -> list[Mail]:
    mails: list[Mail] = [
        Mail(
            user_id = mail_dto.user_id,
            subject = mail_dto.subject,
            body = mail_dto.body,
            from_address = mail_dto.from_address,
            to_address = mail_dto.to_address,
            cc = mail_dto.cc,
            bcc = mail_dto.bcc,
            message_id = mail_dto.message_id,
            thread_id = mail_dto.thread_id,
            mail_sent_at = mail_dto.mail_sent_at
        )
        for mail_dto in mail_list
    ]
    return mails

def get_as_dto(mail: Mail) -> MailDTO:
    return MailDTO(
        id = mail.id,
        user_id = mail.user_id,
        subject = mail.subject,
        body = mail.body,
        from_address = mail.from_address,
        to_address = mail.to_address,
        cc = mail.cc,
        bcc = mail.bcc,
        message_id = mail.message_id,
        thread_id = mail.thread_id,
        mail_sent_at = mail.mail_sent_at,
        created_at = mail.created_at
    )