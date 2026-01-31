import requests
from lexicon.lexicon import LEXICON_RU



def get_price_change(coin_id: str, days: int = 1) -> str:
   url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
   params = {"vs_currency": "usd", "days": days}

   try:
      response = requests.get(url, params=params)
      response.raise_for_status()
      data = response.json()

      prices = [p[1] for p in data['prices']]
      if len(prices) < 2:
         return None

      current_price = prices[-1]
      change_pct = (prices[-1] - prices[0]) / prices[0] * 100


      return (
         f"Монета: {coin_id.title()}\n"
         f"Текущая цена: ${current_price:,.2f}\n"
         f"Изменение за 24ч: {change_pct:+.2f}%"
      )
   except Exception as e:
      return f"Error: {str(e)}"