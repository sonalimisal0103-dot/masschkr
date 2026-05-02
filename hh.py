import time
import threading

def keep_alive():
    def run():
        while True:
            print("Bot is Alive... 💀")
            time.sleep(60)  # Keeps the bot alive on some hosts
    threading.Thread(target=run, daemon=True).start()
