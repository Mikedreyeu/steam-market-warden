from typing import Union

from telegram.ext.jobqueue import Days, Job

from telegram_bot.constants import SELL_PRICE, MEDIAN_PRICE, CURRENCY_SYMBOL, \
    POSTFIX_TO_SYMBOL, DOTW_DICT, JOB_TO_CHAT_DATA_KEY, II_TIMED_JOBS, \
    II_REPEATING_JOBS, II_DAILY_JOBS, II_ALERT_JOBS


def format_item_info(item_info):
    return (
        f'*Name:* {item_info.get("name")}\n'
        f'*Sell price:* ${item_info.get("sell_price")}\n'
        f'*Sell listings:* {item_info.get("sell_listings")}\n'
        f'*Median price:* {"$" if item_info.get("median_price") else ""}'
        f'{item_info.get("median_price")}\n'
        f'*Volume:* {item_info.get("volume")}'
    )


def format_market_search(market_search):
    return (
        f'*App name:* {market_search.get("app_name")} '
        f'(appid: {market_search.get("appid")})\n'
        f'*Item name:* {market_search.get("name")}\n'
        f'*Sell price:* {market_search.get("sell_price_text")}\n'
        f'*Sell listings:* {market_search.get("sell_listings")}'
    )


def format_days_of_the_week(days_list: list, short_form: bool = False):
    if days_list == Days.EVERY_DAY:
        return 'Every day'

    if not short_form:
        days_list = [DOTW_DICT[day][0] for day in days_list]
    else:
        days_list = [DOTW_DICT[day][1] for day in days_list]

    return ', '.join(days_list)


def format_alerts_conditions(conditions):
    from telegram_bot.utils.utils import parse_alert_conditions

    result_text = '<b>Conditions:</b>'

    for condition in parse_alert_conditions(conditions):
        key_name, postfix, cond_value = condition

        if key_name not in (SELL_PRICE, MEDIAN_PRICE):
            currency_symbol = ''
            cond_value = int(cond_value)
        else:
            currency_symbol = CURRENCY_SYMBOL
            cond_value = float(cond_value)

        condition_text = (
            f'{key_name} {POSTFIX_TO_SYMBOL[postfix]} '
            f'{currency_symbol}{cond_value}'
        )

        result_text = f'{result_text}\n{condition_text}'

    return result_text


def format_when_timed_job(when):
    if isinstance(when, int):
        return f'{when} seconds from now'
    else:
        return when


def format_job(job: Job, with_header: bool = True):

    job_item = ', '.join(job.context['item_info_args'])

    if JOB_TO_CHAT_DATA_KEY[job.name] == II_TIMED_JOBS:
        header = ('<b>Timed item info</b> :steam_locomotive:\n'
                  if with_header else '')
        return (
            f'{header}'
            f'<b>Item:</b> {job_item}\n'
            f'<b>Time:</b> {format_when_timed_job(job.context["when"])}'
        )
    elif JOB_TO_CHAT_DATA_KEY[job.name] == II_REPEATING_JOBS:
        header = ('<b>Repeating item info</b> :articulated_lorry:\n'
                  if with_header else '')
        return (
            f'{header}'
            f'<b>Item:</b> {job_item}\n'
            f'Every {job.context["interval"]}\n'
            f'Starting at {job.context["first"]}'
        )
    elif JOB_TO_CHAT_DATA_KEY[job.name] == II_DAILY_JOBS:
        header = '<b>Daily item info</b> :truck:\n' if with_header else ''
        return (
            f'{header}'
            f'<b>Item:</b> {job_item}\n'
            f'<b>Days:</b> {format_days_of_the_week(job.context["days_otw"])}'
            f'\n<b>Time:</b> {job.context["time"]}'
        )
    elif JOB_TO_CHAT_DATA_KEY[job.name] == II_ALERT_JOBS:
        header = '<b>Alert</b> :nail_care:\n' if with_header else ''
        return (
            f'{header}'
            f'<b>Item:</b> {job_item}\n'
            f'{format_alerts_conditions(job.context["conditions"])}'
        )
