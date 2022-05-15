import os
import pandas
from binance import Client
from .config import api_key, secret_key

client = Client(api_key(), secret_key())


class Market:
    """Binance api"""

    def __init__(self):
        self._ticker = {}
        self._all_pairs = []
        self._order_book = {}
        self._last_trades = pandas.DataFrame

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

    @classmethod
    def api_get_history(cls, pair: str) -> pandas.DataFrame:
        market = client.get_historical_klines(f"{pair}", Client.KLINE_INTERVAL_1DAY, '1 Jan, 2015')
        for line in market:
            del line[9:]
        result = pandas.DataFrame(market, columns=['open_time', 'open', 'high', 'low', 'close', 'volume',
                                                   'close_time', 'quote_asset_vol', 'trades'])
        result.set_index('open_time', inplace=True)
        return result

    @classmethod
    def api_get_ticker(cls, pair: str) -> dict:
        result = client.get_ticker(symbol=f'{pair}')
        return result

    @classmethod
    def api_get_order_book(cls, pair: str) -> dict:
        order_book = client.get_order_book(symbol=f'{pair}', limit=500)
        bid_df = pandas.DataFrame(order_book['bids'], columns=['price', 'qty'])
        ask_df = pandas.DataFrame(order_book['asks'], columns=['price', 'qty'])
        result = {'bids': bid_df, 'asks': ask_df}
        return result

    @classmethod
    def api_get_trades(cls, pair: str) -> pandas.DataFrame:
        market = client.get_recent_trades(symbol=f'{pair}')  # last 500 trades
        result = pandas.DataFrame(market, columns=['id', 'price', 'qty', 'quoteQty', 'time',
                                                   'isBuyerMaker', 'isBestMatch'])
        return result

    @classmethod
    def api_get_all_pairs(cls) -> list:
        result = client.get_all_tickers()
        return result
