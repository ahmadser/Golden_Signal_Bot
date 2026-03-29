import os, telebot, yfinance as yf, pandas as pd, pandas_ta as ta
from datetime import datetime
import time, threading
from flask import Flask

# 🔑 الإعدادات
TOKEN = "8571032199:AAHCoP13fVQJ5lkFC0BVZBdnSBp6I5Tw7n4"
CHAT_ID = "8453156230"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 📊 الأصول المختارة
ASSETS = {"سولانا ☀️": "SOL-USD", "البيتكوين ₿": "BTC-USD", "الذهب 🟡": "GC=F"}

# قاموس لتخزين وقت آخر إشارة لكل عملة لمنع التكرار المزعج
last_signal_time = {}

def analyze_market():
    while True:
        for name, ticker in ASSETS.items():
            try:
                # التأكد من مرور 10 دقائق على الأقل قبل إرسال إشارة جديدة لنفس العملة
                current_time = time.time()
                if name in last_signal_time and (current_time - last_signal_time[name]) < 600:
                    continue

                ticker_obj = yf.Ticker(ticker)
                df = ticker_obj.history(period="1d", interval="5m")
                if df.empty or len(df) < 40: continue

                # حساب المؤشرات (الاستراتيجية التي نجحت في صفقتك الأولى)
                df['RSI'] = ta.rsi(df['Close'], length=14)
                bbands = ta.bbands(df['Close'], length=20, std=2)
                
                last = df.iloc[-1]
                price = round(float(last['Close']), 2)
                
                signal = None
                # شروط "الصفقة الناجحة": تشبع قوي + لمس حدود البولنجر
                if last['RSI'] <= 28 and price <= bbands['BBL_20_2.0'].iloc[-1]:
                    signal = "STRONG_BUY"
                elif last['RSI'] >= 72 and price >= bbands['BBU_20_2.0'].iloc[-1]:
                    signal = "STRONG_SELL"

                if signal:
                    send_signal(name, price, signal, last['RSI'])
                    last_signal_time[name] = current_time # تحديث وقت الإرسال
                
                time.sleep(5)
            except: continue
        time.sleep(60)

def send_signal(name, price, s_type, rsi_val):
    is_buy = "BUY" in s_type
    color = "🟢" if is_buy else "🔴"
    action = "شـــــراء | CALL" if is_buy else "بـــيـــــع | PUT"
    msg = f"📍 **إشارة القناص المعتمدة**\n━━━━━━━━━━━━━━\n💎 **الزوج:** `{name}`\n📊 **RSI:** `{round(rsi_val, 2)}` (إشارة نوعية)\n━━━━━━━━━━━━━━\n{color} **الاتجاه:** `{action}`\n━━━━━━━━━━━━━━\n💵 **السعر:** `{price}`\n⏱️ **الفريم:** `5 دقائق`\n⏳ **الانتظار:** `ممنوع التكرار لـ 10 دقائق`\n━━━━━━━━━━━━━━\n📡 `{datetime.now().strftime('%H:%M:%S')}`"
    try: bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
    except: pass

@app.route('/')
def home(): return "رادار أبو جواد الذكي يعمل!"

if __name__ == "__main__":
    threading.Thread(target=analyze_market, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
