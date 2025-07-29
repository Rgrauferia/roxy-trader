# Roxy Trader™ – Versión Compacta para ejecución directa desde iPad o Google Colab

import requests, time, hmac, hashlib, json, websocket, threading
from datetime import datetime
import alpaca_trade_api as alpaca

# === CONFIGURACIÓN ===
DERIV_API_TOKEN = 'YOUR_DERIV_TOKEN_HERE'
DERIV_APP_ID = '1089'  # Default app ID para cuentas normales
ALPACA_KEY = 'YOUR_ALPACA_KEY_HERE'
ALPACA_SECRET = 'YOUR_ALPACA_SECRET_HERE'
ALPACA_PAPER = False  # False = Live trading

WHATSAPP_ALERTS = True
EMAIL_ALERTS = True

CAPITAL_TOTAL = 50
REINVERSION_PORCENTAJE = 0.30
RIESGO = 'medio'

# === ALPACA SETUP ===
alpaca_base_url = 'https://paper-api.alpaca.markets' if ALPACA_PAPER else 'https://api.alpaca.markets'
alpaca_api = alpaca.REST(ALPACA_KEY, ALPACA_SECRET, alpaca_base_url, api_version='v2')

# === FUNCIONES UTILITARIAS ===

def alerta(msg):
    print(f"[ALERTA] {msg}")
    if WHATSAPP_ALERTS:
        print(f"[WhatsApp] {msg}")
    if EMAIL_ALERTS:
        print(f"[Correo] {msg}")

def operar_alpaca_simbolo(symbol='BTC/USD'):
    try:
        print(f"⏳ Consultando {symbol} en Alpaca...")
        barset = alpaca_api.get_barset(symbol.replace('/', ''), '5Min', limit=5)
        bars = barset[symbol.replace('/', '')]
        if len(bars) < 5: return

        prices = [bar.c for bar in bars]
        tendencia = "subiendo" if prices[-1] > prices[0] else "bajando"
        qty = round((CAPITAL_TOTAL * 0.1) / prices[-1], 5)

        if tendencia == "subiendo":
            alpaca_api.submit_order(symbol=symbol.replace('/', ''), qty=qty, side='buy', type='market', time_in_force='gtc')
            alerta(f"✅ Roxy compró {qty} de {symbol} (tendencia: {tendencia})")
        else:
            alerta(f"❌ Roxy no operó {symbol} por tendencia bajista.")
    except Exception as e:
        alerta(f"Error Alpaca: {e}")

# === DERIV – Conexión vía WebSocket ===

def operar_deriv():
    def on_message(ws, message):
        msg = json.loads(message)
        if 'msg_type' in msg and msg['msg_type'] == 'authorize':
            contrato = {
                "ticks": "1",
                "amount": 1,
                "basis": "stake",
                "contract_type": "CALL",
                "currency": "USD",
                "duration": 5,
                "duration_unit": "m",
                "symbol": "R_50"
            }
            ws.send(json.dumps({"buy": 1, "price": 1, "parameters": contrato, "passthrough": {"action": "auto"}}))
            alerta("🟢 Roxy ejecutó CALL en Deriv R_50 por 5 minutos.")

    def on_open(ws):
        ws.send(json.dumps({"authorize": DERIV_API_TOKEN}))

    def on_error(ws, error): alerta(f"⚠️ Error Deriv: {error}")
    def on_close(ws): print("🔌 Conexión Deriv cerrada.")

    ws = websocket.WebSocketApp("wss://ws.derivws.com/websockets/v3?app_id=" + DERIV_APP_ID,
                                on_message=on_message, on_open=on_open,
                                on_error=on_error, on_close=on_close)
    threading.Thread(target=ws.run_forever).start()

# === CICLO PRINCIPAL DE ROXY TRADER ===

def roxy_main_loop():
    alerta("🚀 Roxy Trader™ iniciando operaciones automáticas...")
    while True:
        operar_deriv()
        operar_alpaca_simbolo('BTC/USD')
        time.sleep(300)  # espera 5 minutos

# === EJECUCIÓN ===
if __name__ == "__main__":
    roxy_main_loop()
