import pandas_ta as ta
import yfinance as yf
import requests
import time
import os
from flask import Flask
from threading import Thread

# إعداد السيرفر ليتوافق مع Render تلقائياً
app = Flask('')

@app.route('/')
def home():
    return "الرادار يعمل بكفاءة يا أبو جواد!"

def run():
    # هذا السطر هو السر: يبحث عن المنفذ المطلوب أو يستخدم 10000 كاحتياطي
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# بيانات التلجرام
TOKEN = "8203171259:AAEHyC3hnxnbkIW8G3FxlWLDTyC6stiQSHY"
CHAT_ID = "8453156230"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

def check_market():
    assets = ["GC=F", "EURUSD=X", "GBPUSD=X"]
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    for asset in assets:
        try:
            df = yf.download(asset, period="1d", interval="1m", session=session, progress=False)
            if df.empty or len(df) < 20: continue

            bb = ta.bbands(df['Close'], length=20, std=2)
            rsi = ta.rsi(df['Close'], length=14)
            
            price = df['Close'].iloc[-1]
            lower = bb['BBL_20_2.0'].iloc[-1]
            upper = bb['BBU_20_2.0'].iloc[-1]
            rsi_val = rsi.iloc[-1]

            if price <= lower and rsi_val < 35:
                send_msg(f"🔔 *إشارة شراء* ⬆️\n💹 `{asset}`\n💰 السعر: `{price:.5f}`")
            elif price >= upper and rsi_val > 65:
                send_msg(f"🔔 *إشارة بيع* ⬇️\n💹 `{asset}`\n💰 السعر: `{price:.5f}`")
        except:
            continue

def main_loop():
    while True:
        check_market()
        time.sleep(120)

if __name__ == "__main__":
    # تشغيل Flask أولاً ليرى Render أن المنفذ مفتوح
    Thread(target=run).start()
    time.sleep(5)
    send_msg("🚀 *الرادار استيقظ الآن بنظام المنفذ التلقائي!*")
    main_loop()
