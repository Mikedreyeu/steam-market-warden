import logging
import sys
import traceback
from datetime import datetime, timedelta, timezone

from emoji import emojize
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
from telegram.utils.helpers import mention_html

from market_api.api import get_item_info, market_search_for_command
from settings import BOT_TOKEN, CHAT_FOR_ERRORS
from telegram_bot.constants import NO_IMAGE_ARG, DATETIME_FORMAT, GT_POSTFIX, \
    LT_POSTFIX, GTE_POSTFIX, \
    LTE_POSTFIX, COND_SEPARATOR, KV_SEPARATOR, ALLOWED_KEYS_FOR_ALARM, \
    SELL_PRICE, MEDIAN_PRICE, CURRENCY_SYMBOL
from telegram_bot.exceptions.error_messages import (ERRMSG_NOT_ENOUGH_ARGS,
                                                    WRNMSG_NOT_EXACT,
                                                    ERRMSG_WRONG_ARGUMENT_RUN_ONCE,
                                                    ERRMSG_NO_FUTURE,
                                                    ERRMSG_ALARM_NOT_ALLOWED_KEYS,
                                                    ERRMSG_ALARM_NOT_VALID_POSTFIX,
                                                    ERRMSG_ALARM_NOT_VALID_CONDITIONS)
from telegram_bot.exceptions.exceptions import CommandException, ApiException
from telegram_bot.utils.message_builder import format_item_info, format_market_search
from telegram_bot.utils.job_utils import init_chat_data, save_jobs, load_jobs
from telegram_bot.utils.utils import parse_args, send_typing_action, \
    send_item_message, parse_item_info_args

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def start_command(update, context):
    update.message.reply_text('Hi!')


@send_typing_action
def market_search_command(update, context):
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
def item_info_command(update, context):
    args = parse_args(context.args)
    _send_item_info(context, update.effective_chat.id, args)


def _send_item_info(
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

# def timed_item_info_command(update, context):
#     keyboard = [InlineKeyboardButton('run_once', callback_data='1'),
#                 InlineKeyboardButton('run_repeating', callback_data='2'),
#                 InlineKeyboardButton('run_daily', callback_data='3')]
#
#     reply_markup = InlineKeyboardMarkup(build_menu(keyboard, n_cols=2))
#
#     update.message.reply_text('Please choose:', reply_markup=reply_markup)


def timed_item_info_command(update, context):
    args = parse_args(context.args)

    if args[0].isdigit():
        when = int(args[0])
    else:
        try:
            when = datetime.strptime(
                f'{args[0]} {args[1]}',
                DATETIME_FORMAT
            ).replace(tzinfo=timezone(timedelta(hours=3))) # TODO: this timezone is temporary
        except (ValueError, IndexError):
            raise CommandException(ERRMSG_WRONG_ARGUMENT_RUN_ONCE)

        if when < datetime.now().replace(tzinfo=timezone(timedelta(hours=3))): # TODO: this timezone is temporary
            raise CommandException(ERRMSG_NO_FUTURE)

    init_chat_data(context.chat_data)

    chat_id = update.message.chat_id
    job_context = {
        'chat_id': chat_id,
        'args': args[args.index('-')+1:],
        'chat_jobs': context.chat_data['timed_item_info_jobs']['run_once']
    }

    new_job = context.job_queue.run_once(
        timed_item_info_job, when, context=job_context
    )

    context.chat_data['timed_item_info_jobs']['run_once'].append(new_job)


def alarm_item_info_command(update, context):
    args = parse_args(context.args)

    chat_id = update.message.chat_id

    init_chat_data(context.chat_data)

    job_context = {
        'chat_id': chat_id,
        'conditions': args[:args.index('-')],
        'args': args[args.index('-')+1:],
        'chat_jobs': context.chat_data['item_info_alert_jobs']
    }

    new_job = context.job_queue.run_repeating(
        check_values_of_an_item_info_job, timedelta(seconds=5),  # TODO: Change time
        context=job_context
    )

    context.chat_data['item_info_alert_jobs'].append(new_job)


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
                f':rotating_light: <b>Item alarm</b> \n{formatted_condition_list}'
                , use_aliases=True
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
    _send_item_info(
        context, context.job.context['chat_id'], context.job.context['args'],
        add_to_message=f'\n\n:alarm_clock: _Timed item info request_'
    )

    context.job.context['chat_jobs'].remove(context.job)


def help_command(update, context):
    update.message.reply_text('Help!')


def error_handler(update, context):
    logger.warning(
        'Update "%s" caused error "%s"', update, context.error
    )
    if type(context.error) in (CommandException, ApiException):
        update.message.reply_text(
            context.error.message, parse_mode=ParseMode.MARKDOWN
        )
    else:
        payload = ''

        if update.effective_user:
            user_mention = mention_html(
                update.effective_user.id, update.effective_user.first_name
            )
            payload += f' with the user {user_mention}'
            
        if update.effective_chat:
            payload += f' within the chat <i>{update.effective_chat.title}</i>'
            if update.effective_chat.username:
                payload += f' (@{update.effective_chat.username})'

        if update.poll:
            payload += f' with the poll id {update.poll.id}.'

        trace = ''.join(traceback.format_tb(sys.exc_info()[2]))
        text = (
            f'The error <code>{context.error}</code> '
            f'happened{payload}.\nThe full traceback:\n\n'
            f'<code>{trace}</code>'
        )

        context.bot.send_message(
            CHAT_FOR_ERRORS, text, parse_mode=ParseMode.HTML
        )


def main():
    updater = Updater(BOT_TOKEN, use_context=True)

    job_queue = updater.job_queue
    dp = updater.dispatcher

    # job_queue.run_repeating(save_jobs_job, timedelta(minutes=1))

    try:
        load_jobs(job_queue)
    except FileNotFoundError:
        # First run
        pass

    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler('timed_item_info', timed_item_info_command)],
    #     states={
    #         FIRST: [CallbackQueryHandler(timed_item_info_run_once, pattern='^' + str(ONE) + '$'),],
    #     },
    #     fallbacks=[CommandHandler('timed_item_info', timed_item_info_command)]
    # )
    # dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('item_info', item_info_command))
    dp.add_handler(CommandHandler('market_search', market_search_command))
    dp.add_handler(
        CommandHandler('timed_item_info', timed_item_info_command)
    )
    dp.add_handler(
        CommandHandler('alarm_item_info', alarm_item_info_command)
    )
    dp.add_handler(CommandHandler('help', help_command))

    dp.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()

    save_jobs(job_queue)


if __name__ == '__main__':
    main()
