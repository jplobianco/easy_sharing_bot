from datetime import datetime
from typing import List

from sqlalchemy import create_engine,  and_
from sqlalchemy.orm import sessionmaker

from models import Service, Base, Account

from telegram import Update
from telegram.ext import ContextTypes

engine = create_engine("sqlite:///easy_sharing_bot.db")
Base.metadata.create_all(engine)
Session = sessionmaker(engine)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi pal! I'm a bot, please talk to me!")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botname = update.effective_chat._bot.first_name
    username: str = update.effective_user.username
    msg = f"""Hi {username}.
            \nMy name is {botname} and I'm here to help you share accounts/services with friends and team.
            \nHere is the list of the available commands:
            \n-------------------------------------------------------
            \n  /services
            \n  /status  <service_name>
            \n  /create_service  <service_name>
            \n  /update_service  <service_name>  <new_service_name>
            \n  /delete_service  <service_name>
            \n  /accounts
            \n  /create_account  <service_name>  <username>  <password>
            \n  /update_account  <service_name>  <username>  <new_username>  [new_password]
            \n  /delete_account  <service_name>  <username>
            \n  /use  <service_name>  <username>
            \n  /release  <service_name> [username]
            \n  /check  <service_name>
            \n  /report_broken  <service_name>  <username>
            \n  /ranking  [service_name]"""

    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = update.effective_message.text
    chat_id: int = update.effective_chat.id
    if not _check_args(text, [str]):
        usage = """Usage: /status <service_name>"""
        await context.bot.send_message(chat_id=chat_id, text=usage)
        return
    args: List[str] = text.split()
    username: str = update.effective_user.username
    service_name: str = args[1]
    _status(chat_id=chat_id, service=service_name)
    msg = f'Hi {username}!\n'
    await context.bot.send_message(chat_id=chat_id, text=msg)


async def status_me_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def ranking_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def services_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id: int = update.effective_chat.id
    services = _services(chat_id=chat_id)
    if len(services) <= 0:
        msg = """No services available.\nCreate a new service using:\n/create_service <service_name>"""
    else:
        f_services = "\n  *  ".join([service.name for service in services])
        msg = f'These are the services available: \n  *  {f_services}'
    await context.bot.send_message(chat_id=chat_id, text=msg)


async def create_service_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = update.effective_message.text
    chat_id: int = update.effective_chat.id
    if not _check_args(text, [str]):
        usage = "Usage: /create_service <service_name>"
        await context.bot.send_message(chat_id=chat_id, text=usage)
        return

    args: List[str] = text.split()
    service_name: str = args[1]
    username: str = update.effective_user.username
    _create_service(chat_id=chat_id, service=service_name, username=username)
    msg = f"""Service {service_name} created successfully.
            \nNow add an account for this service using:\n/create_account {service_name} <username> <password>"""
    await context.bot.send_message(chat_id=chat_id, text=msg)


async def update_service_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def delete_service_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def check_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def accounts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = update.effective_message.text
    chat_id: int = update.effective_chat.id
    if not _check_args(text, [str]):
        usage = """Usage: /accounts <service_name>"""
        await context.bot.send_message(chat_id=chat_id, text=usage)
        return

    args = text.split()
    service_name: str = args[1]
    accounts = _accounts(chat_id=chat_id, service_name=service_name)
    if len(accounts) <= 0:
        msg = f"""No accounts available for service {service_name}"""
    else:
        f_accounts = "\n  *  ".join([f"{account.get('username')}\t{account.get('passwd')}" for account in accounts])
        msg = f"""These are the available accounts for service {service_name} \n  *  {f_accounts}"""
    await context.bot.send_message(chat_id=chat_id, text=msg)


async def create_account_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = update.effective_message.text
    chat_id: int = update.effective_chat.id
    if not _check_args(text, [str, str, str]):
        usage = """Usage: /create_account <service_name> <username> <password>"""
        await context.bot.send_message(chat_id=chat_id, text=usage)
        return

    args: List[str] = text.split()
    service_name: str = args[1]
    username: str = args[2]
    password: str = args[3]
    created_by: str = update.effective_user.username
    _create_account(chat_id=chat_id, service_name=service_name, username=username, password=password,
                    created_by=created_by)
    msg = f"""Account {username} successfully created for service {service_name}
             \nTo tell everyone that you are using this account, enter the following command:
             \n  /use {service_name} {username}
             \n
             \nWhen you are not using this account anymore, just enter the following command:
             \n  /release {service_name} {username}
            """
    await context.bot.send_message(chat_id=chat_id, text=msg)


async def update_account_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def delete_account_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def report_broken_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


# actions handlers
async def use_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def release_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


def _services(chat_id: int) -> List[Service]:
    with Session() as session:
        return Service.find_by_chat(session=session, chat_id=chat_id)


def _create_service(chat_id: int, service: str, username: str) -> None:
    with Session() as session:
        service = Service(chat_id=chat_id, name=service, created_by=username, created_at=datetime.now())
        session.add(service)
        session.commit()


def _update_service(chat_id: int, service: str) -> None:
    pass


def _delete_service(chat_id: int, service: str) -> None:
    with Session() as session:
        service = session.query(chat_id=chat_id, name=service).one_or_none()
        if service:
            session.delete(service)
            session.commit()


def _accounts(chat_id: int, service_name: str) -> List[Account]:
    with Session() as session:
        return session.query(Account).join("service").filter(and_(chat_id=chat_id, service__name=service_name))


def _create_account(chat_id: int, service_name: str, username: str, password: str, created_by: str) -> None:
    with Session() as session:
        service = session.query(Service).filter_by(chat_id=chat_id, name=service_name).one_or_none()
        if service:
            account = Account(service=service, username=username, password=password, created_by=created_by,
                              created_at=datetime.now())
            session.add(account)
            session.commit()


def _update_account(chat_id: int, service: str, username: str, password: str) -> None:
    pass


def _delete_account(chat_id: int, service: str, username: str, password: str) -> None:
    pass


def _status(chat_id: int, service: str) -> None:
    pass


def _status_me(chat_id: int, ) -> None:
    pass


def _ranking(chat_id: int, service: str) -> None:
    pass


def _use(chat_id: int, service: str, account: str) -> None:
    pass


def _release(chat_id: int, service: str, account: str) -> None:
    pass


def _check(chat_id: int, service: str) -> None:
    pass


def _report_broken(chat_id: int, service: str, account: str) -> None:
    pass


def _check_args(args: str, expected_args: list) -> bool:
    return (len(args.split()) - 1) == len(expected_args)  # TODO: add typing check here
