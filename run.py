import threading
from src.app.binance_watch import binance_watch
from src.tg_bot.bot_main import bot_run


if __name__ == '__main__':
    thread_market = threading.Thread(target=binance_watch, name='market').start()
    thread_bot = threading.Thread(target=bot_run, name='bot').start()
