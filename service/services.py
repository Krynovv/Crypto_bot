import requests
from lexicon.lexicon import LEXICON_RU


coin = ["bitcoin", "ethereum"]

def get_price_change(coin_id=coin, days=1):
   url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
   params = {"vs_currency": "usd", "days": days}
   response = requests.get(url, params=params)
   data = response.json()

   prices = [p[1] for p in data['prices']]
   if len(prices) < 2:
      return None

   change_pct = (prices[-1] - prices[0]) / prices[0] * 100
   return {
      "current_price": prices[-1],
      "change_pct": change_pct,
      "period_hours": days * 24
   }
