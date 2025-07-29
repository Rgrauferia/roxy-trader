# roxy_trader.py

import alpaca_trade_api as tradeapi
import pandas as pd
import time
from datetime import datetime, timedelta

# 📌 CONFIGURACIÓN
API_KEY = 'PKEEDWE1AK50T5TR3JNM'
API_SECRET = 'o6dUILZjbUUEHu2vUQHeKGjy0K0zhSvhZbLqZtCm'
BASE_URL = 'https://paper-api.alpaca.markets'  # Paper trading URL

SYMBOL = 'AAPL'
RSI_PERIOD = 14
EMA_PERIOD = 9
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_QTY = 1

# 📡 Conectar con la API de Alpaca
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

def fetch_data(symbol):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=2)

    print(f"Obteniendo datos de {symbol}...")
    try:
        bars = api.get_bars(
            symbol,
            tradeapi.TimeFrame.Minute,
            start=start_date.isoformat(),
            end=end_date.isoformat(),
            limit=100
        )
        df = pd.DataFrame([bar.__dict__ for bar in bars])
        df['timestamp'] = pd.to_datetime(df['t'])
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
        df['close'] = pd.to_numeric(df['c'])
        return df
    except Exception as e:
        print(f"❌ Error al obtener datos: {e}")
        return None

def calculate_indicators(df):
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=RSI_PERIOD).mean()
    avg_loss = loss.rolling(window=RSI_PERIOD).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['EMA'] = df['close'].ewm(span=EMA_PERIOD, adjust=False).mean()
    return df

def check_signals(df):
    if df is None or df.empty:
        return None

    rsi = df['RSI'].iloc[-1]
    price = df['close'].iloc[-1]
    ema = df['EMA'].iloc[-1]

    if rsi < RSI_OVERSOLD and price > ema:
        return 'buy'
    elif rsi > RSI_OVERBOUGHT and price < ema:
        return 'sell'
    else:
        return 'hold'

def place_order(side, qty, symbol):
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type='market',
            time_in_force='gtc'
        )
        print(f"✅ Orden enviada: {side.upper()} {qty} {symbol}")
    except Exception as e:
        print(f"❌ Error al enviar orden: {e}")

def roxy_trader():
    print(f"📈 Ejecutando estrategia Roxy Trader con RSI + EMA para {SYMBOL}...")

    df = fetch_data(SYMBOL)
    if df is None:
        print("⚠️ No se pudieron obtener datos.")
        return

    df = calculate_indicators(df)
    signal = check_signals(df)

    print(f"📊 Señal detectada: {signal.upper()}")
    if signal in ['buy', 'sell']:
        place_order(signal, TRADE_QTY, SYMBOL)
    else:
        print("⏸️ No se envió ninguna orden.")

# 🔁 Ejecutar una vez
if __name__ == "__main__":
    roxy_trader()
