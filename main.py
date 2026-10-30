from flask import Flask
from threading import Thread
import yfinance as yf
import time
import requests
import os
from datetime import datetime
import pytz

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = "5563560146"
PAIRES = ["EURUSD=X","GBPUSD=X","EURJPY=X","EURGBP=X","AUDUSD=X"]

app = Flask('')
@app.route('/')
def home():
    return "Bot Mariette en ligne !"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

Thread(target=run).start()

def heure_autoriser():
    tz = pytz.timezone('Africa/Abidjan')
    maintenant = datetime.now(tz)
    h = maintenant.hour + maintenant.minute/60
    return (8 <= h < 12) or (14.5 <= h < 17)

def envoyer(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def analyser(paire):
    try:
        df = yf.download(paire, period="2d", interval="15m", progress=False)
        if len(df) < 30:
            return f"{paire}: pas assez de donnees"
        dernier = float(df['Close'].iloc[-1])
        avant = float(df['Close'].iloc[-2])
        if dernier > avant:
            return f"🟢 ACHAT {paire} {dernier:.5f}"
        else:
            return f"🔴 VENTE {paire} {dernier:.5f}"
    except Exception as e:
        return f"{paire}: erreur"

while True:
    if heure_autoriser():
        for paire in PAIRES:
            envoyer(analyser(paire))
            time.sleep(2)
        time.sleep(3600)
    else:
        time.sleep(300)
