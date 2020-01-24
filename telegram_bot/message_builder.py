def format_item_info(item_info):
    return (
        f'*Name:* {item_info.get("name")}\n'
        f'*Sell price:* {item_info.get("sell_price_text")}\n'
        f'*Sell listings:* {item_info.get("sell_listings")}\n'
        f'*Median price:* {item_info.get("median_price")}\n'
        f'*Volume:* {item_info.get("volume")}'
    )


def format_market_search(market_search):
    return (
        f'*Name:* {market_search.get("name")}\n'
        f'*Sell price:* {market_search.get("sell_price_text")}\n'
        f'*Sell listings:* {market_search.get("sell_listings")}'
    )
