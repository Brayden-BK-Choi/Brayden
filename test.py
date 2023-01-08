import json 
import requests
import time
import urllib
import pandas as pd
import pyupbit
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('fivethirtyeight')




TOKEN = "5653836235:AAEvMZRxlEoXKcvRImmu2ew6pCHZ-Oj-n5A" # 여러분의 Bot 토큰으로 대체하세요.
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
chat_id = '5674922116'
tickers=pyupbit.get_tickers(fiat="KRW")

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def echo_all(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            send_message(text, chat)
        except Exception as e:
            print(e)

        
def condition_rsi_stoch(ticker):
    
    
    data=pyupbit.get_ohlcv(ticker, interval="minute15", count=100)
        
    df = pd.DataFrame(data)

    # df = pd.Series(df['close'].values)
    series = pd.Series(df['close'].values)   
            
    price = pyupbit.get_current_price(ticker)


        
    period=14
    smoothK=3
    smoothD=3
        
    # delta = df.diff()

    # up, down = delta.copy(), delta.copy()
    # up[up < 0] = 0
    # down[down > 0] = 0

    # _gain = up.ewm(com=(period - 1), min_periods=period).mean()
    # _loss = down.abs().ewm(com=(period - 2), min_periods=period).mean()
    # RS = _gain / _loss
        
    # rsi=round(pd.Series(100 - (100 / (1 + RS)), name="RSI").iloc[-1],1) 
    delta = series.diff().dropna()
    ups = delta * 0
    downs = ups.copy()
    ups[delta > 0] = delta[delta > 0]
    downs[delta < 0] = -delta[delta < 0]
    ups[ups.index[period-1]] = np.mean( ups[:period] )
    ups = ups.drop(ups.index[:(period-1)])
    downs[downs.index[period-1]] = np.mean( downs[:period] )
    downs = downs.drop(downs.index[:(period-1)])
    rs = ups.ewm(com=period-1,min_periods=0,adjust=False,ignore_na=False).mean() / \
         downs.ewm(com=period-1,min_periods=0,adjust=False,ignore_na=False).mean() 
    rsi = 100 - 100 / (1 + rs)
    rsi_1 = round(pd.Series(100 - (100 / (1 + rs)), name="RSI").iloc[-1],1) 
    stochrsi  = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
    stochrsi_K = stochrsi.rolling(smoothK).mean()
    stochrsi_D = stochrsi_K.rolling(smoothD).mean()
    
    
    


    print(str(ticker)+'현재가격은'+str(price)+'원')   

    print('RSI: ',rsi_1)
    print('upbit 15 minute stoch_rsi_K: ',stochrsi_K.iloc[-1]*100)
    print('upbit 15 minute stoch_rsi_D: ', stochrsi_D.iloc[-1]*100)
    print('')
   
    

    if rsi_1 < 45:
        if stochrsi_D.iloc[-1]*100 < 15:
            text=str(ticker) + '의 rsi는 ' + str(rsi_1) + '이고 ' + 'stochrsi는 ' + str(stochrsi_D.iloc[-1]*100) + '입니다'
            print(text)
            
            send_message(text, chat_id)
        print('')
        
   


def main():
    while True:
        for ticker in tickers:
            condition_rsi_stoch(ticker)
            # time.sleep(1)
            
           

            
            

if __name__ == '__main__':
    main()
