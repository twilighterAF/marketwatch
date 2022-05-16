import pytest
import pandas
from tests import support_test, alert_test, analitics_test, market_test, CSV_TESTDIR


@pytest.mark.slow
@pytest.mark.binance_api
def test_get_history():
    history = market_test.api_get_history('BTCUSDT')
    history_columns = history.columns.values.tolist()
    required_columns = ['open', 'close', 'volume']
    result = [col for col in required_columns if col in history_columns]
    max_rows_for_report = 360
    assert result == required_columns and len(history.index) > max_rows_for_report


@pytest.mark.slow
@pytest.mark.binance_api
def test_get_ticker():
    market_test.set_ticker(market_test.api_get_ticker('BTCUSDT'))
    ticker_keys = market_test.get_ticker()['volume'], market_test.get_ticker()['weightedAvgPrice']
    assert all(ticker_keys)


@pytest.mark.slow
@pytest.mark.binance_api
def test_get_order_book():
    market_test.set_order_book(market_test.api_get_order_book('BTCUSDT'))
    bids, asks = market_test.get_order_book()['bids'], market_test.get_order_book()['asks']
    bids_columns, asks_columns = bids.columns.values.tolist(), asks.columns.values.tolist()
    required_columns = ['price', 'qty']
    max_rows = 500
    assert bids_columns == asks_columns == required_columns and len(bids) == len(asks) == max_rows


@pytest.mark.slow
@pytest.mark.binance_api
def test_get_trades():
    market_test.set_last_trades(market_test.api_get_trades('BTCUSDT'))
    trades = market_test.get_last_trades()
    columns = market_test.get_last_trades().columns.values.tolist()
    required_columns = ['price', 'qty']
    result = [col for col in required_columns if col in columns]
    max_rows = 500
    assert result == required_columns and len(trades.index) == max_rows


@pytest.mark.parametrize('pair', ['BTCUSDT', 'ETHUSDT', 'BNBBTC', 'BTCRUB'])
@pytest.mark.slow
@pytest.mark.binance_api
def test_get_all_pairs(pair):
    market_test.set_all_pairs(market_test.api_get_all_pairs())
    assert pair in market_test.get_all_pairs()


@pytest.mark.slow
def test_not_find_csv():
    assert not support_test.find_csv(CSV_TESTDIR)


def test_cant_read_history():
    with pytest.raises(Exception):
        support_test.read_history('BNBBTC', CSV_TESTDIR)


def test_create_csv(mocker):
    mocker.patch('tests.support_test.create_csv')
    support_test.create_csv('BTCUSDT', 'history', CSV_TESTDIR)
    support_test.create_csv.assert_called_once_with('BTCUSDT', 'history', CSV_TESTDIR)


def test_del_csv(mocker):
    mocker.patch('tests.support_test.del_csv')
    support_test.del_csv('BTCUSDT', CSV_TESTDIR)
    support_test.del_csv.assert_called_once_with('BTCUSDT', CSV_TESTDIR)


def test_read_history(api_request):
    history = support_test.read_history('BTCUSDT', CSV_TESTDIR)
    assert type(history) == pandas.DataFrame


@pytest.mark.slow
def test_find_csv(api_request):
    assert support_test.find_csv(CSV_TESTDIR)


def test_calc_history(api_request):
    analitics_test.calc_history(support_test.read_history('BTCUSDT', CSV_TESTDIR))
    result = analitics_test.get_history()[360]['volume'], analitics_test.get_history()[7]['avg_price']
    assert all(result)


def test_calc_result(api_request):
    analitics_test.calc_result(market_test.get_ticker())
    result = analitics_test.get_data()[90]['volume'], analitics_test.get_history()[30]['avg_price']
    assert all(result)


def test_calc_trades(api_request):
    trades = analitics_test.calc_trades(market_test.get_last_trades())
    expected = ['min_price', 'avg_price', 'sum_qty', 'price_delta']
    result = [key for key in expected if key in trades]
    assert expected == result


def test_calc_orders(api_request):
    orders = analitics_test.calc_orders(market_test.get_order_book())
    expected = ['bids', 'asks']
    result = [key for key in expected if key in orders]
    assert expected == result


def test_full_report(api_request):
    report = analitics_test.full_report(market_test.get_order_book(), market_test.get_last_trades())
    expected = ['trades', 'orders', 'report']
    result = [key for key in expected if key in report]
    assert expected == result


def test_alert_status(calculate):
    alert = alert_test.alert_status(analitics_test.get_data())
    week, month = analitics_test.get_data()[7], analitics_test.get_data()[30]
    week_condition = week['volume'][0] > 150 and (week['price'] > 135 or week['price'] < 65)
    month_condition = month['volume'][0] > 125 or month['price'] > 125 or month['price'] < 75
    assert alert if week_condition or month_condition else not alert


def test_alert_on(calculate):
    alert_test.alert_off('BTCUSDT')
    assert alert_test.alert_watch('BTCUSDT', True)


def test_alert_off(calculate):
    alert_test.alert_on('BTCUSDT')
    assert not alert_test.alert_watch('BTCUSDT', True)

