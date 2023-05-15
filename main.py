import requests
import pandas as pd
import numpy as np
import time as t
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')
from binance.um_futures import UMFutures

# Не волнуйтесь я вам дал свой старый аккаунт и много что ограничил)
api_key = "OrfCGFfsHgxd87WdMcPoi2dkJASocLVUVi5q4gjxnuefLrRZIV0JrX2WVlIDCdao"
secret_key = "FNjj0sMpjNnBhzxbvBRm01ZF61WQSZkikRrEIMEp0waoXXrs3IbIEKuewzzvkcvG"

symbol = "ETHUSDT"
client = UMFutures(key=api_key, secret=secret_key)


# Чтение спотовой торговли
def kLines(symbol, tf, limit=60):  # , st
    url = 'https://api3.binance.com/api/v3/klines'
    param = {'symbol': symbol, 'interval': tf, 'limit': limit}  # ,'startTime':st,'endTime':ed
    r = requests.get(url, params=param)
    if r.status_code == 200:
        df = pd.DataFrame(r.json())
        m = pd.DataFrame()
        m['date'] = df.iloc[:, 0]
        m['date'] = pd.to_datetime(m['date'], unit='ms')
        m['open'] = df.iloc[:, 1]
        m['high'] = df.iloc[:, 2]
        m['low'] = df.iloc[:, 3]
        m['close'] = df.iloc[:, 4]
        return m
    else:
        return print('Проверте данные')


# Чтение фьючей
def data_sig(symbol1):
    df = pd.DataFrame(client.klines(symbol=symbol1, interval='1m', limit=60))
    m = pd.DataFrame()
    m['date'] = df.iloc[:, 0]
    m['date'] = pd.to_datetime(m['date'], unit='ms')
    m['open'] = df.iloc[:, 1]
    m['high'] = df.iloc[:, 2]
    m['low'] = df.iloc[:, 3]
    m['close'] = df.iloc[:, 4]
    return m

# Ожидание следующей минуты
def wait_for_next_min(prev):
    check = 0
    while check == 0:
        w_time = datetime.now().strftime('%M')
        w_time = int(w_time)
        if w_time != prev:
            check = 1
        else:
            t.sleep(2)

    return w_time

# Нахождение изменения цены или самостоятельных движений
def find_delta(df):
    min_val = float(min(df['low']))
    max_val = float(max(df['high']))
    close = float(df['low'][len(df) - 1])
    positive_delta = (close - min_val) / min_val

    if positive_delta >= 0.01:
        positive_delta_res = 1
    else:
        positive_delta_res = 0

    neg_delta = (close - max_val) / max_val
    if neg_delta <= -0.01:
        neg_delta_res = 1
    else:
        neg_delta_res = 0

    return positive_delta * 100, positive_delta_res, neg_delta * 100, neg_delta_res


#Основная рабочая часть
prev = 0
while (True):
    loaded_ETH = False
    loaded_ETHBTC = False
    prev = wait_for_next_min(prev)

    try:
        df_ETH = data_sig('ETHUSDT')
        loaded_ETH = True
    except:
        print('Не удалось скачать данные с биржы')
    if loaded_ETH:
        print('ETH: ' + df_ETH['close'][59])
        res_eth = find_delta(df_ETH)
        if res_eth[1] == 1:
            print(f'Цена выросла на {round(res_eth[0], 2)}% от минимума за последний час')
        if res_eth[3] == 1:
            print(f'Цена упала на {round(res_eth[2], 2)}% от максимума за последний час')

    try:
        df_ETHBTC = kLines("ETHBTC", '1m', limit=60)
        loaded_ETHBTC = True
    except:
        print('Не удалось скачать данные с биржы 2 ')

    if loaded_ETHBTC:
        print('ETHBTC: ' + df_ETHBTC['close'][59])
        res_ethbtc = find_delta(df_ETHBTC)
        if res_ethbtc[1] == 1:
            print(f'Цена относительно BTC выросла на {round(res_ethbtc[0], 2)}% от минимума  за последний час')
        if res_ethbtc[3] == 1:
            print(f'Цена относительно BTC упала на {round(res_ethbtc[2], 2)}% от максимума за последний час')
