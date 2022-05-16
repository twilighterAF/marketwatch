# marketwatch
watching for crypto market

Bot itself just an interface, you can check market status/add and delete pairs.
Script iterates through pairs you added(BTCUSDT by default), if limits passed(set in alerts.py), then alert would be send in telegram.

Alert can be sent only once in day for each pair, daily update csv and alerts reset in 03.03 a.m.

Commands
/start - start bot and keyboard show

/alert - start alert watching(needs to realert after bot restart)

![image](https://user-images.githubusercontent.com/59505313/168646417-eb986d55-999f-4da4-b060-125e4040ba7f.png)
For start you need to setup os.environments in root dir
Binance keys are not neccessary for this functionality by now, only BOT_TOKEN and CLIENT_ID required

