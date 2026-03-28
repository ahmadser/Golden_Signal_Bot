import os, telebot, yfinance as yf, pandas as pd, pandas_ta as ta
from datetime import datetime
import time, threading
from flask import Flask

# 🔑 الإعدادات
TOKEN = "8571032199:AAHCoP13fVQJ5lkFC0BVZBdnSBp6I5Tw7n4"
CHAT_ID = "8453156230"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 📊 الأصول (التركيز على الأقوى حركة)
ASSETS = {
    "الذهب 🟡": "GC=F", "البيتكوين ₿": "BTC-USD",
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X", "إيثيريوم 💠": "ETH-USD"
}

def analyze_market():
    while True:
        print(f"🔄 فحص رادار القناص: {datetime.now().strftime('%H:%M:%S')}")
        for name, ticker in ASSETS.items():
            try:
                ticker_obj = yf.Ticker(ticker)
                df = ticker_obj.history(period="2d", interval="5m") # جلب بيانات يومين لضمان دقة المؤشرات
                if df.empty or len(df) < 50: continue

                # حساب المؤشرات (الاستراتيجية الثلاثية)
                df['RSI'] = ta.rsi(df['Close'], length=14)
                df['EMA_200'] = ta.ema(df['Close'], length=200)
                bbands = ta.bbands(df['Close'], length=20, std=2)
                df['BBU'] = bbands['BBU_20_2.0'] # الحد العلوي
                df['BBL'] = bbands['BBL_20_2.0'] # الحد السفلي
                
                last = df.iloc[-1]
                price = round(float(last['Close']), 5)
                signal = None

                # 🔥 شروط الاستراتيجية القوية (لن ترسل صفقات كثيرة، لكنها دقيقة)
                
                # شرط الشراء (CALL): السعر فوق الـ 200 + لمس الحد السفلي للبولنجر + RSI تحت 30
                if price > last['EMA_200'] and price <= last['BBL'] and last['RSI'] <= 30:
                    signal = "PRO_BUY"
                
                # شرط البيع (PUT): السعر تحت الـ 200 + لمس الحد العلوي للبولنجر + RSI فوق 70
                elif price < last['EMA_200'] and price >= last['BBU'] and last['RSI'] >= 70:
                    signal = "PRO_SELL"

                if signal:
                    send_formatted_signal(name, price, signal, last['RSI'])
                
                time.sleep(15) 
            except: continue
        time.sleep(300) # فحص كل 5 دقائق (ليناسب فريم الشمعة)

def send_formatted_signal(name, price, s_type, rsi_val):
    is_buy = "BUY" in s_type
    arrow = "⬆️⬆️" if is_buy else "⬇️⬇️"
    color = "🟢" if is_buy else "🔴"
    action = "شـــــراء | CALL" if is_buy else "بـــيـــــع | PUT"
    
    msg = f"📍 **تنبيه القناص المحترف**\n━━━━━━━━━━━━━━\n💎 **الزوج:** `{name}`\n📊 **القوة (RSI):** `{round(rsi_val, 2)}`\n━━━━━━━━━━━━━━\n{color} **الاتجاه:** `{action}`\n{arrow} **القرار:** `{arrow} دخول قوي {arrow}`\n━━━━━━━━━━━━━━\n💵 **السعر:** `{price}`\n⏱️ **الفريم:** `5 دقائق`\n⏳ **المدة:** `5 دقائق`\n━━━━━━━━━━━━━━\n📡 `{datetime.now().strftime('%H:%M:%S')}`"
    
    try:
        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
    except: pass

@app.route('/')
def home(): return "رادار القناص يعمل بأعلى دقة!"

if __name__ == "__main__":
    threading.Thread(target=analyze_market, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
