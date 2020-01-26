import logging
import sys
import traceback
from datetime import datetime, timedelta, timezone

from emoji import emojize
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
from telegram.utils.helpers import mention_html

from market_api.api import market_search_for_command
from settings import BOT_TOKEN, CHAT_FOR_ERRORS
from telegram_bot.constants import NO_IMAGE_ARG, DATETIME_FORMAT, MINUTES, \
    HOURS, DAYS
from telegram_bot.exceptions.error_messages import (ERRMSG_NOT_ENOUGH_ARGS,
                                                    ERRMSG_WRONG_ARGUMENT_RUN_ONCE,
                                                    ERRMSG_NO_FUTURE)
from telegram_bot.exceptions.exceptions import CommandException, ApiException
from telegram_bot.jobs import timed_item_info_job, \
    check_values_of_an_item_info_job
from telegram_bot.utils.job_utils import init_chat_data, save_jobs, load_jobs
from telegram_bot.utils.message_builder import format_market_search
from telegram_bot.utils.utils import parse_args, send_typing_action, \
    send_item_message, send_item_info, parse_datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def start_command(update, context):
    update.message.reply_text('Hi!')


@send_typing_action
def market_search_command(update, context):
    args = parse_args(context.args)

    if len(args) < 1:
        raise CommandException(ERRMSG_NOT_ENOUGH_ARGS)

    no_image = NO_IMAGE_ARG in args
    if no_image:
        args = [arg for arg in args if arg != NO_IMAGE_ARG]

    market_search_dict = market_search_for_command(query=args[0])

    message_text = format_market_search(market_search_dict)

    send_item_message(
        context, update.effective_chat.id, message_text,
        no_image, market_search_dict['icon_url']
    )


@send_typing_action
def item_info_command(update, context):
    args = parse_args(context.args)
    send_item_info(context, update.effective_chat.id, args)


# def timed_item_info_command(update, context):
#     keyboard = [InlineKeyboardButton('run_once', callback_data='1'),
#                 InlineKeyboardButton('run_repeating', callback_data='2'),
#                 InlineKeyboardButton('run_daily', callback_data='3')]
#
#     reply_markup = InlineKeyboardMarkup(build_menu(keyboard, n_cols=2))
#
#     update.message.reply_text('Please choose:', reply_markup=reply_markup)


def timed_item_info_command(update, context):
    args = parse_args(context.args)

    if args[0].isdigit():
        when = int(args[0])
    else:
        when = parse_datetime(f'{args[0]} {args[1]}')

    init_chat_data(context.chat_data)

    chat_id = update.message.chat_id
    job_context = {
        'chat_id': chat_id,
        'args': args[args.index('-')+1:],
        'chat_jobs': context.chat_data['timed_item_info_jobs']['run_once']
    }

    new_job = context.job_queue.run_once(
        timed_item_info_job, when, context=job_context
    )

    context.chat_data['timed_item_info_jobs'].append(new_job)


def repeated_item_info_command(update, context):
    args = parse_args(context.args)

    chat_id = update.message.chat_id

    if args[0][:-1].isdigit() and args[0][-1] in (MINUTES, HOURS, DAYS):
        interval = int(args[0][:-1])

    first = parse_datetime(f'{args[1]} {args[2]}')

    init_chat_data(context.chat_data)

    job_context = {
        'chat_id': chat_id,
        'args': args[args.index('-') + 1:],
        'chat_jobs': context.chat_data['timed_item_info_jobs']
    }


def alarm_item_info_command(update, context):
    args = parse_args(context.args)

    chat_id = update.message.chat_id

    init_chat_data(context.chat_data)

    job_context = {
        'chat_id': chat_id,
        'conditions': args[:args.index('-')],
        'args': args[args.index('-')+1:],
        'chat_jobs': context.chat_data['item_info_alert_jobs']
    }

    context.job_queue.run_once(
        check_values_of_an_item_info_job, 1, context=job_context
    )

    new_job = context.job_queue.run_repeating(
        check_values_of_an_item_info_job, timedelta(minutes=20),
        context=job_context
    )

    context.chat_data['item_info_alert_jobs'].append(new_job)


def help_command(update, context):
    update.message.reply_text('Help!')


def error_handler(update, context):
    logger.warning(
        'Update "%s" caused error "%s"', update, context.error
    )
    if type(context.error) in (CommandException, ApiException):
        update.message.reply_text(
            context.error.message, parse_mode=ParseMode.MARKDOWN
        )
    else:
        update.message.reply_text(
            emojize(
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

    # job_queue.run_repeating(save_jobs_job, timedelta(minutes=1))

    try:
        load_jobs(job_queue)
    except FileNotFoundError:
        # First run
        pass

    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler('timed_item_info', timed_item_info_command)],
    #     states={
    #         FIRST: [CallbackQueryHandler(timed_item_info_run_once, pattern='^' + str(ONE) + '$'),],
    #     },
    #     fallbacks=[CommandHandler('timed_item_info', timed_item_info_command)]
    # )
    # dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('item_info', item_info_command))
    dp.add_handler(CommandHandler('market_search', market_search_command))
    dp.add_handler(
        CommandHandler('timed_item_info', timed_item_info_command)
    )
    dp.add_handler(
        CommandHandler('repeated_item_info', repeated_item_info_command)
    )
    dp.add_handler(
        CommandHandler('alarm_item_info', alarm_item_info_command)
    )
    dp.add_handler(CommandHandler('help', help_command))

    dp.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()

    save_jobs(job_queue)


if __name__ == '__main__':
    main()
