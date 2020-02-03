from emoji import emojize
from telegram import ParseMode
from telegram.ext import CallbackContext

from market_api.api import get_item_info
from telegram_bot.constants import SELL_PRICE, \
    MEDIAN_PRICE, CURRENCY_SYMBOL, ALLOWED_KEYS_FOR_ALERT, GT_POSTFIX, \
    LT_POSTFIX, GTE_POSTFIX, LTE_POSTFIX, POSTFIX_TO_SYMBOL, ALLOWED_POSTFIXES
from telegram_bot.exceptions.error_messages import \
    ERRMSG_ALERT_NOT_VALID_CONDITIONS, ERRMSG_ALERT_NOT_ALLOWED_KEYS, \
    ERRMSG_ALERT_NOT_VALID_POSTFIX
from telegram_bot.exceptions.exceptions import CommandException
from telegram_bot.utils.job_utils import save_jobs, remove_job
from telegram_bot.utils.message_builder import format_item_info
from telegram_bot.utils.utils import parse_item_info_args, send_item_message, \
    send_item_info, job_error_handler, parse_alert_conditions


@job_error_handler
def check_values_of_an_item_info_job(context: CallbackContext):
    args, no_image = parse_item_info_args(context.job.context['item_info_args'])
    item_info_dict = get_item_info(args[0], args[1])

    meets_conditions_list = []

    for condition in parse_alert_conditions(context.job.context['conditions']):
        try:
            key_name, postfix, cond_value = condition

            if key_name in (SELL_PRICE, MEDIAN_PRICE):
                currency_symbol = CURRENCY_SYMBOL
                cond_value = float(cond_value)
            else:
                currency_symbol = ''
                cond_value = int(cond_value)
        except ValueError:
            raise CommandException(ERRMSG_ALERT_NOT_VALID_CONDITIONS)

        if key_name not in ALLOWED_KEYS_FOR_ALERT:
            raise CommandException(ERRMSG_ALERT_NOT_ALLOWED_KEYS)

        if not item_info_dict[key_name]:
            continue

        alert_text = (
            f'<b>{key_name}: {currency_symbol}{item_info_dict[key_name]}</b>'
            f' {{}} '
            f'{currency_symbol}{cond_value}'
        )

        if postfix not in ALLOWED_POSTFIXES:
            raise CommandException(ERRMSG_ALERT_NOT_VALID_POSTFIX)

        if postfix == GT_POSTFIX and item_info_dict[key_name] > cond_value:
            meets_conditions_list.append(
                alert_text.format(POSTFIX_TO_SYMBOL[GT_POSTFIX])
            )
        elif postfix == LT_POSTFIX and item_info_dict[key_name] < cond_value:
            meets_conditions_list.append(
                alert_text.format(POSTFIX_TO_SYMBOL[LT_POSTFIX])
            )
        elif postfix == GTE_POSTFIX and item_info_dict[key_name] >= cond_value:
            meets_conditions_list.append(
                alert_text.format(POSTFIX_TO_SYMBOL[GTE_POSTFIX])
            )
        elif postfix == LTE_POSTFIX and item_info_dict[key_name] <= cond_value:
            meets_conditions_list.append(
                alert_text.format(POSTFIX_TO_SYMBOL[LTE_POSTFIX])
            )

    if len(meets_conditions_list) == len(context.job.context['conditions']):
        chat_id = context.job.context['chat_id']

        formatted_condition_list = "\n".join(meets_conditions_list)
        context.bot.send_message(
            chat_id, emojize(
                f':rotating_light: <b>Item alert</b> '
                f'\n{formatted_condition_list}',
                use_aliases=True
            ),
            parse_mode=ParseMode.HTML
        )

        send_item_message(
            context, chat_id, format_item_info(item_info_dict),
            no_image, item_info_dict['icon_url'], item_info_dict['market_url']
        )

        remove_job(context, chat_id, context.job)


@job_error_handler
def item_info_repeating_job(context: CallbackContext):
    send_item_info(
        context, context.job.context['chat_id'], context.job.context['item_info_args'],
        add_to_message=f'\n\n:alarm_clock: _Repeating item info request_'
    )


@job_error_handler
def item_info_daily_job(context: CallbackContext):
    send_item_info(
        context, context.job.context['chat_id'], context.job.context['item_info_args'],
        add_to_message=f'\n\n:alarm_clock: _Daily item info request_'
    )


@job_error_handler
def item_info_timed_job(context: CallbackContext):
    chat_id = context.job.context['chat_id']

    send_item_info(
        context, chat_id, context.job.context['item_info_args'],
        add_to_message=f'\n\n:alarm_clock: _Timed item info request_'
    )

    remove_job(context, chat_id, context.job)


@job_error_handler
def save_jobs_job(context: CallbackContext):
    save_jobs(context.job_queue)
