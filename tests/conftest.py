import pytest
from tests import market_test, analitics_test, alert_test, support_test, CSV_TESTDIR


@pytest.fixture(scope='session')
def api_request():
    pair = 'BTCUSDT'
    support_test.create_csv(pair, market_test.api_get_history(pair), CSV_TESTDIR)
    market_test.set_ticker(market_test.api_get_ticker(pair))
    market_test.set_last_trades(market_test.api_get_trades(pair))
    market_test.set_order_book(market_test.api_get_order_book(pair))
    yield
    support_test.del_csv(pair, CSV_TESTDIR)


@pytest.fixture(scope='session')
def calculate(api_request):
    analitics_test.calc_history(support_test.read_history('BTCUSDT', CSV_TESTDIR))
    analitics_test.calc_result(market_test.get_ticker())
