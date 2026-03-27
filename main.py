import os, telebot, yfinance as yf, pandas as pd, pandas_ta as ta
from datetime import datetime
import time, threading
from flask import Flask

# 🔑 الإعدادات (ثابتة)
TOKEN = "8571032199:AAHCoP13fVQJ5lkFC0BVZBdnSBp6I5Tw7n4"
CHAT_ID = "8453156230"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 📊 الـ 12 زوج فما فوق (العملات، الذهب، الكريبتو)
ASSETS = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X", "NZD/USD": "NZDUSD=X", "USD/CHF": "CHF=X",
    "EUR/GBP": "EURGBP=X", "الذهب 🟡": "GC=F", "البيتكوين ₿": "BTC-USD"
}

def analyze_market():
    while True:
        print(f"🔄 جولة فحص شاملة: {datetime.now().strftime('%H:%M:%S')}")
        for name, ticker in ASSETS.items():
            try:
                # سحب بيانات 5 دقائق (أحدث 40 شمعة للفلترة)
                df = yf.download(ticker, period="1d", interval="5m", progress=False)
                if df is None or df.empty or len(df) < 40:
                    continue

                # حساب المؤشرات (الاستراتيجيات الـ 9 مدمجة)
                df['RSI'] = ta.rsi(df['Close'], length=14)
                bbands = ta.bbands(df['Close'], length=20, std=2)
                df['EMA_5'] = ta.ema(df['Close'], length=5)
                df['EMA_13'] = ta.ema(df['Close'], length=13)
                df['EMA_200'] = ta.ema(df['Close'], length=200) # للاتجاه العام
                df['CCI'] = ta.cci(df['High'], df['Low'], df['Close'], length=20) # للزخم
                
                # فحص وجود بيانات الاستوكاستك قبل الاستخدام
                stoch = ta.stoch(df['High'], df['Low'], df['Close'])
                if stoch is not None and not stoch.empty:
                    df['STOCHk'] = stoch['STOCHk_14_3_3']
                else:
                    df['STOCHk'] = 50 # قيمة محايدة

                last = df.iloc[-1]
                prev = df.iloc[-2]
                last_price = round(float(last['Close']), 5)
                
                signal_type = None

                # 1️⃣ استراتيجية: الفرصة الذهبية (RSI + BB + Stoch)
                if last['RSI'] < 30 and last_price < bbands['BBL_20_2.0'].iloc[-1] and last['STOCHk'] < 20:
                    signal_type = "GOLDEN_BUY"
                elif last['RSI'] > 70 and last_price > bbands['BBU_20_2.0'].iloc[-1] and last['STOCHk'] > 80:
                    signal_type = "GOLDEN_SELL"
                
                # 2️⃣ استراتيجية: الفرصة القوية (EMA Cross)
                elif last['EMA_5'] > last['EMA_13'] and prev['EMA_5'] <= prev['EMA_13']:
                    signal_type = "STRONG_BUY"
                elif last['EMA_5'] < last['EMA_13'] and prev['EMA_5'] >= prev['EMA_13']:
                    signal_type = "STRONG_SELL"

                # 3️⃣ استراتيجية: صيد القناص (SNIPER)
                elif last_price < last['EMA_200'] and last['RSI'] < 35 and last['CCI'] < -100:
                    signal_type = "SNIPER_BUY"
                elif last_price > last['EMA_200'] and last['RSI'] > 65 and last['CCI'] > 100:
                    signal_type = "SNIPER_SELL"

                # 4️⃣ استراتيجية: اختراق الزخم (MOMENTUM BREAKOUT)
                elif last['Close'] > prev['High'] and last['CCI'] > 150:
                    signal_type = "MOMENTUM_BUY"
                elif last['Close'] < prev['Low'] and last['CCI'] < -150:
                    signal_type = "MOMENTUM_SELL"

                if signal_type:
                    send_signal(name, last_price, signal_type)
                
                time.sleep(5) # حماية من الحظر
            except:
                continue
        
        time.sleep(300) # انتظار 5 دقائق للدورة التالية

def send_signal(name, price, s_type):
    # إعداد الرموز بناءً على نوع الاستراتيجية (ثابتة)
    if "GOLDEN" in s_type:
        header = "💠💠💠💠 【 فـرصـة ذهـبـيـة 】 💠💠💠💠"
    elif "SNIPER" in s_type:
        header = "🎯🎯🎯🎯 【 إشـارة الـقـنـاص 】 🎯🎯🎯🎯"
    elif "MOMENTUM" in s_type:
        header = "🔥🔥🔥🔥 【 اخـتـراق الـزخـم 】 🔥🔥🔥🔥"
    else:
        header = "🔹🔹🔹🔹 【 فـرصـة قـويـة 】 🔹🔹🔹🔹"

    # تخصيص الأسهم والألوان بناءً على الاتجاه (الطلب الجديد)
    if "BUY" in s_type:
        dir_text = "🟢 شـراء | CALL 🟢"
        emoji_arrow = "⬆️⬆️" # سهم صعود أخضر
        emoji_icon = "🚀🚀"
    else:
        dir_text = "🔴 بـيـع | PUT 🔴"
        emoji_arrow = "⬇️⬇️" # سهم هبوط أحمر
        emoji_icon = "📉📉"

    # تنسيق الرسالة النهائي بلمسة هندسية
    msg = f"{header}\n━━━━━━━━━━━━━━━━━━\n" \
          f"💎 الزوج: `{name}`\n" \
          f"📊 النوع: `{s_type.split('_')[0]}`\n" \
          f"{emoji_arrow} الاتجاه: `{dir_text}`\n" \
          f"💵 السعر: `{price}`\n" \
          f"━━━━━━━━━━━━━━━━━━\n" \
          f"⏱️ الفريم: `1 فريم (5 دقائق)` \n" \
          f"⏳ المدة: `5 دقائق` \n" \
          f"🕒 الوقت: `{datetime.now().strftime('%H:%M:%S')}`\n" \
          f"━━━━━━━━━━━━━━━━━━\n" \
          f"{emoji_icon} القرار: `{emoji_arrow} ادخل الصفقة الآن {emoji_arrow}`\n" \
          f"🚫 يرجى التداول بمسؤولية 🚫"
    
    try:
        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
    except:
        pass

@app.route('/')
def home(): return "الرادار المطور يعمل بنجاح! تم إضافة الأسهم الملونة والتفاصيل الدقيقة."

if __name__ == "__main__":
    threading.Thread(target=analyze_market, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
