# marketwatch
watching for crypto market

Bot itself just an interface, you can check market status/add and delete pairs.
Script iterates through pairs you added(BTCUSDT by default), if limits passed(set in alerts.py), then alert would be send in telegram.

Alert can be sent only once in day for each pair, daily update csv and alerts reset in 03.03 a.m.

Commands
/start - start bot and keyboard show
/alert - start alert watching(needs to realert after bot restart)

