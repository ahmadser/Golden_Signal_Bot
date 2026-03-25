import os
import telebot
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import time
from flask import Flask
import threading

# 🔑 إعدادات البوت (التوكن والـ ID الخاص بك)
TOKEN = "8571032199:AAHCoP13fVQJ5lkFC0BVZBdnSBp6I5Tw7n4"
CHAT_ID = "8453156230"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 📊 قائمة الـ 12 زوج (الأكثر سيولة للخيارات الثنائية)
ASSETS = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X", "NZD/USD": "NZDUSD=X", "USD/CHF": "CHF=X",
    "EUR/GBP": "EURGBP=X", "الذهب 🟡": "GC=F", "البيتكوين ₿": "BTC-USD"
}

def analyze_market():
    while True:
        print("🔄 بدء دورة تحليل جديدة للرادار...")
        for name, ticker in ASSETS.items():
            try:
                # 📥 جلب البيانات (شمعة 5 دقائق)
                df = yf.download(ticker, period="1d", interval="5m", progress=False)
                
                if df is None or df.empty or len(df) < 30:
                    continue

                # 📉 حساب المؤشرات الفنية (الـ 6 استراتيجيات)
                df['RSI'] = ta.rsi(df['Close'], length=14)
                bbands = ta.bbands(df['Close'], length=20, std=2)
                df['EMA_5'] = ta.ema(df['Close'], length=5)
                df['EMA_13'] = ta.ema(df['Close'], length=13)
                df['STOCH_K'] = ta.stoch(df['High'], df['Low'], df['Close'])['STOCHk_14_3_3']
                
                # جلب القيم الأخيرة
                last_price = round(float(df['Close'].iloc[-1]), 5)
                rsi_val = df['RSI'].iloc[-1]
                entry_time = datetime.now().strftime("%H:%M:%S")
                
                # 🚦 منطق الاستراتيجيات (فرصة ذهبية vs فرصة قوية)
                signal = None
                strategy_name = ""

                # 1. فرصة ذهبية (RSI + Bollinger + Stoch)
                if rsi_val < 30 and last_price < bbands['BBL_20_2.0'].iloc[-1]:
                    signal = "GOLDEN_BUY"
                    strategy_name = "الانعكاس من القاع (BB + RSI)"
                elif rsi_val > 70 and last_price > bbands['BBU_20_2.0'].iloc[-1]:
                    signal = "GOLDEN_SELL"
                    strategy_name = "الانعكاس من القمة (BB + RSI)"
                
                # 2. فرصة قوية (EMA Cross + Trend)
                elif df['EMA_5'].iloc[-1] > df['EMA_13'].iloc[-1] and df['EMA_5'].iloc[-2] <= df['EMA_13'].iloc[-2]:
                    signal = "STRONG_BUY"
                    strategy_name = "تقاطع المتوسطات السريعة"
                elif df['EMA_5'].iloc[-1] < df['EMA_13'].iloc[-1] and df['EMA_5'].iloc[-2] >= df['EMA_13'].iloc[-2]:
                    signal = "STRONG_SELL"
                    strategy_name = "تقاطع المتوسطات السريع"

                if signal:
                    send_telegram_signal(name, last_price, entry_time, signal, strategy_name)
                
                # 🛡️ تأخير 5 ثوانٍ لتجنب حظر Yahoo Finance (Rate Limit)
                time.sleep(5)

            except Exception as e:
                print(f"❌ خطأ في تحليل {name}: {e}")
        
        print("😴 اكتمال الدورة، انتظار 5 دقائق للفحص القادم...")
        time.sleep(300) # فحص كل 5 دقائق

def send_telegram_signal(name, price, entry_time, type, strategy):
    if "GOLDEN" in type:
        title = "🟢 [ 💠 فرصة ذهبية 💠 ] 🟡"
    else:
        title = "🔵 [ 💠 فرصة قوية 💠 ] ⚪"

    direction = "شـراء (UP) ⬆️" if "BUY" in type else "بـيـع (DOWN) ⬇️"
    footer = "✅ ادخل الآن - صعود أخضر" if "BUY" in type else "🛑 ادخل الآن - هبوط أحمر"
    
    msg = f"{title}\n" \
          f"━━━━━━━━━━━━━━\n" \
          f"💎 **الزوج:** `{name}`\n" \
          f"📈 **الاتجاه:** {direction}\n" \
          f"💵 **السعر:** `{price}`\n" \
          f"⏱️ **المدة:** 5 دقائق\n" \
          f"🕒 **وقت الدخول:** `{entry_time}`\n" \
          f"💠 **الاستراتيجية:** {strategy}\n" \
          f"━━━━━━━━━━━━━━\n" \
          f"{footer}"
    
    bot.send_message(CHAT_ID, msg, parse_mode="Markdown")

@app.route('/')
def home():
    return "الرادار يعمل بكفاءة Live!"

if __name__ == "__main__":
    # تشغيل التحليل في خيط منفصل (Thread) ليبقى السيرفر يعمل
    threading.Thread(target=analyze_market, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
