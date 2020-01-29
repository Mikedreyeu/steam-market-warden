from collections import defaultdict
from itertools import chain

from emoji import emojize
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from telegram_bot.constants import (CHOOSE_JOB_TYPE, DAILY, TIMED, ALERT,
                                    REPEATING, CANCEL,
                                    CALLBACK_TO_CHAT_DATA_KEY, ALL,
                                    II_ALERT_JOBS, II_TIMED_JOBS,
                                    II_REPEATING_JOBS, II_DAILY_JOBS,
                                    CHOOSE_JOB, JOB_TO_CHAT_DATA_KEY,
                                    SELECTED_JOB, KV_SEPARATOR, COND_SEPARATOR)
from telegram_bot.exceptions.exceptions import CommandException
from telegram_bot.utils.utils import build_menu, parse_alert_conditions
from telegram_bot.utils.message_builder import format_when_timed_job


def manage_item_info_jobs_command(update: Update, context: CallbackContext):
    try:
        jobs_dict = context.chat_data['jobs']
    except KeyError:
        jobs_dict = defaultdict(list)

    alert_count = len(jobs_dict[II_REPEATING_JOBS])
    timed_count = len(jobs_dict[II_TIMED_JOBS])
    repeating_count = len(jobs_dict[II_REPEATING_JOBS])
    daily_count = len(jobs_dict[II_DAILY_JOBS])
    total_count = alert_count + timed_count + repeating_count + daily_count

    button_list = [
        InlineKeyboardButton(
            emojize(
                f':nail_care: Alert [{alert_count}]',
                use_aliases=True
            ),
            callback_data=ALERT
        ),
        InlineKeyboardButton(
            emojize(
                f':steam_locomotive: Timed [{timed_count}]',
                use_aliases=True)
            ,
            callback_data=TIMED
        ),
        InlineKeyboardButton(
            emojize(
                f':articulated_lorry: Repeating [{repeating_count}]',
                use_aliases=True
            ),
            callback_data=REPEATING
        ),
        InlineKeyboardButton(
            emojize(
                f':truck: Daily [{daily_count}]',
                use_aliases=True
            ),
            callback_data=DAILY
        ),
        InlineKeyboardButton(
            emojize(
                f':nail_care::steam_locomotive: All [{total_count}]'
                f' :articulated_lorry::truck:',
                use_aliases=True
            ),
            callback_data=DAILY
        ),
        InlineKeyboardButton('Cancel', callback_data=CANCEL),
    ]

    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))

    update.message.reply_text('Choose a job type:', reply_markup=reply_markup)

    return CHOOSE_JOB_TYPE


def choose_job_conv(update: Update, context: CallbackContext):
    match = context.match.group()

    try:
        if match != ALL:
            chat_data_key = CALLBACK_TO_CHAT_DATA_KEY[context.match.group()]
            jobs_list = context.chat_data['jobs'][chat_data_key]
            if not jobs_list:
                raise CommandException(message='You have no jobs of this type')
        else:
            jobs_list = list(
                chain.from_iterable(context.chat_data['jobs'].values())
            )
            if not jobs_list:
                raise CommandException(message='You have no jobs')
    except (KeyError, CommandException) as e:
        query = update.callback_query

        if isinstance(e, CommandException):
            error_message = e.message
        else:
            error_message = ':no_entry_sign: You have no jobs'

        context.bot.answer_callback_query(
            query.id,
            text=emojize(error_message, use_aliases=True)
        )

        return CHOOSE_JOB_TYPE

    button_list = []

    for job in jobs_list:
        job_type = JOB_TO_CHAT_DATA_KEY[job.name]
        button_text = ", ".join(job.context["item_info_args"])

        if job_type == II_TIMED_JOBS:
            button_text = (f'[{format_when_timed_job(job.context["when"])}] '
                           f'{button_text}')
        elif job_type == II_ALERT_JOBS:
            conditions_keys = []
            for condition in parse_alert_conditions(job.context['conditions']):
                key_name, _, _ = condition
                conditions_keys.append(key_name)
            button_text = f'[{", ".join(conditions_keys)}] {button_text}'
        elif job_type == II_REPEATING_JOBS:
            button_text = (f'[Every {job.context["interval"]}, '
                           f'start:{job.context["first"]}] {button_text}')
        elif job_type == II_DAILY_JOBS:
            button_text = (f'[{job.context["interval"]}, '
                           f'Time: {job.context["time"]}] {button_text}')

        context.user_data[SELECTED_JOB] = job

        button_list.append(
            InlineKeyboardButton(button_text, callback_data=ALERT)
        )

    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))

    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text='Choose a job:',
        reply_markup=reply_markup
    )

    return CHOOSE_JOB


def end_conversation(update: Update, context: CallbackContext):
    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text='Manage item info canceled'
    )
    return ConversationHandler.END
