import os
import time
from .binance_api import Market
from .analysis import Analysis
from .alerts import Alert
from .utils import Support
from src.logger import get_logger


CSV_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'historical_data')
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
    logger.info(f'Pair: {support.get_current_pair()}')
    market.set_ticker(market.api_get_ticker(pair))
    history = support.read_history(pair, CSV_DIR)
    analytics.calc_history(history)
    analytics.calc_result(market.get_ticker())


def daily_update(pair: str):
    logger.info('Daily update')
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
                if binance_time[3] == 3 and binance_time[4] == 30:  # 03:30 a.m. daily update
                    daily_update(pair)
                time.sleep(1)
        except Exception as e:
            logger.exception(f'Event loop exception {e}')
            time.sleep(1)
            raise e
