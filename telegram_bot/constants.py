JOBS_PICKLE = '../pickles/user_jobs.pickle'

NO_IMAGE_ARG = '-no_image'

QUOTATION_MARKS = ('"', "'", '`', '“', '‘', '’')


# Stages
ST_CHOOSE_JOB_TYPE, ST_CHOOSE_JOB, ST_MANAGE_JOB = range(3)

# Callback data
(CB_ALERT, CB_TIMED, CB_REPEATING, CB_DAILY, CB_ALL, CB_CANCEL, CB_MANAGE_JOB,
 CB_BACK) = (str(item) for item in range(8))

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
II_TIMED_JOBS = 'item_info_timed'
II_REPEATING_JOBS = 'item_info_repeating'
II_DAILY_JOBS = 'item_info_daily'

CHOOSE_JOB_TYPE_REGEX = (
    f'^(?P<job_type>{"|".join([CB_ALERT, CB_TIMED, CB_REPEATING, CB_DAILY, CB_ALL])})'
    f'-(?P<page_number>\\d+)$'
)

MANAGE_JOB_REGEX = (
    f'^{CB_MANAGE_JOB}'
    f'-(?P<job_type>{"|".join([II_ALERT_JOBS, II_TIMED_JOBS, II_REPEATING_JOBS, II_DAILY_JOBS])})'
    f'-(?P<job_index>\\d+)$'
)

CALLBACK_TO_TYPE = {
    CB_ALERT: 'alert',
    CB_TIMED: 'timed',
    CB_REPEATING: 'repeating',
    CB_DAILY: 'daily',
    CB_ALL: ''
}

JOB_TO_CHAT_DATA_KEY = {
    'check_values_of_an_item_info_job': II_ALERT_JOBS,
    'item_info_timed_job': II_TIMED_JOBS,
    'item_info_repeating_job': II_REPEATING_JOBS,
    'item_info_daily_job': II_DAILY_JOBS
}

CALLBACK_TO_CHAT_DATA_KEY = {
    CB_ALERT: II_ALERT_JOBS,
    CB_TIMED: II_TIMED_JOBS,
    CB_REPEATING: II_REPEATING_JOBS,
    CB_DAILY: II_DAILY_JOBS
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