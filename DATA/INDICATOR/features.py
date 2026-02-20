def main_features(df):
   cols = [
      # price
      'Close','Volume',

      # tech
      'rsi','macd','macd_signal',
      'bb_mid','bb_high','bb_low',

      # funding
      'fundingRate','funding_ma','funding_diff','funding_signal',

      # fear_greed
      'fng_value',

      # candles
      'body_rel', 'upper_wick_rel', 'lower_wick_rel', 'range_rel',
      'open_close', 'high_low',

      # extra
      'ema10', 'ema20', 'ema50',
      'close_ema10', 'close_ema20', 'close_ema50',
      'atr', 'roc',
      'volatility_10', 'volatility_20',
      'stoch_k', 'stoch_d',
      'obv'
   ]

   return df[cols]