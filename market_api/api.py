import asyncio
from typing import List

import requests
from aiohttp import ClientSession

from market_api.constants import (
    SEARCH_KEYS_TO_EXTRACT, PRICE_OVERVIEW_KEYS_TO_EXTRACT, PRICE_OVERVIEW_URL,
    MARKET_SEARCH_URL
)
from market_api.utils import build_icon_url
from telegram_bot.exceptions.exceptions import ApiException


async def fetch(session, url: str, params: dict):
    async with session.get(url, params=params) as response:
        return await response.json()


async def run_async_requests(url_params_tuples: List[tuple]):
    async with ClientSession() as session:
        tasks = [
            asyncio.create_task(fetch(session, url, params))
            for url, params in url_params_tuples
        ]

        return await asyncio.gather(*tasks)


def request_item_info_async(
        appid: int, market_hash_name: str, currency: int = 1
):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    price_overview_tuple = (
        PRICE_OVERVIEW_URL,
        {
            'appid': appid,
            'market_hash_name': market_hash_name,
            'currency': currency
        }
    )
    market_search_tuple = (
        MARKET_SEARCH_URL,
        {
            'norender': 1,
            'query': market_hash_name,
            'appid': appid
        }
    )

    reslting_dicts = loop.run_until_complete(run_async_requests([
        price_overview_tuple, market_search_tuple
    ]))

    return reslting_dicts[0], reslting_dicts[1]


def price_overview(appid: int, market_hash_name: str, currency: int = 1):
    response = requests.get(
        PRICE_OVERVIEW_URL,
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
        MARKET_SEARCH_URL,
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
    item_info = {'exact_item': True}

    (price_overview_response,
     market_search_response) = request_item_info_async(
        appid, market_hash_name, currency
    )

    if market_search_response['success']:
        result = market_search_response['results'][0]

        item_info.update(
            {key: result.get(key) for key in SEARCH_KEYS_TO_EXTRACT}
        )

        item_info['icon_url'] = build_icon_url(
            result['asset_description']['icon_url']
        )

        if market_hash_name.lower() not in (
                result['hash_name'].lower(), result['name'].lower()
        ):
            item_info['exact_item'] = False
            price_overview_response = price_overview(
                appid=appid,
                market_hash_name=market_search_response['results'][0][
                    'hash_name'
                ],
                currency=currency
            )

    if price_overview_response['success']:
        item_info.update(
            {
                key: price_overview_response.get(key)
                for key in PRICE_OVERVIEW_KEYS_TO_EXTRACT
            }
        )

    if (not price_overview_response['success']
            and market_search_response['total_count'] == 0):
        raise ApiException('NOTHING_FOUND')

    return item_info


def market_search_for_command(
        query: str = None, appid: int = None, count: int = None,
        sort_column: str = None, sort_dir: str = None, **kwargs
):
    market_search_dict = {}

    market_search_response = market_search(query=query)

    if market_search_response['success']:
        result = market_search_response['results'][0]

        market_search_dict.update(
            {key: result.get(key) for key in SEARCH_KEYS_TO_EXTRACT}
        )

        market_search_dict['icon_url'] = build_icon_url(
            result['asset_description']['icon_url']
        )

    return market_search_dict
