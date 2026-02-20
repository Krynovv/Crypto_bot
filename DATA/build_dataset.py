import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import numpy as np

from DATA.INDICATOR.loader import load_price_data, add_funding_to_df
from DATA.INDICATOR.indicators import add_technical_indicators, add_fear_greed_to_df, add_candles_indicator, add_extra_indicators
from DATA.INDICATOR.features import main_features
from DATA.sequences import create_sequences
from DATA.scaler import scaler_train_val
from DATA.config import COINS, SEQ_LENGTH, PREDICTION_HORIZON, TRAIN_RATIO, SCALER_TYPE


all_X_train, all_y_train = [], []
all_X_val, all_y_val = [], []

for ticker in COINS:
    print("processing", ticker)

    df = load_price_data(ticker)
    df = add_funding_to_df(df, ticker)
    df = add_fear_greed_to_df(df)
    df = add_technical_indicators(df)
    df = add_candles_indicator(df)
    df = add_extra_indicators(df)

    feats = main_features(df)
    train_scaled, val_scaled, scaler = scaler_train_val(feats.values, train_ratio=TRAIN_RATIO, scaler_type=SCALER_TYPE)

    X_train_seq, y_train_seq = create_sequences(train_scaled, seq_length=SEQ_LENGTH, prediction_horizon=PREDICTION_HORIZON)
    X_val_seq, y_val_seq = create_sequences(val_scaled, seq_length=SEQ_LENGTH, prediction_horizon=PREDICTION_HORIZON)

    all_X_train.append(X_train_seq)
    all_y_train.append(y_train_seq)
    all_X_val.append(X_val_seq)
    all_y_val.append(y_val_seq)

X_train = np.concatenate(all_X_train, axis=0)
y_train = np.concatenate(all_y_train, axis=0)
X_val = np.concatenate(all_X_val, axis=0)
y_val = np.concatenate(all_y_val, axis=0)

torch.save({
    "X_train": torch.FloatTensor(X_train),
    "y_train": torch.FloatTensor(y_train),
    "X_val": torch.FloatTensor(X_val),
    "y_val": torch.FloatTensor(y_val),
    "feature_columns": feats.columns.tolist()
}, "data/processed/dataset.pt")

print("✅ dataset ready")
