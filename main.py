import time

import pandas as pd

import keys
from binance.client import Client
from binance.cm_futures import CMFutures
from binance.exceptions import BinanceAPIException


def get_top_coin():
    try:
        all_tickers = pd.DataFrame(client.get_ticker())
        usdt = all_tickers[all_tickers.symbol.str.contains('USDT')]
        work = usdt[~((usdt.symbol.str.contains('UP')) |
                      (usdt.symbol.str.contains('DOWN')))]
        top_coin = work[work.priceChangePercent ==
                        work.priceChangePercent.max()]
        top_coin = top_coin.symbol.values[0]
        return top_coin
    except BinanceAPIException as e:
        return e


def get_coin_price(symbol):
    try:
        coin = client.get_symbol_ticker(symbol=symbol)
        value = float(coin['price'])
        return f'{symbol } Spot price: {value}'
    except BinanceAPIException as e:
        return e


def get_future_price(symbol):
    try:
        ticker_data = client.futures_symbol_ticker(symbol=symbol)
        current_price = float(ticker_data['price'])
        return f'{symbol } Futures price: {current_price}'
    except BinanceAPIException as e:
        return f'No current future price {symbol} coin'


def hour_price_change(symbol):
    try:
        klines = client.futures_klines(symbol=symbol, interval='1h')
        df = pd.DataFrame(klines).iloc[:, :6]
        df.columns = ['time', 'open', 'higth', 'low', 'close', 'volume']
        max_price = float(max(df['higth']))
        coin = client.get_symbol_ticker(symbol=symbol)
        current_price = float(coin['price'])
        if (max_price - current_price / current_price * 100 <= -1):
            return True
    except BinanceAPIException as e:
        return e


def last_data(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(
        symbol, interval, lookback + 'min ago UTC'))
    frame = frame.iloc[:, :6]
    frame.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
    frame = frame.set_index('time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame


if __name__ == '__main__':
    client = Client(keys.api_key, keys.secret_key)
    future_symbol = CMFutures(keys.api_key, keys.secret_key)
    while True:
        symbol = get_top_coin()
        print(
            f'\nTop coin: {get_top_coin()}\n{get_coin_price(symbol)}\n{get_future_price(symbol)}')
        print(last_data(symbol, '1m', '10'))
        if hour_price_change(symbol) == True:
            print(
                f'Futures price of the {symbol} fell by 1% from the maximum price in the last hour')
        time.sleep(5)
