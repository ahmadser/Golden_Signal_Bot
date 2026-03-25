import pandas_ta as ta
import yfinance as yf
import requests
import time
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "رادار أبو جواد - فحص الاتصال"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# البيانات (تأكد من صحتها مرة أخيرة)
TOKEN = "8203171259:AAEHyC3hnxnbkIW8G3FxlWLDTyC6stiQSHY"
CHAT_ID = "8453156230"

def force_send(text):
    print(f"--- محاولة إرسال: {text} ---")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
        print(f"النتيجة من تلجرام: {r.text}")
        return r.json().get("ok")
    except Exception as e:
        print(f"خطأ أثناء الإرسال: {e}")
        return False

if __name__ == "__main__":
    keep_alive()
    time.sleep(5)
    
    # محاولة إرسال رسالة ترحيب قوية
    success = force_send("🚀 *منصة أبو جواد استيقظت!*\nإذا استلمت هذه الرسالة، فالاتصال سليم تماماً والخلل كان في السوق.")
    
    if not success:
        print("❌ فشل الإرسال.. يرجى التأكد من التوكن أو الشات آيدي")
    
    while True:
        # فحص بسيط للذهب فقط للتجربة
        try:
            gold = yf.download("GC=F", period="1d", interval="1m", progress=False)
            if not gold.empty:
                print("✅ تم جلب بيانات الذهب بنجاح.. النظام يعمل!")
        except:
            print("⚠️ مشكلة في جلب البيانات من ياهو")
        
        time.sleep(60)
