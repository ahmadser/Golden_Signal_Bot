import os, telebot, yfinance as yf, pandas as pd, pandas_ta as ta
from datetime import datetime
import time, threading
from flask import Flask

# 🔑 الإعدادات
TOKEN = "8571032199:AAHCoP13fVQJ5lkFC0BVZBdnSBp6I5Tw7n4"
CHAT_ID = "8453156230"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 📊 الأصول (التي تعمل بنجاح)
ASSETS = {
    "البيتكوين ₿": "BTC-USD", "إيثيريوم 💠": "ETH-USD",
    "سولانا ☀️": "SOL-USD", "الذهب 🟡": "GC=F",
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X"
}

def analyze_market():
    while True:
        print(f"🔄 فحص جديد: {datetime.now().strftime('%H:%M:%S')}")
        for name, ticker in ASSETS.items():
            try:
                ticker_obj = yf.Ticker(ticker)
                df = ticker_obj.history(period="1d", interval="5m")
                
                if df.empty or len(df) < 30: continue

                df['RSI'] = ta.rsi(df['Close'], length=14)
                df['EMA_200'] = ta.ema(df['Close'], length=200)
                df['CCI'] = ta.cci(df['High'], df['Low'], df['Close'], length=20)
                
                last = df.iloc[-1]
                price = round(float(last['Close']), 5)
                signal = None

                if price < last['EMA_200'] and last['RSI'] < 40: signal = "SNIPER_BUY"
                elif price > last['EMA_200'] and last['RSI'] > 60: signal = "SNIPER_SELL"
                elif last['CCI'] > 100: signal = "MOMENTUM_BUY"
                elif last['CCI'] < -100: signal = "MOMENTUM_SELL"

                if signal:
                    send_formatted_signal(name, price, signal)
                
                time.sleep(15) 
            except: continue
        time.sleep(120)

def send_formatted_signal(name, price, s_type):
    is_buy = "BUY" in s_type
    arrow = "⬆️⬆️" if is_buy else "⬇️⬇️"
    color = "🟢" if is_buy else "🔴"
    action = "شـــــراء | CALL" if is_buy else "بـــيـــــع | PUT"
    
    # 📋 تم إصلاح تنسيق الرسالة هنا (إغلاق الأقواس بشكل صحيح)
    msg = (
        f"📍 **تنبيه الرادار الذكي**\n"
        f"━━━━━━━━━━━━━━\n"
        f"💎 **الزوج:** `{name}`\n"
        f"📊 **النوع:** `{s_type}`\n"
        f"━━━━━━━━━━━━━━\n"
        f"{color} **الاتجاه:** `{action}`\n"
        f"{arrow} **القرار:** `{arrow} ادخل الآن {arrow}`\n"
        f"━━━━━━━━━━━━━━\n"
        f"💵 **السعر:** `{price}`\n"
        f"⏱️ **الفريم:** `5 دقائق`\n"
        f"⏳ **المدة:** `5 دقائق`\n"
        f"━━━━━━━━━━━━━━\n"
        f"📡 `{datetime.now().strftime('%H:%M:%S')}`"
    )
    try:
        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
    except: pass

@app.route('/')
def home():
    try:
        bot.send_message(CHAT_ID, "✅ **تم إصلاح الكود وتنشيط الرادار!**\nالآن التنسيق والاتصال يعملان بانسجام.")
        return "الرادار يعمل!"
    except:
        return "الرادار يعمل!"

if __name__ == "__main__":
    threading.Thread(target=analyze_market, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
