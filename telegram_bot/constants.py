JOBS_PICKLE = '../pickles/user_jobs.pickle'

NO_IMAGE_ARG = '-no_image'

QUOTATION_MARKS = ('"', "'", '`', '“', '‘', '’')


# Stages
CHOOSE_JOB_TYPE, CHOOSE_JOB = range(2)
# Callback data
ALERT, TIMED, REPEATING, DAILY, ALL, CANCEL = (str(item) for item in range(6))

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

JOB_TO_CHAT_DATA_KEY = {
    'check_values_of_an_item_info_job': II_ALERT_JOBS,
    'item_info_timed_job': II_TIMED_JOBS,
    'item_info_repeating_job': II_REPEATING_JOBS,
    'item_info_daily_job': II_DAILY_JOBS
}

CALLBACK_TO_CHAT_DATA_KEY = {
    ALERT: II_ALERT_JOBS,
    TIMED: II_TIMED_JOBS,
    REPEATING: II_REPEATING_JOBS,
    DAILY: II_DAILY_JOBS
}
