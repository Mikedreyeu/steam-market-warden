from emoji import emojize
from telegram import ParseMode

from market_api.api import get_item_info
from telegram_bot.constants import KV_SEPARATOR, COND_SEPARATOR, SELL_PRICE, \
    MEDIAN_PRICE, CURRENCY_SYMBOL, ALLOWED_KEYS_FOR_ALARM, GT_POSTFIX, \
    LT_POSTFIX, GTE_POSTFIX, LTE_POSTFIX
from telegram_bot.exceptions.error_messages import \
    ERRMSG_ALARM_NOT_VALID_CONDITIONS, ERRMSG_ALARM_NOT_ALLOWED_KEYS, \
    ERRMSG_ALARM_NOT_VALID_POSTFIX
from telegram_bot.exceptions.exceptions import CommandException
from telegram_bot.utils.job_utils import save_jobs
from telegram_bot.utils.message_builder import format_item_info
from telegram_bot.utils.utils import parse_item_info_args, send_item_message, \
    send_item_info


def check_values_of_an_item_info_job(context):
    args, no_image = parse_item_info_args(context.job.context['args'])

    item_info_dict = get_item_info(args[0], args[1])

    meets_conditions_list = []

    for condition in context.job.context['conditions']:
        try:
            cond_key, cond_value = condition.lower().split(KV_SEPARATOR)
            key_name, postfix = cond_key.split(COND_SEPARATOR)

            if key_name in (SELL_PRICE, MEDIAN_PRICE):
                currency_symbol = CURRENCY_SYMBOL
                cond_value = float(cond_value)
            else:
                currency_symbol = ''
                cond_value = int(cond_value)
        except ValueError:
            raise CommandException(ERRMSG_ALARM_NOT_VALID_CONDITIONS)

        if key_name not in ALLOWED_KEYS_FOR_ALARM:
            raise CommandException(ERRMSG_ALARM_NOT_ALLOWED_KEYS)

        alarm_text = (
            f'<b>{key_name}: {currency_symbol}{item_info_dict[key_name]}</b>'
            f' {{}} '
            f'{currency_symbol}{cond_value}'
        )

        if postfix == GT_POSTFIX:
            if item_info_dict[key_name] > cond_value:
                meets_conditions_list.append(
                    alarm_text.format('>')
                )
        elif postfix == LT_POSTFIX:
            if item_info_dict[key_name] < cond_value:
                meets_conditions_list.append(
                    alarm_text.format('<')
                )
        elif postfix == GTE_POSTFIX:
            if item_info_dict[key_name] >= cond_value:
                meets_conditions_list.append(
                    alarm_text.format('>=')
                )
        elif postfix == LTE_POSTFIX:
            if item_info_dict[key_name] <= cond_value:
                meets_conditions_list.append(
                    alarm_text.format('<=')
                )
        else:
            raise CommandException(ERRMSG_ALARM_NOT_VALID_POSTFIX)

    if len(meets_conditions_list) == len(context.job.context['conditions']):
        chat_id = context.job.context['chat_id']

        formatted_condition_list = "\n".join(meets_conditions_list)
        context.bot.send_message(
            chat_id, emojize(
                f':rotating_light: <b>Item alarm</b> '
                f'\n{formatted_condition_list}',
                use_aliases=True
            ),
            parse_mode=ParseMode.HTML
        )

        send_item_message(
            context, chat_id, format_item_info(item_info_dict),
            no_image, item_info_dict['icon_url']
        )

        context.job.schedule_removal()
        context.job.context['chat_jobs'].remove(context.job)


def save_jobs_job(context):
    save_jobs(context.job_queue)


def timed_item_info_job(context):
    send_item_info(
        context, context.job.context['chat_id'], context.job.context['args'],
        add_to_message=f'\n\n:alarm_clock: _Timed item info request_'
    )

    context.job.context['chat_jobs'].remove(context.job)
