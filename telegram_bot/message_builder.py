def format_item_info(item_info):
    return (
        f'*Name:* {item_info["name"]}\n'
        f'*Sell price:* {item_info["sell_price_text"]}\n'
        f'*Sell listings:* {item_info["sell_listings"]}\n'
        f'*Median price:* {item_info["median_price"]}\n'
        f'*Volume:* {item_info["volume"]}'
    )
