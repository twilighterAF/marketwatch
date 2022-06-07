import telebot
import time
from telebot import types
from .config import bot_token, client_id
from src.app.binance_watch import CSV_DIR, market, send_report, analytics, alert, support
from src.logger import get_logger


logger = get_logger(__name__)
bot = telebot.TeleBot(bot_token())


@bot.message_handler(commands=['start'])
def start(message: types.Message):
    if message.chat.id == client_id():
        bot.send_message(message.chat.id, 'Hey im your alert market watch bot',
                         reply_markup=add_main_keyboard())
    else:
        bot.send_message(message.chat.id, 'Access Denied', reply_to_message_id=False)


@bot.message_handler(content_types=['text'])
def main_menu(message: types.Message):
    if message.text == 'Check Market':
        msg = bot.send_message(message.chat.id, 'Input pair to check')
        bot.register_next_step_handler(msg, check_market)
    elif message.text == 'Pairs':
        bot.send_message(message.chat.id, 'Pairs\n' + '\n'.join(map(str, support.get_pair_pool().values())))
        bot.send_message(message.chat.id, 'What we will doing?', reply_markup=add_pairs_keyboard())


@bot.message_handler(content_types=['text'])
def check_market(message: types.Message):
    logger.info('Check market')
    if message.text in support.get_pair_pool().keys():
        report = report_output(send_report(message.text))
        bot.send_message(message.chat.id, f'{report}')
    else:
        bot.send_message(message.chat.id, 'Wrong pair')


@bot.callback_query_handler(func=lambda call: True)
def callback_pairs(call: types.CallbackQuery):
    if call.data == 'Add pair':
        msg = bot.send_message(call.message.chat.id, 'Input pair to add')
        bot.register_next_step_handler(msg, add_pair)
    elif call.data == 'Delete pair':
        msg = bot.send_message(call.message.chat.id, 'Input pair to delete')
        bot.register_next_step_handler(msg, del_pair)


@bot.message_handler(commands=['alert'])
def alerting(message: types.Message):
    bot.send_message(message.chat.id, 'start alerting')
    while True:
        alert_status = alert.alert_status(analytics.get_data())
        alert_watch = alert.alert_watch(support.get_current_pair(), alert_status)
        if alert_watch:
            report = report_output(send_report(message.text))
            bot.send_message(message.chat.id, f'Alert {support.get_current_pair()}\n{report}')
        time.sleep(1)


@bot.message_handler(content_types=['text'])
def add_pair(message: types.Message):
    logger.info('Add pair')
    if message.text in support.get_pair_pool().keys():
        bot.send_message(message.chat.id, 'Already have that pair')
    elif message.text not in market.get_all_pairs():
        bot.send_message(message.chat.id, 'Pair doesnt exist')
    else:
        pair = message.text
        support.create_csv(pair, market.api_get_history(pair), CSV_DIR)
        alert.alert_off(pair)
        support.set_pair(pair)
        bot.send_message(message.chat.id, f'{pair} added to MarketWatch')


@bot.message_handler(content_types=['text'])
def del_pair(message: types.Message):
    logger.info('Delete pair')
    if message.text not in support.get_pair_pool().keys():
        bot.send_message(message.chat.id, 'Doesnt have that pair')
    elif len(support.get_pair_pool()) == 1:
        bot.send_message(message.chat.id, 'Cannot delete last pair')
    else:
        support.del_pair(message.text)
        alert.del_alert(message.text)
        support.del_csv(message.text, CSV_DIR)
        bot.send_message(message.chat.id, f'{message.text} deleted from MarketWatch')


def add_main_keyboard() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button1 = types.KeyboardButton('Check Market')
    button2 = types.KeyboardButton('Pairs')
    markup.add(button1, button2)
    return markup


def add_pairs_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton('Add pair', callback_data='Add pair')
    button2 = types.InlineKeyboardButton('Delete pair', callback_data='Delete pair')
    markup.add(button1, button2)
    return markup


def report_output(data: dict) -> str:
    logger.info('Send report')
    pair = list(data.keys())[0]
    report = data[pair]
    result = f"REPORT {pair} \n" \
        "7 DAYS\n" \
        f"volume from avg: {report['report'][7]['volume'][0]}%\n" \
        f"volume from max: {report['report'][7]['volume'][1]}%\n" \
        f"price from avg: {report['report'][7]['price']}%\n" \
        "30 DAYS\n" \
        f"volume from avg: {report['report'][30]['volume'][0]}%\n" \
        f"volume from max: {report['report'][30]['volume'][1]}%\n" \
        f"price from avg: {report['report'][30]['price']}%\n" \
        "90 DAYS\n" \
        f"volume from avg: {report['report'][90]['volume'][0]}%\n" \
        f"volume from max: {report['report'][90]['volume'][1]}%\n" \
        f"price from avg: {report['report'][90]['price']}%\n" \
        "ORDER BOOK\n" \
        "Bids | Asks\n" \
        f"sum bid: {report['orders']['bids']['sum']} | sum ask: {report['orders']['asks']['sum']}\n" \
        f"max bid: {report['orders']['bids']['max']} | max ask: {report['orders']['asks']['max']}\n" \
        f"avg bid: {report['orders']['bids']['avg']} | avg ask: {report['orders']['asks']['avg']}\n" \
        "LAST 500 TRADES\n" \
        f"max price: {report['trades']['max_price']} | min price: {report['trades']['min_price']}\n" \
        f"avg price: {report['trades']['avg_price']} | price delta: {report['trades']['price_delta']}\n" \
        f"max quantity: {report['trades']['max_qty']} | sum quantity: {report['trades']['sum_qty']}\n" \
        f"avg quantity: {report['trades']['avg_qty']}"
    return result


def bot_run():
    try:
        logger.info('Start bot')
        bot.infinity_polling(timeout=60)
    except Exception as e:
        logger.exception(f'Bot exception {e}')
        raise e

