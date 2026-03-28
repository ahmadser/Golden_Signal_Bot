import os, telebot, yfinance as yf, pandas as pd, pandas_ta as ta
from datetime import datetime
import time, threading
from flask import Flask

# 🔑 الإعدادات (ثابتة)
TOKEN = "8571032199:AAHCoP13fVQJ5lkFC0BVZBdnSBp6I5Tw7n4"
CHAT_ID = "8453156230"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 📊 الأصول (التي تعمل الآن بنجاح)
ASSETS = {
    "البيتكوين ₿": "BTC-USD", "إيثيريوم 💠": "ETH-USD",
    "سولانا ☀️": "SOL-USD", "الذهب 🟡": "GC=F",
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X"
}

def analyze_market():
    while True:
        print(f"🔄 جولة فحص رادار أبو جواد: {datetime.now().strftime('%H:%M:%S')}")
        for name, ticker in ASSETS.items():
            try:
                # 🛡️ استخدام نفس الطريقة التي نجحت معك
                ticker_obj = yf.Ticker(ticker)
                df = ticker_obj.history(period="1d", interval="5m")
                
                if df.empty or len(df) < 30:
                    continue

                # حساب المؤشرات بدقة
                df['RSI'] = ta.rsi(df['Close'], length=14)
                bbands = ta.bbands(df['Close'], length=20, std=2)
                df['EMA_200'] = ta.ema(df['Close'], length=200)
                df['CCI'] = ta.cci(df['High'], df['Low'], df['Close'], length=20)
                
                last = df.iloc[-1]
                price = round(float(last['Close']), 5)
                signal = None

                # 💠 الاستراتيجيات (نفس المنطق الذي أرسل لك الصفقات)
                # 1. القناص (SNIPER)
                if price < last['EMA_200'] and last['RSI'] < 40: signal = "SNIPER_BUY"
                elif price > last['EMA_200'] and last['RSI'] > 60: signal = "SNIPER_SELL"
                # 2. الزخم (MOMENTUM)
                elif last['CCI'] > 100: signal = "MOMENTUM_BUY"
                elif last['CCI'] < -100: signal = "MOMENTUM_SELL"

                if signal:
                    send_formatted_signal(name, price, signal)
                
                time.sleep(15) # مهلة أمان
            except Exception as e:
                print(f"❌ خطأ في {name}: {e}")
                time.sleep(10)
        
        time.sleep(120) # فحص كل دقيقتين

def send_formatted_signal(name, price, s_type):
    # 🎨 التنسيق الاحترافي الملون
    is_buy = "BUY" in s_type
    arrow = "⬆️⬆️" if is_buy else "⬇️⬇️"
    color = "🟢" if is_buy else "🔴"
    action = "شـــــراء | CALL" if is_buy else "بـــيـــــع | PUT"
    
    msg = (
        f"📍 **تنبيه الرادار الذكي**\n"
        f"━━━━━━━━━━━━━━\n"
        f"💎 **الزوج:** `{name}`\n"
