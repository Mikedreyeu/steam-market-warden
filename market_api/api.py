import requests
import urllib.parse

from market_api.constants import SEARCH_KEYS_TO_EXTRACT, \
    PRICE_OVERVIEW_KEYS_TO_EXTRACT


def price_overview(appid: int, market_hash_name: str, currency: int = 1):
    response = requests.get(
        'https://steamcommunity.com/market/priceoverview',
        params={
            'appid': appid,
            'market_hash_name': market_hash_name,
            'currency': currency
        }
    )

    return response.json()


def market_search(
        query: str = None, appid: int = None, count: int = None,
        sort_column: str = None, sort_dir: str = None, **kwargs
):
    response = requests.get(
        'https://steamcommunity.com/market/search/render',
        params={
            'norender': 1,
            'query': query,
            'appid': appid,
            'count': count,
            'sort_column': sort_column,
            'sort_dir': sort_dir,
            **kwargs
        }
    )

    return response.json()


def get_item_info(appid: int, market_hash_name: str, currency: int = 1):
    item_info = {}
    price_overview_response = price_overview(appid, market_hash_name, currency)
    price_overview_dict = price_overview_response.json()

    market_search_response = market_search(market_hash_name, appid)
    market_search_dict = market_search_response.json()

    if price_overview_dict['success']:
        item_info.update(
            {
                key: price_overview_response[key]
                for key in PRICE_OVERVIEW_KEYS_TO_EXTRACT
            }
        )

    if (market_search_dict['success']
            and market_search_dict['total_count'] == 1):
        result = market_search_dict['results'][0]

        item_info.update({key: result[key] for key in SEARCH_KEYS_TO_EXTRACT})

        item_info['icon_url'] = _build_icon_url(
            result['asset_description']['icon_url']
        )


def _build_icon_url(icon_url: str, size_argument: str = None):
    """
    :param icon_url: icon_url
    :param size_argument: {pixels}fx{pixels}f,
    :return: full url
    """
    return (
        f'https://steamcommunity-a.akamaihd.net/economy/image'
        f'/{icon_url}/{size_argument}'
    )
