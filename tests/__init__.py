import os
from src.app.binance_watch import Alert, Analysis, Market, Support


CSV_TESTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'historical_testdir')
market_test = Market()
alert_test = Alert()
analitics_test = Analysis()
support_test = Support()
