# ==============================================
# VISUALIZACIONES FINANCIERAS CON PLOTLY
# ==============================================

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.spatial import ConvexHull
import yfinance as yf
import pandas as pd

# -------------------------------------------------
# CARGA DE DATOS
# -------------------------------------------------
# Lista de empresas (puedes añadir más tickers si lo deseas)
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
df.to_csv("acciones_limpio.csv", index=False)

# -------------------------------------------------
# VISUALIZACIÓN 1: PIE CHART (Distribución Volumen)
# -------------------------------------------------

volumen_medio = df.groupby("Ticker")["Volume"].mean().reset_index()

pie_fig = go.Pie(
    labels=volumen_medio["Ticker"],
    values=volumen_medio["Volume"],
    textinfo="label+percent+value",
    hovertemplate="<b>%{label}</b><br>Volumen medio: %{value:,.0f}<br>%{percent}",
    textposition="auto",
    # Comentario: usar hole=0.3 para crear un donut chart más moderno
    hole=0.3,
    marker=dict(line=dict(color="#FFFFFF", width=2))
)

pie_layout = go.Layout(
    title="Distribución del volumen medio por empresa",
    showlegend=False
)

pie_chart = go.Figure(data=[pie_fig], layout=pie_layout)


# -------------------------------------------------
# VISUALIZACIÓN 2: CANDLESTICK CHART (Evolución temporal)
# -------------------------------------------------

# Creamos la figura base con subplots
fig_candlestick = make_subplots(rows=1, cols=1, subplot_titles=["Evolución temporal de precios"])

# Tickers únicos
tickers = df["Ticker"].unique()

# Agregamos un trace por cada ticker (se muestran alternadamente)
for ticker in tickers:
    sub_df = df[df["Ticker"] == ticker]
    trace = go.Candlestick(
        x=sub_df["Date"],
        open=sub_df["Open"],
        high=sub_df["High"],
        low=sub_df["Low"],
        close=sub_df["Close"],
        name=ticker,
        increasing_line_color="#00CC96",  # verde-azul para días alcistas
        decreasing_line_color="#EF553B",  # rojo para días bajistas
        visible=True if ticker == tickers[0] else False
    )
    fig_candlestick.add_trace(trace)

# Selector dropdown para elegir ticker
buttons = []
for i, ticker in enumerate(tickers):
    visible = [False] * len(tickers)
    visible[i] = True
    buttons.append(
        dict(label=ticker,
             method="update",
             args=[{"visible": visible},
                   {"title": f"Evolución de precios OHLC: {ticker}"}])
    )

fig_candlestick.update_layout(
    updatemenus=[dict(active=0, buttons=buttons, x=0.15, xanchor="left", y=1.1, yanchor="top")],
    xaxis_title="Fecha",
    yaxis_title="Precio ($)",
    xaxis_rangeslider_visible=True,
    title="Evolución de precios OHLC",
    template="plotly_white"
)

# -------------------------------------------------
# VISUALIZACIÓN 3: CONVEX HULL (Open vs Close)
# -------------------------------------------------

fig_hull = go.Figure()

colors = {"AAPL": "#1f77b4", "MSFT": "#2ca02c", "GOOG": "#ff7f0e"}

for ticker in tickers:
    sub_df = df[df["Ticker"] == ticker]
    points = sub_df[["Open", "Close"]].values

    # Calcular envolvente convexa
    hull = ConvexHull(points)
    hull_points = points[hull.vertices]

    # Scatter de puntos
    fig_hull.add_trace(go.Scatter(
        x=sub_df["Open"],
        y=sub_df["Close"],
        mode="markers",
        name=f"{ticker}",
        opacity=0.6,
        marker=dict(size=6, color=colors[ticker]),
        hovertemplate=(
            f"<b>{ticker}</b><br>"
            "Fecha: %{text}<br>"
            "Open: %{x:.2f}<br>"
            "Close: %{y:.2f}"
        ),
        text=sub_df["Date"].dt.strftime("%Y-%m-%d")
    ))

    # Línea de la envolvente convexa
    fig_hull.add_trace(go.Scatter(
        x=np.append(hull_points[:, 0], hull_points[0, 0]),
        y=np.append(hull_points[:, 1], hull_points[0, 1]),
        mode="lines",
        line=dict(color=colors[ticker], width=2),
        name=f"Convex Hull - {ticker}"
    ))

# Línea de referencia y=x
fig_hull.add_trace(go.Scatter(
    x=[df["Open"].min(), df["Open"].max()],
    y=[df["Open"].min(), df["Open"].max()],
    mode="lines",
    line=dict(color="gray", dash="dash"),
    name="y = x (Open = Close)"
))

fig_hull.update_layout(
    title="🔷 Relación entre precio de apertura y cierre con Envolvente Convexa",
    xaxis_title="Precio de apertura (Open)",
    yaxis_title="Precio de cierre (Close)",
    legend_title="Ticker",
    template="plotly_white"
)

# -------------------------------------------------
# LAYOUT GENERAL EN GRID
# -------------------------------------------------

from plotly.subplots import make_subplots

# Definir tipos: 'domain' para el pie chart, 'xy' para los otros
fig_final = make_subplots(
    rows=2, cols=2,
    specs=[
        [{"type": "domain", "colspan": 2}, None],  # Pie chart arriba
        [{"type": "xy"}, {"type": "xy"}]           # Candlestick y Convex Hull abajo
    ],
    subplot_titles=("Distribución Volumen Medio", "Candlestick Chart", "Envolvente Convexa")
)

# Añadir pie chart (fila 1)
for trace in pie_chart.data:
    fig_final.add_trace(trace, row=1, col=1)

# Añadir candlestick (fila 2, col 1)
for trace in fig_candlestick.data:
    fig_final.add_trace(trace, row=2, col=1)

# Añadir convex hull (fila 2, col 2)
for trace in fig_hull.data:
    fig_final.add_trace(trace, row=2, col=2)

# Ajustes generales
fig_final.update_layout(
    height=1000,
    showlegend=True,
    template="plotly_white",
    title_text="Análisis Financiero de Acciones — Pie Chart, Candlestick y Convex Hull",
)

fig_final.write_html("visualizaciones_financieras.html")
fig_final.show()

