import yfinance as yf, time, requests
from datetime import datetime
import pytz

TOKEN = "8670091118:AAEGhBCpx4G4NEcWKUphp-YrGoHxa1KJ-3w"
CHAT_ID = "5563560146"
PAIRES = ["EURUSD=X", "GBPUSD=X", "EURJPY=X", "GBPJPY=X"]

def heure_autorisee():
    tz = pytz.timezone('Africa/Abidjan')
    now = datetime.now(tz)
    h = now.hour + now.minute/60.0
    return (8 <= h < 12) or (14.5 <= h < 19)

def envoyer(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except: pass

def analyse(paire):
    try:
        df = yf.download(paire, period="1d", interval="5m", progress=False)
        if len(df) < 30: return f"⚪ {paire.replace('=X','')}: Attente"
        close = df['Close']
        ema9 = close.ewm(span=9).mean().iloc[-1]
        ema21 = close.ewm(span=21).mean().iloc[-1]
        delta = close.diff()
        gain = delta.where(delta>0,0).rolling(14).mean().iloc[-1]
        loss = -delta.where(delta<0,0).rolling(14).mean().iloc[-1]
        rsi = 100 - (100/(1+ (gain/loss if loss!=0 else 1)))
        nom = paire.replace('=X','')
        if rsi < 40 and ema9 > ema21:
            return f"🟢 ACHAT {nom} | 2-3min | RSI {rsi:.0f}"
        elif rsi > 60 and ema9 < ema21:
            return f"🔴 VENTE {nom} | 2-3min | RSI {rsi:.0f}"
        else:
            return f"⚪ {nom}: Pas de signal - RSI {rsi:.0f}"
    except: return f"⚪ {paire}: erreur"

envoyer("✅ Bot Mariette lance ! Signaux toutes les 10min 08h-12h et 14h30-19h Abidjan")

while True:
    if heure_autorisee():
        tz = pytz.timezone('Africa/Abidjan')
        heure = datetime.now(tz).strftime('%H:%M')
        msg = f"📊 Signaux {heure} Abidjan\n\n"
        for p in PAIRES:
            msg += analyse(p) + "\n"
        envoyer(msg)
        time.sleep(600)
    else:
        time.sleep(300)
