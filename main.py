import pandas_ta as ta
import yfinance as yf
import requests
import time
import os
from flask import Flask
from threading import Thread

# إعداد سيرفر الويب للبقاء حياً على Render
app = Flask('')
@app.route('/')
def home(): return "الرادار الذهبي يعمل بنجاح يا أبو جواد!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# بيانات البوت الجديدة من صورك
TOKEN = "8571032199:AAHCoP13fVQJ5lkFC0BVZBdnsBp6I5Tw7n4"
CHAT_ID = "8453156230"

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def get_signals():
    # الأصول: الذهب، اليورو/دولار، الاسترليني/دولار
    assets = {"الذهب 🟡": "GC=F", "EUR/USD 🇪🇺": "EURUSD=X", "GBP/USD 🇬🇧": "GBPUSD=X"}
    
    for name, ticker in assets.items():
        try:
            df = yf.download(ticker, period="1d", interval="5m", progress=False)
            if df.empty or len(df) < 30: continue

            # حساب المؤشرات (RSI و Bollinger Bands)
            df['RSI'] = ta.rsi(df['Close'], length=14)
            bbands = ta.bbands(df['Close'], length=20, std=2)
            
            current_price = df['Close'].iloc[-1]
            rsi_val = df['RSI'].iloc[-1]
            lower_band = bbands['BBL_20_2.0'].iloc[-1]
            upper_band = bbands['BBU_20_2.0'].iloc[-1]

            # استراتيجية أبو جواد (تشبع بيعي + لمس النطاق السفلي)
            if current_price <= lower_band and rsi_val <= 30:
                msg = f"🚀 *إشارة شراء قوية!* \n📌 الأداة: {name}\n💰 السعر: {current_price:.2f}\n📉 RSI: {rsi_val:.2f}\n⚠️ السعر تحت خط بولنجر السفلي!"
                send_telegram_msg(msg)

            # استراتيجية أبو جواد (تشبع شرائي + لمس النطاق العلوي)
            elif current_price >= upper_band and rsi_val >= 70:
                msg = f"📉 *إشارة بيع قوية!* \n📌 الأداة: {name}\n💰 السعر: {current_price:.2f}\n📈 RSI: {rsi_val:.2f}\n⚠️ السعر فوق خط بولنجر العلوي!"
                send_telegram_msg(msg)
                
        except Exception as e:
            print(f"Error checking {name}: {e}")

if __name__ == "__main__":
    # تشغيل السيرفر في خلفية منفصلة
    Thread(target=run).start()
    
    send_telegram_msg("✅ *تم تشغيل رادار أبو جواد للمراقبة الفنية بنجاح!*")
    
    while True:
        get_signals()
        time.sleep(300) # فحص كل 5 دقائق
