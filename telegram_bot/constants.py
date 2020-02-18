JOBS_PICKLE_FOLDER = '../pickles/'
JOBS_PICKLE = f'{JOBS_PICKLE_FOLDER}user_jobs.pickle'

NO_IMAGE_ARG = '-no_image'

QUOTATION_MARKS = ('"', "'", '`', '“', '”', '‘', '’')

API_REQUEST_COOLDOWN = 5

# Stages
ST_CHOOSE_JOB_TYPE, ST_CHOOSE_JOB, ST_MANAGE_JOB = range(3)

# Callback data
(CB_ALL, CB_CANCEL, CB_MANAGE_JOB,
 CB_BACK, CB_EDIT_JOB, CB_DELETE_JOB) = (str(item) for item in range(6))

DATETIME_FORMAT = '%H:%M %d.%m.%Y'

KV_SEPARATOR = '='

SELL_PRICE = 'sell_price'
SELL_LISTINGS = 'sell_listings'
MEDIAN_PRICE = 'median_price'
VOLUME = 'volume'

COND_SEPARATOR = '__'

GT_POSTFIX = 'gt'
LT_POSTFIX = 'lt'
GTE_POSTFIX = 'gte'
LTE_POSTFIX = 'lte'

ALLOWED_POSTFIXES = (GT_POSTFIX, LT_POSTFIX, GTE_POSTFIX, LTE_POSTFIX)

POSTFIX_TO_SYMBOL = {
    GT_POSTFIX: '&gt;',
    LT_POSTFIX: '&lt;',
    GTE_POSTFIX: '&gt;=',
    LTE_POSTFIX: '&lt;=',
}

ALLOWED_KEYS_FOR_ALERT = (SELL_PRICE, SELL_LISTINGS, MEDIAN_PRICE, VOLUME)

CURRENCY_SYMBOL = '$'  # tmp

MINUTES = 'm'
HOURS = 'h'
DAYS = 'd'
WEEKS = 'w'

TIMEDELTA_KEYS = {
    MINUTES: 'minutes',
    HOURS: 'hours',
    DAYS: 'days',
    WEEKS: 'weeks'
}

INTERVAL_UNIT_REGEX = fr'(\d+)([{MINUTES}{HOURS}{DAYS}{WEEKS}])'

JOBS = 'jobs'
SELECTED_JOB = 'selected_job'

II_ALERT_JOBS = 'item_info_alert'
II_TIMED_JOBS = 'timed'
II_REPEATING_JOBS = 'repeating'
II_DAILY_JOBS = 'daily'

WL_REQUEST = 'whitelist_request'

CHOOSE_JOB_TYPE_REGEX = (
    f'^(?P<job_type>{"|".join([II_ALERT_JOBS, II_TIMED_JOBS, II_REPEATING_JOBS, II_DAILY_JOBS, CB_ALL])})'
    f'-(?P<page_number>\\d+)$'
)

MANAGE_JOB_REGEX = (
    f'^{CB_MANAGE_JOB}'
    f'-(?P<job_type>{"|".join([II_ALERT_JOBS, II_TIMED_JOBS, II_REPEATING_JOBS, II_DAILY_JOBS])})'
    f'-(?P<job_index>\\d+)$'
)

CALLBACK_TO_TYPE = {
    II_ALERT_JOBS: 'alert',
    II_TIMED_JOBS: 'timed',
    II_REPEATING_JOBS: 'repeating',
    II_DAILY_JOBS: 'daily',
    CB_ALL: ''
}

JOB_TO_CHAT_DATA_KEY = {
    'check_values_of_an_item_info_job': II_ALERT_JOBS,
    'timed_job': II_TIMED_JOBS,
    'repeating_job': II_REPEATING_JOBS,
    'daily_job': II_DAILY_JOBS
}

DOTW_DICT = {
    0: ('Monday', 'Mon'),
    1: ('Tuesday', 'Tue'),
    2: ('Wednesday', 'Wed'),
    3: ('Thursday', 'Thu'),
    4: ('Friday', 'Fri'),
    5: ('Saturday', 'Sat'),
    6: ('Sunday', 'Sun')
}

NUMBERS = {
    1: ':one:',
    2: ':two:',
    3: ':three:',
    4: ':four:',
    5: ':five:',
    6: ':six:',
    7: ':seven:',
    8: ':eight:',
    9: ':nine:'
}


help_command_text_part_1 = (
    'You can control this bot by sending these commands:\n\n'
    
    '<b>:rocket: Get item info</b>\n'
    '<b>Usage:</b> /item_info <i>appid item_name</i> [<i>-no_image</i>]\n'
    '\n<b>Args:</b>\n'
    '<b>1. <i>appid</i></b> - id of an app\n'
    f'<b>2. <i>item_name</i></b> - name of the item or part of it.\nIf <i>item_name</i> has spaces, you need to type it inside quotation marks({" ".join(QUOTATION_MARKS)})\n'
    '<b>3. <i>-no_image</i></b> - you can add this to your command if you want item info without image\n'
    '\n<b>Examples:</b> \n<i>/item_info 440 "Mann Co. Supply Crate Key"</i>\n'
    '<i>/item_info 440 "Mann Co. Supply Crate Key" -no_item</i>\n\n'
    

    '<b>:helicopter: Search the market</b>\n'
    '<b>Usage:</b> /market_search <i>query</i> [<i>-no_image</i>]\n'
    '\n<b>Args:</b>\n'
    f'<b>1. <i>query</i></b> - name of the item or part of it.\nIf <i>query</i> has spaces, you need to type it inside quotation marks({" ".join(QUOTATION_MARKS)})\n'
    '<b>2. <i>-no_image</i></b> - same as in /item_info\n'
    '\n<b>Example:</b> <i>/market_search gloves</i>\n'
)

