import requests
import pandas as pd

BINANCE_URL = "https://fapi.binance.com/fapi/v1/fundingRate"

def fetch_funding_rate(symbol: str, start_ms: int, end_ms: int):
   """
   Загружаем историю ставок финансирования с Binance
   Возвращаем DataFrame - 'funding_ma', 'funding_diff', 'funding_signall' для loader.py
   """
   params = {
      "symbol": symbol.upper(),
      "startTime": start_ms,
      "endTime": end_ms,
      "limit": 1000
   }

   res = requests.get(BINANCE_URL, params=params).json()

   if not isinstance(res, list) or len(res) == 0:
      return pd.DataFrame()

   df = pd.DataFrame(res)

   df["fundingRate"] = df["fundingRate"].astype(float)
   df["time"] = pd.to_datetime(df["fundingTime"], unit="ms")

   df = df[["time", "fundingRate"]]
   df = df.set_index("time")

   df["funding_ma"] = df["fundingRate"].rolling(3).mean()
   df["funding_diff"] = df["fundingRate"].diff()
   df["funding_signal"] = (df["fundingRate"] > 0).astype(int)

   return df

