import logging
import sys
import traceback
from datetime import timedelta

from emoji import emojize
from telegram import ParseMode, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, \
    ConversationHandler, CallbackQueryHandler
from telegram.utils.helpers import mention_html

from settings import BOT_TOKEN, CHAT_FOR_ERRORS
from telegram_bot.commands import start_command, item_info_command, \
    market_search_command, item_info_timed_command, item_info_daily_command, \
    item_info_alert_command, item_info_repeating_command, help_command
from telegram_bot.constants import (ST_CHOOSE_JOB_TYPE, CB_CANCEL,
                                    ST_CHOOSE_JOB, CB_BACK,
                                    ST_MANAGE_JOB, MANAGE_JOB_REGEX,
                                    CHOOSE_JOB_TYPE_REGEX, CB_EDIT_JOB,
                                    CB_DELETE_JOB)
from telegram_bot.conversations import manage_item_info_jobs_command, end_conv, \
    choose_job_conv, manage_job_conv, delete_job_conv, edit_job_conv
from telegram_bot.exceptions.exceptions import CommandException, ApiException
from telegram_bot.jobs import save_jobs_job
from telegram_bot.utils.job_utils import save_jobs, load_jobs

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def error_handler(update: Update, context: CallbackContext):
    logger.warning(
        'Update "%s" caused error "%s"', update, context.error
    )
    if type(context.error) in (CommandException, ApiException):
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=context.error.message,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=emojize(
                ':thinking_face: Something went wrong...', use_aliases=True
            )
        )

        payload = ''

        if update.effective_user:
            user_mention = mention_html(
                update.effective_user.id, update.effective_user.first_name
            )
            payload += f' with the user {user_mention}'

        if update.effective_chat:
            payload += f' within the chat <i>{update.effective_chat.title}</i>'
            if update.effective_chat.username:
                payload += f' (@{update.effective_chat.username})'

        if update.poll:
            payload += f' with the poll id {update.poll.id}.'

        trace = ''.join(traceback.format_tb(sys.exc_info()[2]))
        text = (
            f'The error <code>{context.error}</code> '
            f'happened{payload}.\nThe full traceback:\n\n'
            f'<code>{trace}</code>'
        )

        context.bot.send_message(
            CHAT_FOR_ERRORS, text, parse_mode=ParseMode.HTML
        )


def main():
    updater = Updater(BOT_TOKEN, use_context=True)

    job_queue = updater.job_queue
    dp = updater.dispatcher

    job_queue.run_repeating(save_jobs_job, timedelta(minutes=1))

    try:
        load_jobs(dp, job_queue)
    except FileNotFoundError:
        # First run
        pass

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                'manage_item_info_jobs', manage_item_info_jobs_command
            )
        ],
        states={
            ST_CHOOSE_JOB_TYPE: [
                CallbackQueryHandler(
                    choose_job_conv, pattern=CHOOSE_JOB_TYPE_REGEX
                ),
                CallbackQueryHandler(end_conv, pattern=f'^{CB_CANCEL}$'),
            ],
            ST_CHOOSE_JOB: [
                CallbackQueryHandler(
                    manage_job_conv, pattern=MANAGE_JOB_REGEX
                ),
                CallbackQueryHandler(
                    manage_item_info_jobs_command, pattern=f'^{CB_BACK}$'
                ),
                CallbackQueryHandler(
                    choose_job_conv, pattern=CHOOSE_JOB_TYPE_REGEX
                ),
            ],
            ST_MANAGE_JOB: [
                CallbackQueryHandler(
                    edit_job_conv, pattern=CB_EDIT_JOB
                ),
                CallbackQueryHandler(
                    delete_job_conv, pattern=CB_DELETE_JOB
                ),
            ]
        },
        fallbacks=[
            CommandHandler(
                'manage_item_info_jobs', manage_item_info_jobs_command
            )
        ]
    )
    dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('item_info', item_info_command))
    dp.add_handler(CommandHandler('market_search', market_search_command))
    dp.add_handler(CommandHandler('item_info_timed', item_info_timed_command))
    dp.add_handler(CommandHandler('item_info_daily', item_info_daily_command))
    dp.add_handler(CommandHandler('item_info_alert', item_info_alert_command))
    dp.add_handler(
        CommandHandler('item_info_repeating', item_info_repeating_command)
    )
    dp.add_handler(CommandHandler('help', help_command))

    dp.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()

    save_jobs(job_queue)


if __name__ == '__main__':
    main()
