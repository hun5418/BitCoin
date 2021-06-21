from re import DEBUG
import time
import pyupbit
import datetime
from slacker import Slacker
import requests
import os, sys, ctypes
from numpy import load
import time, calendar
import requests
from re import DEBUG
import time
import pyupbit
import datetime
from slacker import Slacker
import requests
import os, sys, ctypes
from numpy import load
import time, calendar
import requests

def dbgout(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
    print(str(text))
 
myToken ="xoxb-1647169481493-2188016124277-D9arJ96a2v7ZLslF2p5J3cEG"
 

access = "5fDHPiW76V7EXo8hlH8ughdJQ8JTt35gYw9Z40vB"
secret = "aSxf6DpfxW9zCvhvBcmx6G8xu14lza8T4Bbx1SBi"

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
    price_Average = []
    sell_price = []
    buy_price = 0
    trading = False
    sell_trading = False
    # 로그인
    upbit = pyupbit.Upbit(access, secret)

    dbgout(myToken,"#bitcoin-","autotrade start")
    dbgout(myToken,"#bitcoin-","현재 잔고 : " + str(upbit.get_balance("KRW")))

    now = datetime.datetime.now()
    today_high, today_low = get_target_price("KRW-BTC")
    time.sleep(60 * (4 - (now.minute % 5)))
    if now.second < 60:
        time.sleep(60 - now.second)
    
    # 자동매매 시작
    while True:
        try:
            now = datetime.datetime.now()
            start_time = get_start_time("KRW-BTC")
            end_time = start_time + datetime.timedelta(days=1)
            btc = get_balance("BTC")
            if btc > 0:
                sell_trading = True
                trading = False
            else:
                sell_trading = False
                if trading == True:
                    trading = True
                else:
                    trading = False
            if sell_trading ==False:
                current_prices.append(get_current_price("KRW-BTC"))
                price_Average.append(get_current_price("KRW-BTC"))
            else:
                if sell_price % 5 ==0:
                    current_prices.append(get_current_price("KRW-BTC"))
                    price_Average.append(get_current_price("KRW-BTC"))


            if len(current_prices) > 5:
                current_prices = current_prices[1:]
            if len(price_Average) > 12:
                price_Average = price_Average[1:]
            hour = now.hour
            minute = now.minute
            second = now.second
            dbgout(myToken,"#bitcoin-","[" + str(hour) + " : " + str(minute) + " : " + str(second) + "]")
            try:
                if sell_trading == True :
                    sell_price.append(get_current_price("KRW-BTC"))
                    if buy_price * 1.0015 < max(sell_price) > sell_price[-1] or buy_price * 0.995 > sell_price[-1]:
                        btc = get_balance("BTC")
                        if btc > 0.00008:
                            upbit.sell_market_order("KRW-BTC", btc)
                            dbgout(myToken,"#bitcoin-","sell")
                            krw = get_balance("KRW")
                            dbgout(myToken,"#bitcoin-","현재 잔고 : " + str(upbit.get_balance("KRW")))
                            sell_price.clear()
                            sell_trading =False
                            now = datetime.datetime.now()
                            time.sleep(60 * (4 - (now.minute % 5)))
                            if 0 <= now.second <57:
                                time.sleep((57-now.second))
                            else:
                                time.sleep(((60-now.second) + 57))
                            continue
                            
                    
                        

                if (current_prices[-4] >  current_prices[-3] > current_prices[-2] or current_prices[-2] * 1.0025 <= current_prices[-3] ) and trading == False and sell_trading == False:
                    trading =True
                
                if trading == True and current_prices * 1.005 > current_prices[-3] > current_prices[-2] < current_prices[-1] :
                    if min(price_Average) +  (max(price_Average) - min(price_Average) * 0.5) < current_prices[-1]:
                        now = datetime.datetime.now()
                        if 0 <= now.second <57:
                            time.sleep(240+(57-now.second))
                        else:
                            time.sleep(240+((60-now.second) + 57))
                        continue
                    else:
                        krw = get_balance("KRW")
                        if krw > 5000:
                            upbit.buy_market_order("KRW-BTC", krw*0.9995)
                            buy_price = get_current_price("KRW-BTC")
                            sell_trading = True
                            trading = False
                            sell_price.append(get_current_price("KRW-BTC"))
                            dbgout(myToken,"#bitcoin-","buy")



                now = datetime.datetime.now()
                if sell_trading == True:
                    if 0 <= now.second <57:
                        time.sleep((57-now.second))
                    else:
                        time.sleep(((60-now.second) + 57))
                    continue

                if 0 <= now.second <57:
                    time.sleep(240+(57-now.second))
                else:
                    time.sleep(240+((60-now.second) + 57))
            except Exception as e:
                print(str(e))
                now = datetime.datetime.now()
                if 0 <= now.second <57:
                    time.sleep(240+(57 - now.second))
                else:
                    time.sleep(240+((60 - now.second) + 57))
                pass

        except Exception as e:
            dbgout(myToken,"#bitcoin-",str(e))
