from datetime import datetime
from typing import List

from sqlalchemy import create_engine, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, selectinload

from models import Service, Base, Account, Usage

from telegram import Update
from telegram.ext import ContextTypes

import os

from dotenv import load_dotenv
import logging

from telegram.ext import ApplicationBuilder, CommandHandler

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

engine = create_engine("sqlite:///bot.db")
Base.metadata.create_all(engine)
Session = sessionmaker(engine)

PERMISSION_DENIED_MESSAGE = "This command is only available for admins."


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
            \n  /ranking  [service_name]
            \n  /status_me"""

    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = update.effective_message.text
    chat_id: int = update.effective_chat.id
    if not _check_args(text, [str]):
        usage = """Usage: /status <service_name>"""
        await context.bot.send_message(chat_id=chat_id, text=usage)
        return
    args: List[str] = text.split()
    service_name: str = args[1]
    with Session() as session:
        accounts_list: List[Account] = Account.find_by__chat_id__and__service_name(session=session, chat_id=chat_id,
                                                                               service=service_name)
    msg = [f"This is the list of accounts for service {service_name}."]
    for account in accounts_list:
        msg.append(f"\n  *  {account}")
    await context.bot.send_message(chat_id=chat_id, text="".join(msg))


async def status_me_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id: int = update.effective_message.chat_id
    current_user: str = update.effective_user.username
    accounts_used_by_me: List[Account] = []
    with Session() as session:
        accounts_used_by_me = (session
                               .query(Account)
                               .options(selectinload(Account.service))
                               .join(Service)
                               .filter(Account.service_id == Service.service_id)
                               .filter(Service.chat_id == chat_id)
                               .filter(Account.grabbed_by == current_user)
                               .filter(Account.released_at.is_(None))
                               .order_by(Service.name)
                               .order_by(Account.username)
                               .all())

    if len(accounts_used_by_me) > 0:
        msg = [f"You are currently using {len(accounts_used_by_me)} account(s):"]
        for account in accounts_used_by_me:
            msg.append(f"\nService: {account.service.name}; Username: {account.grabbed_by}; Password: {account.password};")
        msg = "".join(msg)
    else:
        msg = "You are not using any account currently."
    await context.bot.send_message(chat_id=chat_id, text=msg)


async def ranking_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # TODO: implement in the future
    pass


async def services_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id: int = update.effective_chat.id
    try:
        with Session() as session:
            services = Service.find_by__chat_id(session=session, chat_id=chat_id)
            if len(services) <= 0:
                msg = """No services available.\nCreate a new service using:\n/create_service <service_name>"""
            else:
                f_services = "\n  *  ".join([service.name for service in services])
                msg = f'These are the services available: \n  *  {f_services}'
            await context.bot.send_message(chat_id=chat_id, text=msg)
    except SQLAlchemyError as err:
        print(err.message)
        await context.bot.send_message(chat_id=chat_id, text="An error occurred while retrieving services")


async def create_service_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = update.effective_message.text
    chat_id: int = update.effective_chat.id
    if not _check_args(text, [str]):
        usage = "Usage: /create_service <service_name>"
        await context.bot.send_message(chat_id=chat_id, text=usage)
        return

    if not _is_admin_or_creator(update, context):
        await context.bot.send_message(chat_id=chat_id, text=PERMISSION_DENIED_MESSAGE)
        return

    args: List[str] = text.split()
    service_name: str = args[1]
    username: str = update.effective_user.username
    _create_service(chat_id=chat_id, service=service_name, username=username)
    msg = f"""Service {service_name} created successfully.
            \nNow add an account for this service using:\n/create_account {service_name} <username> <password>"""
    await context.bot.send_message(chat_id=chat_id, text=msg)


async def update_service_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = update.effective_message.text
    chat_id: int = update.effective_message.chat_id
    if not _check_args(text, [str, str]):
        usage = "Usage: /update_service <service_name> <new_service_name>"
        await context.bot.send_message(chat_id=chat_id, text=usage)
        return

    if not _is_admin_or_creator(update, context):
        await context.bot.send_message(chat_id=chat_id, text=PERMISSION_DENIED_MESSAGE)
        return

    args = text.split()
    service_name = args[1]
    new_service_name = args[2]
    if _update_service(chat_id=chat_id, service=service_name, new_service=new_service_name):
        msg = "Service updated successfully"
    else:
        msg = "Service not found"
    await context.bot.send_message(chat_id=chat_id, text=msg)


async def delete_service_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = update.effective_message.text
    chat_id: int = update.effective_message.chat_id
    if not _check_args(text, [str]):
        usage = "Usage: /delete_service <service_name>"
        await context.bot.send_message(chat_id=chat_id, text=usage)
        return

    if not _is_admin_or_creator(update, context):
        await context.bot.send_message(chat_id=chat_id, text=PERMISSION_DENIED_MESSAGE)
        return

    args: List[str] = text.split()
    service_name = args[1]
    if _delete_service(chat_id=chat_id, service=service_name):
        msg = f"""Service deleted successfully"""
    else:
        msg = f"""Service not found"""
    await context.bot.send_message(chat_id=chat_id, text=msg)



async def check_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = update.effective_message.text
    chat_id: str = update.effective_message.chat_id
    if not _check_args(text, [str]):
        usage = "Usage: /check <service_name>"
        await context.bot.send_message(chat_id=chat_id, text=usage)
        return

    args = text.split()
    service_name = args[1]

    msg = "Service not found"
    with Session() as session:
        using_accounts = (session
                          .query(Account)
                          .join(Service)
                          .filter(Account.service_id == Service.service_id)
                          .filter(Service.name == service_name)
                          .filter(Account.grabbed_at.is_not(None))
                          .filter(Account.released_at.is_(None))
                          .all())

        if len(using_accounts) > 0:
            msg = [f"Hi there. Are you still using the following account(s) for service {service_name}?\n"]
            for account in using_accounts:
                msg.append(f"\nUsername: {account.username}  (@{account.grabbed_by})")
            msg = "".join(msg)
        else:
            msg = "Service not found or no accounts for this service or all accounts are available to be used"
    await context.bot.send_message(chat_id=chat_id, text=msg)


async def accounts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = update.effective_message.text
    chat_id: int = update.effective_chat.id
    if not _check_args(text, [str]):
        usage = """Usage: /accounts <service_name>"""
        await context.bot.send_message(chat_id=chat_id, text=usage)
        return

    args = text.split()
    service_name: str = args[1]
    with Session() as session:
        accounts = Account.find_by__chat_id__and__service_name(session=session, chat_id=chat_id, service=service_name)
    if len(accounts) <= 0:
        msg = f"""No accounts available for service {service_name}"""
    else:
        f_accounts = """\n *  """.join([f"{account.username}\t{account.password}" for account in accounts])
        msg = f"""These are the accounts for service {service_name} \n *  {f_accounts}"""
    await context.bot.send_message(chat_id=chat_id, text=msg)


async def create_account_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = update.effective_message.text
    chat_id: int = update.effective_chat.id
    if not _check_args(text, [str, str, str]):
        usage = """Usage: /create_account <service_name> <username> <password>"""
        await context.bot.send_message(chat_id=chat_id, text=usage)
        return

    if not _is_admin_or_creator(update, context):
        await context.bot.send_message(chat_id=chat_id, text=PERMISSION_DENIED_MESSAGE)
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
    text: str = update.effective_message.text
    chat_id: int = update.effective_message.chat_id
    if not _check_args(text, [str, str, str]):
        usage = "Usage: /update_account [service_name] [username] [new_password]"
        await context.bot.send_message(chat_id=chat_id, text=usage)

    if not _is_admin_or_creator(update, context):
        await context.bot.send_message(chat_id=chat_id, text=PERMISSION_DENIED_MESSAGE)
        return

    args = text.split()
    service_name = args[1]
    username = args[2]
    new_password = args[3]

    if _update_account(chat_id=chat_id, service=service_name, username=username, new_password=new_password):
        msg = "Account updated successfully"
    else:
        msg = "Service or Account not found"
    await context.bot.send_message(chat_id=chat_id, text=msg)


async def delete_account_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = update.effective_message.text
    chat_id: int = update.effective_message.chat_id
    if not _check_args(text, [str, str]):
        usage = "Usage: /delete_account <service_name> <username>"
        await context.bot.send_message(chat_id=chat_id, text=usage)
        return

    if not _is_admin_or_creator(update, context):
        await context.bot.send_message(chat_id=chat_id, text=PERMISSION_DENIED_MESSAGE)
        return

    args: List[str] = text.split()
    service_name: str = args[1]
    username: str = args[2]
    if _delete_account(chat_id=chat_id, service=service_name, username=username):
        msg = "Account deleted successfully"
    else:
        msg = f"""Account not found"""
    await context.bot.send_message(chat_id=chat_id, text=msg)


async def report_broken_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


# actions handlers
async def use_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = update.effective_message.text
    chat_id: int = update.effective_message.chat_id
    if not _check_args(text, [str, str]):
        usage = "Usage: /use <service_name> <username>"
        await context.bot.send_message(chat_id=chat_id, text=usage)
        return

    args = text.split()
    service_name = args[1]
    username = args[2]
    current_user = update.effective_user.username
    if _use(chat_id=chat_id, service=service_name, username=username, current_user=current_user):
        msg = f"You are now using service {service_name} with account {username}"
    else:
        msg = f"Account not found or the account is already being used"
    await context.bot.send_message(chat_id=chat_id, text=msg)


async def release_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = update.effective_message.text
    chat_id: int = update.effective_message.chat_id
    if not _check_args(text, [str, str]):
        usage = "Usage: /release <service_name> <username>"
        await context.bot.send_message(chat_id=chat_id, text=usage)
        return

    args = text.split()
    service_name = args[1]
    username = args[2]
    current_user = update.effective_user.username
    if _release(chat_id=chat_id, service=service_name, username=username, current_user=current_user):
        msg = "Account released successfully"
    else:
        msg = "Account not found or not being used by you"
    await context.bot.send_message(chat_id=chat_id, text=msg)


def _create_service(chat_id: int, service: str, username: str) -> None:
    with Session() as session:
        service = Service(chat_id=chat_id, name=service, created_by=username, created_at=datetime.now())
        session.add(service)
        session.commit()


def _update_service(chat_id: int, service: str, new_service: str) -> bool:
    result = False
    with Session() as session:
        service = session.query(Service).filter(Service.name == service).filter(Service.chat_id == chat_id).one_or_none()
        if service:
            service.name = new_service
            session.commit()
            result = True
    return result


def _delete_service(chat_id: int, service: str) -> bool:
    result = False
    with Session() as session:
        service = session.query(Service).filter(Service.chat_id == chat_id, Service.name == service).one_or_none()
        if service:
            session.delete(service)
            session.commit()
            result = True
    return result


def _create_account(chat_id: int, service_name: str, username: str, password: str, created_by: str) -> None:
    with Session() as session:
        service = session.query(Service).filter_by(chat_id=chat_id, name=service_name).one_or_none()
        if service:
            account = Account(service=service, username=username, password=password, created_by=created_by,
                              created_at=datetime.now())
            session.add(account)
            session.commit()


def _update_account(chat_id: int, service: str, username: str, new_password: str) -> bool:
    result = False
    with Session() as session:
        account = (session.query(Account)
                   .join(Service)
                   .filter(Service.service_id == Account.service_id)
                   .filter(Service.chat_id == chat_id)
                   .filter(Service.name == service)
                   .filter(Account.username == username)
                   .one_or_none())
        if account:
            account.password = new_password
            session.commit()
            result = True
    return result


def _delete_account(chat_id: int, service: str, username: str) -> bool:
    result = False
    with Session() as session:
        account = (session.query(Account).join(Service)
                   .filter(Account.username == username)
                   .filter(Service.name == service)
                   .filter(Service.chat_id == chat_id)
                   .one_or_none())
        if account:
            session.delete(account)
            session.commit()
            result = True
    return result


def _use(chat_id: int, service: str, username: str, current_user: str) -> bool:
    result = False
    with Session() as session:
        available_account = (session
                             .query(Account)
                             .join(Service)
                             .filter(Account.service_id == Service.service_id)
                             .filter(Service.chat_id == chat_id)
                             .filter(Service.name == service)
                             .filter(Account.username == username)
                             .filter(or_(Account.grabbed_at.is_(None), Account.released_at.is_not(None)))
                             ).one_or_none()
        if available_account:
            available_account.grabbed_at = datetime.now()
            available_account.released_at = None
            available_account.grabbed_by = current_user

            usage = Usage(account_id=available_account.account_id,
                          performed_by=current_user,
                          started_at=datetime.now())
            session.add(usage)
            session.commit()
            result = True
    return result


def _release(chat_id: int, service: str, username: str, current_user: str) -> bool:
    result = False
    with Session() as session:
        try:
            account = (session
                       .query(Account)
                       .join(Service)
                       .filter(Account.service_id == Service.service_id)
                       .filter(Service.chat_id == chat_id)
                       .filter(Service.name == service)
                       .filter(Account.username == username)
                       .filter(Account.grabbed_by == current_user)
                       .filter(Account.released_at.is_(None)).one_or_none())
            if account:
                account.released_at = datetime.now()
                usages = (session
                          .query(Usage)
                          .filter(Usage.account_id == account.account_id)
                          .filter(Usage.performed_by == current_user)
                          .filter(Usage.finished_at.is_(None))
                          .all())
                now = datetime.now()
                for usage in usages:
                    usage.finished_at = now
                session.commit()
                result = True
        except Exception as e:
            session.rollback()
            print(e)
    return result


def _check_args(args: str, expected_args: list) -> bool:
    return (len(args.split()) - 1) == len(expected_args)  # TODO: add typing check here


async def _is_admin_or_creator(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat_member = await context.bot.get_chat_member(chat_id=update.effective_chat.id, user_id=update.effective_user.id)
    return chat_member.status in ["admin", "creator"]


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # create generic handlers
    start_handler = CommandHandler('start', start_handler)
    help_handler = CommandHandler('help', help_handler)
    status_handler = CommandHandler('status', status_handler)
    status_me_handler = CommandHandler('status_me', status_me_handler)
    ranking_handler = CommandHandler('ranking', ranking_handler)

    # create service handlers
    services_handler = CommandHandler('services', services_handler)
    create_service_handler = CommandHandler('create_service', create_service_handler)
    update_service_handler = CommandHandler('update_service', update_service_handler)
    delete_service_handler = CommandHandler('delete_service', delete_service_handler)
    check_handler = CommandHandler('check', check_handler)

    # create account handlers
    accounts_handler = CommandHandler('accounts', accounts_handler)
    create_account_handler = CommandHandler('create_account', create_account_handler)
    update_account_handler = CommandHandler('update_account', update_account_handler)
    delete_account_handler = CommandHandler('delete_account', delete_account_handler)
    report_broken_handler = CommandHandler('report_broken', report_broken_handler)

    # create usage handlers
    use_handler = CommandHandler('use', use_handler)
    release_handler = CommandHandler('release', release_handler)

    # register handlers
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(status_handler)
    application.add_handler(status_me_handler)
    application.add_handler(ranking_handler)
    application.add_handler(services_handler)
    application.add_handler(create_service_handler)
    application.add_handler(update_service_handler)
    application.add_handler(delete_service_handler)
    application.add_handler(check_handler)
    application.add_handler(accounts_handler)
    application.add_handler(create_account_handler)
    application.add_handler(update_account_handler)
    application.add_handler(delete_account_handler)
    application.add_handler(report_broken_handler)
    application.add_handler(use_handler)
    application.add_handler(release_handler)

    application.run_polling()
