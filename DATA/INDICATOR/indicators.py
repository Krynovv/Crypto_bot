import ta
import pandas as pd
from DATA.UTILS.utils import yf_to_binance_symbol
from DATA.INDICATOR.loader import fetch_fear_greed
import numpy as np

def add_fear_greed_to_df(df, start_date=None, end_date=None):
   if start_date is None:
      start_date = df.index.min().date()
   if end_date is None:
      end_date = df.index.max().date()

   fng_df = fetch_fear_greed(start_date, end_date)
   fng_df['date'] = pd.to_datetime(fng_df['date'])

   df = df.copy()
   df['date'] = df.index
   df = df.merge(fng_df[['date', 'fng_value']], on='date', how='left')

   df['fng_value'] = df['fng_value'].ffill().bfill()


   df.set_index('date', inplace=True)
   return df


#===Функция -> Технические Индикаторы===
def add_technical_indicators(df):

   #= RSI =#
   df['rsi'] = ta.momentum.RSIIndicator(df['Close']).rsi()

   #= MACD =#
   macd = ta.trend.MACD(df['Close'])
   df['macd'] = macd.macd()
   df['macd_signal'] = macd.macd_signal()

   #= Полосы Боллиджера =#
   bb = ta.volatility.BollingerBands(df['Close'])
   df['bb_mid'] = bb.bollinger_mavg()
   df['bb_high'] = bb.bollinger_hband()
   df['bb_low'] = bb.bollinger_lband()

   # -> Скользящее среднее объёма
   df['volume_ma'] = df['Volume'].rolling(20).mean()

   return df.dropna()

def add_candles_indicator(df):
   df['body'] = df['Close'] - df['Open']  # тело свечи: >0 бычья, <0 медвежья
   df['upper_wick'] = df['High'] - df[['Open', 'Close']].max(axis=1)
   df['lower_wick'] = df[['Open', 'Close']].min(axis=1) - df['Low']

   df['candle_direction'] = (df['Close'] > df['Open']).astype(int)  # 1 = бычья, 0 = медвежья
   df['range'] = df['High'] - df['Low']  # полный диапазон свечи

   df['body_rel'] = df['body'] / df['Open']
   df['upper_wick_rel'] = df['upper_wick'] / df['Open']
   df['lower_wick_rel'] = df['lower_wick'] / df['Open']
   df['range_rel'] = df['range'] / df['Open']

   df['open_close'] = (df['Close'] - df['Open']) / df['Open']
   df['high_low'] = (df['High'] - df['Low']) / df['Open']

   return df

def add_extra_indicators(df):

   close = df['Close']
   high = df['High']
   low = df['Low']
   volume = df['Volume']

   # === EMA ===
   df['ema10'] = close.ewm(span=10).mean()
   df['ema20'] = close.ewm(span=20).mean()
   df['ema50'] = close.ewm(span=50).mean()

   df['close_ema10'] = (close - df['ema10']) / close
   df['close_ema20'] = (close - df['ema20']) / close
   df['close_ema50'] = (close - df['ema50']) / close

   # === ATR ===
   tr = np.maximum.reduce([
      high - low,
      abs(high - close.shift()),
      abs(low - close.shift())
   ])
   df['atr'] = pd.Series(tr).rolling(14).mean()

   # === Волатильность ===
   df['volatility_10'] = close.pct_change().rolling(10).std()
   df['volatility_20'] = close.pct_change().rolling(20).std()

   # === ROC ===
   df['roc'] = close.pct_change(5)

   # === Stochastic ===
   low14 = low.rolling(14).min()
   high14 = high.rolling(14).max()

   df['stoch_k'] = 100 * (close - low14) / (high14 - low14 + 1e-9)
   df['stoch_d'] = df['stoch_k'].rolling(3).mean()

   # === OBV ===
   obv = [0]
   for i in range(1, len(close)):
      if close.iloc[i] > close.iloc[i-1]:
         obv.append(obv[-1] + volume.iloc[i])
      elif close.iloc[i] < close.iloc[i-1]:
         obv.append(obv[-1] - volume.iloc[i])
      else:
         obv.append(obv[-1])

   df['obv'] = obv

   df.fillna(0, inplace=True)

   return df
