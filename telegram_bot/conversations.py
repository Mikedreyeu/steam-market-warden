from collections import defaultdict
from itertools import chain

from emoji import emojize
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, \
    ParseMode
from telegram.ext import CallbackContext, ConversationHandler

from telegram_bot.constants import (ST_CHOOSE_JOB_TYPE, CB_DAILY, CB_TIMED, CB_ALERT,
                                    CB_REPEATING, CB_CANCEL,
                                    CALLBACK_TO_CHAT_DATA_KEY, CB_ALL,
                                    II_ALERT_JOBS, II_TIMED_JOBS,
                                    II_REPEATING_JOBS, II_DAILY_JOBS,
                                    ST_CHOOSE_JOB, JOB_TO_CHAT_DATA_KEY,
                                    SELECTED_JOB, CALLBACK_TO_TYPE,
                                    CB_MANAGE_JOB, NUMBERS, CB_BACK)
from telegram_bot.exceptions.exceptions import CommandException
from telegram_bot.utils.message_builder import format_when_timed_job, \
    format_days_of_the_week, format_job
from telegram_bot.utils.utils import build_menu, parse_alert_conditions, \
    get_paginated_list


def manage_item_info_jobs_command(update: Update, context: CallbackContext):
    try:
        jobs_dict = context.chat_data['jobs']
    except KeyError:
        jobs_dict = defaultdict(list)

    alert_count = len(jobs_dict[II_ALERT_JOBS])
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
            callback_data=f'{CB_ALERT}-0'
        ),
        InlineKeyboardButton(
            emojize(
                f':steam_locomotive: Timed [{timed_count}]',
                use_aliases=True)
            ,
            callback_data=f'{CB_TIMED}-0'
        ),
        InlineKeyboardButton(
            emojize(
                f':articulated_lorry: Repeating [{repeating_count}]',
                use_aliases=True
            ),
            callback_data=f'{CB_REPEATING}-0'
        ),
        InlineKeyboardButton(
            emojize(
                f':truck: Daily [{daily_count}]',
                use_aliases=True
            ),
            callback_data=f'{CB_DAILY}-0'
        ),
        InlineKeyboardButton(
            emojize(
                f':nail_care::steam_locomotive: All [{total_count}]'
                f' :articulated_lorry::truck:',
                use_aliases=True
            ),
            callback_data=f'{CB_ALL}-0'
        ),
        InlineKeyboardButton('Cancel', callback_data=CB_CANCEL),
    ]

    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))

    if context.match is None:
        update.message.reply_text(
            'Choose a job type:', reply_markup=reply_markup
        )
    elif context.match.group() == CB_BACK:
        query = update.callback_query
        context.bot.edit_message_text(
            chat_id=query.message.chat_id, message_id=query.message.message_id,
            text='Choose a job type:', reply_markup=reply_markup
        )

    return ST_CHOOSE_JOB_TYPE


def choose_job_type_conv(update: Update, context: CallbackContext):
    match_job_type = context.match.group('job_type')
    current_page = int(context.match.group('page_number'))

    try:
        if match_job_type != CB_ALL:
            chat_data_key = CALLBACK_TO_CHAT_DATA_KEY[match_job_type]
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

        return ST_CHOOSE_JOB_TYPE

    job_list_paginated = get_paginated_list(
        [(job, format_job(job)) for job in jobs_list],
        page_size=6
    )

    n_cols = 3
    button_list = []

    text_job_list = (f'You have {len(jobs_list)}'
                     f' {CALLBACK_TO_TYPE[match_job_type]} jobs\n\n')

    for index, (job, job_info) in enumerate(job_list_paginated[current_page]):
        text_job_list += f'{NUMBERS[index+1]} {job_info}\n\n'

        chat_data_key = JOB_TO_CHAT_DATA_KEY[job.name]
        job_index = context.chat_data['jobs'][chat_data_key].index(job)
        callback_data = f'{CB_MANAGE_JOB}-{chat_data_key}-{job_index}'

        button_list.append(
            InlineKeyboardButton(
                emojize(f'{NUMBERS[index+1]}', use_aliases=True),
                callback_data=callback_data
            )
        )

    while len(button_list) % n_cols:
        button_list.append(InlineKeyboardButton('', callback_data=CB_MANAGE_JOB))

    if len(job_list_paginated) > 1:
        if current_page == 0:
            previous_button_text = ''
            next_button_text = f'{current_page+2} >'
        elif current_page == len(job_list_paginated) - 1:
            previous_button_text = f'< {current_page}'
            next_button_text = ''
        else:
            previous_button_text = f'< {current_page}'
            next_button_text = f'{current_page + 2} >'
    else:
        previous_button_text = ''
        next_button_text = ''

    button_list.extend([
        InlineKeyboardButton(previous_button_text, callback_data=CB_MANAGE_JOB),
        InlineKeyboardButton(f'Back', callback_data=CB_BACK),
        InlineKeyboardButton(next_button_text, callback_data=CB_MANAGE_JOB)
    ])

    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=n_cols))

    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=emojize(
            f'{text_job_list}Choose a {CALLBACK_TO_TYPE[match_job_type]} job:',
            use_aliases=True
        ),
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

    return ST_CHOOSE_JOB


def manage_job_conv(update: Update, context: CallbackContext):
    pass


def end_conv(update: Update, context: CallbackContext):
    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text='Manage item info canceled'
    )
    return ConversationHandler.END
