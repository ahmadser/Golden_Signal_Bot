import os
import telebot
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import time
from flask import Flask

# إعدادات البوت والتوكن الخاص بك (المفتاح الشغال)
TOKEN = "8571032199:AAHCoP13fVQJ5lkFC0BVZBdnSBp6I5Tw7n4"
CHAT_ID = "8453156230"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# قائمة الـ 12 زوج (عملات + ذهب + بيتكوين)
ASSETS = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X", "NZD/USD": "NZDUSD=X", "USD/CHF": "CHF=X",
    "EUR/GBP": "EURGBP=X", "الذهب 🟡": "GC=F", "البيتكوين ₿": "BTC-USD"
}

def analyze_and_send():
    for name, ticker in ASSETS.items():
        try:
            # جلب البيانات (5 دقائق)
            df = yf.download(ticker, period="1d", interval="5m", progress=False)
            if df.empty or len(df) < 20: continue
            
            # حساب المؤشرات الفنية (الـ 6 استراتيجيات)
            df['RSI'] = ta.rsi(df['Close'], length=14)
            bbands = ta.bbands(df['Close'], length=20, std=2)
            df['EMA_5'] = ta.ema(df['Close'], length=5)
            df['EMA_13'] = ta.ema(df['Close'], length=13)
            
            last_price = round(df['Close'].iloc[-1], 5)
            rsi_val = df['RSI'].iloc[-1]
            entry_time = datetime.now().strftime("%H:%M:%S")
            
            # منطق "الفرصة الذهبية" و "الفرصة القوية"
            signal = None
            if rsi_val < 30 and last_price < bbands['BBL_20_2.0'].iloc[-1]:
                signal = "GOLDEN_BUY"
            elif rsi_val > 70 and last_price > bbands['BBU_20_2.0'].iloc[-1]:
                signal = "GOLDEN_SELL"
            elif df['EMA_5'].iloc[-1] > df['EMA_13'].iloc[-1] and df['EMA_5'].iloc[-2] <= df['EMA_13'].iloc[-2]:
                signal = "STRONG_BUY"
            elif df['EMA_5'].iloc[-1] < df['EMA_13'].iloc[-1] and df['EMA_5'].iloc[-2] >= df['EMA_13'].iloc[-2]:
                signal = "STRONG_SELL"

            if signal:
                send_telegram_signal(name, last_price, entry_time, signal)
            
            time.sleep(2) # تأخير بسيط لتجنب الحظر
        except Exception as e:
            print(f"Error analyzing {name}: {e}")

def send_telegram_signal(name, price, entry_time, type):
    if "GOLDEN" in type:
        title = "🟢 [ 💠 فرصة ذهبية 💠 ] 🟡"
        strategy = "RSI + Bollinger Bands"
    else:
        title = "🔵 [ 💠 فرصة قوية 💠 ] ⚪"
        strategy = "EMA Cross (5/13)"

    direction = "شـراء (UP) ⬆️" if "BUY" in type else "بـيـع (DOWN) ⬇️"
    footer = "✅ ادخل الآن - صعود أخضر" if "BUY" in type else "🛑 ادخل الآن - هبوط أحمر"
    
    msg = f"{title}\n" \
          f"━━━━━━━━━━━━━━\n" \
          f"💎 الزوج: `{name}`\n" \
          f"📈 الاتجاه: {direction}\n" \
          f"💵 السعر: `{price}`\n" \
          f"⏱️ المدة: 5 دقائق\n" \
          f"🕒 وقت الدخول: `{entry_time}`\n" \
          f"💠 الاستراتيجية: {strategy}\n" \
          f"━━━━━━━━━━━━━━\n" \
          f"{footer}"
    
    bot.send_message(CHAT_ID, msg, parse_mode="Markdown")

@app.route('/')
def home(): return "الرادار الذهبي يعمل بنجاح!"

if __name__ == "__main__":
    # تشغيل التحليل في الخلفية
    analyze_and_send()
    app.run(host='0.0.0.0', port=10000)
