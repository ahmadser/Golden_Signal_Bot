import pandas_ta as ta
import yfinance as yf
import requests
import time
import pandas as pd
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "نظام أبو جواد للصيد يعمل!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

TOKEN = "8203171259:AAEHyC3hnxnbkIW8G3FxlWLDTyC6stiQSHY"
CHAT_ID = "8453156230"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try: requests.get(url, timeout=10)
    except: pass

def check_market():
    pairs = ["GC=F", "EURUSD=X", "GBPUSD=X", "JPY=X", "AUDUSD=X"]
    for pair in pairs:
        try:
            df = yf.download(tickers=pair, period="2d", interval="5m", progress=False)
            if df.empty or len(df) < 200: continue
            
            df['EMA200'] = ta.ema(df['Close'], length=200)
            bb = ta.bbands(df['Close'], length=20, std=2)
            stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3)
            df = pd.concat([df, bb, stoch], axis=1)
            last = df.iloc[-1]

            # متغيرات الشروط
            is_uptrend = last['Close'] > last['EMA200']
            is_downtrend = last['Close'] < last['EMA200']
            touch_lower = last['Low'] <= last['BBL_20_2.0']
            touch_upper = last['High'] >= last['BBU_20_2.0']
            stoch_oversold = last['STOCHk_14_3_3'] < 20
            stoch_overbought = last['STOCHk_14_3_3'] > 80

            # 1. فحص الصفقة الذهبية (3 شروط)
            if (is_uptrend and touch_lower and stoch_oversold):
                send_telegram_msg(f"👑 صفقة ذهبية (شراء)\nالزوج: {pair}\nالسعر: {float(last['Close']):.5f}")
            elif (is_downtrend and touch_upper and stoch_overbought):
                send_telegram_msg(f"👑 صفقة ذهبية (بيع)\nالزوج: {pair}\nالسعر: {float(last['Close']):.5f}")
            
            # 2. فحص الصفقة الفضية (شرطان فقط)
            elif (is_uptrend and (touch_lower or stoch_oversold)):
                send_telegram_msg(f"🥈 صفقة فضية (شراء)\nالزوج: {pair}\nالسعر: {float(last['Close']):.5f}")
            elif (is_downtrend and (touch_upper or stoch_overbought)):
                send_telegram_msg(f"🥈 صفقة فضية (بيع)\nالزوج: {pair}\nالسعر: {float(last['Close']):.5f}")

        except: continue

if __name__ == "__main__":
    keep_alive()
    send_telegram_msg("⚙️ تم تحديث النظام: إضافة خطة الصيد الفضية بنجاح!")
    while True:
        check_market()
        time.sleep(300)
