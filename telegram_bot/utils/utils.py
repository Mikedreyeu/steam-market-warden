import math
import sys
import traceback
from datetime import timezone, timedelta, datetime, time
from functools import wraps

from emoji import emojize
from orator.exceptions.orm import ModelNotFound
from telegram import ChatAction, ParseMode, Update, InlineKeyboardMarkup, \
    InlineKeyboardButton
from telegram.ext import CallbackContext

from db.models import Whitelist
from market_api.api import get_item_info
from settings import CHAT_FOR_ERRORS, ADMIN_ID
from telegram_bot.constants import NO_IMAGE_ARG, DATETIME_FORMAT, \
    QUOTATION_MARKS, KV_SEPARATOR, COND_SEPARATOR, JOB_TO_CHAT_DATA_KEY, \
    II_ALERT_JOBS, WL_REQUEST
from telegram_bot.exceptions.error_messages import ERRMSG_BRACKETS_ERROR, \
    ERRMSG_NOT_ENOUGH_ARGS, ERRMSG_APPID_NOT_INT, WRNMSG_NOT_EXACT, \
    ERRMSG_WRONG_DATE_FORMAT, ERRMSG_NO_FUTURE, ERRMSG_WRONG_TIME_FORMAT, \
    WRNMSG_NOT_FULL_INFO, ERRMSG_ALERT_NOT_VALID_CONDITIONS
from telegram_bot.exceptions.exceptions import CommandException, ApiException
from telegram_bot.utils.job_utils import remove_job
from telegram_bot.utils.message_builder import format_item_info


def parse_args(original_args: list):
    arguments = []

    args_iter = iter(original_args)
    try:
        for arg in args_iter:
            if arg.startswith((*QUOTATION_MARKS, '«')):
                while not arg.endswith((*QUOTATION_MARKS, '»')):
                    arg += f' {next(args_iter)}'
            arguments.append(
                arg.strip(
                    "".join([*QUOTATION_MARKS, ' ', '«', '»'])
                )
            )
    except StopIteration:
        raise CommandException(ERRMSG_BRACKETS_ERROR)

    return arguments


def parse_item_info_args(args: list):
    if len(args) < 2:
        raise CommandException(ERRMSG_NOT_ENOUGH_ARGS)

    if not args[0].isdigit():
        raise CommandException(ERRMSG_APPID_NOT_INT)

    no_image = NO_IMAGE_ARG in args
    if no_image:
        args = [arg for arg in args if arg != NO_IMAGE_ARG]

    return args, no_image


def parse_time(time_str: str):
    try:
        return time.fromisoformat(
            time_str
        ).replace(tzinfo=timezone(timedelta(hours=3)))  # TODO: this timezone is temporary
    except ValueError:
        raise CommandException(ERRMSG_WRONG_TIME_FORMAT)


def parse_datetime(datetime_str: str, datetime_format: str = DATETIME_FORMAT):
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
    def command_func(update: Update, context: CallbackContext, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=ChatAction.TYPING
        )
        return func(update, context,  *args, **kwargs)

    return command_func


def whitelist_only(func):
    @wraps(func)
    def command_func(update: Update, context: CallbackContext, *args, **kwargs):
        try:
            Whitelist.where(
                'user_id', update.effective_user.id
            ).first_or_fail()
        except ModelNotFound:
            text = emojize(
                ':no_entry: You are not on the whitelist', use_aliases=True
            )
            reply_markup = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    'Request to be whitelisted',
                    callback_data=WL_REQUEST
                )
            ]])
            context.bot.send_message(
                chat_id=update.effective_message.chat_id, text=text,
                reply_markup=reply_markup
            )
            return

        return func(update, context,  *args, **kwargs)

    return command_func


def admin_only(func):
    @wraps(func)
    def command_func(update: Update, context: CallbackContext, *args, **kwargs):
        if update.effective_user.id != ADMIN_ID:
            return

        return func(update, context,  *args, **kwargs)

    return command_func


def send_item_message(
        context, chat_id: int, message_text: str,
        no_image: bool, image_url: str, url: str
):
    if url:
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton('Market link', url=url)]]
        )
    else:
        reply_markup = None

    if not no_image and image_url:
        context.bot.send_photo(
            chat_id=chat_id,
            photo=image_url,
            caption=message_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text=message_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
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

    if not item_info_dict['full_info']:
        message_text = (
            f'{message_text}\n\n:exclamation: {WRNMSG_NOT_FULL_INFO}'
        )

    if add_to_message:
        message_text += add_to_message

    message_text = emojize(message_text, use_aliases=True)

    send_item_message(
        context, chat_id, message_text, no_image, item_info_dict['icon_url'],
        item_info_dict['market_url']
    )


def handle_job_error(context: CallbackContext, chat_id: int):
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
            if JOB_TO_CHAT_DATA_KEY[context.job.name] in (II_ALERT_JOBS,):
                job = context.job.context['job']
            else:
                job = context.job

            remove_job(context, context.job.context['chat_id'], job)

    return job_func


def parse_alert_conditions(conditions: list):
    resulting_conditions = []

    try:
        for condition in conditions:
            cond_key, cond_value = condition.lower().split(KV_SEPARATOR)
            key_name, postfix = cond_key.split(COND_SEPARATOR)

            resulting_conditions.append((key_name, postfix, cond_value))
    except ValueError:
        raise CommandException(ERRMSG_ALERT_NOT_VALID_CONDITIONS)

    return resulting_conditions


def get_paginated_list(some_list: list, page_size: int):
    paginated_list = []

    for index in range(math.ceil(len(some_list)/page_size)):
        start_index = index*page_size
        paginated_list.append(some_list[start_index:start_index+page_size])

    return paginated_list
