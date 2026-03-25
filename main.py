import os
import telebot
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import time
from flask import Flask
import threading

# 🔑 إعدادات البوت
TOKEN = "8571032199:AAHCoP13fVQJ5lkFC0BVZBdnSBp6I5Tw7n4"
CHAT_ID = "8453156230"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 📊 الأصول الـ 12
ASSETS = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X", "NZD/USD": "NZDUSD=X", "USD/CHF": "CHF=X",
    "EUR/GBP": "EURGBP=X", "الذهب 🟡": "GC=F", "البيتكوين ₿": "BTC-USD"
}import os, telebot, yfinance as yf, pandas as pd, pandas_ta as ta
from datetime import datetime
import time, threading
from flask import Flask

# 🔑 الإعدادات الأساسية
TOKEN = "8571032199:AAHCoP13fVQJ5lkFC0BVZBdnSBp6I5Tw7n4"
CHAT_ID = "8453156230"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 📊 الـ 12 زوج عملات المختارة بدقة
ASSETS = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X", "NZD/USD": "NZDUSD=X", "USD/CHF": "CHF=X",
    "EUR/GBP": "EURGBP=X", "الذهب 🟡": "GC=F", "البيتكوين ₿": "BTC-USD"
}

def analyze_market():
    while True:
        for name, ticker in ASSETS.items():
            try:
                df = yf.download(ticker, period="1d", interval="5m", progress=False)
                if df is None or df.empty or len(df) < 30: continue

                # حساب المؤشرات الستة
                df['RSI'] = ta.rsi(df['Close'], length=14)
                bbands = ta.bbands(df['Close'], length=20, std=2)
                df['EMA_5'] = ta.ema(df['Close'], length=5)
                df['EMA_13'] = ta.ema(df['Close'], length=13)
                stoch = ta.stoch(df['High'], df['Low'], df['Close'])
                df['STOCHk'] = stoch['STOCHk_14_3_3']
                df['STOCHd'] = stoch['STOCHd_14_3_3']

                last = df.iloc[-1]
                prev = df.iloc[-2]
                last_price = round(float(last['Close']), 5)
                
                signal_type = None
                
                # 🟡 1. منطق الفرصة الذهبية (دمج 3 مؤشرات)
                if last['RSI'] < 30 and last_price < bbands['BBL_20_2.0'].iloc[-1] and last['STOCHk'] < 20:
                    signal_type = "GOLDEN_BUY"
                elif last['RSI'] > 70 and last_price > bbands['BBU_20_2.0'].iloc[-1] and last['STOCHk'] > 80:
                    signal_type = "GOLDEN_SELL"
                
                # 🔵 2. منطق الفرصة القوية (تقاطع EMA)
                elif last['EMA_5'] > last['EMA_13'] and prev['EMA_5'] <= prev['EMA_13']:
                    signal_type = "STRONG_BUY"
                elif last['EMA_5'] < last['EMA_13'] and prev['EMA_5'] >= prev['EMA_13']:
                    signal_type = "STRONG_SELL"

                if signal_type:
                    send_signal(name, last_price, signal_type)
                
                time.sleep(5) # حماية من الحظر
            except: continue
        time.sleep(300)

def send_signal(name, price, s_type):
    # إعداد الشكل الهندسي والألوان
    if "GOLDEN" in s_type:
        header = "💠💠 【 فـرصـة ذهـبـيـة 】 💠💠"
        color_box = "⭐"
    else:
        header = "🔹🔹 【 فـرصـة قـويـة 】 🔹🔹"
        color_box = "⚡"

    if "BUY" in s_type:
        dir_text = "شـراء | UP ⬆️"
        action_color = "🟢 صعود أخضر (CALL)"
        emoji = "🚀"
    else:
        dir_text = "بـيـع | DOWN ⬇️"
        action_color = "🔴 هبوط أحمر (PUT)"
        emoji = "📉"

    msg = f"{header}\n" \
          f"━━━━━━━━━━━━━━\n" \
          f"💎 **الزوج:** `{name}`\n" \
          f"📊 **الاتجاه:** {dir_text}\n" \
          f"💵 **السعر:** `{price}`\n" \
          f"⏱️ **المدة:** `5 دقائق`\n" \
          f"🕒 **الوقت:** `{datetime.now().strftime('%H:%M:%S')}`\n" \
          f"━━━━━━━━━━━━━━\n" \
          f"{emoji} **القرار:** {action_color}\n" \
          f"{color_box} **ادخل الصفقة الآن!**"
    
    bot.send_message(CHAT_ID, msg, parse_mode="Markdown")

@app.route('/')
def home(): return "الرادار يعمل Live!"

if __name__ == "__main__":
    threading.Thread(target=analyze_market, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)

def analyze_market():
    while True:
        print("🔄 دورة تحليل جديدة...")
        for name, ticker in ASSETS.items():
            try:
                # جلب البيانات بهدوء لتجنب الحظر
                df = yf.download(ticker, period="1d", interval="5m", progress=False)
                
                # التأكد من وصول البيانات بنجاح
                if df is None or df.empty or len(df) < 20:
                    print(f"⚠️ لا توجد بيانات كافية لـ {name} حالياً")
                    continue

                # حساب المؤشرات مع التأكد من القيم
                rsi_series = ta.rsi(df['Close'], length=14)
                if rsi_series is None or rsi_series.empty or pd.isna(rsi_series.iloc[-1]):
                    continue
                
                df['RSI'] = rsi_series
                bbands = ta.bbands(df['Close'], length=20, std=2)
                
                # فحص وجود بيانات البولنجر
                if bbands is None or 'BBL_20_2.0' not in bbands:
                    continue

                last_price = float(df['Close'].iloc[-1])
                rsi_val = float(df['RSI'].iloc[-1])
                entry_time = datetime.now().strftime("%H:%M:%S")
                
                signal = None
                if rsi_val < 30 and last_price < bbands['BBL_20_2.0'].iloc[-1]:
                    signal = "GOLDEN_BUY"
                elif rsi_val > 70 and last_price > bbands['BBU_20_2.0'].iloc[-1]:
                    signal = "GOLDEN_SELL"

                if signal:
                    send_telegram_signal(name, round(last_price, 5), entry_time, signal)
                
                # 🛡️ أهم خطوة: تأخير 5 ثوانٍ بين كل عملة لمنع الحظر
                time.sleep(5)

            except Exception as e:
                print(f"❌ خطأ بسيط في {name}: {e}")
        
        print("😴 انتظار 5 دقائق للفحص القادم...")
        time.sleep(300)

def send_telegram_signal(name, price, entry_time, type):
    title = "🟢 [ 💠 فرصة ذهبية 💠 ] 🟡"
    direction = "شـراء (UP) ⬆️" if "BUY" in type else "بـيـع (DOWN) ⬇️"
    footer = "✅ ادخل الآن - صعود أخضر" if "BUY" in type else "🛑 ادخل الآن - هبوط أحمر"
    
    msg = f"{title}\n━━━━━━━━━━━━━━\n" \
          f"💎 **الزوج:** `{name}`\n📈 **الاتجاه:** {direction}\n" \
          f"💵 **السعر:** `{price}`\n⏱️ **المدة:** 5 دقائق\n" \
          f"🕒 **وقت الدخول:** `{entry_time}`\n━━━━━━━━━━━━━━\n{footer}"
    
    bot.send_message(CHAT_ID, msg, parse_mode="Markdown")

@app.route('/')
def home(): return "الرادار يعمل Live!"

if __name__ == "__main__":
    threading.Thread(target=analyze_market, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
