from time import sleep
from exceptions import MailServerAuthError
from filter.service import start_filter
from mail.service import start_sync
from action.service import start_action
from user.service import mark_auth_error
from threading import Thread

def __do_mail_sync() -> None:
    while True:
        try:
            start_sync()
            sleep(10)
        except MailServerAuthError as auth_error:
            mark_auth_error(auth_error.user_id)
            print(f"Auth error happened, please re-login {auth_error}")
        except Exception as e:
            print(e)
        
def __do_filter() -> None:
    while True:
        try:
            start_filter()
            sleep(10)
        except Exception as e:
            print(e)

def __do_action() -> None:
    while True:
        try:
            start_action()
            sleep(10)
        except MailServerAuthError as auth_error:
            mark_auth_error(auth_error.user_id)
            print(f"Auth error happened, please re-login {auth_error}")
        except Exception as e:
            print(e)

def execute_methods_in_threads() -> None:
    thread_list: list[Thread] = [
        Thread(target = method)
        for method in [__do_mail_sync, __do_filter, __do_action]
    ]
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()

if __name__ == '__main__':
    execute_methods_in_threads()
