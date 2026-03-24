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
    try:
        requests.get(url, timeout=10)
    except Exception as e:
        print(f"⚠️ خطأ في الإرسال: {e}")

def check_market():
    # قائمة الأزواج للمراقبة: الذهب والعملات الرئيسية
    pairs = ["GC=F", "EURUSD=X", "GBPUSD=X", "JPY=X", "AUDUSD=X"]
    for pair in pairs:
        try:
            # جلب بيانات السوق
            df = yf.download(tickers=pair, period="2d", interval="5m", progress=False)
            if df.empty or len(df) < 200:
                continue
            
            # حساب المؤشرات الفنية
            df['EMA200'] = ta.ema(df['Close'], length=200)
            bb = ta.bbands(df['Close'], length=20, std=2)
            stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3)
            
            # دمج البيانات
            df = pd.concat([df, bb, stoch], axis=1)
            last = df.iloc[-1]

            # شروط الصيد الذهبي (صعود)
            if last['Close'] > last['EMA200'] and last['Low'] <= last['BBL_20_2.0'] and last['STOCHk_14_3_3'] < 20:
                send_telegram_msg(f"🚨 صيد ذهبي (صعود - CALL)\nالزوج: {pair}\nالسعر: {float(last['Close']):.5f}")
            
            # شروط الصيد الذهبي (هبوط)
            elif last['Close'] < last['EMA200'] and last['High'] >= last['BBU_20_2.0'] and last['STOCHk_14_3_3'] > 80:
                send_telegram_msg(f"🚨 صيد ذهبي (هبوط - PUT)\nالزوج: {pair}\nالسعر: {float(last['Close']):.5f}")
        
        except Exception as e:
            print(f"❌ خطأ في فحص {pair}: {e}")
            continue

if __name__ == "__main__":
    # تشغيل الخادم الوهمي لإبقاء الخدمة تعمل
    keep_alive()
    
    # رسالة التأكيد الفورية
    print("🚀 جاري إرسال رسالة الترحيب...")
    send_telegram_msg("🚀 نظام أبو جواد للصيد الذهبي متصل بالسحاب وجاهز لاقتناص الفرص!")
    
    # حلقة الفحص المستمر
    while True:
        check_market()
        time.sleep(300) # فحص كل 5 دقائق
