from functools import wraps

from telegram import ChatAction, ParseMode

from telegram_bot.exceptions.error_messages import BRACKETS_ERROR
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
        raise CommandException(BRACKETS_ERROR)

    return arguments


def send_message(update, message_text: str, no_image: bool, image_url: str):
    if not no_image:
        update.message.reply_photo(
            photo=image_url,
            caption=message_text,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        update.message.reply_text(
            message_text,
            parse_mode=ParseMode.MARKDOWN
        )


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
