# roxy_trader.py

import time
import requests
import pandas as pd
from datetime import datetime
from alerts import enviar_alerta

# 🔑 CLAVES API DE PRUEBA (PAPER ACCOUNT)
APCA_API_KEY_ID = "AKYWWJD1R9L6WDBXYJX8"
APCA_API_SECRET_KEY = "Qif6Gem2Yqc0InhozQeOU4aTmfPDMP"
BASE_URL = "https://paper-api.alpaca.markets"
DATA_URL = "https://data.alpaca.markets"

HEADERS = {
    "APCA-API-KEY-ID": APCA_API_KEY_ID,
    "APCA-API-SECRET-KEY": APCA_API_SECRET_KEY
}

SYMBOL = "AAPL"
TIMEFRAME = "1Day"
LIMIT = 100

def obtener_datos():
    url = f"{DATA_URL}/v2/stocks/{SYMBOL}/bars?timeframe={TIMEFRAME}&limit={LIMIT}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        raise Exception(f"Error al obtener datos: {response.status_code} - {response.text}")
    
    data = response.json()["bars"]
    df = pd.DataFrame(data)
    df['t'] = pd.to_datetime(df['t'])
    df.set_index('t', inplace=True)
    return df

def calcular_rsi(df, period=14):
    delta = df['c'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calcular_ema(df, period=20):
    return df['c'].ewm(span=period, adjust=False).mean()

def ejecutar_estrategia():
    print(f"Ejecutando estrategia Roxy Trader con RSI + EMA...")
    df = obtener_datos()
    df["RSI"] = calcular_rsi(df)
    df["EMA"] = calcular_ema(df)
    
    ultima_fila = df.iloc[-1]
    precio_actual = ultima_fila["c"]
    rsi = ultima_fila["RSI"]
    ema = ultima_fila["EMA"]

    print(f"Precio actual: {precio_actual:.2f}, RSI: {rsi:.2f}, EMA: {ema:.2f}")
    
    if rsi < 30 and precio_actual > ema:
        mensaje = f"🔵 Señal de COMPRA para {SYMBOL}\nRSI: {rsi:.2f} | EMA: {ema:.2f} | Precio: {precio_actual:.2f}"
        enviar_alerta(mensaje)
    elif rsi > 70 and precio_actual < ema:
        mensaje = f"🔴 Señal de VENTA para {SYMBOL}\nRSI: {rsi:.2f} | EMA: {ema:.2f} | Precio: {precio_actual:.2f}"
        enviar_alerta(mensaje)
    else:
        print("⏳ Sin señal clara en este momento.")

# 🔁 Ejecutar una vez
if __name__ == "__main__":
    try:
        ejecutar_estrategia()
    except Exception as e:
        print("❌ Error al ejecutar Roxy Trader:")
        print(e)
