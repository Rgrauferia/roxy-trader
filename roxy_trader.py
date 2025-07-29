import alpaca_trade_api as tradeapi
import datetime
import pandas as pd
import numpy as np

# ✅ Configura tus credenciales (PAPER TRADING)
API_KEY = 'PKEEDWE1AK50T5TR3JNM'  # <- Puedes poner la tuya
API_SECRET = 'o6dUILZjbUUEHu2vUQHekGjy0K0xxxxxxxxxxxx'  # <- Completa con tu secret
BASE_URL = 'https://paper-api.alpaca.markets'  # ✅ PAPER endpoint

# ✅ Inicializa la API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# ✅ Parámetros
SYMBOL = "AAPL"
TIMEFRAME = tradeapi.TimeFrame.Minute
LIMIT = 100  # Últimos 100 minutos
END_DATE = datetime.datetime.now()
START_DATE = END_DATE - datetime.timedelta(minutes=LIMIT)

# ✅ Obtener datos de velas con get_bars (la forma correcta)
print(f"⏳ Obteniendo datos de {SYMBOL}...")
bars = api.get_bars(
    SYMBOL,
    TIMEFRAME,
    start=START_DATE.isoformat(),
    end=END_DATE.isoformat(),
    adjustment='raw',
    limit=LIMIT
)

# ✅ Convertir a DataFrame
df = bars.df[SYMBOL]

# ✅ Calcular RSI
def calcular_rsi(series, period=14):
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

df["RSI"] = calcular_rsi(df["close"])

# ✅ Calcular EMA (Exponential Moving Average)
df["EMA"] = df["close"].ewm(span=14, adjust=False).mean()

# ✅ Lógica de trading
ultimo_rsi = df["RSI"].iloc[-1]
ultimo_precio = df["close"].iloc[-1]
ultima_ema = df["EMA"].iloc[-1]

print("\n📊 Últimos datos:")
print(f"🟢 Precio: {ultimo_precio}")
print(f"🔵 EMA: {ultima_ema}")
print(f"🟠 RSI: {ultimo_rsi}")

# ✅ Ejemplo de señal
if ultimo_rsi < 30 and ultimo_precio > ultima_ema:
    print("✅ Señal: COMPRA 📈")
elif ultimo_rsi > 70 and ultimo_precio < ultima_ema:
    print("❌ Señal: VENTA 📉")
else:
    print("⏸️ Señal: ESPERAR...")

# (Opcional) Aquí podrías ejecutar una orden real de compra/venta si lo deseas
