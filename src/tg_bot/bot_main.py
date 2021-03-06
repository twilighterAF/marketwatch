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
        bot.send_message(message.chat.id, 'Hey im your alert market watch bot 🧐',
                         reply_markup=add_main_keyboard())

    else:
        bot.send_message(message.chat.id, 'Access Denied', reply_to_message_id=False)


@bot.message_handler(content_types=['text'])
def main_menu(message: types.Message):
    if message.text == 'Check Market 📊':
        msg = bot.send_message(message.chat.id, 'Input pair to check')
        bot.register_next_step_handler(msg, check_market)

    elif message.text == 'Pairs ✅':
        bot.send_message(message.chat.id, 'Pairs\n' + '\n'.join(map(str, support.get_pair_pool().values())))
        bot.send_message(message.chat.id, 'What we will doing?', reply_markup=add_pairs_keyboard())

    elif message.text == '/alert':
        alerting(message)


@bot.message_handler(content_types=['text'])
def check_market(message: types.Message):
    logger.info('Check market')
    pair = message.text.upper()

    if pair in support.get_pair_pool().keys():
        report = report_output(send_report(pair))
        bot.send_message(message.chat.id, report)

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


@bot.message_handler(content_types=['text'])
def alerting(message: types.Message):
    if not alert.get_alertwatch():
        bot.send_message(message.chat.id, 'Start alerting')
        alert.set_alertwatch(status=True)

        while True:
            pair = support.get_current_pair()
            alert_status = alert.alert_status(pair, analytics.get_data())
            alert_watch = alert.alert_watch(pair, alert_status)

            if alert_watch:
                report = report_output(send_report(pair))
                bot.send_message(message.chat.id, f'ALERT ❗️\n{report}')

            time.sleep(1)
    else:
        bot.send_message(message.chat.id, 'Already watching')


@bot.message_handler(content_types=['text'])
def add_pair(message: types.Message):
    logger.info('Add pair')
    pair = message.text.upper()

    if pair in support.get_pair_pool().keys():
        bot.send_message(message.chat.id, 'Already have that pair')

    elif pair not in market.get_all_pairs():
        bot.send_message(message.chat.id, 'Pair doesnt exist')

    else:
        support.create_csv(pair, market.api_get_history(pair), CSV_DIR)
        alert.alert_off(pair)
        support.set_pair(pair)
        bot.send_message(message.chat.id, f'{pair} added to MarketWatch')


@bot.message_handler(content_types=['text'])
def del_pair(message: types.Message):
    logger.info('Delete pair')
    pair = message.text.upper()

    if pair not in support.get_pair_pool().keys():
        bot.send_message(message.chat.id, 'Doesnt have that pair')

    elif len(support.get_pair_pool()) == 1:
        bot.send_message(message.chat.id, 'Cannot delete last pair')

    else:
        support.del_pair(pair)
        alert.del_alert(pair)
        support.del_csv(pair, CSV_DIR)
        bot.send_message(message.chat.id, f'{pair} deleted from MarketWatch')


def add_main_keyboard() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button1 = types.KeyboardButton('Check Market 📊')
    button2 = types.KeyboardButton('Pairs ✅')
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
    report = data[pair]['report'][pair]
    orders = data[pair]['orders']
    trades = data[pair]['trades']

    result = f"REPORT {pair} \n" \
        f"24h average price - {report[7]['price_online']} \n\n" \
        "7 DAYS\n" \
        f"volume from avg: {report[7]['volume'][0]}%\n" \
        f"volume from max: {report[7]['volume'][1]}%\n" \
        f"price from avg: {report[7]['price']}%\n" \
        "30 DAYS\n" \
        f"volume from avg: {report[30]['volume'][0]}%\n" \
        f"volume from max: {report[30]['volume'][1]}%\n" \
        f"price from avg: {report[30]['price']}%\n\n" \
        "ORDER BOOK\n" \
        "Bids | Asks\n" \
        f"sum bid: {orders['bids']['sum']} | sum ask: {orders['asks']['sum']}\n" \
        f"max bid: {orders['bids']['max']} | max ask: {orders['asks']['max']}\n" \
        f"avg bid: {orders['bids']['avg']} | avg ask: {orders['asks']['avg']}\n\n" \
        "LAST 500 TRADES\n" \
        f"max price: {trades['max_price']} | min price: {trades['min_price']}\n" \
        f"avg price: {trades['avg_price']} | price delta: {trades['price_delta']}\n" \
        f"max quantity: {trades['max_qty']} | sum quantity: {trades['sum_qty']}\n" \
        f"avg quantity: {trades['avg_qty']}"
    return result


def set_commands():
    bot.set_my_commands([
        telebot.types.BotCommand("/start", "Start bot and send main menu"),
        telebot.types.BotCommand("/alert", "Start alertwatch")])


def bot_run():
    set_commands()
    try:
        logger.info('Start bot')
        bot.infinity_polling(timeout=60)

    except Exception:
        logger.exception('Bot exception')
        raise

