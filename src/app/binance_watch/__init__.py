import os
import time
from .binance_api import Market
from .analysis import Analysis
from .alerts import Alert
from .utils import Support
from src.logger import get_logger


CSV_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'historical_data')
UPDATE_TIME = {'hour': 3, 'min': 30}
market = Market()
analytics = Analysis()
alert = Alert()
support = Support()
logger = get_logger(__name__)


def setup_loop():
    logger.info('Start loop')
    files = support.find_csv(CSV_DIR)

    if not files:
        default_pair = 'BTCUSDT'
        support.create_csv(default_pair, market.api_get_history(default_pair), CSV_DIR)
        support.set_pair(default_pair)

    alert.init_alerts(support.get_pair_pool())
    market.set_all_pairs(market.api_get_all_pairs())


def event_loop(pair: str):
    support.set_current_pair(pair)
    market.set_ticker(market.api_get_ticker(pair))
    history = support.read_history(pair, CSV_DIR)
    analytics.calc_history(history)
    analytics.calc_result(pair, market.get_ticker())


def daily_update(pair: str):
    logger.warning('Daily update')
    market.clear_all_pairs()
    market.set_all_pairs(market.api_get_all_pairs())
    support.create_csv(pair, market.api_get_history(pair), CSV_DIR)
    alert.alert_off(pair)


def send_report(pair: str) -> dict:
    market.set_last_trades(market.api_get_trades(pair))
    market.set_order_book(market.api_get_order_book(pair))
    report = analytics.full_report(market.get_order_book(), market.get_last_trades())
    result = {pair: report}
    return result


def binance_watch():
    """Event loop"""
    setup_loop()
    nanosec = 1000

    while True:
        try:
            iter_list = list(support.get_pair_pool())

            for pair in iter_list:
                event_loop(pair)
                binance_time = time.localtime(float(market.get_ticker()['closeTime']) // nanosec)
                time_conditions = (binance_time[3] == UPDATE_TIME['hour'],
                                   binance_time[4] == UPDATE_TIME['min'])

                if all(time_conditions):  # 03:30 a.m. daily update
                    daily_update(pair)

                time.sleep(15)

        except Exception:
            logger.exception('Event loop exception')
            raise
