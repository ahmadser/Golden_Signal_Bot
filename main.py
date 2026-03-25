import pandas_ta as ta
import yfinance as yf
import requests
import time
import os
from flask import Flask
from threading import Thread

# --- إعدادات السيرفر لضمان عدم الإغلاق ---
app = Flask('')
@app.route('/')
def home(): return "الرادار يعمل بنجاح!"

def run():
    # استخدام المنفذ الذي يطلبه Render تلقائياً
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- بيانات التلجرام ---
TOKEN = "8203171259:AAEHyC3hnxnbkIW8G3FxlWLDTyC6stiQSHY"
CHAT_ID = "8453156230"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.json()
    except: return None

def check_market():
    # الذهب وأهم العملات
    pairs = ["GC=F", "EURUSD=X", "GBPUSD=X", "JPY=X", "GBPJPY=X"]
    for pair in pairs:
        try:
            time.sleep(5) 
            data = yf.download(pair, period="1d", interval="1m", progress=False)
            if data.empty: continue
            
            # التحليل الفني
            bb = ta.bbands(data['Close'], length=20, std=2)
            rsi = ta.rsi(data['Close'], length=14)
            stoch = ta.stoch(data['High'], data['Low'], data['Close'])
            
            last_price = data['Close'].iloc[-1]
            last_rsi = rsi.iloc[-1]
            last_stoch = stoch['STOCHk_14_3_3'].iloc[-1]
            upper_bb = bb['BBU_20_2.0'].iloc[-1]
            lower_bb = bb['BBL_20_2.0'].iloc[-1]

            # شروط الصيد (ألوان وأسهم كما طلبت)
            if last_price <= lower_bb and last_rsi < 30:
                msg = f"💎 *فرصة ذهبية (شراء) ⬆️*\n💹 الزوج: `{pair}`\n💰 السعر: `{last_price:.5f}`\n🟢 الاتجاه: *صعود*\n⏱ المدة: `5 دقائق`"
                send_telegram_msg(msg)
            elif last_price >= upper_bb and last_rsi > 70:
                msg = f"💎 *فرصة ذهبية (بيع) ⬇️*\n💹 الزوج: `{pair}`\n💰 السعر: `{last_price:.5f}`\n🔴 الاتجاه: *هبوط*\n⏱ المدة: `5 دقائق`"
                send_telegram_msg(msg)
        except: continue

if __name__ == "__main__":
    # 1. تشغيل السيرفر في الخلفية
    keep_alive()
    
    # 2. إرسال رسالة ترحيب فورية لكسر الصمت
    time.sleep(2)
    print("إرسال رسالة التفعيل...")
    send_telegram_msg("🚀 *تم تفعيل الرادار يا أبو جواد!*\nالنظام الآن يراقب الذهب والعملات بدقة.")
    
    # 3. حلقة الفحص المستمر
    while True:
        check_market()
        time.sleep(60)
