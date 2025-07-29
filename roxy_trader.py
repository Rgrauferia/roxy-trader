import alpaca_trade_api as tradeapi
import pandas as pd
import time

# 📌 CONFIGURACIÓN: Reemplaza aquí tu clave secreta si falta
API_KEY = 'PKEEDWE1AK50T5TR3JNM'
API_SECRET = 'o6dUILZjbUUEHu2vUQHekGjy0K0xxxxxxxxxx'  # ← asegúrate de poner tu secreto aquí
BASE_URL = 'https://paper-api.alpaca.markets'

# 🔑 Inicializar conexión con la API de Alpaca (modo paper)
api = tradeapi.REST(API_KEY, API_SECRET, base_url=BASE_URL, api_version='v2')

# ✅ Verificación de cuenta
try:
    account = api.get_account()
    print(f"💼 Cuenta conectada: {account.id}")
    print(f"💵 Saldo disponible: {account.cash}")
except Exception as e:
    print("🚫 Error conectando a la cuenta Alpaca:", e)
    exit()

# ⚙️ CONFIGURACIÓN DE LA ESTRATEGIA
symbol = 'AAPL'
timeframe = '1Min'
limit = 100

# 📊 OBTENER DATOS HISTÓRICOS
try:
    print("📈 Descargando datos históricos...")
    bars = api.get_bars(symbol, timeframe, limit=limit).df
    bars = bars[bars['symbol'] == symbol]
except Exception as e:
    print("🚫 Error obteniendo datos:", e)
    exit()

# 🧠 CÁLCULO DE INDICADORES TÉCNICOS (RSI + EMA)
def calculate_indicators(df):
    df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()

    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

bars = calculate_indicators(bars)

# 🧪 IMPRIMIR ÚLTIMAS SEÑALES
latest = bars.iloc[-1]
print(f"\n📊 Último cierre: {latest['close']:.2f}")
print(f"📉 RSI: {latest['RSI']:.2f}")
print(f"📈 EMA20: {latest['EMA20']:.2f}")

# 📍 LÓGICA DE COMPRA/VENTA SIMPLIFICADA
try:
    if latest['RSI'] < 30 and latest['close'] > latest['EMA20']:
        print("🟢 Señal de COMPRA detectada. Ejecutando orden...")
        api.submit_order(symbol=symbol, qty=1, side='buy', type='market', time_in_force='gtc')
    elif latest['RSI'] > 70 and latest['close'] < latest['EMA20']:
        print("🔴 Señal de VENTA detectada. Ejecutando orden...")
        api.submit_order(symbol=symbol, qty=1, side='sell', type='market', time_in_force='gtc')
    else:
        print("⏸ No se detectó ninguna señal clara. Esperando próxima vela.")
except Exception as e:
    print("🚫 Error ejecutando la orden:", e)
