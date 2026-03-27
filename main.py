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

# 📊 الـ 12 زوج (العملات، الذهب، الكريبتو)
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
                df = yf.download(ticker, period="1d", interval="5m", progress=False)
                if df is None or df.empty or len(df) < 40:
                    continue

                # --- الاستراتيجيات القديمة (محفوظة بالكامل) ---
                df['RSI'] = ta.rsi(df['Close'], length=14)
                bbands = ta.bbands(df['Close'], length=20, std=2)
                df['EMA_5'] = ta.ema(df['Close'], length=5)
                df['EMA_13'] = ta.ema(df['Close'], length=13)
                stoch = ta.stoch(df['High'], df['Low'], df['Close'])
                df['STOCHk'] = stoch['STOCHk_14_3_3'] if stoch is not None else 50
                
                # --- الاستراتيجيات الجديدة المضافة (أبو جواد V2) ---
                df['EMA_200'] = ta.ema(df['Close'], length=200) # للاتجاه العام
                df['CCI'] = ta.cci(df['High'], df['Low'], df['Close'], length=20) # للزخم
                df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14) # للتذبذب

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

                # 3️⃣ استراتيجية: صيد القناص (SNIPER - الارتداد من المتوسط)
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
                
                time.sleep(3) # تسريع الفحص قليلاً
            except Exception as e:
                continue
        
        time.sleep(300)

def send_signal(name, price, s_type):
    # تخصيص المظهر حسب الاستراتيجية
    if "GOLDEN" in s_type:
        header, icon, emoji = "💠 【 فـرصـة ذهـبـيـة 】 💠", "⭐", "🚀"
    elif "SNIPER" in s_type:
        header, icon, emoji = "🎯 【 إشـارة الـقـنـاص 】 🎯", "🏹", "🔭"
    elif "MOMENTUM" in s_type:
        header, icon, emoji = "🔥 【 اخـتـراق الـزخـم 】 🔥", "⚡", "🌪️"
    else:
        header, icon, emoji = "🔹 【 فـرصـة قـويـة 】 🔹", "⚡", "📈"

    direction = "شـراء | UP ⬆️" if "BUY" in s_type else "بـيـع | DOWN ⬇️"
    action = "🟢 صعود (CALL)" if "BUY" in s_type else "🔴 هبوط (PUT)"

    msg = f"{header}\n━━━━━━━━━━━━━━\n" \
          f"💎 **الزوج:** `{name}`\n" \
          f"📊 **النوع:** `{s_type.split('_')[0]}`\n" \
          f"📈 **الاتجاه:** {direction}\n" \
          f"💵 **السعر:** `{price}`\n" \
          f"━━━━━━━━━━━━━━\n" \
          f"{emoji} **القرار:** {action}\n" \
          f"{icon} **ادخل الآن (5 دقائق)**"
    
    try:
        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
    except:
        pass

@app.route('/')
def home():
    return "الرادار المطور يعمل بنجاح! تم إضافة استراتيجيات القناص والزخم."

if __name__ == "__main__":
    try:
        bot.send_message(CHAT_ID, "✅ **تم تحديث الرادار بنجاح!**\nالآن أراقب بـ 9 استراتيجيات (ذهبية، قناص، زخم، وقوية).")
    except:
        pass
    threading.Thread(target=analyze_market, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
