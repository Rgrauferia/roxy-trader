import alpaca_trade_api as tradeapi
import time
import pandas as pd

# 🔐 CONFIGURACIÓN DE CREDENCIALES Y API (PAPER TRADING)
API_KEY = "PKEEDWE1AK50T5TR3JNM"
API_SECRET = "o6dUILZjbUUUHu2vUQHekGjy0K0tVqmbdkJLOzqv"
BASE_URL = "https://paper-api.alpaca.markets"

# 🔄 Conexión con Alpaca
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# 📈 PARÁMETROS DE TRADING
symbol = "AAPL"         # Puedes cambiarlo por otro como "TSLA" o "MSFT"
qty = 1                 # Número de acciones a comprar/vender
rsi_period = 14
rsi_overbought = 70
rsi_oversold = 30
ema_period = 20

def get_data():
    barset = api.get_bars(symbol, tradeapi.TimeFrame.Minute, limit=100)
    df = pd.DataFrame([{
        'time': bar.t,
        'open': bar.o,
        'high': bar.h,
        'low': bar.l,
        'close': bar.c,
        'volume': bar.v
    } for bar in barset])
    df.set_index('time', inplace=True)
    return df

def calculate_indicators(df):
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(rsi_period).mean()
    avg_loss = loss.rolling(rsi_period).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['EMA'] = df['close'].ewm(span=ema_period, adjust=False).mean()
    return df

def check_signals(df):
    rsi = df['RSI'].iloc[-1]
    price = df['close'].iloc[-1]
    ema = df['EMA'].iloc[-1]

    if rsi < rsi_oversold and price > ema:
        return "buy"
    elif rsi > rsi_overbought and price < ema:
        return "sell"
    else:
        return "hold"

def place_order(signal):
    if signal == "buy":
        print(f"🟢 Enviando orden de COMPRA de {qty} acciones de {symbol}...")
        api.submit_order(symbol=symbol, qty=qty, side='buy', type='market', time_in_force='gtc')
    elif signal == "sell":
        print(f"🔴 Enviando orden de VENTA de {qty} acciones de {symbol}...")
        api.submit_order(symbol=symbol, qty=qty, side='sell', type='market', time_in_force='gtc')
    else:
        print("🟡 No se ejecuta orden. Señal = HOLD.")

def run_strategy():
    print("▶️ Ejecutando estrategia Roxy Trader con RSI + EMA...")

    try:
        df = get_data()
        df = calculate_indicators(df)
        signal = check_signals(df)
        place_order(signal)
    except Exception as e:
        print("❌ Error al ejecutar Roxy Trader:")
        print(e)

if __name__ == "__main__":
    run_strategy()
