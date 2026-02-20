from sklearn.preprocessing import StandardScaler, MinMaxScaler
import pickle

def scaler_train_val(features, train_ratio = 0.8, scaler_type="standart"):
   split = int(len(features) * train_ratio)

   train = features[:split]
   val = features[split:]

   if scaler_type == "minmax":
      scaler = MinMaxScaler()
   else:
      scaler = StandardScaler()

   train_scaled = scaler.fit_transform(train)
   val_scaled = scaler.transform(val)

   # Сохраняем scaler для использования в боте
   with open("Model/scaler.pkl", "wb") as f:
      pickle.dump(scaler, f)
   print("✅ Scaler сохранён в Model/scaler.pkl")

   return train_scaled, val_scaled, scaler