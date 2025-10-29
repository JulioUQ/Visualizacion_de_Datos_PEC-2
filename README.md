# Técnicas de Visualización de Datos – PEC 2

Este proyecto forma parte del Máster en **Ciencia de Datos** y presenta tres técnicas de visualización aplicadas a datos financieros de **Apple (AAPL)**, **Microsoft (MSFT)** y **Google (GOOG)**, extraídos del archivo `acciones_limpio.csv`.

Autor: **Julio Úbeda Quesada**

## Descripción general

El objetivo del proyecto es ilustrar distintos enfoques de **visualización de datos financieros**, combinando perspectivas de proporción, evolución temporal y análisis geométrico.

Las tres técnicas presentadas son:

1. **Pie Chart (Gráfico de pastel)**  
   - Representa proporciones relativas entre categorías.  
   - En este caso, muestra el **volumen medio de negociación** por empresa.  
   - Tecnología usada: `Plotly`.

2. **Candlestick Chart (Gráfico de velas japonesas)**  
   - Visualiza la **evolución temporal de precios (OHLC)**.  
   - Permite observar tendencias, volatilidad y fases de consolidación.  
   - Tecnología usada: `Plotly Graph Objects`.

3. **Convex Hull (Envolvente convexa)**  
   - Representa el **polígono convexo mínimo** que contiene un conjunto de puntos.  
   - Permite analizar **dispersión y estabilidad** de precios entre empresas.  
   - Tecnología usada: `scipy.spatial.ConvexHull` y `Plotly`.

## Estructura de los datos

Archivo principal: `acciones_limpio.csv`

Columnas principales:
| Columna | Descripción |
|----------|--------------|
| Date     | Fecha de registro |
| Ticker   | Código bursátil (AAPL, MSFT, GOOG) |
| Open     | Precio de apertura |
| High     | Precio máximo |
| Low      | Precio mínimo |
| Close    | Precio de cierre |
| Volume   | Volumen negociado |