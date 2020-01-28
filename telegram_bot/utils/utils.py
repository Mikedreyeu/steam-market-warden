import sys
import traceback
from datetime import timezone, timedelta, datetime, time
from functools import wraps

from emoji import emojize
from telegram import ChatAction, ParseMode, Chat

from market_api.api import get_item_info
from settings import CHAT_FOR_ERRORS
from telegram_bot.constants import NO_IMAGE_ARG, DATETIME_FORMAT
from telegram_bot.exceptions.error_messages import ERRMSG_BRACKETS_ERROR, \
    ERRMSG_NOT_ENOUGH_ARGS, ERRMSG_APPID_NOT_INT, WRNMSG_NOT_EXACT, \
    ERRMSG_WRONG_DATE_FORMAT, ERRMSG_NO_FUTURE, ERRMSG_WRONG_TIME_FORMAT
from telegram_bot.exceptions.exceptions import CommandException, ApiException
from telegram_bot.utils.message_builder import format_item_info


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


def parse_time(time_str):
    try:
        return time.fromisoformat(
            time_str
        ).replace(tzinfo=timezone(timedelta(hours=3)))  # TODO: this timezone is temporary
    except ValueError:
        raise CommandException(ERRMSG_WRONG_TIME_FORMAT)


def parse_datetime(datetime_str, datetime_format=DATETIME_FORMAT):
    try:
        dt_object = datetime.strptime(
            datetime_str, datetime_format
        ).replace(tzinfo=timezone(timedelta(hours=3)))  # TODO: this timezone is temporary
    except ValueError:
        raise CommandException(ERRMSG_WRONG_DATE_FORMAT)

    if dt_object < datetime.now().replace(tzinfo=timezone(timedelta(hours=3))):  # TODO: this timezone is temporary
        raise CommandException(ERRMSG_NO_FUTURE)

    return dt_object


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


def send_item_info(
        context, chat_id: int, args: list, add_to_message: str = None
):
    args, no_image = parse_item_info_args(args)

    item_info_dict = get_item_info(args[0], args[1])

    message_text = format_item_info(item_info_dict)

    if not item_info_dict['exact_item']:
        message_text = (
            f'{message_text}\n\n:information_source: {WRNMSG_NOT_EXACT}'
        )

    if add_to_message:
        message_text += add_to_message

    message_text = emojize(message_text, use_aliases=True)

    send_item_message(
        context, chat_id, message_text, no_image, item_info_dict['icon_url']
    )


def handle_job_error(context, chat_id):
    if type(context.error) in (CommandException, ApiException):
        context.bot.send_message(
            chat_id=chat_id,
            text=context.error.message,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text=emojize(
                ':thinking_face: Something went wrong...',
                use_aliases=True
            )
        )

        payload = f' within the chat <i>{chat_id}</i>'

        trace = ''.join(traceback.format_tb(sys.exc_info()[2]))
        text = (f'The error <code>{context.error}</code> '
                f'happened during the job execution{payload}.\n'
                f'The full traceback:\n\n'
                f'<code>{trace}</code>')

        context.bot.send_message(
            CHAT_FOR_ERRORS, text, parse_mode=ParseMode.HTML
        )


def job_error_handler(func):
    @wraps(func)
    def job_func(context, *args, **kwargs):
        try:
            return func(context, *args, **kwargs)
        except Exception as e:
            context.error = e
            handle_job_error(context, context.job.context['chat_id'])

    return job_func
