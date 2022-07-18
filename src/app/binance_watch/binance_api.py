import os
import pandas
import datetime
from binance import Client
from .config import api_key, secret_key


class Market:
    """Binance api"""

    def __init__(self):
        self._ticker = {}
        self._all_pairs = []  # all pairs in binance
        self._order_book = {}
        self._last_trades = pandas.DataFrame
        self.client = Client(api_key(), secret_key(), {'timeout': 60})

    def get_ticker(self) -> dict:
        return self._ticker

    def set_ticker(self, ticker: dict):
        self._ticker = ticker

    def clear_all_pairs(self):
        self._all_pairs.clear()

    def set_all_pairs(self, pairs: list):
        for pair in pairs:
            self._all_pairs.append(pair['symbol'])

    def get_all_pairs(self) -> list:
        return self._all_pairs

    def get_order_book(self) -> dict:
        return self._order_book

    def set_order_book(self, book: dict):
        self._order_book = book

    def get_last_trades(self) -> pandas.DataFrame:
        return self._last_trades

    def set_last_trades(self, trades: pandas.DataFrame):
        self._last_trades = trades

    def api_get_history(self, pair: str) -> pandas.DataFrame:
        history_date = datetime.date.today() - datetime.timedelta(days=95)
        market = self.client.get_historical_klines(pair, Client.KLINE_INTERVAL_1DAY,
                                              datetime.datetime.strftime(history_date, '%d %b, %Y'))

        for line in market:
            del line[9:]

        result = pandas.DataFrame(market, columns=['open_time', 'open', 'high', 'low', 'close', 'volume',
                                                   'close_time', 'quote_asset_vol', 'trades'])
        result.set_index('open_time', inplace=True)
        return result

    def api_get_ticker(self, pair: str) -> dict:
        result = self.client.get_ticker(symbol=pair)
        return result

    def api_get_order_book(self, pair: str) -> dict:
        order_book = self.client.get_order_book(symbol=pair, limit=500)
        bid_df = pandas.DataFrame(order_book['bids'], columns=['price', 'qty'])
        ask_df = pandas.DataFrame(order_book['asks'], columns=['price', 'qty'])
        result = {'bids': bid_df, 'asks': ask_df}
        return result

    def api_get_trades(self, pair: str) -> pandas.DataFrame:
        market = self.client.get_recent_trades(symbol=pair)  # last 500 trades
        result = pandas.DataFrame(market, columns=['id', 'price', 'qty', 'quoteQty', 'time',
                                                   'isBuyerMaker', 'isBestMatch'])
        return result

    def api_get_all_pairs(self) -> list:
        result = self.client.get_all_tickers()
        return result
