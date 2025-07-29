import time
import pandas as pd
import numpy as np
import requests
from alpaca_trade_api.rest import REST, TimeFrame
from alerts import enviar_alerta

# === CONFIGURACIÓN ===
API_KEY = "TU_API_KEY"
API_SECRET = "TU_API_SECRET"
BASE_URL = "https://paper-api.alpaca.markets"
SYMBOL = "AAPL"
CANTIDAD = 1

# === Inicializar conexión con Alpaca ===
api = REST(API_KEY, API_SECRET, BASE_URL)

# === Función para obtener RSI ===
def calcular_rsi(data, period=14):
    delta = data.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# === Función principal ===
def roxy_trader():
    print("🚀 Ejecutando estrategia Roxy Trader con RSI + EMA...")
    try:
        # Obtener datos históricos de 1D
        bars = api.get_bars(SYMBOL, TimeFrame.Day, limit=100).df
        df = bars.copy()
        df['close'] = df['close'].astype(float)

        # Calcular EMA y RSI
        df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['RSI'] = calcular_rsi(df['close'])

        # Último valor
        precio_actual = df['close'].iloc[-1]
        ema_actual = df['EMA20'].iloc[-1]
        rsi_actual = df['RSI'].iloc[-1]

        print(f"📉 Precio: {precio_actual:.2f} | 📊 EMA20: {ema_actual:.2f} | 💪 RSI: {rsi_actual:.2f}")

        # Señal de compra
        if rsi_actual < 30 and precio_actual > ema_actual:
            orden = api.submit_order(
                symbol=SYMBOL,
                qty=CANTIDAD,
                side='buy',
                type='market',
                time_in_force='gtc'
            )
            print(f"✅ Orden ejecutada: {orden.id}")
            enviar_alerta(f"🟢 Roxy compró {CANTIDAD} de {SYMBOL} a {precio_actual:.2f}")
        else:
            print("⚠️ No hay señal clara. No se compra.")
    except Exception as e:
        print(f"❌ Error en Roxy Trader: {e}")
        enviar_alerta(f"❌ Error al ejecutar Roxy Trader:\n{e}")

# === Ejecutar ===
if __name__ == "__main__":
    roxy_trader()
