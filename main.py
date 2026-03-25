import pandas_ta as ta
import yfinance as yf
import requests
import time
import pandas as pd
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "رادار أبو جواد - وضع الأمان مفعل"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

TOKEN = "8203171259:AAEHyC3hnxnbkIW8G3FxlWLDTyC6stiQSHY"
CHAT_ID = "8453156230"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def check_market():
    # تقليل القائمة لضمان عدم الحظر (الذهب + أهم 4 عملات)
    pairs = ["GC=F", "EURUSD=X", "GBPUSD=X", "JPY=X", "GBPJPY=X"]
    
    for pair in pairs:
        try:
            # زيادة الفاصل الزمني بين كل عملة وأخرى لـ 5 ثوانٍ (للأمان القصوى)
            time.sleep(5) 
            
            # جلب البيانات
            ticker = yf.Ticker(pair)
            df = ticker.history(period="1d", interval="1m")
            
            if df.empty or len(df) < 20: continue
            
            # حساب المؤشرات
            bb = ta.bbands(df['Close'], length=20, std=2)
            stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3)
            rsi = ta.rsi(df['Close'], length=14)
            df = pd.concat([df, bb, stoch, rsi], axis=1)
            last = df.iloc[-1]

            price = round(float(last['Close']), 5)
            bb_l, bb_u = float(last['BBL_20_2.0']), float(last['BBU_20_2.0'])
            stoch_k = float(last['STOCHk_14_3_3'])
            rsi_v = float(last['RSI_14'])

            # شروط الخيارات الثنائية القوية
            if price <= bb_l and stoch_k < 20 and rsi_v < 35:
                send_telegram_msg(f"💎 *فرصة ذهبية (شراء) ⬆️*\n💹 `{pair}`\n💰 السعر: `{price}`\n⏱ المدة: `5 دقائق`")
            elif price >= bb_u and stoch_k > 80 and rsi_v > 65:
                send_telegram_msg(f"💎 *فرصة ذهبية (بيع) ⬇️*\n💹 `{pair}`\n💰 السعر: `{price}`\n⏱ المدة: `5 دقائق`")

        except Exception as e:
            print(f"Error in {pair}: {e}")
            continue

if __name__ == "__main__":
    keep_alive()
    # رسالة فورية للتأكد من التلجرام
    send_telegram_msg("🚀 *تم تفعيل وضع الأمان القصوى!*\nجاري فحص الذهب والعملات الرئيسية الآن...")
    while True:
        check_market()
        time.sleep(120) # فحص كل دقيقتين لضمان عدم الحظر مجدداً
