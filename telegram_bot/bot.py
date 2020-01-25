import logging
import sys
import traceback
from datetime import datetime, timedelta, timezone

from emoji import emojize
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
from telegram.utils.helpers import mention_html

from market_api.api import get_item_info, market_search_for_command
from settings import BOT_TOKEN, CHAT_FOR_ERRORS
from telegram_bot.constants import NO_IMAGE_ARG, DATETIME_FORMAT
from telegram_bot.exceptions.error_messages import (APPID_NOT_INT,
                                                    NOT_ENOUGH_ARGS, NOT_EXACT,
                                                    WRONG_ARGUMENT_RUN_ONCE,
                                                    NO_FUTURE)
from telegram_bot.exceptions.exceptions import CommandException, ApiException
from telegram_bot.message_builder import format_item_info, format_market_search
from telegram_bot.utils import parse_args, send_typing_action, send_message

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
        raise CommandException(NOT_ENOUGH_ARGS)

    no_image = NO_IMAGE_ARG in args
    if no_image:
        args = [arg for arg in args if arg != NO_IMAGE_ARG]

    market_search_dict = market_search_for_command(query=args[0])

    message_text = format_market_search(market_search_dict)

    send_message(
        context, update.effective_chat.id, message_text,
        no_image, market_search_dict['icon_url']
    )


@send_typing_action
def item_info_command(update, context):
    args = parse_args(context.args)
    _send_item_info(context, update.effective_chat.id, args)


def _send_item_info(context, chat_id, args):
    if len(args) < 2:
        raise CommandException(NOT_ENOUGH_ARGS)

    if not args[0].isdigit():
        raise CommandException(APPID_NOT_INT)

    no_image = NO_IMAGE_ARG in args
    if no_image:
        args = [arg for arg in args if arg != NO_IMAGE_ARG]

    item_info_dict = get_item_info(args[0], args[1])

    message_text = format_item_info(item_info_dict)

    if not item_info_dict['exact_item']:
        message_text = emojize(
            f'{message_text}\n\n:information_source: {NOT_EXACT}',
            use_aliases=True
        )

    send_message(
        context, chat_id, message_text, no_image, item_info_dict['icon_url']
    )

# def timed_item_info_command(update, context):
#     keyboard = [InlineKeyboardButton('run_once', callback_data='1'),
#                 InlineKeyboardButton('run_repeating', callback_data='2'),
#                 InlineKeyboardButton('run_daily', callback_data='3')]
#
#     reply_markup = InlineKeyboardMarkup(build_menu(keyboard, n_cols=2))
#
#     update.message.reply_text('Please choose:', reply_markup=reply_markup)


def timed_item_info_run_once_job(context):
    chat_id, args = context.job.context
    _send_item_info(context, chat_id, args)


def timed_item_info_run_once(update, context):
    args = parse_args(context.args)

    if args[0].isdigit():
        when = int(args[0])
    else:
        try:
            when = datetime.strptime(
                f'{args[0]} {args[1]}',
                DATETIME_FORMAT
            ).replace(tzinfo=timezone(timedelta(hours=3))) # TODO: this timezone is temporary
        except (ValueError, IndexError):
            raise CommandException(WRONG_ARGUMENT_RUN_ONCE)

        if when < datetime.now().replace(tzinfo=timezone(timedelta(hours=3))): # TODO: this timezone is temporary
            raise CommandException(NO_FUTURE)

    chat_id = update.message.chat_id
    job_context = (chat_id, args[args.index('-')+1:])

    new_job = context.job_queue.run_once(
        timed_item_info_run_once_job, when, context=job_context
    )

    if not context.chat_data.get('timed_item_info_jobs'):
        context.chat_data['timed_item_info_jobs'] = {}
        context.chat_data['timed_item_info_jobs']['run_once'] = [new_job]
    elif not context.chat_data['timed_item_info_jobs'].get('run_once'):
        context.chat_data['timed_item_info_jobs']['run_once'] = [new_job]
    else:
        context.chat_data['timed_item_info_jobs']['run_once'].append(new_job)


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

    dp = updater.dispatcher

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
    dp.add_handler(CommandHandler('test', timed_item_info_run_once))
    dp.add_handler(CommandHandler('help', help_command))

    dp.add_error_handler(error_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
