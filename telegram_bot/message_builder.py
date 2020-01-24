def format_item_info(item_info):
    return (
        f'*Name:* {item_info.get("name")}\n'
        f'*Sell price:* {item_info.get("sell_price_text")}\n'
        f'*Sell listings:* {item_info.get("sell_listings")}\n'
        f'*Median price:* {item_info.get("median_price")}\n'
        f'*Volume:* {item_info.get("volume")}'
    )
