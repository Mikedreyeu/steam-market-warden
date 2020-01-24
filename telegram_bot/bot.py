import logging
import time

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler

from market_api.api import get_item_info
from settings import BOT_TOKEN
from telegram_bot.constants import NO_IMAGE_ARG
from telegram_bot.exceptions.error_messages import (APPID_NOT_INT,
                                                    BRACKETS_ERROR,
                                                    NOT_ENOUGH_ARGS)
from telegram_bot.exceptions.exceptions import CommandException
from telegram_bot.message_builder import format_item_info
from telegram_bot.utils import parse_args

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text('Hi!')


def item_info(update, context):
    args = parse_args(context.args)

    if len(args) < 2:
        raise CommandException(NOT_ENOUGH_ARGS)

    no_photo = NO_IMAGE_ARG in args
    if no_photo:
        args = [arg for arg in args if arg != NO_IMAGE_ARG]

    if not args[0].isdigit():
        raise CommandException(APPID_NOT_INT)

    item_info_dict = get_item_info(args[0], args[1])

    if not no_photo:
        update.message.reply_photo(
            photo=item_info_dict['icon_url'],
            caption=f'{format_item_info(item_info_dict)}',
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        update.message.reply_text(
            format_item_info(item_info_dict),
            parse_mode=ParseMode.MARKDOWN
        )


def help(update, context):
    update.message.reply_text('Help!')


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    if context.error in (CommandException, ):
        update.message.reply_text(
            context.error.message, parse_mode=ParseMode.MARKDOWN
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