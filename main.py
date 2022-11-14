import os

from dotenv import load_dotenv
import logging

from telegram.ext import ApplicationBuilder, CommandHandler
import bot_commands

load_dotenv()

API_KEY = os.getenv('API_KEY')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


if __name__ == '__main__':
    application = ApplicationBuilder().token(API_KEY).build()

    # create generic handlers
    start_handler = CommandHandler('start', bot_commands.start_handler)
    help_handler = CommandHandler('help', bot_commands.help_handler)
    status_handler = CommandHandler('status', bot_commands.status_handler)
    status_me_handler = CommandHandler('status_me', bot_commands.status_me_handler)
    ranking_handler = CommandHandler('ranking', bot_commands.ranking_handler)

    # create service handlers
    services_handler = CommandHandler('services', bot_commands.services_handler)
    create_service_handler = CommandHandler('create_service', bot_commands.create_service_handler)
    update_service_handler = CommandHandler('update_service', bot_commands.update_service_handler)
    delete_service_handler = CommandHandler('delete_service', bot_commands.delete_service_handler)
    check_handler = CommandHandler('check', bot_commands.check_handler)

    # create account handlers
    accounts_handler = CommandHandler('accounts', bot_commands.accounts_handler)
    create_account_handler = CommandHandler('create_account', bot_commands.create_account_handler)
    update_account_handler = CommandHandler('update_account', bot_commands.update_account_handler)
    delete_account_handler = CommandHandler('delete_account', bot_commands.delete_account_handler)
    report_broken_handler = CommandHandler('report_broken', bot_commands.report_broken_handler)

    # create usage handlers
    use_handler = CommandHandler('use', bot_commands.use_handler)
    release_handler = CommandHandler('release', bot_commands.release_handler)

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
