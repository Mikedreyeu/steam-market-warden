from telegram.ext.jobqueue import Days

from telegram_bot.constants import KV_SEPARATOR, COND_SEPARATOR, SELL_PRICE, \
    MEDIAN_PRICE, CURRENCY_SYMBOL, GT_POSTFIX, LT_POSTFIX, GTE_POSTFIX, \
    LTE_POSTFIX, POSTFIX_TO_SYMBOL, DOTW_DICT


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
