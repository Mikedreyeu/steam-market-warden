# steam-market-warden

This bot can get info about Steam Community Market items, search items on the market and set "jobs" in order to receive item info depending on the conditions set for a job, e.g. send item info every day or set an alarm to trigger if an item reaches a certain price, etc.
### Screenshots
![s1](https://user-images.githubusercontent.com/27430505/114098356-ea332180-98c9-11eb-80d6-47b597b98a23.jpg) ![s2](https://user-images.githubusercontent.com/27430505/114098359-eacbb800-98c9-11eb-8362-caa7549d1523.jpg)

## _/help_ dump
You can control this bot by sending these commands:



<br/><b>:rocket: Get item info</b>

<b>Usage:</b> /item_info <i>appid item_name</i> [<i>-no_image</i>]



<b>Args:</b>

<b>1. <i>appid</i></b> - id of an app

<b>2. <i>item_name</i></b> - name of the item or part of it.

If <i>item_name</i> has spaces, you need to type it inside quotation marks (" ' ` “ ” ‘ ’)

<b>3. <i>-no_image</i></b> - you can add this to your command if you want item info without image



<b>Examples:</b>

<i>/item_info 440 "Mann Co. Supply Crate Key"</i>

<i>/item_info 440 "Mann Co. Supply Crate Key" -no_item</i>



<b>:helicopter: Search the market</b>

<b>Usage:</b> /market_search <i>query</i> [<i>-no_image</i>]



<b>Args:</b>

<b>1. <i>query</i></b> - name of the item or part of it.

If <i>query</i> has spaces, you need to type it inside quotation marks (" ' ` “ ” ‘ ’)

<b>2. <i>-no_image</i></b> - same as in /item_info



<b>Example:</b> <i>/market_search gloves</i>

<br/><b>:man_construction_worker::woman_firefighter:  Jobs :woman_mechanic::man_factory_worker:</b>



<b>:books: Manage your jobs</b>

<b>Usage:</b> /manage_jobs



<b>:steam_locomotive: Get item info on specific time once</b>

<b>Usage:</b> <i>/timed when - appid item_name</i> [<i>-no_image</i>]



<b>Args:</b>

<b>1. <i>when</i></b> - time in or at which the item info should be sent to you:

• If it\'s a datetime in format <i>hh:mm dd.mm.yyyy</i> it will be interpreted as a specific date and time at which the job should run

• If it\'s an integer it will be interpreted as “seconds from now” in which the job should run

<b>2. <i>appid</i>, <i>item_name</i>, <i>-no_image</i></b> - same as in /item_info



<b>Examples:</b>

<i>/timed 14:35 31.01.2020 - 440 "Mann Co. Supply Crate Key"</i>

<i>/timed 200 - 440 "Mann Co. Supply Crate Key</i>



<b>:articulated_lorry: Get item info repeatedly</b>

<b>Usage:</b> /repeating <i>interval</i> [<i>first</i>] - <i>appid</i> <i>item_name</i> [<i>-no_image</i>]



<b>Args:</b>

<b>1. <i>interval</i></b> - interval in which item info should be sent in format <i>[[number][m|h|d|w]]+</i> where <i>number</i> means any positive integer, <i>|</i> means "or", <i>+</i> means any number of times

<b>2. <i>first</i></b> - datetime in format <i>hh:mm dd.mm.yyyy</i> at which the item info should be sent for the first time(defaults to now)

<b>3. <i>appid</i>, <i>item_name</i>, <i>-no_image</i></b> - same as in /item_info



<b>Examples:</b>

<i>/repeating 6h20m 23:08 31.01.2020 - 440 "Mann Co. Supply Crate Key"</i>

<i>/repeating 1m1h1d1w - 440 "Mann Co. Supply Crate Key"</i>



<b>:truck: Get item info every day (or on some days of the week)</b>

<b>Usage:</b> /daily [<i>days_of_the_week</i>] <i>time</i> - <i>appid</i> <i>item_name</i> [<i>-no_image</i>]



<b>Args:</b>

<b>1. <i>days_of_the_week</i></b> - defines on which days of the week the item info should be sent. Defaults to every day. Format: days represented as numbers (1 = Monday) and separated by comma (",") without space

<b>2. <i>time</i></b> - time of day at which the item info should be sent

<b>3. <i>appid</i>, <i>item_name</i>, <i>-no_image</i></b> - same as in /item_info



<b>Examples:</b>

<i>/daily 22:54 - 440 "Mann Co. Supply Crate Key"</i>

<i>/daily 1,3,5 20:54 - 440 "Mann Co. Supply Crate Key"</i>



<b>:nail_care: Set item info alert</b>

When all conditions are met an alarm will be sent.

<b>Usage:</b> <i>/alert conditions - appid item_name</i> [<i>-no_image</i>]



<b>Args:</b>

<b>1. <i>conditions</i></b> - set of conditions in format <i>property__sign=value</i> separated with spaces:

• Available <i>properties</i>: <i>sell_price</i>, <i>sell_listings</i>, <i>median_price</i>, <i>volume</i>

• Available <i>signs</i>: <i>gt</i> (greater than), <i>lt</i> (less than), <i>gte</i> (greater than or equal to), <i>lte</i> (less than or equal to)

• <i>Value</i> is a floating-point number

<b>2. <i>appid</i>, <i>item_name</i>, <i>-no_image</i></b> - same as in /item_info



<b>Examples:</b>

<i>/alert sell_price__gt=2.55 - 440 "Mann Co. Supply Crate Key"</i>

<i>/alert sell_price__gt=6 sell_listings__lt=50 median_price__gte=5.22 volume__lte=10 - 440 "Mann Co. Supply Crate Key" </i>


