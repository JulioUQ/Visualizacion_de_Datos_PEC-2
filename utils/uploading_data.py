import yfinance as yf
import pandas as pd

# Lista de empresas seleccionadas
tickers = ["AAPL", "MSFT", "GOOG"]

# Descarga de datos (desde 2023 hasta fin de 2024)
data = yf.download(tickers, start="2023-01-01", end="2025-01-01", group_by="ticker", progress=False)

# Reorganizamos el DataFrame a formato plano
frames = []
for ticker in tickers:
    df_ticker = data[ticker].copy() # type: ignore
    df_ticker["Ticker"] = ticker
    df_ticker.reset_index(inplace=True)
    frames.append(df_ticker)

# Unimos todos los tickers en un solo DataFrame
df = pd.concat(frames, ignore_index=True)

# Seleccionamos solo las columnas necesarias
df = df[["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]]

# Aseguramos los tipos de datos
df["Date"] = pd.to_datetime(df["Date"])            # datetime64
df["Ticker"] = df["Ticker"].astype(str)            # string
for col in ["Open", "High", "Low", "Close"]:
    df[col] = df[col].astype(float)                # float64
df["Volume"] = df["Volume"].astype("int64")        # int64

# Verificamos tipos
print(df.dtypes)

# Vista previa
print(df.head())

# Guardar CSV con encabezados correctos
df.to_csv(r"C:\Users\jubeda2\Desktop\Visualizacion_de_Datos_PEC-2\Data\acciones_limpio.csv", index=False)

print("\nDataset 'acciones_limpio.csv' creado correctamente con encabezados y tipos de datos adecuados.")
