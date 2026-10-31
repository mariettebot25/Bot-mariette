from flask import Flask
from threading import Thread
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
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        pass

def analyser(paire):
    try:
        # Nouvelle méthode qui marche sur Render (pas yfinance)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{paire}?interval=15m&range=2d"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, headers=headers, timeout=15)
        data = r.json()
        
        result = data['chart']['result'][0]
        closes = result['indicators']['quote'][0]['close']
        closes = [c for c in closes if c is not None]
        
        if len(closes) < 2:
            return f"{paire}: pas assez de donnees"
            
        dernier = float(closes[-1])
        avant = float(closes[-2])
        
        if dernier > avant:
            return f"🟢 ACHAT {paire} {dernier:.5f}"
        else:
            return f"🔴 VENTE {paire} {dernier:.5f}"
            
    except Exception as e:
        print(f"Erreur {paire}: {e}")
        return f"{paire}: erreur"

# Envoie un message de démarrage
envoyer("✅ Bot Mariette redémarré et prêt !")

while True:
    if heure_autoriser():
        for paire in PAIRES:
            envoyer(analyser(paire))
            time.sleep(2)
        time.sleep(3600) # attend 1h
    else:
        time.sleep(300) # attend 5 min hors horaires
