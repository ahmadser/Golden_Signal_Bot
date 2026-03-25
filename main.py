import pandas_ta as ta
import yfinance as yf
import requests
import time
import pandas as pd
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "منصة أبو جواد للبيناري تعمل!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

TOKEN = "8203171259:AAEHyC3hnxnbkIW8G3FxlWLDTyC6stiQSHY"
CHAT_ID = "8453156230"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&parse_mode=Markdown"
    try: requests.get(url, timeout=10)
    except: pass

def check_market():
    # قائمة الأزواج الأكثر سيولة للبيناري
    pairs = ["GC=F", "EURUSD=X", "GBPUSD=X", "JPY=X", "AUDUSD=X", "EURJPY=X", "GBPJPY=X"]
    
    for pair in pairs:
        try:
            time.sleep(2) # حماية من الحظر
            ticker = yf.Ticker(pair)
            # جلب بيانات دقيقة واحدة (1m) لتحليل البيناري السريع
            df = ticker.history(period="1d", interval="1m")
            
            if df.empty or len(df) < 30: continue
            
            # حساب المؤشرات
            bb = ta.bbands(df['Close'], length=20, std=2)
            stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3)
            rsi = ta.rsi(df['Close'], length=14)
            df = pd.concat([df, bb, stoch, rsi], axis=1)
            last = df.iloc[-1]

            # استخراج القيم
            price = round(float(last['Close']), 5)
            low_p, high_p = float(last['Low']), float(last['High'])
            bb_l, bb_u = float(last['BBL_20_2.0']), float(last['BBU_20_2.0'])
            stoch_k = float(last['STOCHk_14_3_3'])
            rsi_v = float(last['RSI_14'])

            # شروط الصعود (شراء)
            up_cond = [low_p <= bb_l, stoch_k < 20, rsi_v < 30]
            # شروط الهبوط (بيع)
            down_cond = [high_p >= bb_u, stoch_k > 80, rsi_v > 70]

            score_up = sum(up_cond)
            score_down = sum(down_cond)

            # تحديد نوع الفرصة
            label = ""
            if score_up == 3 or score_down == 3: label = "💎 *فرصة ذهبية*"
            elif score_up == 2 or score_down == 2: label = "🔥 *فرصة قوية*"
            elif score_up == 1 or score_down == 1: label = "⚡ *فرصة سريعة*"

            if score_up >= 1:
                msg = f"{label}\n\n💹 *الزوج:* `{pair}`\n🟢 *الاتجاه:* `شراء ⬆️` (CALL)\n💰 *السعر:* `{price}`\n⏱ *المدة:* `5 دقائق`\n\n✳️ *استعد للدخول الآن!*"
                send_telegram_msg(msg)
            elif score_down >= 1:
                msg = f"{label}\n\n💹 *الزوج:* `{pair}`\n🔴 *الاتجاه:* `بيع ⬇️` (PUT)\n💰 *السعر:* `{price}`\n⏱ *المدة:* `5 دقائق`\n\n✳️ *استعد للدخول الآن!*"
                send_telegram_msg(msg)

        except: continue

if __name__ == "__main__":
    keep_alive()
    send_telegram_msg("🛠 *تم تحديث المنصة:* رادار البيناري الاحترافي قيد التشغيل!")
    while True:
        check_market()
        time.sleep(60) # فحص كل دقيقة
