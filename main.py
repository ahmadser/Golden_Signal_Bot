import pandas_ta as ta
import yfinance as yf
import requests
import time
import pandas as pd
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "رادار أبو جواد الشامل يعمل!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

TOKEN = "8203171259:AAEHyC3hnxnbkIW8G3FxlWLDTyC6stiQSHY"
CHAT_ID = "8453156230"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try: requests.get(url, timeout=10)
    except: pass

def check_market():
    # القائمة الشاملة (ذهب، فضة، وعملات)
    pairs = [
        "GC=F", "SI=F", "EURUSD=X", "GBPUSD=X", "JPY=X", 
        "AUDUSD=X", "NZDUSD=X", "EURJPY=X", "GBPJPY=X", 
        "EURGBP=X", "USDCAD=X", "USDCHF=X"
    ]
    
    for pair in pairs:
        try:
            # استخدام Ticker لجلب البيانات بطريقة أكثر استقراراً
            ticker = yf.Ticker(pair)
            df = ticker.history(period="2d", interval="5m")
            
            if df.empty or len(df) < 50: continue
            
            # الحسابات الفنية
            df['EMA200'] = ta.ema(df['Close'], length=200)
            bb = ta.bbands(df['Close'], length=20, std=2)
            stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3)
            df = pd.concat([df, bb, stoch], axis=1)
            last = df.iloc[-1]

            # استخراج القيم الحالية
            close_p = float(last['Close'])
            ema_v = float(last['EMA200'])
            low_p = float(last['Low'])
            high_p = float(last['High'])
            bb_low = float(last['BBL_20_2.0'])
            bb_up = float(last['BBU_20_2.0'])
            stoch_k = float(last['STOCHk_14_3_3'])

            # فحص الشروط
            is_uptrend = close_p > ema_v
            is_downtrend = close_p < ema_v
            
            # 1. الصفقة الذهبية 👑 (3 شروط)
            if is_uptrend and low_p <= bb_low and stoch_k < 20:
                send_telegram_msg(f"👑 صفقة ذهبية (شراء)\nالزوج: {pair}\nالسعر: {close_p:.5f}")
            elif is_downtrend and high_p >= bb_up and stoch_k > 80:
                send_telegram_msg(f"👑 صفقة ذهبية (بيع)\nالزوج: {pair}\nالسعر: {close_p:.5f}")
            
            # 2. الصفقة الفضية 🥈 (شرطان فقط - السعر مع أحد المؤشرات)
            elif is_uptrend and (low_p <= bb_low or stoch_k < 20):
                send_telegram_msg(f"🥈 صفقة فضية (شراء)\nالزوج: {pair}\nالسعر: {close_p:.5f}")
            elif is_downtrend and (high_p >= bb_up or stoch_k > 80):
                send_telegram_msg(f"🥈 صفقة فضية (بيع)\nالزوج: {pair}\nالسعر: {close_p:.5f}")

        except:
            continue

if __name__ == "__main__":
    keep_alive()
    send_telegram_msg("🚀 تم إطلاق الرادار الشامل (ذهب + فضة + عملات).. الصيد بدأ!")
    while True:
        check_market()
        time.sleep(300) # فحص كل 5 دقائق
