import os, telebot, yfinance as yf, pandas as pd, pandas_ta as ta
from datetime import datetime
import time, threading
from flask import Flask

# 🔑 الإعدادات
TOKEN = "8571032199:AAHCoP13fVQJ5lkFC0BVZBdnSBp6I5Tw7n4"
CHAT_ID = "8453156230"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 📊 الأصول
ASSETS = {"البيتكوين ₿": "BTC-USD", "سولانا ☀️": "SOL-USD", "إيثيريوم 💠": "ETH-USD"}
last_signal_time = {}

def send_welcome_message():
    """وظيفة مخصصة لإرسال رسالة الترحيب عند التشغيل"""
    for i in range(3):  # محاولة الإرسال 3 مرات في حال الفشل
        try:
            bot.send_message(CHAT_ID, "🛡️ **تم تفعيل رادار أبو جواد المطور بنجاح!**\n\n✅ الاتصال مستقر.\n✅ نظام القفل الزمني (10 دقائق) نشط.\n✅ مراقبة الكريبتو بدأت الآن.")
            print("✅ Welcome message sent successfully!")
            break
        except Exception as e:
            print(f"❌ Attempt {i+1} to send welcome failed: {e}")
            time.sleep(5)

def analyze_market():
    send_welcome_message() # تشغيل رسالة الترحيب فوراً
    while True:
        for name, ticker in ASSETS.items():
            try:
                current_time = time.time()
                if name in last_signal_time and (current_time - last_signal_time[name]) < 600:
                    continue

                ticker_obj = yf.Ticker(ticker)
                df = ticker_obj.history(period="1d", interval="5m")
                if df.empty or len(df) < 30: continue

                df['RSI'] = ta.rsi(df['Close'], length=14)
                bbands = ta.bbands(df['Close'], length=20, std=2)
                
                last = df.iloc[-1]
                price = round(float(last['Close']), 2)
                
                signal = None
                if last['RSI'] <= 28 and price <= bbands['BBL_20_2.0'].iloc[-1]:
                    signal = "STRONG_BUY"
                elif last['RSI'] >= 72 and price >= bbands['BBU_20_2.0'].iloc[-1]:
                    signal = "STRONG_SELL"

                if signal:
                    is_buy = "BUY" in signal
                    color = "🟢" if is_buy else "🔴"
                    action = "شـــــراء | CALL" if is_buy else "بـــيـــــع | PUT"
                    msg = f"📍 **إشارة القناص المعتمدة**\n━━━━━━━━━━━━━━\n💎 **الزوج:** `{name}`\n📊 **RSI:** `{round(last['RSI'], 2)}`\n━━━━━━━━━━━━━━\n{color} **الاتجاه:** `{action}`\n━━━━━━━━━━━━━━\n💵 **السعر:** `{price}`\n⏱️ **الفريم:** `5 دقائق`\n⏳ **الانتظار:** `10 دقائق لمنع التكرار`\n━━━━━━━━━━━━━━\n📡 `{datetime.now().strftime('%H:%M:%S')}`"
                    bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
                    last_signal_time[name] = current_time
                
                time.sleep(5)
            except: continue
        time.sleep(60)

@app.route('/')
def home(): return "الرادار يعمل! انتظر رسالة الترحيب في تلجرام."

if __name__ == "__main__":
    # تشغيل التحليل في خلفية السيرفر
    threading.Thread(target=analyze_market, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
