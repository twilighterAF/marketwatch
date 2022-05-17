# marketwatch
watching for crypto market

Bot itself just an interface, you can check market status/add and delete pairs.
Script iterates through pairs you added(BTCUSDT by default), if limits passed(set in alerts.py), then alert would be send in telegram.

Alert can be sent only once per day for each pair, daily update csv and alerts reset in 03.03 a.m.

Commands

/start - start bot and keyboard show

/alert - start alert watching(needs to realert after bot restart)



For start bot you just need to follow next few steps:

1) git clone repository
2) pip install -r requirements.txt
3) set up  environment.env file in marketwatch dir (Binance keys are not neccessary for this version by now, only BOT_TOKEN and CLIENT_ID (yourself tg id) required)
