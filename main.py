import os, telebot, yfinance as yf, pandas as pd, pandas_ta as ta
from datetime import datetime
import time, threading
from flask import Flask

# 🔑 الإعدادات
TOKEN = "8571032199:AAHCoP13fVQJ5lkFC0BVZBdnSBp6I5Tw7n4"
CHAT_ID = "8453156230"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 📊 الأصول المختارة (لضمان السرعة والدقة)
ASSETS = {
    "الذهب 🟡": "GC=F", "البيتكوين ₿": "BTC-USD",
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X", "EUR/JPY": "EURJPY=X"
}

def analyze_market():
    while True:
        print(f"🔄 جولة فحص: {datetime.now().strftime('%H:%M:%S')}")
        for name, ticker in ASSETS.items():
            try:
                df = yf.download(ticker, period="1d", interval="5m", progress=False, timeout=10)
                if df.empty or len(df) < 35: continue

                # حساب المؤشرات
                df['RSI'] = ta.rsi(df['Close'], length=14)
                bbands = ta.bbands(df['Close'], length=20, std=2)
                df['EMA_200'] = ta.ema(df['Close'], length=200)
                df['CCI'] = ta.cci(df['High'], df['Low'], df['Close'], length=20)
                
                last = df.iloc[-1]
                price = round(float(last['Close']), 5)
                signal = None

                # منطق الاستراتيجيات (تم دمج الحساسية)
                if last['RSI'] < 30 and price < bbands['BBL_20_2.0'].iloc[-1]: signal = "GOLDEN_BUY"
                elif last['RSI'] > 70 and price > bbands['BBU_20_2.0'].iloc[-1]: signal = "GOLDEN_SELL"
                elif price < last['EMA_200'] and last['RSI'] < 35: signal = "SNIPER_BUY"
                elif price > last['EMA_200'] and last['RSI'] > 65: signal = "SNIPER_SELL"
                elif last['CCI'] > 100: signal = "MOMENTUM_BUY"
                elif last['CCI'] < -100: signal = "MOMENTUM_SELL"

                if signal:
                    send_signal(name, price, signal)
                
                time.sleep(10) 
            except: continue
        time.sleep(120)

def send_signal(name, price, s_type):
    # 🎨 هندسة الألوان والرموز
    is_buy = "BUY" in s_type
    color_icon = "🟢" if is_buy else "🔴"
    arrow = "⬆️" if is_buy else "⬇️"
    action = "شـــــراء | CALL" if is_buy else "بـــيـــــع | PUT"
    
    # 📋 الترتيب الجديد المنظم
    msg = (
        f"📍 **تنبيه الرادار الذكي**\n"
        f"━━━━━━━━━━━━━━\n"
        f"💎 **الزوج:** `{name}`\n"
        f"📊 **الاستراتيجية:** `{s_type.split('_')[0]}`\n"
        f"━━━━━━━━━━━━━━\n"
        f"{color_icon} **الاتجاه:** `{action}`\n"
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
def home(): return "الرادار بتنسيق أبو جواد الجديد يعمل!"

if __name__ == "__main__":
    threading.Thread(target=analyze_market, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
