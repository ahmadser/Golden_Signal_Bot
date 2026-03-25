import os
import telebot
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import time
import threading
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
        print(f"🔄 دورة تحليل جديدة بدأت في {datetime.now().strftime('%H:%M:%S')}")
        for name, ticker in ASSETS.items():
            try:
                # سحب البيانات لفريم 5 دقائق
                df = yf.download(ticker, period="1d", interval="5m", progress=False)
                if df is None or df.empty or len(df) < 30:
                    continue

                # حساب المؤشرات الفنية (الاستراتيجيات الست)
                df['RSI'] = ta.rsi(df['Close'], length=14)
                bbands = ta.bbands(df['Close'], length=20, std=2)
                df['EMA_5'] = ta.ema(df['Close'], length=5)
                df['EMA_13'] = ta.ema(df['Close'], length=13)
                stoch = ta.stoch(df['High'], df['Low'], df['Close'])
                
                # التحقق من وجود بيانات الاستوكاستك
                if stoch is not None:
                    df['STOCHk'] = stoch['STOCHk_14_3_3']
                else:
                    df['STOCHk'] = 50 # قيمة محايدة إذا فشل الحساب

                last = df.iloc[-1]
                prev = df.iloc[-2]
                last_price = round(float(last['Close']), 5)
                
                signal_type = None
                
                # 🟡 1. منطق الفرصة الذهبية (RSI + Bollinger + Stochastic)
                if last['RSI'] < 30 and last_price < bbands['BBL_20_2.0'].iloc[-1] and last['STOCHk'] < 20:
                    signal_type = "GOLDEN_BUY"
                elif last['RSI'] > 70 and last_price > bbands['BBU_20_2.0'].iloc[-1] and last['STOCHk'] > 80:
                    signal_type = "GOLDEN_SELL"
                
                # 🔵 2. منطق الفرصة القوية (EMA Cross + Trend)
                elif last['EMA_5'] > last['EMA_13'] and prev['EMA_5'] <= prev['EMA_13']:
                    signal_type = "STRONG_BUY"
                elif last['EMA_5'] < last['EMA_13'] and prev['EMA_5'] >= prev['EMA_13']:
                    signal_type = "STRONG_SELL"

                if signal_type:
                    send_signal(name, last_price, signal_type)
                
                # حماية من الحظر (تأخير 5 ثوانٍ بين كل عملة)
                time.sleep(5)
            except Exception as e:
                print(f"⚠️ خطأ في {name}: {e}")
                continue
        
        # انتظار 5 دقائق للدورة القادمة
        time.sleep(300)

def send_signal(name, price, s_type):
    # تحديد التنسيق الجمالي والألوان
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
def home():
    return "الرادار يعمل بكفاءة Live!"

if __name__ == "__main__":
    # تشغيل التحليل في خيط منفصل لضمان استمرار السيرفر
    threading.Thread(target=analyze_market, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
