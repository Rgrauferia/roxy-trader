# Instalar la librería oficial de Alpaca (solo necesario una vez)
!pip install --upgrade alpaca-py

# === CONFIGURACIÓN DE ROXY TRADER ===
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import pandas as pd
import datetime

# 🔐 Tus credenciales Paper
API_KEY = "PKEEDWE1AK50T5TR3JNM"
API_SECRET = "o6dUILZjbUUEHu2vUQHekGjy0K0xxxxxxxxxx"  # reemplaza si cambia
USE_PAPER = True  # True para paper, False para real

# Cliente de datos y cliente de trading
data_client = StockHistoricalDataClient(API_KEY, API_SECRET)
trading_client = TradingClient(API_KEY, API_SECRET, paper=USE_PAPER)

# === PARÁMETROS DE LA ESTRATEGIA ===
symbol = "AAPL"
timeframe = TimeFrame.Minute
limit = 100

# Solicitar datos históricos de AAPL
request_params = StockBarsRequest(
    symbol_or_symbols=symbol,
    timeframe=timeframe,
    limit=limit,
    start=datetime.datetime.now() - datetime.timedelta(minutes=limit),
)
bars = data_client.get_stock_bars(request_params).df

# Verificar si se obtuvieron datos
if bars.empty:
    print("❌ No se obtuvieron datos del mercado.")
else:
    df = bars[bars.symbol == symbol].copy()

    # === CÁLCULO DE INDICADORES ===
    df['close'] = df['close'].astype(float)
    df['delta'] = df['close'].diff()
    df['gain'] = df['delta'].clip(lower=0)
    df['loss'] = -df['delta'].clip(upper=0)

    avg_gain = df['gain'].rolling(window=14).mean()
    avg_loss = df['loss'].rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()

    # Últimos valores
    last_rsi = df['RSI'].iloc[-1]
    last_price = df['close'].iloc[-1]
    last_ema = df['EMA20'].iloc[-1]

    print(f"📊 Último cierre: {last_price:.2f}")
    print(f"📉 RSI: {last_rsi:.2f}")
    print(f"📈 EMA20: {last_ema:.2f}")

    # === LÓGICA DE TRADING ===
    if last_rsi < 30 and last_price > last_ema:
        print("🟢 Señal de COMPRA detectada")

        order = MarketOrderRequest(
            symbol=symbol,
            qty=1,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        response = trading_client.submit_order(order)
        print("✅ Orden de compra enviada:", response.id)

    elif last_rsi > 70 and last_price < last_ema:
        print("🔴 Señal de VENTA detectada")

        order = MarketOrderRequest(
            symbol=symbol,
            qty=1,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
        response = trading_client.submit_order(order)
        print("✅ Orden de venta enviada:", response.id)

    else:
        print("⚪️ Sin señales claras en este momento.")
