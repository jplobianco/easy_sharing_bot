import os
from typing import List

from dotenv import load_dotenv
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import bot_commands

load_dotenv()

API_KEY = os.getenv('API_KEY')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def _check_args(args: str, expected_args: list) -> bool:
    return (len(args.split()) - 1) == len(expected_args)  # TODO: add typing check here


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id: int = update.effective_chat.id
    username: str = update.effective_user.username
    text: str = update.effective_message.text
    #first_name: str = update.effective_user.first_name
    #language_code: str = update.effective_user.language_code
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi pal! I'm a bot, please talk to me!")


# help handler function
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botname = update.effective_chat._bot.first_name
    username: str = update.effective_user.username
    msg = f"""Hi {username}.
            \nMy name is {botname} and I'm here to help you share you accounts/services with friends and team members.
            \nHere is a list of the available commands:
            \n/services
            \n/status <service_name>
            \n/create_service <service_name>
            \n/update_service <service_name> <new_service_name>
            \n/delete_service <service_name>
            \n/create_account <service_name> <username> <password>
            \n/update_account <service_name> <username> <new_username> [<new_password>]
            \n/delete_account <service_name> <username>"""

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
    bot_commands.status(chat_id=chat_id, service=service_name)
    msg = f'Hi {username}!\n'
    await context.bot.send_message(chat_id=chat_id, text=msg)


async def status_me_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def ranking_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


async def services_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id: int = update.effective_chat.id
    services = bot_commands.services(chat_id=chat_id)
    if len(services) <= 0:
        msg = """No services available.\nCreate a new service using:\n/create_service <service_name>"""
    else:
        _services = "\n* ".join([service.get('name') for service in services])
        msg = f'These are the services available: \n* {_services}'
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
    bot_commands.create_service(chat_id=chat_id, service=service_name, username=username)
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
    _accounts = bot_commands.accounts(chat_id=chat_id, service_name=service_name)
    if len(_accounts) <= 0:
        msg = f"""No accounts available for service {service_name}"""
    else:
        _accounts = "\n* ".join([f"{account.get('username')}\t{account.get('passwd')}" for account in _accounts])
        msg = f"""These are the available accounts for service {service_name} \n* {_accounts}"""
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
    bot_commands.create_account(chat_id=chat_id, service=service_name, username=username, password=password,
                                created_by=created_by)
    msg = f"""Account {username} successfully created for service {service_name}"""
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


if __name__ == '__main__':
    application = ApplicationBuilder().token(API_KEY).build()

    bot_commands.create_database()

    # generic handlers
    start_handler = CommandHandler('start', start_handler)
    help_handler = CommandHandler('help', help_handler)
    status_handler = CommandHandler('status', status_handler)
    status_me_handler = CommandHandler('status_me', status_me_handler)
    ranking_handler = CommandHandler('ranking', ranking_handler)

    # service handlers
    services_handler = CommandHandler('services', services_handler)
    create_service_handler = CommandHandler('create_service', create_service_handler)
    update_service_handler = CommandHandler('update_service', update_service_handler)
    delete_service_handler = CommandHandler('delete_service', delete_service_handler)
    check_handler = CommandHandler('check', check_handler)

    # account handlers
    accounts_handler = CommandHandler('accounts', accounts_handler)
    create_account_handler = CommandHandler('create_account', create_account_handler)
    update_account_handler = CommandHandler('update_account', update_account_handler)
    delete_account_handler = CommandHandler('delete_account', delete_account_handler)
    report_broken_handler = CommandHandler('report_broken', report_broken_handler)

    # actions handlers
    use_handler = CommandHandler('use', use_handler)
    release_handler = CommandHandler('release', release_handler)

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
