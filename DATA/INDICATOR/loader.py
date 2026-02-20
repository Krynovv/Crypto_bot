import yfinance as yf
import pandas as pd
import requests

from DATA.UTILS.utils import yf_to_binance_symbol
from DATA.INDICATOR.funding import fetch_funding_rate

def fetch_fear_greed(start_date, end_date):
   """
   Загружаем Fear & Greed за период
   Возвращаем DataFrame - 'date', 'fng_value', 'fng_classisficate'
   """

   url = "https://api.alternative.me/fng/?limit=2000"
   responce = requests.get(url)
   data = responce.json()['data']

   fng_df = pd.DataFrame(data)
   fng_df['timestamp'] = pd.to_numeric(fng_df['timestamp'])
   fng_df['date'] = pd.to_datetime(fng_df['timestamp'], unit='s').dt.date
   fng_df['fng_value'] = fng_df['value'].astype(int)

   start_dt = pd.to_datetime(start_date).date()
   end_dt = pd.to_datetime(end_date).date()
   mask = (fng_df['date'] >= start_dt) & (fng_df['date'] <= end_dt)
   fng_df = fng_df[mask].copy()

   return fng_df[['date', 'fng_value']]

def add_funding_to_df(df, ticker):
   symbol = yf_to_binance_symbol(ticker)

   start_ms = int(df.index[0].timestamp() * 1000)
   end_ms = int(df.index[-1].timestamp() * 1000)

   funding_df = fetch_funding_rate(symbol, start_ms, end_ms)

   if funding_df.empty:
      df["fundingRate"] = 0
      return df

   funding_df = funding_df.resample("1h").ffill()

   df = df.merge(
      funding_df,
      left_index=True,
      right_index=True,
      how="left"
   )

   df[["fundingRate", "funding_ma", "funding_diff", "funding_signal"]] = df[["fundingRate", "funding_ma", "funding_diff", "funding_signal"]].fillna(0)

   return df

def load_price_data(ticker, period="2y", interval="1d"):
   data = yf.download(ticker, period=period, interval=interval)

   if isinstance(data.columns, pd.MultiIndex):
      data.columns = data.columns.droplevel(1)
   return data