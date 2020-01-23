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