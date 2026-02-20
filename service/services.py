import torch
import numpy as np
import pickle
import requests

from lexicon.lexicon import LEXICON_RU


#===CryLSTM Model (такая же как при обучении)===
class CryLSTM(torch.nn.Module):
    def __init__(self, input_size=32, hidden_size=128, num_layers=2, dropout=0.3):
        super().__init__()
        self.lstm = torch.nn.LSTM(
            input_size,
            hidden_size,
            num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True
        )
        self.norm = torch.nn.LayerNorm(hidden_size * 2)
        self.dropout = torch.nn.Dropout(dropout)
        self.fc1 = torch.nn.Linear(hidden_size * 2, hidden_size)
        self.fc2 = torch.nn.Linear(hidden_size, 1)

    def forward(self, X):
        out, _ = self.lstm(X)
        features = out[:, -1, :]
        features = self.norm(features)
        features = self.dropout(features)
        features = torch.relu(self.fc1(features))
        features = self.dropout(features)
        return self.fc2(features).squeeze(-1)


#===CryptoPredictor для бота===
class CryptoPredictor:
    def __init__(self, model_path: str, scaler_path: str):
        # Загрузка модели
        self.model = CryLSTM(input_size=32, hidden_size=128, num_layers=2, dropout=0.3)
        self.model.load_state_dict(torch.load(model_path, weights_only=True))
        self.model.eval()

        # Загрузка scaler
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)

        # Параметры
        self.sequence_length = 30
        self.feature_columns = [
            'Close', 'Volume', 'rsi', 'macd', 'macd_signal',
            'bb_mid', 'bb_high', 'bb_low', 'fundingRate', 'funding_ma',
            'funding_diff', 'funding_signal', 'fng_value', 'body_rel',
            'upper_wick_rel', 'lower_wick_rel', 'range_rel', 'open_close',
            'high_low', 'ema10', 'ema20', 'ema50', 'close_ema10',
            'close_ema20', 'close_ema50', 'atr', 'roc', 'volatility_10',
            'volatility_20', 'stoch_k', 'stoch_d', 'obv'
        ]

    def get_historical_data(self, coin_id: str, days: int = 60) -> dict:
        """Получить исторические данные с Binance (цены + объём)"""
        symbol_map = {
            'bitcoin': 'BTCUSDT',
            'ethereum': 'ETHUSDT',
            'binancecoin': 'BNBUSDT',
            'solana': 'SOLUSDT'
        }
        symbol = symbol_map.get(coin_id, 'BTCUSDT')

        url = f"https://api.binance.com/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': '1d',
            'limit': days
        }

        response = requests.get(url, params=params)
        data = response.json()

        df_data = {
            'Open': [], 'High': [], 'Low': [], 'Close': [], 'Volume': []
        }
        for kline in data:
            df_data['Open'].append(float(kline[1]))
            df_data['High'].append(float(kline[2]))
            df_data['Low'].append(float(kline[3]))
            df_data['Close'].append(float(kline[4]))
            df_data['Volume'].append(float(kline[5]))

        return df_data

    def calculate_indicators(self, df: dict) -> np.ndarray:
        """Рассчитать 32 технических индикатора (упрощённая версия)"""
        import pandas as pd

        df = pd.DataFrame(df)
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']

        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-9)
        rsi = 100 - (100 / (1 + rs))

        # MACD
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd = ema12 - ema26
        macd_signal = macd.ewm(span=9).mean()

        # Bollinger Bands
        sma = close.rolling(20).mean()
        std = close.rolling(20).std()
        bb_mid = sma
        bb_high = sma + (std * 2)
        bb_low = sma - (std * 2)

        # EMA
        ema10 = close.ewm(span=10).mean()
        ema20 = close.ewm(span=20).mean()
        ema50 = close.ewm(span=50).mean()

        # ATR
        tr = np.maximum.reduce([
            high - low,
            abs(high - close.shift()),
            abs(low - close.shift())
        ])
        atr = pd.Series(tr).rolling(14).mean()

        # Stochastic
        low14 = low.rolling(14).min()
        high14 = high.rolling(14).max()
        stoch_k = 100 * (close - low14) / (high14 - low14 + 1e-9)
        stoch_d = stoch_k.rolling(3).mean()

        # ROC
        roc = close.pct_change(5)

        # Volatility
        volatility_10 = close.pct_change().rolling(10).std()
        volatility_20 = close.pct_change().rolling(20).std()

        # Candles
        body = close - df['Open']
        upper_wick = high - df[['Open', 'Close']].max(axis=1)
        lower_wick = df[['Open', 'Close']].min(axis=1) - low
        range_ = high - low

        # Собираем все признаки
        features = pd.DataFrame()
        features['Close'] = close
        features['Volume'] = volume
        features['rsi'] = rsi
        features['macd'] = macd
        features['macd_signal'] = macd_signal
        features['bb_mid'] = bb_mid
        features['bb_high'] = bb_high
        features['bb_low'] = bb_low
        features['fundingRate'] = 0  # упрощённо
        features['funding_ma'] = 0
        features['funding_diff'] = 0
        features['funding_signal'] = 0
        features['fng_value'] = 50  # упрощённо
        features['body_rel'] = body / df['Open']
        features['upper_wick_rel'] = upper_wick / df['Open']
        features['lower_wick_rel'] = lower_wick / df['Open']
        features['range_rel'] = range_ / df['Open']
        features['open_close'] = (close - df['Open']) / df['Open']
        features['high_low'] = range_ / df['Open']
        features['ema10'] = ema10
        features['ema20'] = ema20
        features['ema50'] = ema50
        features['close_ema10'] = (close - ema10) / close
        features['close_ema20'] = (close - ema20) / close
        features['close_ema50'] = (close - ema50) / close
        features['atr'] = atr
        features['roc'] = roc
        features['volatility_10'] = volatility_10
        features['volatility_20'] = volatility_20
        features['stoch_k'] = stoch_k
        features['stoch_d'] = stoch_d
        features['obv'] = (volume * (close.diff() > 0).astype(int) - volume * (close.diff() < 0).astype(int)).cumsum()

        features = features.fillna(0)
        return features.values

    def predict(self, coin_id: str) -> str:
        """Основной метод для предсказания"""
        try:
            # 1. Получить данные
            df = self.get_historical_data(coin_id, days=60)

            # 2. Рассчитать признаки
            features = self.calculate_indicators(df)

            # Сохраняем последние значения индикаторов для отображения
            last_indicators = features[-1]

            # 3. Нормализовать
            features_scaled = self.scaler.transform(features)

            # 4. Взять последние 30 дней
            sequence = features_scaled[-self.sequence_length:]

            # 5. Преобразовать в тензор
            X = torch.FloatTensor(sequence).unsqueeze(0)  # (1, 30, 32)

            # 6. Предикт
            with torch.no_grad():
                logits = self.model(X)
                prob = torch.sigmoid(logits).item()

            # 7. Интерпретация (порог 0.5)
            direction = "📈 ВЫРАСТЕТ" if prob > 0.5 else "📉 УПАДЕТ"
            confidence = prob if prob > 0.5 else 1 - prob

            # 8. Формируем ответ с индикаторами
            # Индексы: Close=0, Volume=1, rsi=2, macd=3, macd_signal=4, bb_mid=5, bb_high=6, bb_low=7
            rsi = last_indicators[2]
            macd = last_indicators[3]
            macd_sig = last_indicators[4]
            bb_mid = last_indicators[5]
            bb_high = last_indicators[6]
            bb_low = last_indicators[7]
            close = last_indicators[0]
            stoch_k = last_indicators[30]
            stoch_d = last_indicators[31]
            atr = last_indicators[25]

            # Определяем сигналы индикаторов
            rsi_signal = "🟢 Перепродан" if rsi < 30 else "🔴 Перекуплен" if rsi > 70 else "⚪ Нейтрально"
            macd_signal = "🟢 Бычий" if macd > macd_sig else "🔴 Медвежий"
            bb_position = "Вверху" if close > bb_high else "Внизу" if close < bb_low else "Внутри канала"
            stoch_signal = "🟢 Перепродан" if stoch_k < 20 else "🔴 Перекуплен" if stoch_k > 80 else "⚪ Нейтрально"

            return (
                f"Прогноз для {coin_id.upper()}:\n"
                f"{direction}\n"
                f"Вероятность: {confidence:.1%}\n\n"
                f"📊 Ключевые индикаторы:\n"
                f"─────────────────────\n"
                f"RSI (14): {rsi:.1f} - {rsi_signal}\n"
                f"MACD: {macd:.4f} / {macd_sig:.4f} - {macd_signal}\n"
                f"BB: {bb_low:.2f} - {bb_mid:.2f} - {bb_high:.2f}\n"
                f"Stoch: {stoch_k:.1f} / {stoch_d:.1f} - {stoch_signal}\n"
                f"ATR: {atr:.2f}\n"
                f"Позиция BB: {bb_position}"
            )

        except Exception as e:
            return f"Ошибка: {str(e)}"


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
