# roxy_trader.py – Bot automático con Deriv y Alpaca
import time
import requests
import json
from alpaca_trade_api.rest import REST, TimeFrame
from alerts import enviar_alerta  # Asegúrate de tener alerts.py

# ================== CONFIGURACIÓN ==================
# --- Deriv API ---
DERIV_API_TOKEN = "tu_token_de_deriv"
DERIV_APP_ID = "12345"
DERIV_SYMBOL = "R_50"

# --- Alpaca API ---
ALPACA_API_KEY = "TU_ALPACA_API_KEY"
ALPACA_SECRET_KEY = "TU_ALPACA_SECRET_KEY"
ALPACA_PAPER = True  # False si quieres usar real

# --- Estrategia básica ---
TAKE_PROFIT = 5.0
STOP_LOSS = -3.0

# ================== CONEXIONES ==================
# Deriv Websocket (via REST para ejemplo básico)
def abrir_trade_deriv():
    headers = {
        "Authorization": f"Bearer {DERIV_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "amount": 1,
        "basis": "stake",
        "contract_type": "CALL",
        "currency": "USD",
        "duration": 1,
        "duration_unit": "m",
        "symbol": DERIV_SYMBOL
    }
    try:
        r = requests.post("https://api.deriv.com/binary/v3/trade", headers=headers, data=json.dumps(payload))
        if r.ok:
            enviar_alerta("🚀 Trade ejecutado en Deriv.")
            print("✅ Trade ejecutado en Deriv")
        else:
            enviar_alerta("❌ Error al ejecutar trade en Deriv.")
            print("❌ Error al ejecutar trade en Deriv")
    except Exception as e:
        print("🛑 Error:", e)

# Alpaca client
alpaca = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url="https://paper-api.alpaca.markets" if ALPACA_PAPER else "https://api.alpaca.markets")

def abrir_trade_alpaca():
    try:
        alpaca.submit_order(
            symbol="AAPL",
            qty=1,
            side="buy",
            type="market",
            time_in_force="gtc"
        )
        enviar_alerta("📈 Trade ejecutado en Alpaca.")
        print("✅ Trade ejecutado en Alpaca")
    except Exception as e:
        enviar_alerta("⚠️ Error al ejecutar trade en Alpaca.")
        print("❌ Error:", e)

# ================== LÓGICA AUTOMÁTICA ==================
def estrategia_roxy():
    while True:
        print("⏳ Evaluando oportunidad...")
        # Aquí podrías leer indicadores, condiciones o señales externas

        # Simulación de decisión
        decision = "comprar"

        if decision == "comprar":
            abrir_trade_deriv()
            abrir_trade_alpaca()
        else:
            print("🚫 No hay señal de entrada")

        time.sleep(300)  # Esperar 5 minutos

# ================== EJECUCIÓN ==================
if __name__ == "__main__":
    enviar_alerta("🤖 Roxy Trader iniciado.")
    estrategia_roxy()
