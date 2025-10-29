# **Guion global de presentación – Técnicas de visualización de datos**

## **1. Introducción**

Hola, soy **Julio Úbeda Quesada**, estudiante del máster en **Ciencia de Datos**.
En esta presentación voy a mostrar tres técnicas de visualización aplicadas a datos financieros de las empresas **Apple (AAPL)**, **Microsoft (MSFT)** y **Google (GOOG)**, extraídos del archivo `acciones_limpio.csv`.
Cada técnica se centra en un enfoque diferente: proporciones, evolución temporal y relación geométrica.

## **2. Primera técnica: Pie Chart o gráfico de pastel**

### **Definición general**

El **pie chart**, introducido por *William Playfair* en 1801 y popularizado por *Florence Nightingale*, representa un conjunto de categorías como sectores proporcionales de un círculo.
Cada sector muestra la **participación relativa** de una categoría respecto al total.

### **Datos y estructura**

Requiere una tabla sencilla con:

* **Categoría** (p. ej. empresa)
* **Valor numérico** (p. ej. volumen medio de negociación)

Adecuado para **pocos grupos** (3 – 6 categorías) y datos **cuantitativos resumidos**.
No se recomienda para series temporales ni grandes volúmenes.

### **Visualización práctica**

Se calculó el **volumen medio** negociado por empresa y se representó con un **gráfico de donut** (variación moderna del pie chart) usando Plotly:

```python
volumen_medio = df.groupby("Ticker")["Volume"].mean().reset_index()
fig = go.Figure([go.Pie(labels=volumen_medio["Ticker"],
                        values=volumen_medio["Volume"],
                        textinfo="label+percent+value",
                        hole=0.3)])
```

### **Interpretación**

El gráfico muestra que **Apple** concentra aproximadamente un **56 % del volumen medio total**, mientras que **Microsoft** y **Google** suman el resto.
Esto refleja **mayor liquidez y actividad bursátil** en Apple.
El objetivo es ofrecer una visión clara y rápida de la **proporción de mercado** de cada empresa.

## **3. Segunda técnica: Candlestick Chart o gráfico de velas japonesas**

### **Definición general**

Desarrollado en el siglo XVIII por el comerciante japonés **Munehisa Homma** y popularizado por **Steve Nison** en 1991, el **candlestick chart** representa la **evolución temporal del precio** de un activo mediante velas con los valores **OHLC** (Open, High, Low, Close).

Cada vela muestra:

* El **cuerpo**: diferencia entre apertura y cierre.
* Las **mechas**: precios máximos y mínimos.
* Color verde/rojo: subida o bajada del precio.

### **Datos y estructura**

Requiere una **serie temporal ordenada** con al menos 30 – 40 observaciones.
Columnas típicas:
| Fecha | Open | High | Low | Close |

Opcionalmente puede incluir un **ticker** o indicador como la **media móvil (SMA20)**.

### **Visualización práctica**

Con Plotly Graph Objects se graficaron las velas de las tres empresas junto con sus medias móviles:

```python
fig.add_trace(go.Candlestick(x=sub_df["Date"],
                             open=sub_df["Open"],
                             high=sub_df["High"],
                             low=sub_df["Low"],
                             close=sub_df["Close"],
                             name=ticker))
```

Se añadió una línea discontinua de **SMA20** para suavizar la tendencia.

### **Interpretación**

El gráfico muestra la **evolución diaria de precios entre 2023 y 2024**.
Se observan **tendencias alcistas**, con **mayor volatilidad en Apple**, cuyos cuerpos de vela son más amplios.
Las medias móviles ayudan a detectar fases de consolidación y cambios de tendencia.
El objetivo comunicativo es **mostrar de forma dinámica la evolución histórica y comparativa de precios**.

## **4. Tercera técnica: Envolvente Convexa (*Convex Hull*)**

### **Definición general**

La **envolvente convexa** o *Convex Hull* es un concepto de **geometría computacional** que forma el **polígono convexo mínimo** que contiene un conjunto de puntos.
Imaginemos una goma elástica rodeando los puntos: esa forma es la envolvente.

Desarrollada en los años 70 mediante algoritmos como:

* *Graham Scan*
* *Quickhull*
* *Marcha de Jarvis*

### **Aplicaciones**

Se usa en:

* **Optimización financiera** (fronteras eficientes)
* **Detección de anomalías**
* **Análisis espacial** o **clustering**

### **Datos y estructura**

Utiliza pares de coordenadas **(x, y)** cuantitativos.
En este caso:

* **X:** precio de apertura
* **Y:** precio de cierre
  Requiere al menos **3 puntos no colineales** y es sensible a valores extremos.

### **Visualización práctica**

Se calculó con `scipy.spatial.ConvexHull` y se visualizó con Plotly, mostrando los puntos y la envolvente por empresa.

Cada área coloreada delimita el **espacio de variabilidad de precios**.

### **Interpretación**

Las envolventes permiten comparar la **dispersión y estabilidad** de las acciones:

* **Apple:** envolvente más estrecha → menor volatilidad
* **Microsoft:** mayor dispersión → más riesgo
* **Google:** comportamiento intermedio

La técnica permite identificar **límites de comportamiento y valores anómalos**, siendo útil para análisis exploratorios y financieros.

## **5. Cierre y síntesis**

En resumen:

* El **Pie Chart** muestra proporciones globales.
* El **Candlestick** revela evolución temporal y volatilidad.
* El **Convex Hull** delimita el espacio de variación y posibles anomalías.

Estas tres técnicas combinan **claridad visual, diversidad analítica y aplicabilidad práctica** a datos reales del mercado financiero.
