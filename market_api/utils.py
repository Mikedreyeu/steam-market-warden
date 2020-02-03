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

