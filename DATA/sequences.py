import numpy as np

def create_sequences(data, seq_length=60, prediction_horizon=10):
    X, y_dir = [], []
    for i in range(len(data) - seq_length - prediction_horizon + 1):
        X.append(data[i:i+seq_length])
        current = data[i + seq_length - 1, 0]  # цена закрытия
        future = data[i + seq_length + prediction_horizon - 1, 0]
        direction = 1 if future > current else 0
        y_dir.append(direction)
    return np.array(X), np.array(y_dir)