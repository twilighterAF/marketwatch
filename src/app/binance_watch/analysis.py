import pandas
from statistics import mean


class Analysis:
    """All analysis"""

    def __init__(self):
        self._data = {}
        self._history = {30: {}, 7: {}}  # days

    def get_history(self) -> dict:
        return self._history

    def set_history(self, history: dict):
        self._history = history

    def get_data(self) -> dict:
        return self._data

    def set_data(self, pair: str, data: dict):
        self._data[pair] = data

    def calc_history(self, history: pandas.DataFrame):
        result = {}

        for date_slice in self.get_history().keys():
            history_slice = history.tail(date_slice)
            history_data = ((history_slice['volume'].max(), history_slice['volume'].mean()),
                            (history_slice['open'].max(), history_slice['open'].min()),
                            (history_slice['close'].max(), history_slice['close'].min()))
            volume, open_price, close_price = history_data

            avg_price = list(map(lambda x, y: (x + y) / 2, open_price, close_price))
            result_price = (avg_price[0] + avg_price[1]) / 2
            result[date_slice] = {'volume': volume, 'avg_price': result_price}
            self.set_history(result)

    def calc_result(self, pair: str, ticker: dict):
        result = {}
        percent = 100
        volume_on, avg_price_on = float(ticker['volume']), float(ticker['weightedAvgPrice'])

        for date_slice, data in self.get_history().items():
            volume_hstr, avg_price_hstr = data['volume'], data['avg_price']
            volume_change = ((volume_on / volume_hstr[1]) * percent)
            volume_from_max = ((volume_on / volume_hstr[0]) * percent)
            price_change = ((avg_price_on / avg_price_hstr) * percent)

            calculations = list(map(round, map(float, (volume_change, volume_from_max, price_change, avg_price_on))))
            result[date_slice] = {'volume': (calculations[0], calculations[1]),
                                  'price': calculations[2], 'price_online': calculations[3]}
            self.set_data(pair, result)

    @staticmethod
    def calc_trades(last_trades: pandas.DataFrame) -> dict:
        prices, qty = last_trades['price'].apply(float), last_trades['qty'].apply(float)
        summary = round(sum(qty), 4)
        maximum = max(prices), max(qty)
        minimum = min(prices)
        average = mean(prices), round(mean(qty), 4)
        price_delta = round((maximum[0] - minimum), 4)

        result = {'min_price': minimum, 'max_price': maximum[0], 'avg_price': average[0], 'price_delta': price_delta,
                  'max_qty': maximum[1], 'avg_qty': average[1], 'sum_qty': summary}
        return result

    @staticmethod
    def calc_orders(order_book: dict) -> dict:
        result = {}

        for makers, orders in order_book.items():
            qty_orders = orders['qty'].apply(float)
            summary = round(sum(qty_orders), 4)
            maximum = round(max(qty_orders), 4)
            average = round(mean(qty_orders), 4)
            result[makers] = {'sum': summary, 'max': maximum, 'avg': average}

        return result

    def full_report(self, order_book: tuple, last_trades: pandas.DataFrame) -> dict:
        trades, orders = self.calc_trades(last_trades), self.calc_orders(order_book)
        result = {'trades': trades, 'orders': orders, 'report': self.get_data()}
        return result
