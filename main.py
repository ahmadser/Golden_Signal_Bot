import requests
import time
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "بوت الاختبار يعمل!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# بيانات التلجرام
TOKEN = "8203171259:AAEHyC3hnxnbkIW8G3FxlWLDTyC6stiQSHY"
CHAT_ID = "8453156230"

def test_msg():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": "🔔 رسالة اختبار: إذا رأيت هذه الرسالة فالبوت سليم والربط ناجح 100%!"}
    try:
        r = requests.post(url, json=payload)
        print(f"Telegram response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    keep_alive()
    # إرسال رسالة فورية عند التشغيل للاختبار
    time.sleep(5)
    test_msg()
    while True:
        time.sleep(60)
