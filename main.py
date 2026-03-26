import os
import telebot
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import time
import threading
from flask import Flask

# 🔑 الإعدادات الأساسية (تأكد من صحة التوكن والـ ID)
TOKEN = "8571032199:AAHCoP13fVQJ5lkFC0BVZBdnSBp6I5Tw7n4"
CHAT_ID = "8453156230"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 📊 الـ 12 زوج عملات (تم اختيارها بعناية لسيولة عالية)
ASSETS = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X", "NZD/USD": "NZDUSD=X", "USD/CHF": "CHF=X",
    "EUR/GBP": "EURGBP=X", "الذهب 🟡": "GC=F", "البيتكوين ₿": "BTC-USD"
}

def analyze_market():
    """وظيفة المراقبة والتحليل المستمر"""
    while True:
        print(f"🔄 جولة فحص جديدة: {datetime.now().strftime('%H:%M:%S')}")
        for name, ticker in ASSETS.items():
            try:
                # سحب بيانات 5 دقائق (أحدث 100 شمعة للفلترة)
                df = yf.download(ticker, period="1d", interval="5m", progress=False)
                if df is None or df.empty or len(df) < 30:
                    continue

                # حساب المؤشرات (الاستراتيجيات الست المدمجة)
                df['RSI'] = ta.rsi(df['Close'], length=14)
                bbands = ta.bbands(df['Close'], length=20, std=2)
                df['EMA_5'] = ta.ema(df['Close'], length=5)
                df['EMA_13'] = ta.ema(df['Close'], length=13)
                stoch = ta.stoch(df['High'], df['Low'], df['Close'])
                
                # معالجة بيانات الاستوكاستك بحذر
                if stoch is not None and not stoch.empty:
                    df['STOCHk'] = stoch['STOCHk_14_3_3']
                else:
                    df['STOCHk'] = 50 

                last = df.iloc[-1]
                prev = df.iloc[-2]
                last_price = round(float(last['Close']), 5)
                
                signal_type = None
                
                # 🟡 1. منطق الفرصة الذهبية (RSI + Bollinger + Stochastic)
                # شراء ذهبي: RSI تحت 30 + سعر تحت البولنجر السفلي + استوكاستك تحت 20
                if last['RSI'] < 30 and last_price < bbands['BBL_20_2.0'].iloc[-1] and last['STOCHk'] < 20:
                    signal_type = "GOLDEN_BUY"
                # بيع ذهبي: RSI فوق 70 + سعر فوق البولنجر العلوي + استوكاستك فوق 80
                elif last['RSI'] > 70 and last_price > bbands['BBU_20_2.0'].iloc[-1] and last['STOCHk'] > 80:
                    signal_type = "GOLDEN_SELL"
                
                # 🔵 2. منطق الفرصة القوية (تقاطع المتوسطات EMA 5/13)
                elif last['EMA_5'] > last['EMA_13'] and prev['EMA_5'] <= prev['EMA_13']:
                    signal_type = "STRONG_BUY"
                elif last['EMA_5'] < last['EMA_13'] and prev['EMA_5'] >= prev['EMA_13']:
                    signal_type = "STRONG_SELL"

                # إرسال التنبيه إذا تحققت الشروط
                if signal_type:
                    send_signal(name, last_price, signal_type)
                
                # تأخير 5 ثوانٍ بين العملات لحماية الـ IP
                time.sleep(5)
            except Exception as e:
                print(f"⚠️ خطأ في تحليل {name}: {e}")
                continue
        
        # انتظار 5 دقائق للدورة التالية
        time.sleep(300)

def send_signal(name, price, s_type):
    """تنسيق وإرسال الرسالة الجمالية للتلقرام"""
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
    
    try:
        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
        print(f"✅ تم إرسال إشارة لـ {name}")
    except Exception as e:
        print(f"❌ خطأ في إرسال التلجرام: {e}")

@app.route('/')
def home():
    return "الرادار يعمل بكفاءة Live! صيداً موفقاً يا أبو جواد."

if __name__ == "__main__":
    # 1. إرسال رسالة ترحيب فورية للتأكد من الربط
    try:
        bot.send_message(CHAT_ID, "🚀 **رادار أبو جواد انطلق!**\nجاري مراقبة الأسواق الآن بـ 6 استراتيجيات قوية.")
        print("✅ رسالة الترحيب أرسلت بنجاح.")
    except Exception as e:
        print(f"❌ خطأ في رسالة الترحيب: {e}")

    # 2. بدء خيط التحليل الفني
    threading.Thread(target=analyze_market, daemon=True).start()
    
    # 3. تشغيل سيرفر الويب (Flask)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
