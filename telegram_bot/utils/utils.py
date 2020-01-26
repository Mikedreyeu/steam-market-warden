from functools import wraps

from telegram import ChatAction, ParseMode

from telegram_bot.constants import NO_IMAGE_ARG
from telegram_bot.exceptions.error_messages import ERRMSG_BRACKETS_ERROR, \
    ERRMSG_NOT_ENOUGH_ARGS, ERRMSG_APPID_NOT_INT
from telegram_bot.exceptions.exceptions import CommandException


def parse_args(original_args: list):
    arguments = []

    args_iter = iter(original_args)
    try:
        for arg in args_iter:
            if arg.startswith(('"', "'", '`')):
                while not arg.endswith(('"', "'", '`')):
                    arg += f' {next(args_iter)}'
            arguments.append(arg.strip(', "\'`'))
    except StopIteration:
        raise CommandException(ERRMSG_BRACKETS_ERROR)

    return arguments


def parse_item_info_args(args):
    if len(args) < 2:
        raise CommandException(ERRMSG_NOT_ENOUGH_ARGS)

    if not args[0].isdigit():
        raise CommandException(ERRMSG_APPID_NOT_INT)

    no_image = NO_IMAGE_ARG in args
    if no_image:
        args = [arg for arg in args if arg != NO_IMAGE_ARG]

    return args, no_image


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def send_typing_action(func):
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=ChatAction.TYPING
        )
        return func(update, context,  *args, **kwargs)

    return command_func


def send_item_message(
        context, chat_id: int, message_text: str,
        no_image: bool, image_url: str
):
    if not no_image:
        context.bot.send_photo(
            chat_id=chat_id,
            photo=image_url,
            caption=message_text,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text=message_text,
            parse_mode=ParseMode.MARKDOWN
        )

