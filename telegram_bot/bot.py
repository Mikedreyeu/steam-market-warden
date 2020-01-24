import logging
import sys
import traceback
from telegram.utils.helpers import mention_html
from emoji import emojize
from telegram import ParseMode, ChatAction
from telegram.ext import Updater, CommandHandler

from market_api.api import get_item_info
from settings import BOT_TOKEN, CHAT_FOR_ERRORS
from telegram_bot.constants import NO_IMAGE_ARG
from telegram_bot.exceptions.error_messages import (
    APPID_NOT_INT,NOT_ENOUGH_ARGS, NOT_EXACT
)
from telegram_bot.exceptions.exceptions import CommandException, ApiException
from telegram_bot.message_builder import format_item_info
from telegram_bot.utils import parse_args, send_typing_action

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text('Hi!')


@send_typing_action
def item_info(update, context):
    args = parse_args(context.args)

    if len(args) < 2:
        raise CommandException(NOT_ENOUGH_ARGS)

    if not args[0].isdigit():
        raise CommandException(APPID_NOT_INT)

    no_photo = NO_IMAGE_ARG in args
    if no_photo:
        args = [arg for arg in args if arg != NO_IMAGE_ARG]

    context.bot.send_chat_action(
        chat_id=update.effective_message.chat_id, action=ChatAction.TYPING
    )

    item_info_dict = get_item_info(args[0], args[1])

    message_text = format_item_info(item_info_dict)

    if not item_info_dict['exact_item']:
        message_text = emojize(
            f'{message_text}\n\n:information_source: {NOT_EXACT}',
            use_aliases=True
        )

    if not no_photo:
        update.message.reply_photo(
            photo=item_info_dict['icon_url'],
            caption=message_text,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        update.message.reply_text(
            message_text,
            parse_mode=ParseMode.MARKDOWN
        )


def help(update, context):
    update.message.reply_text('Help!')


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    if context.error in (CommandException, ApiException):
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
        text = (f'The error <code>{context.error}</code> happened{payload}.\n'
                f'The full traceback:\n\n<code>{trace}/code>')

        context.bot.send_message(
            CHAT_FOR_ERRORS, text, parse_mode=ParseMode.HTML
        )


def main():
    updater = Updater(BOT_TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("item_info", item_info))
    dp.add_handler(CommandHandler("help", help))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
