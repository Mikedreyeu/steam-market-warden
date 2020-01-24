from functools import wraps

from telegram import ChatAction

from telegram_bot.exceptions.error_messages import BRACKETS_ERROR
from telegram_bot.exceptions.exceptions import CommandException


def parse_args(original_args):
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


def send_typing_action(func):
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=ChatAction.TYPING
        )
        return func(update, context,  *args, **kwargs)

    return command_func
