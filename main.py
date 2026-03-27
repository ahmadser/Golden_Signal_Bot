import os, telebot, yfinance as yf, pandas as pd, pandas_ta as ta
from datetime import datetime
import time, threading
from flask import Flask

# 🔑 الإعدادات (ثابتة ومؤكدة)
TOKEN = "8571032199:AAHCoP13fVQJ5lkFC0BVZBdnSBp6I5Tw7n4"
CHAT_ID = "8453156230"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 📊 القائمة الذهبية (تم اختيارها لضمان عدم الحظر)
ASSETS = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "الذهب 🟡": "GC=F",
    "البيتكوين ₿": "BTC-USD", "USD/JPY": "JPY=X", "EUR/JPY": "EURJPY=X"
}

def analyze_market():
    while True:
        current_hour = datetime.now().hour
        print(f"🔄 فحص النشاط: {datetime.now().strftime('%H:%M:%S')}")
        
        for name, ticker in ASSETS.items():
            try:
                # سحب البيانات مع مهلة زمنية (Timeout) لتجنب التعليق
                df = yf.download(ticker, period="1d", interval="5m", progress=False, timeout=10)
                
                if df is None or df.empty or len(df) < 35:
                    continue

                # حساب الاستراتيجيات (تم تبسيط الحساب لسرعة الاستجابة)
                df['RSI'] = ta.rsi(df['Close'], length=14)
                bbands = ta.bbands(df['Close'], length=20, std=2)
                df['EMA_200'] = ta.ema(df['Close'], length=200)
                df['CCI'] = ta.cci(df['High'], df['Low'], df['Close'], length=20)
                
                last = df.iloc[-1]
                prev = df.iloc[-2]
                price = round(float(last['Close']), 5)
                
                signal = None

                # 💠 الاستراتيجيات (تم دمج الحساسية العالية)
                if last['RSI'] < 32 and price < bbands['BBL_20_2.0'].iloc[-1]: signal = "GOLDEN_BUY"
                elif last['RSI'] > 68 and price > bbands['BBU_20_2.0'].iloc[-1]: signal = "GOLDEN_SELL"
                elif price < last['EMA_200'] and last['RSI'] < 38: signal = "SNIPER_BUY"
                elif price > last['EMA_200'] and last['RSI'] > 62: signal = "SNIPER_SELL"
                elif last['CCI'] > 120: signal = "MOMENTUM_BUY"
                elif last['CCI'] < -120: signal = "MOMENTUM_SELL"

                if signal:
                    send_formatted_signal(name, price, signal)
                
                time.sleep(12) # فواصل زمنية مدروسة لمنع الحظر
            except Exception as e:
                print(f"⚠️ تنبيه: تعذر فحص {name} حالياً، سينتقل للتالي.")
                time.sleep(5)
                continue
        
        time.sleep(180) # العودة للفحص كل 3 دقائق لضمان الاستمرارية

def send_formatted_signal(name, price, s_type):
    # إعداد الرموز والألوان (الطلب السابق لأبو جواد)
    is_buy = "BUY" in s_type
    arrow = "⬆️⬆️" if is_buy else "⬇️⬇️"
    header = "🎯 【 إشـارة جـديـدة 】 🎯"
    dir_text = "🟢 شـراء | CALL" if is_buy else "🔴 بـيـع | PUT"
    
    msg = f"{header}\n━━━━━━━━━━━━━━\n" \
          f"💎 الزوج: `{name}`\n" \
          f"📊 النوع: `{s_type.split('_')[0]}`\n" \
          f"📈 الاتجاه: {dir_text} {arrow}\n" \
          f"💵 السعر: `{price}`\n" \
          f"━━━━━━━━━━━━━━\n" \
          f"⏱️ الفريم: `5 دقائق`\n" \
          f"⏳ المدة: `5 دقائق`\n" \
          f"🕒 الوقت: `{datetime.now().strftime('%H:%M')}`\n" \
          f"━━━━━━━━━━━━━━\n" \
          f"🚀 {arrow} ادخل الصفقة الآن {arrow} 🚀"
    
    try:
        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
    except: pass

@app.route('/')
def home(): return "الرادار يعمل بنظام إعادة التشغيل التلقائي!"

if __name__ == "__main__":
    # رسالة تنبيه عند إعادة التشغيل
    try: bot.send_message(CHAT_ID, "🔄 **تم إعادة تشغيل الرادار تلقائياً بنجاح!**\nجاري استئناف الصيد...")
    except: pass
    
    threading.Thread(target=analyze_market, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
