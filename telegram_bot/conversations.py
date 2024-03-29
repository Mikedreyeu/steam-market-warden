from collections import defaultdict
from itertools import chain

from emoji import emojize
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, \
    ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from telegram.utils.helpers import mention_html

from settings import CHAT_FOR_REQUESTS
from telegram_bot.constants import (ST_CHOOSE_JOB_TYPE, CB_ALL, II_ALERT_JOBS,
                                    II_TIMED_JOBS, II_REPEATING_JOBS,
                                    II_DAILY_JOBS, ST_CHOOSE_JOB,
                                    JOB_TO_CHAT_DATA_KEY, SELECTED_JOB,
                                    CALLBACK_TO_TYPE, CB_MANAGE_JOB, NUMBERS,
                                    CB_BACK, ST_MANAGE_JOB, JOBS,
                                    CB_DELETE_JOB, CB_EDIT_JOB, CB_CANCEL,
                                    WL_REQUEST)
from telegram_bot.exceptions.exceptions import CommandException
from telegram_bot.utils.job_utils import remove_job
from telegram_bot.utils.message_builder import format_job
from telegram_bot.utils.utils import build_menu, get_paginated_list, \
    whitelist_only


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
            callback_data=f'{II_ALERT_JOBS}-0'
        ),
        InlineKeyboardButton(
            emojize(
                f':steam_locomotive: Timed [{timed_count}]',
                use_aliases=True)
            ,
            callback_data=f'{II_TIMED_JOBS}-0'
        ),
        InlineKeyboardButton(
            emojize(
                f':articulated_lorry: Repeating [{repeating_count}]',
                use_aliases=True
            ),
            callback_data=f'{II_REPEATING_JOBS}-0'
        ),
        InlineKeyboardButton(
            emojize(
                f':truck: Daily [{daily_count}]',
                use_aliases=True
            ),
            callback_data=f'{II_DAILY_JOBS}-0'
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
    elif context.match.group() in (CB_BACK, CB_DELETE_JOB):
        query = update.callback_query
        context.bot.edit_message_text(
            chat_id=query.message.chat_id, message_id=query.message.message_id,
            text='Choose a job type:', reply_markup=reply_markup
        )

    return ST_CHOOSE_JOB_TYPE


def choose_job_conv(update: Update, context: CallbackContext):
    query = update.callback_query

    if not context.args:
        job_type = context.match.group('job_type')
        current_page = int(context.match.group('page_number'))
    else:
        job_type = context.args.get('job_type')
        current_page = 0

    try:
        if job_type != CB_ALL:
            jobs_list = context.chat_data['jobs'][job_type]
            if not jobs_list:
                raise CommandException(message='You have no jobs of this type')
        else:
            jobs_list = list(
                chain.from_iterable(context.chat_data['jobs'].values())
            )
            if not jobs_list:
                raise CommandException(message='You have no jobs')
    except (KeyError, CommandException) as e:
        if isinstance(e, CommandException):
            error_message = e.message
        else:
            error_message = ':no_entry_sign: You have no jobs'

        context.bot.answer_callback_query(
            query.id,
            text=emojize(error_message, use_aliases=True)
        )

        if context.args:  # if job is deleted and there is no more jobs of that type
            return manage_item_info_jobs_command(update, context)

        return ST_CHOOSE_JOB_TYPE

    job_list_paginated = get_paginated_list(
        [(job, format_job(job)) for job in jobs_list],
        page_size=6
    )

    n_cols = 3
    button_list = []

    if len(job_list_paginated) > 1:
        header_pages_text = (f'<i>(page {current_page + 1}'
                             f'/{len(job_list_paginated)})</i>')
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
        header_pages_text = ''
        previous_button_text = ''
        next_button_text = ''

    text_job_list = (f'You have {len(jobs_list)}'
                     f' {CALLBACK_TO_TYPE[job_type]} jobs '
                     f'{header_pages_text}\n\n')

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

    button_list.extend([
        InlineKeyboardButton(
            previous_button_text, callback_data=f'{job_type}-{current_page-1}'
        ),
        InlineKeyboardButton(f'Back', callback_data=CB_BACK),
        InlineKeyboardButton(
            next_button_text, callback_data=f'{job_type}-{current_page+1}'
        )
    ])

    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=n_cols))

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=emojize(
            f'{text_job_list}Choose a {CALLBACK_TO_TYPE[job_type]} job:',
            use_aliases=True
        ),
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

    return ST_CHOOSE_JOB


def manage_job_conv(update: Update, context: CallbackContext):
    job_type = context.match.group('job_type')
    job_index = int(context.match.group('job_index'))

    job = context.chat_data[JOBS][job_type][job_index]
    job_info = format_job(job, emoji_in_front=True)

    button_list = [
        InlineKeyboardButton(
            'Edit', callback_data=CB_EDIT_JOB
        ),
        InlineKeyboardButton(
            'Delete', callback_data=CB_DELETE_JOB
        ),
        InlineKeyboardButton(
            'Back', callback_data=CB_BACK
        )
    ]

    context.user_data[SELECTED_JOB] = job

    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))

    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=emojize(
            f'{job_info}\n\nChoose an action:',
            use_aliases=True
        ),
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

    return ST_MANAGE_JOB


def edit_job_conv(update: Update, context: CallbackContext):
    return ST_MANAGE_JOB


def delete_job_conv(update: Update, context: CallbackContext):
    query = update.callback_query
    job = context.user_data[SELECTED_JOB]

    remove_job(
        context, query.message.chat_id, job
    )

    del context.user_data[SELECTED_JOB]

    query = update.callback_query
    context.bot.answer_callback_query(
        query.id,
        text=emojize('Job deleted', use_aliases=True)
    )

    context.args = {'job_type': JOB_TO_CHAT_DATA_KEY[job.name]}
    return choose_job_conv(update, context)


def back_to_choose_job_conv(update: Update, context: CallbackContext):
    job = context.user_data[SELECTED_JOB]
    context.args = {'job_type': JOB_TO_CHAT_DATA_KEY[job.name]}
    return choose_job_conv(update, context)


def end_conv(update: Update, context: CallbackContext):
    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text='Manage item info canceled'
    )
    return ConversationHandler.END


def whitelist_request_conv(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == WL_REQUEST:
        user_info_text = ''

        if update.effective_chat:
            user_info_text += f'Chat: <i>{update.effective_chat.title}</i>'
            if update.effective_chat.username:
                user_info_text += f' (@{update.effective_chat.username})'

        if update.effective_user:
            user_mention = mention_html(
                update.effective_user.id, update.effective_user.first_name
            )
            user_info_text = (
                f'User: {user_mention}\n'
                f'{user_info_text}\n'
                f'/add_to_whitelist@SteamMarketWardenBot'
                f' {update.effective_user.id}'
            )

        context.bot.send_message(
            CHAT_FOR_REQUESTS, user_info_text, parse_mode=ParseMode.HTML
        )

        text = emojize(
            ':no_entry: You are not on the whitelist\n:envelope: Request sent',
            use_aliases=True
        )

        context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=text
        )
