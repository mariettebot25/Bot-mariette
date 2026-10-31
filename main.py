from flask import Flask
from threading import Thread
import time, requests, os

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = "5563560146"
# 8 paires au total
PAIRES = ["EURUSD=X","GBPUSD=X","EURJPY=X","EURGBP=X","AUDUSD=X","USDJPY=X","GBPJPY=X","BTC-USD"]

app = Flask('')
@app.route('/')
def home(): return "Bot 1min Mariette 8 paires ON"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
Thread(target=run).start()

def envoyer(msg):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

def analyser_1min(paire):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{paire}?interval=1m&range=1d"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15).json()
        closes = r['chart']['result'][0]['indicators']['quote'][0]['close']
        closes = [c for c in closes if c is not None]
        if len(closes) < 50: return None

        def ema(data, p):
            k = 2/(p+1); e = data[0]
            for c in data[1:]: e = c*k + e*(1-k)
            return e
        ema9 = ema(closes[-21:], 9)
        ema21 = ema(closes[-21:], 21)

        gains = pertes = 0
        for i in range(1, 15):
            d = closes[-i] - closes[-i-1]
            if d > 0: gains += d
            else: pertes += abs(d)
        rsi = 100 - (100/(1+gains/pertes)) if pertes !=0 else 70

        dernier = closes[-1]; avant = closes[-2]
        nom = paire.replace("=X","").replace("-USD","/USD")

        # Si marché BON -> on envoie
        if ema9 > ema21 and rsi > 50 and rsi < 70 and dernier > avant:
            return f"🟢 ACHAT {nom}\n⏰ 1 MINUTE\n📈 Marché BON - EMA9>EMA21 RSI {rsi:.0f}\n👉 ENTRE MAINTENANT"

        if ema9 < ema21 and rsi < 50 and rsi > 30 and dernier < avant:
            return f"🔴 VENTE {nom}\n⏰ 1 MINUTE\n📉 Marché BON - EMA9<EMA21 RSI {rsi:.0f}\n👉 ENTRE MAINTENANT"
        
        return None
    except: return None

envoyer("✅ BOT 8 PAIRES LANCÉ (1 MIN)\nEURUSD, GBPUSD, EURJPY, EURGBP, AUDUSD, USDJPY, GBPJPY, BTC\nJe t'envoie un signal dès que UNE paire est bonne.")

while True:
    for paire in PAIRES:
        sig = analyser_1min(paire)
        if sig:
            envoyer(sig)
            time.sleep(1)
    time.sleep(30)