help_command_text_part_2 = (
    '<b>:man_construction_worker::woman_firefighter:  Jobs :woman_mechanic::man_factory_worker:</b>\n\n'

    '<b>:books: Manage your jobs</b>\n'
    '<b>Usage:</b> /manage_jobs\n\n'

    '<b>:steam_locomotive: Get item info on specific time once</b>\n'
    '<b>Usage:</b> <i>/timed when - appid item_name</i> [<i>-no_image</i>]\n'
    '\n<b>Args:</b>\n'
    '<b>1. <i>when</i></b> - time in or at which the item info should be sent to you:\n'
    '   • If it\'s a datetime in format <i>hh:mm dd.mm.yyyy</i> it will be interpreted as a specific date and time at which the job should run\n'
    '   • If it\'s an integer it will be interpreted as “seconds from now” in which the job should run\n'
    '<b>2. <i>appid</i>, <i>item_name</i>, <i>-no_image</i></b> - same as in /item_info\n'
    '\n<b>Examples:</b>\n'
    '<i>/timed 14:35 31.01.2020 - 440 "Mann Co. Supply Crate Key"</i>\n'
    '<i>/timed 200 - 440 "Mann Co. Supply Crate Key</i>\n\n'

    '<b>:articulated_lorry: Get item info repeatedly</b>\n'
    '<b>Usage:</b> /repeating <i>interval</i> [<i>first</i>] - <i>appid</i> <i>item_name</i> [<i>-no_image</i>]\n'
    '\n<b>Args:</b>\n'
    '<b>1. <i>interval</i></b> - interval in which item info should be sent in format <i>[[number][m|h|d|w]]+</i> where <i>number</i> means any positive integer, <i>|</i> means "or", <i>+</i> means any number of times\n'
    '<b>2. <i>first</i></b> - datetime in format <i>hh:mm dd.mm.yyyy</i> at which the item info should be sent for the first time(defaults to now)\n'
    '<b>3. <i>appid</i>, <i>item_name</i>, <i>-no_image</i></b> - same as in /item_info\n'
    '\n<b>Examples:</b>\n'
    '<i>/repeating 6h20m 23:08 31.01.2020 - 440 "Mann Co. Supply Crate Key"</i>\n'
    '<i>/repeating 1m1h1d1w - 440 "Mann Co. Supply Crate Key"</i>\n\n'

    '<b>:truck: Get item info every day (or on some days of the week)</b>\n'
    '<b>Usage:</b> /daily [<i>days_of_the_week</i>] <i>time</i> - <i>appid</i> <i>item_name</i> [<i>-no_image</i>]\n'
    '\n<b>Args:</b>\n'
    '<b>1. <i>days_of_the_week</i></b> - defines on which days of the week the item info should be sent. Defaults to every day. Format: days represented as numbers (1 = Monday) and separated by comma (",") without space\n'
    '<b>2. <i>time</i></b> - time of day at which the item info should be sent\n'
    '<b>3. <i>appid</i>, <i>item_name</i>, <i>-no_image</i></b> - same as in /item_info\n'
    '\n<b>Examples:</b>\n'
    '<i>/daily 22:54 - 440 "Mann Co. Supply Crate Key"</i>\n'
    '<i>/daily 1,3,5 20:54 - 440 "Mann Co. Supply Crate Key"</i>\n\n'


    '<b>:nail_care: Set item info alert</b>\n'
    'When all conditions are met an alarm will be sent.\n'
    '<b>Usage:</b> <i>/alert conditions - appid item_name</i> [<i>-no_image</i>]\n'
    '\n<b>Args:</b>\n'
    '<b>1. <i>conditions</i></b> - set of conditions in format <i>property__sign=value</i> separated with spaces:\n'
    f'  • Available <i>properties</i>: <i>{SELL_PRICE}</i>, <i>{SELL_LISTINGS}</i>, <i>{MEDIAN_PRICE}</i>, <i>{VOLUME}</i>\n'
    f'  • Available <i>signs</i>: <i>{GT_POSTFIX}</i> (greater than), <i>{LT_POSTFIX}</i> (less than), <i>{GTE_POSTFIX}</i> (greater than or equal to), <i>{LTE_POSTFIX}</i> (less than or equal to)\n'
    '   • <i>Value</i> is a floating-point number\n'
    '<b>2. <i>appid</i>, <i>item_name</i>, <i>-no_image</i></b> - same as in /item_info\n'
    '\n<b>Examples:</b>\n'
    '<i>/alert sell_price__gt=2.55 - 440 "Mann Co. Supply Crate Key"</i>\n'
    '<i>/alert sell_price__gt=6 sell_listings__lt=50 median_price__gte=5.22 volume__lte=10 - 440 "Mann Co. Supply Crate Key" </i>\n'
)
