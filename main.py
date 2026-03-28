import os, telebot, yfinance as yf, pandas as pd, pandas_ta as ta
from datetime import datetime
import time, threading
from flask import Flask

# 🔑 الإعدادات المؤكدة لـ "أبو جواد"
TOKEN = "8571032199:AAHCoP13fVQJ5lkFC0BVZBdnSBp6I5Tw7n4"
CHAT_ID = "8453156230"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 📊 الأصول (التركيز على البيتكوين اليوم السبت لأن السوق مغلق)
ASSETS = {
    "البيتكوين ₿": "BTC-USD",
    "إيثيريوم 💠": "ETH-USD",
    "سولانا ☀️": "SOL-USD",
    "الذهب 🟡": "GC=F",
    "EUR/USD": "EURUSD=X"
}

def analyze_market():
    while True:
        print(f"🔄 جولة فحص رادار أبو جواد: {datetime.now().strftime('%H:%M:%S')}")
        for name, ticker in ASSETS.items():
            try:
                # سحب بيانات 5 دقائق (أحدث 50 شمعة)
                df = yf.download(ticker, period="1d", interval="5m", progress=False, timeout=15)
                if df.empty or len(df) < 35: continue

                # حساب المؤشرات بدقة عالية
                df['RSI'] = ta.rsi(df['Close'], length=14)
                bbands = ta.bbands(df['Close'], length=20, std=2)
                df['EMA_200'] = ta.ema(df['Close'], length=200)
                df['CCI'] = ta.cci(df['High'], df['Low'], df['Close'], length=20)
                
                last = df.iloc[-1]
                price = round(float(last['Close']), 2 if "USD" in ticker else 5)
                signal = None

                # 💠 استراتيجيات الصيد (حساسية مطورة)
                # 1. الفرصة الذهبية
                if last['RSI'] < 31 and price < bbands['BBL_20_2.0'].iloc[-1]: signal = "GOLDEN_BUY"
                elif last['RSI'] > 69 and price > bbands['BBU_20_2.0'].iloc[-1]: signal = "GOLDEN_SELL"
                # 2. صيد القناص
                elif price < last['EMA_200'] and last['RSI'] < 36: signal = "SNIPER_BUY"
                elif price > last['EMA_200'] and last['RSI'] > 64: signal = "SNIPER_SELL"
                # 3. زخم السوق
                elif last['CCI'] > 110: signal = "MOMENTUM_BUY"
                elif last['CCI'] < -110: signal = "MOMENTUM_SELL"

                if signal:
                    send_signal(name, price, signal)
                
                time.sleep(15) # مهلة زمنية لمنع حظر ياهو فاينانس
            except: continue
        time.sleep(120) # فحص كل دقيقتين

def send_signal(name, price, s_type):
    is_buy = "BUY" in s_type
    arrow = "⬆️⬆️" if is_buy else "⬇️⬇️"
    color = "🟢" if is_buy else "🔴"
    action = "شـــــراء | CALL" if is_buy else "بـــيـــــع | PUT"
    
    # 📋 التنسيق الاحترافي المعتمد
    msg = (
        f"📍 **تنبيه الرادار الذكي**\n"
        f"━━━━━━━━━━━━━━\n"
        f"💎 **الزوج:** `{name}`\n"
        f"📊 **الاستراتيجية:** `{s_type.split('_')[0]}`\n"
        f"━━━━━━━━━━━━━━\n"
        f"{color} **الاتجاه:** `{action}`\n"
        f"{arrow} **القرار:** `{arrow} ادخل الآن {arrow}`\n"
        f"━━━━━━━━━━━━━━\n"
        f"💵 **السعر:** `{price}`\n"
        f"⏱️ **الفريم:** `5 دقائق`\n"
        f"⏳ **المدة:** `5 دقائق`\n"
        f"━━━━━━━━━━━━━━\n"
        f"📡 `{datetime.now().strftime('%H:%M:%S')}`"
    )
    try: bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
    except: pass

@app.route('/')
def home():
    # عند فتح الرابط سيرسل رسالة تجربة فوراً لتلجرام للتأكد من الاتصال
    try:
        bot.send_message(CHAT_ID, "✅ **تم تفعيل الرادار بنجاح!**\nالاتصال مستقر وجاري مراقبة البيتكوين والعملات الرقمية الآن.")
        return "الرادار يعمل! تحقق من تلجرام، لقد أرسلت لك رسالة اختبار."
    except Exception as e:
        return f"الرادار يعمل ولكن هناك خطأ في التلجرام: {e}"

if __name__ == "__main__":
    threading.Thread(target=analyze_market, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
