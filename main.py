import pandas_ta as ta
import yfinance as yf
import requests
import time
import os
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "الرادار يعمل يا أبو جواد!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# بياناتك الصحيحة
TOKEN = "8203171259:AAEHyC3hnxnbkIW8G3FxlWLDTyC6stiQSHY"
CHAT_ID = "8453156230"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=15)
        # طباعة النتيجة في السجلات لمعرفة السبب
        print(f"Telegram Response: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Connection Error: {e}")
        return False

def check_market():
    # سنبدأ بالذهب فقط للتجربة السريعة
    asset = "GC=F"
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    try:
        df = yf.download(asset, period="1d", interval="1m", session=session, progress=False)
        if not df.empty and len(df) >= 20:
            price = df['Close'].iloc[-1]
            # إرسال تحديث بسيط كل دورة للتأكد أن البوت حي
            print(f"Checking {asset}... Current Price: {price}")
    except Exception as e:
        print(f"Market Error: {e}")

if __name__ == "__main__":
    Thread(target=run).start()
    time.sleep(10)
    
    # محاولة إرسال رسالة اختبار فورية
    print("Sending test message...")
    success = send_msg("🚀 *يا أبو جواد، إذا وصلت هذه الرسالة فإن الربط سليم بنسبة 100%!*")
    
    if not success:
        print("❌ فشل إرسال الرسالة، يرجى التأكد من الـ Token أو أنك ضغطت Start للبوت.")

    while True:
        check_market()
        time.sleep(60)
