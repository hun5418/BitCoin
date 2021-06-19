from re import DEBUG
import time
import pyupbit
import datetime
from slacker import Slacker
import requests
import os, sys, ctypes
from numpy import load
import win32com.client
import time, calendar
import requests

def dbgout(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
    print(str(text))
 
myToken = ""
 

access = ""
secret = ""

def get_target_price(ticker):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    today_high = df.iloc[1]['high']
    today_low = df.iloc[1]['low']
    return today_high, today_low

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]



if __name__ == '__main__':
    current_prices = []
    buy_price = 0
    trading = False
    # 로그인
    upbit = pyupbit.Upbit(access, secret)

    dbgout(myToken,"#bitcoin-","autotrade start")
    dbgout(myToken,"#bitcoin-","현재 잔고 : " + str(upbit.get_balance("KRW")))

    now = datetime.datetime.now()
    today_high, today_low = get_target_price("KRW-BTC")
    minute = 4 - (now.minute % 5)
    time.sleep(60 * minute)
    if now.second < 60:
        time.sleep(60 - now.second)
    
    # 자동매매 시작
    while True:
        try:
            now = datetime.datetime.now()
            start_time = get_start_time("KRW-BTC")
            end_time = start_time + datetime.timedelta(days=1)

            current_prices.append(get_current_price("KRW-BTC"))
            if len(current_prices) > 5:
                current_prices = current_prices[1:]
            hour = now.hour
            minute = now.minute
            second = now.second
            dbgout(myToken,"#bitcoin-","[" + str(hour) + " : " + str(minute) + " : " + str(second) + "]" + str(current_prices))
            try:
                if buy_price * 1.0015 < current_prices[-1] and trading == True:
                    btc = get_balance("BTC")
                    if btc > 0.00008:
                        upbit.sell_market_order("KRW-BTC", btc)
                        dbgout(myToken,"#bitcoin-","sell")
                        krw = get_balance("KRW")
                        dbgout(myToken,"#bitcoin-","현재 잔고 : " + str(upbit.get_balance("KRW")))
                        trading = False

                if current_prices[-5] >= current_prices[-4] >=  current_prices[-3] >= current_prices[-2] < current_prices[-1] and trading == False:
                    krw = get_balance("KRW")
                    if krw > 5000:
                        upbit.buy_market_order("KRW-BTC", krw*0.9995)
                        buy_price = get_current_price("KRW-BTC")
                        dbgout(myToken,"#bitcoin-","autotrade start")
                        dbgout(myToken,"#bitcoin-","buy")
                        trading =True
                now = datetime.datetime.now()
                if 0 <= now.second <57:
                    time.sleep(240+ (57-now.second))
                else:
                    time.sleep(240 + ((60-now.second) + 57))
            except:
                now = datetime.datetime.now()
                if 0 <= now.second <57:
                    time.sleep(240 + (57 - now.second))
                else:
                    time.sleep(240 + ((60 - now.second) + 57))
                continue

        except Exception as e:
            dbgout(myToken,"#bitcoin-",str(e))