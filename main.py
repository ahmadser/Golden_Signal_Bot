import pandas_ta as ta
import yfinance as yf
import requests
import time
import pandas as pd
from flask import Flask
from threading import Thread

# --- إعداد خادم لإبقاء البوت حياً ---
app = Flask('')
@app.route('/')
def home():
    return "نظام أبو جواد يعمل بنجاح!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- بياناتك الخاصة ---
TOKEN = "8203171259:AAEHyC3hnxnbkIW8G3FxlWLDTyC6stiQSHY"
CHAT_ID = "8453156230"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try: requests.get(url, timeout=10)
    except: print("⚠️ خطأ في الإرسال")

def check_market():
    pairs = ["EURUSD=X", "GBPUSD=X", "JPY=X", "GC=F"] # عملات وذهب
    for pair in pairs:
        try:
            df = yf.download(tickers=pair, period="2d", interval="5m", progress=False)
            if len(df) < 50: continue
            
            # حساب المؤشرات
            df['EMA200'] = ta.ema(df['Close'], length=200)
            # منطق بسيط للتنبيه في Logs للتأكد من العمل
            print(f"✅ فحص {pair} بنجاح...")
        except: continue

if __name__ == "__main__":
    keep_alive()
    # رسالة التأكيد التي ستصل لهاتفك فور الإطلاق
    send_telegram_msg("🚀 نظام أبو جواد للصيد الذهبي متصل بالسحاب وجاهز لاقتناص الفرص!")
    
    while True:
        check_market()
        time.sleep(300) # فحص كل 5 دقائق
