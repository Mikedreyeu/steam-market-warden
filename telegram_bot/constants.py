JOBS_PICKLE = 'user_jobs.pickle'

NO_IMAGE_ARG = '-no_image'

# Stages
FIRST, SECOND = range(2)
# Callback data
ONE, TWO, THREE, FOUR = range(4)

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

ALLOWED_KEYS_FOR_ALARM = (SELL_PRICE, SELL_LISTINGS, MEDIAN_PRICE, VOLUME)

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

INTERVAL_UNIT_REGEX = f'(\d+)([{MINUTES}{HOURS}{DAYS}{WEEKS}])'
