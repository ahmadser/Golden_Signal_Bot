import os, telebot, yfinance as yf, pandas as pd, pandas_ta as ta
from datetime import datetime
import time, threading
from flask import Flask

# 🔑 الإعدادات الأساسية
TOKEN = "8571032199:AAHCoP13fVQJ5lkFC0BVZBdnSBp6I5Tw7n4"
CHAT_ID = "8453156230"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 📊 الأصول (التركيز على الكريبتو لأن السوق مفتوح الآن)
ASSETS = {
    "البيتكوين ₿": "BTC-USD", 
    "إيثيريوم 💠": "ETH-USD",
    "سولانا ☀️": "SOL-USD"
}

def analyze_market():
    # رسالة ترحيب عند بدء التشغيل للتأكد من الربط
    try:
        bot.send_message(CHAT_ID, "🚀 **رادار أبو جواد تم تشغيله الآن!**\nجاري مراقبة البيتكوين والعملات الرقمية بأعلى دقة...")
    except: pass

    while True:
        print(f"🔄 جولة فحص: {datetime.now().strftime('%H:%M:%S')}")
        for name, ticker in ASSETS.items():
            try:
                ticker_obj = yf.Ticker(ticker)
                df = ticker_obj.history(period="1d", interval="5m")
                if df.empty or len(df) < 30: continue

                df['RSI'] = ta.rsi(df['Close'], length=14)
                bbands = ta.bbands(df['Close'], length=20, std=2)
                
                last = df.iloc[-1]
                price = round(float(last['Close']), 2)
                
                # 🛡️ استراتيجية متوازنة (ليست صعبة وليست سهلة)
                signal = None
                if last['RSI'] < 35: signal = "BUY_SIGNAL"
                elif last['RSI'] > 65: signal = "SELL_SIGNAL"

                if signal:
                    send_signal(name, price, signal, last['RSI'])
                
                time.sleep(10) # مهلة بين الأصول
            except Exception as e:
                print(f"Error with {name}: {e}")
                continue
        time.sleep(180) # فحص كل 3 دقائق

def send_signal(name, price, s_type, rsi_val):
    is_buy = "BUY" in s_type
    color = "🟢" if is_buy else "🔴"
    action = "شـــــراء | CALL" if is_buy else "بـــيـــــع | PUT"
    
    msg = f"📍 **إشارة رادار جديدة**\n━━━━━━━━━━━━━━\n💎 **الزوج:** `{name}`\n📊 **RSI:** `{round(rsi_val, 2)}`\n━━━━━━━━━━━━━━\n{color} **الاتجاه:** `{action}`\n━━━━━━━━━━━━━━\n💵 **السعر:** `{price}`\n⏱️ **الفريم:** `5 دقائق`\n📡 `{datetime.now().strftime('%H:%M:%S')}`"
    
    try:
        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
    except: pass

@app.route('/')
def home(): return "الرادار يعمل! تحقق من تلجرام."

if __name__ == "__main__":
    threading.Thread(target=analyze_market, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
