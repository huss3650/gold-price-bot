import requests
from flask import Flask, request
import datetime

app = Flask(__name__)

BOT_TOKEN = "7968743622:AAGxoSf3Ij9a-fugA7QVmvkNjJ0-wRVNBFU"
GOLD_API_KEY = "goldapi-do7ibsm96atiml-io"
GOLD_API_URL = "https://www.goldapi.io/api/XAU/USD"
USD_TO_QAR = 3.65

subscribers = set()

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            subscribers.add(chat_id)
            send_message(chat_id, "💰 تم تسجيلك لاستلام أسعار الذهب مرتين يوميًا")
            send_menu(chat_id)
        elif "السعر الآن" in text:
            send_gold_price(chat_id)
        else:
            send_message(chat_id, "🟨 أرسل لي السعر الآن لمعرفة سعر الذهب الحالي.")
    return "OK"

def send_menu(chat_id):
    reply_markup = {
        "keyboard": [[{"text": "🟨 أرسل لي السعر الآن"}]],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": "اختر خيارًا من القائمة:",
            "reply_markup": reply_markup
        }
    )

def send_gold_price(chat_id):
    headers = {
        "x-access-token": GOLD_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.get(GOLD_API_URL, headers=headers)
    if response.status_code == 200:
        data = response.json()
        price_usd_24k = data.get("price_gram_24k", 0)
        price_usd_21k = data.get("price_gram_21k", 0)
        price_qar_24k = round(price_usd_24k * USD_TO_QAR, 2)
        price_qar_21k = round(price_usd_21k * USD_TO_QAR, 2)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        msg = f"📈 أسعار الذهب:

🔹 24K: {price_qar_24k} ريال قطري
🔸 21K: {price_qar_21k} ريال قطري

⏰ التاريخ: {now}"
        send_message(chat_id, msg)
    else:
        send_message(chat_id, "❌ تعذر الحصول على السعر. الرجاء المحاولة لاحقًا.")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route("/", methods=["GET"])
def index():
    return "Gold Price Bot is Running!"

if __name__ == "__main__":
    app.run(debug=True)
