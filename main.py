import pandas_ta as ta
import yfinance as yf
import requests
import time
import pandas as pd
from flask import Flask
from threading import Thread

# --- إعداد خادم لإبقاء البوت حياً على Render ---
app = Flask('')
@app.route('/')
def home():
    return "نظام أبو جواد للصيد الذهبي يعمل بالسحاب!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- بيانات التلجرام الخاصة بك ---
TOKEN = "8203171259:AAEHyC3hnxnbkIW8G3FxlWLDTyC6stiQSHY"
CHAT_ID = "8453156230"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try: requests.get(url, timeout=10)
    except: print("⚠️ فشل إرسال التنبيه")

def check_market():
    # قائمة الأزواج للمراقبة المستمرة
    pairs = ["EURUSD=X", "GBPUSD=X", "JPY=X", "AUDUSD=X", "EURJPY=X", "GBPJPY=X", "GC=F"]
    for pair in pairs:
        try:
            df = yf.download(tickers=pair, period="2d", interval="5m", progress=False, auto_adjust=True)
            if df is None or len(df) < 200: continue
            
            # حساب المؤشرات الذهبية
            df['EMA200'] = ta.ema(df['Close'], length=200)
            bb = ta.bbands(df['Close'], length=20, std=2)
            df = pd.concat([df, bb], axis=1)
            stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3)
            df = pd.concat([df, stoch], axis=1)

            last = df.iloc[-1]
            # منطق الصيد: (سعر فوق المتوسط + لمس البولنجر السفلي + تشبع بيعي)
            if last['Close'] > last['EMA200'] and last['Low'] <= last['BBL_20_2.0'] and last['STOCHk_14_3_3'] < 20:
                send_telegram_msg(f"🚨 صيد ذهبي (صعود - CALL) \nالزوج: {pair} \nالسعر: {float(last['Close']):.5f}")
            # منطق الصيد: (سعر تحت المتوسط + لمس البولنجر العلوي + تشبع شرائي)
            elif last['Close'] < last['EMA200'] and last['High'] >= last['BBU_20_2.0'] and last['STOCHk_14_3_3'] > 80:
                send_telegram_msg(f"🚨 صيد ذهبي (هبوط - PUT) \nالزوج: {pair} \nالسعر: {float(last['Close']):.5f}")
        except: continue

if __name__ == "__main__":
    keep_alive() # تشغيل الخادم
    print("🚀 نظام أبو جواد انطلق للسحاب...")
    while True:
        check_market()
        time.sleep(300) # فحص كل 5 دقائق
