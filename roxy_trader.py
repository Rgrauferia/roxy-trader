import requests
import pandas as pd

# === Configuración de claves Alpaca (Paper) ===
API_KEY = "PKGGAJO1SKOQX5XMD8J4"
API_SECRET = "jrmAlbLfzhbq07pXJeRukC73RUG67P7"
BASE_URL = "https://paper-api.alpaca.markets"  # <- Esta línea es clave

HEADERS = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": API_SECRET
}

# === Parámetros de estrategia ===
SYMBOL = "AAPL"
TIMEFRAME = "1Day"
LIMIT = 100

# === Obtener datos históricos ===
def obtener_datos():
    url = f"{BASE_URL}/v2/stocks/{SYMBOL}/bars?timeframe={TIMEFRAME}&limit={LIMIT}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        raise Exception(f"Error al obtener datos: {response.status_code} – {response.text}")
    
    datos = response.json()["bars"]
    df = pd.DataFrame(datos)
    df["t"] = pd.to_datetime(df["t"])
    df.set_index("t", inplace=True)
    return df

# === Cálculos de indicadores técnicos (RSI y EMA) ===
def calcular_indicadores(df):
    df["EMA_10"] = df["c"].ewm(span=10).mean()

    delta = df["c"].diff()
    ganancia = delta.clip(lower=0)
    perdida = -delta.clip(upper=0)
    media_ganancia = ganancia.rolling(window=14).mean()
    media_perdida = perdida.rolling(window=14).mean()
    rs = media_ganancia / media_perdida
    df["RSI_14"] = 100 - (100 / (1 + rs))

    return df

# === Ejecutar estrategia simple (solo imprime señal) ===
def ejecutar_estrategia(df):
    ultima_fila = df.iloc[-1]
    rsi = ultima_fila["RSI_14"]
    ema = ultima_fila["EMA_10"]
    precio = ultima_fila["c"]

    print(f"\n📈 Último precio: {precio:.2f}")
    print(f"📊 RSI 14: {rsi:.2f}")
    print(f"📊 EMA 10: {ema:.2f}")

    if rsi < 30 and precio > ema:
        print("✅ Señal: COMPRAR (RSI sobrevendido y precio sobre EMA)")
    elif rsi > 70 and precio < ema:
        print("❌ Señal: VENDER (RSI sobrecomprado y precio bajo EMA)")
    else:
        print("⚠️ Señal: MANTENER (No hay condición clara)")

# === Script principal ===
if __name__ == "__main__":
    print("🚀 Ejecutando estrategia Roxy Trader con RSI + EMA...")
    try:
        df = obtener_datos()
        df = calcular_indicadores(df)
        ejecutar_estrategia(df)
    except Exception as e:
        print(f"❌ Error al ejecutar Roxy Trader:\n{e}")
