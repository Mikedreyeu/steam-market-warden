import re
from datetime import timedelta, datetime, timezone

from emoji import emojize
from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from telegram.ext.jobqueue import Days

from market_api.api import market_search_for_command
from telegram_bot.constants import (NO_IMAGE_ARG, TIMEDELTA_KEYS,
                                    INTERVAL_UNIT_REGEX, II_TIMED_JOBS,
                                    II_DAILY_JOBS, II_REPEATING_JOBS,
                                    II_ALERT_JOBS, JOBS)
from telegram_bot.exceptions.error_messages import (ERRMSG_NOT_ENOUGH_ARGS,
                                                    ERRMSG_WRONG_INTERVAL_FORMAT,
                                                    ERRMSG_WRONG_DOTW_FORMAT)
from telegram_bot.exceptions.exceptions import CommandException
from telegram_bot.jobs import item_info_timed_job, \
    check_values_of_an_item_info_job, item_info_repeating_job, \
    item_info_daily_job
from telegram_bot.utils.job_utils import save_jobs, init_jobs_dict_chat_data
from telegram_bot.utils.message_builder import format_market_search, \
    format_days_of_the_week, format_alerts_conditions, format_when_timed_job
from telegram_bot.utils.utils import parse_args, send_typing_action, \
    send_item_message, send_item_info, parse_datetime, parse_time


def start_command(update: Update, context: CallbackContext):
    update.message.reply_text(text='Hi!')


@send_typing_action
def market_search_command(update: Update, context: CallbackContext):
    args = parse_args(context.args)

    if len(args) < 1:
        raise CommandException(ERRMSG_NOT_ENOUGH_ARGS)

    no_image = NO_IMAGE_ARG in args
    if no_image:
        args = [arg for arg in args if arg != NO_IMAGE_ARG]

    market_search_dict = market_search_for_command(query=args[0])

    message_text = format_market_search(market_search_dict)

    send_item_message(
        context, update.effective_chat.id, message_text,
        no_image, market_search_dict['icon_url']
    )


@send_typing_action
def item_info_command(update: Update, context: CallbackContext):
    args = parse_args(context.args)
    send_item_info(context, update.effective_chat.id, args)


def item_info_timed_command(update: Update, context: CallbackContext):
    args = parse_args(context.args)

    if args[0].isdigit():
        when = int(args[0])
    else:
        when = parse_datetime(f'{args[0]} {args[1]}')

    chat_id = update.message.chat_id
    job_context = {
        'chat_id': chat_id,
        'item_info_args': args[args.index('-')+1:],
        'when': when
    }

    new_job = context.job_queue.run_once(
        item_info_timed_job, when, job_context
    )

    init_jobs_dict_chat_data(context.chat_data)
    context.chat_data[JOBS][II_TIMED_JOBS].append(new_job)

    success_text = (
        f':steam_locomotive: <b>Timed item info set</b>\n'
        f'<b>Item:</b> {", ".join(args[args.index("-")+1:])}\n'
        f'<b>Time:</b> {format_when_timed_job(when)}'
    )

    update.message.reply_text(
        emojize(success_text, use_aliases=True),
        parse_mode=ParseMode.HTML
    )


def item_info_repeating_command(update: Update, context: CallbackContext):
    args = parse_args(context.args)

    chat_id = update.message.chat_id

    interval_str = args[0]

    if not re.fullmatch(fr'({INTERVAL_UNIT_REGEX})+', interval_str):
        raise CommandException(ERRMSG_WRONG_INTERVAL_FORMAT)

    interval_tuples = re.findall(INTERVAL_UNIT_REGEX, interval_str)
    timedelta_kwargs = {
        TIMEDELTA_KEYS[interval_letter]: int(interval_units)
        for interval_units, interval_letter in interval_tuples
    }
    interval = timedelta(**timedelta_kwargs)

    if args.index('-') >= 3:
        first = parse_datetime(f'{args[1]} {args[2]}')
    else:
        first = datetime.now(tz=timezone(timedelta(hours=3)))

    job_context = {
        'chat_id': chat_id,
        'item_info_args': args[args.index('-')+1:],
        'interval': interval,
        'first': first
    }

    new_job = context.job_queue.run_repeating(
        item_info_repeating_job, interval, first, job_context
    )

    init_jobs_dict_chat_data(context.chat_data)
    context.chat_data[JOBS][II_REPEATING_JOBS].append(new_job)

    success_text = (
        f':articulated_lorry: <b>Repeating item info set</b>\n'
        f'<b>Item:</b> {", ".join(args[args.index("-")+1:])}\n'
        f'Every {interval}\n'
        f'Starting at {first}'
    )

    update.message.reply_text(
        emojize(success_text, use_aliases=True),
        parse_mode=ParseMode.HTML
    )


def item_info_daily_command(update: Update, context: CallbackContext):
    args = parse_args(context.args)

    chat_id = update.message.chat_id

    if args.index('-') >= 2:
        time_str = args[1]
        try:
            days_otw = tuple(int(dotw) - 1 for dotw in args[0].split(','))
        except (ValueError, IndexError):
            raise CommandException(ERRMSG_WRONG_DOTW_FORMAT)
    else:
        days_otw = Days.EVERY_DAY
        time_str = args[0]

    time_object = parse_time(time_str)

    job_context = {
        'chat_id': chat_id,
        'item_info_args': args[args.index('-')+1:],
        'days_otw': days_otw,
        'time': time_object
    }

    new_job = context.job_queue.run_daily(
        item_info_daily_job, time_object, days_otw, job_context
    )

    init_jobs_dict_chat_data(context.chat_data)
    context.chat_data[JOBS][II_DAILY_JOBS].append(new_job)

    success_text = (
        f':truck: <b>Daily item info set</b>\n'
        f'<b>Item:</b> {", ".join(args[args.index("-")+1:])}\n'
        f'<b>Days:</b> {format_days_of_the_week(days_otw)}\n'
        f'<b>Time:</b> {time_object}'
    )

    update.message.reply_text(
        emojize(success_text, use_aliases=True),
        parse_mode=ParseMode.HTML
    )


def item_info_alert_command(update: Update, context: CallbackContext):
    args = parse_args(context.args)

    chat_id = update.message.chat_id

    job_context = {
        'chat_id': chat_id,
        'conditions': args[:args.index('-')],
        'item_info_args': args[args.index('-')+1:]
    }

    context.job_queue.run_once(
        check_values_of_an_item_info_job, 1, job_context
    )

    new_job = context.job_queue.run_repeating(
        check_values_of_an_item_info_job, timedelta(minutes=20),
        context=job_context
    )

    init_jobs_dict_chat_data(context.chat_data)
    context.chat_data[JOBS][II_ALERT_JOBS].append(new_job)

    success_text = (
        f':nail_care: <b>Alert set</b>\n'
        f'<b>Item:</b> {", ".join(args[args.index("-")+1:])}\n'
        f'{format_alerts_conditions(args[:args.index("-")])}'
    )

    update.message.reply_text(
        emojize(success_text, use_aliases=True),
        parse_mode=ParseMode.HTML
    )


def help_command(update: Update, context: CallbackContext):
    update.message.reply_text('Help!')
    save_jobs(context.job_queue)  # TODO: temporary


def test_command(update: Update, context: CallbackContext):
    pass
