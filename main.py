import os, telebot, yfinance as yf, pandas as pd, pandas_ta as ta
from datetime import datetime
import time, threading, os
from flask import Flask

# 🔑 الإعدادات
TOKEN = "8571032199:AAHCoP13fVQJ5lkFC0BVZBdnSBp6I5Tw7n4"
CHAT_ID = "8453156230"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 📊 تقليل القائمة لتركيز القوة وتجنب الحظر (أهم 6 أصول)
ASSETS = {
    "الذهب 🟡": "GC=F", "البيتكوين ₿": "BTC-USD",
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X", "EUR/JPY": "EURJPY=X"
}

def analyze_market():
    while True:
        print(f"🔄 فحص جديد: {datetime.now().strftime('%H:%M:%S')}")
        for name, ticker in ASSETS.items():
            try:
                # محاولة جلب البيانات مع "تكرار" في حال الفشل
                data = yf.Ticker(ticker)
                df = data.history(period="1d", interval="5m")
                
                if df.empty or len(df) < 30:
                    print(f"⚠️ {name}: لا توجد بيانات حالياً.")
                    continue

                # حساب المؤشرات (الاستراتيجيات الـ 9 مدمجة)
                df['RSI'] = ta.rsi(df['Close'], length=14)
                bbands = ta.bbands(df['Close'], length=20, std=2)
                df['EMA_5'] = ta.ema(df['Close'], length=5)
                df['EMA_13'] = ta.ema(df['Close'], length=13)
                df['EMA_200'] = ta.ema(df['Close'], length=200)
                df['CCI'] = ta.cci(df['High'], df['Low'], df['Close'], length=20)
                
                last = df.iloc[-1]
                prev = df.iloc[-2]
                price = round(float(last['Close']), 5)
                signal = None

                # 1. القناص (SNIPER) - جعلناها أكثر حساسية
                if price < last['EMA_200'] and last['RSI'] < 40: signal = "SNIPER_BUY"
                elif price > last['EMA_200'] and last['RSI'] > 60: signal = "SNIPER_SELL"
                
                # 2. الزخم (MOMENTUM)
                elif last['CCI'] > 100: signal = "MOMENTUM_BUY"
                elif last['CCI'] < -100: signal = "MOMENTUM_SELL"

                if signal:
                    send_signal(name, price, signal)
                
                # 💡 زيادة وقت الانتظار بين العملات لتجنب الحظر
                time.sleep(15) 
            except Exception as e:
                print(f"❌ خطأ في {name}: {e}")
                time.sleep(30) # انتظار طويل في حال الخطأ
        
        time.sleep(120) # فحص كل دقيقتين

def send_signal(name, price, s_type):
    # تنسيق الرسالة
    emoji = "🚀" if "BUY" in s_type else "📉"
    msg = f"✨ **إشارة جديدة مكتشفة!**\n\n💎 الزوج: `{name}`\n📈 النوع: `{s_type}`\n💵 السعر: `{price}`\n\n{emoji} القرار: {'شراء' if 'BUY' in s_type else 'بيع'}"
    try:
        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
    except: pass

@app.route('/')
def home(): return "الرادار يعمل!"

if __name__ == "__main__":
    threading.Thread(target=analyze_market, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
