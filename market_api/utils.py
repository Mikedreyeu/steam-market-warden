from market_api.constants import SEARCH_KEYS_TO_EXTRACT


def build_icon_url(icon_url: str, size_argument: str = None):
    """
    :param icon_url: icon_url
    :param size_argument: {pixels}fx{pixels}f, (200fx100f = small sized)
    :return: full url
    """
    return (
        f'https://steamcommunity-a.akamaihd.net/economy/image'
        f'/{icon_url}/{size_argument}'
    )


def build_market_url(appid: int, item_name: str):
    return (
        f'https://steamcommunity.com/market/listings'
        f'/{appid}/{item_name}'
    )


def parse_market_search_general_info(market_item_result: dict):
    market_search_dict = {}

    market_search_dict.update(
        {key: market_item_result.get(key) for key in SEARCH_KEYS_TO_EXTRACT}
    )

    market_search_dict['icon_url'] = build_icon_url(
        market_item_result['asset_description']['icon_url']
    )

    market_search_dict['market_url'] = build_market_url(
        market_item_result['asset_description']['appid'],
        market_item_result['hash_name']
    )

    return market_search_dict
