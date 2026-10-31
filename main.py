from flask import Flask
from threading import Thread
import time, requests, os

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = "5563560146"
PAIRES = ["EURUSD=X","GBPUSD=X","EURJPY=X","EURGBP=X","AUDUSD=X","USDJPY=X","GBPJPY=X","BTC-USD"]

app = Flask('')
@app.route('/')
def home(): return "Bot Mariette FINAL OK"
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
            k=2/(p+1); e=data[0]
            for c in data[1:]: e=c*k+e*(1-k)
            return e
        ema9=ema(closes[-21:],9); ema21=ema(closes[-21:],21)
        gains=pertes=0
        for i in range(1,15):
            d=closes[-i]-closes[-i-1]
            if d>0: gains+=d
            else: pertes+=abs(d)
        rsi = 70 if pertes==0 else 100-(100/(1+gains/pertes))
        dernier=closes[-1]; avant=closes[-2]
        nom=paire.replace("=X","").replace("-USD","/USD")
        # PLUS STRICT pour éviter spam
        if ema9 > ema21 and 55 < rsi < 68 and dernier > avant:
            return f"🟢 ACHAT {nom}\n⏰ 1 MINUTE\n📈 RSI {rsi:.0f} -> ENTRE"
        if ema9 < ema21 and 32 < rsi < 45 and dernier < avant:
            return f"🔴 VENTE {nom}\n⏰ 1 MINUTE\n📉 RSI {rsi:.0f} -> ENTRE"
        return None
    except: return None

envoyer("✅ BOT REGLÉ ANTI-SPAM 10 MIN\nMaintenant 1 signal max / 10min par paire")

dernier_signal={}
while True:
    for paire in PAIRES:
        sig=analyser_1min(paire)
        if sig:
            if paire not in dernier_signal or time.time()-dernier_signal[paire] > 600: # 10 minutes
                envoyer(sig)
                dernier_signal[paire]=time.time()
                break # on envoie 1 seul puis on attend 1 min
        time.sleep(1)
    time.sleep(60)
