########################################
#### LIBRERIAS NECESARIAS           ####
import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import warnings
warnings.simplefilter(action='ignore', category=UserWarning)

import xlwings as xw

import pandas as pd
from pandas._typing import MergeHow
########################################

def xlimport():
    """
    Importa los datos de la región actual de Excel como un DataFrame de pandas.
    
    :return: DataFrame con los datos importados desde Excel.
    """
    data = xw.books.active.app.selection.current_region.value # type: ignore
    return pd.DataFrame(data[1:], columns=data[0]) # type: ignore

def xlexport(df):
    '''
    Esta funcion exporta la el DataFrame 'df' a la celda activa de excel
    
    :param df: Dataframe de pandas.
    '''
    xw.books.active.app.selection.options(index=False).value = df # type: ignore


def get_excel_sheet_names(excel_path):
    """
    Retorna una lista con los nombres de las hojas en un archivo Excel.
    """
    try:
        with pd.ExcelFile(excel_path) as xls:
            return xls.sheet_names
    except Exception as e:
        print(f"Error al obtener los nombres de las hojas: {e}")
        return []

def load_excel_sheets(path, sheet_name=None):
    """
    Carga hojas de un archivo Excel en DataFrames.

    Parámetros:
        path (str): Ruta del archivo Excel.
        sheet_name (str, opcional): Nombre de la hoja a cargar. 
                                     Si no se indica, carga todas las hojas.

    Retorna:
        dict o DataFrame: 
            - Si sheet_name es None, retorna un diccionario {hoja: DataFrame}.
            - Si se especifica sheet_name, retorna directamente el DataFrame de esa hoja.
    """
    hojas = get_excel_sheet_names(path)
    if not hojas:
        raise FileNotFoundError(f"No se pudieron leer hojas del archivo: {path}")

    if sheet_name:
        if sheet_name not in hojas:
            raise ValueError(f"La hoja '{sheet_name}' no existe en el archivo. Hojas disponibles: {hojas}")
        return pd.read_excel(path, sheet_name=sheet_name)
    else:
        dfs = {hoja: pd.read_excel(path, sheet_name=hoja) for hoja in hojas}
        return dfs



def exportar_excel(file_path, sheets):
    """
    Exporta múltiples DataFrames a un archivo Excel, cada uno en su propia hoja.

    Parámetros:
        file_path (str): Ruta completa del archivo Excel a crear.
        sheets (list de tuplas): Cada tupla debe contener ('nombre_hoja', DataFrame).
                                 Ejemplo: [('Hoja1', df1), ('Hoja2', df2)]
    Ejemplo de uso:
        exportar_excel('ruta/del/archivo.xlsx', [('Hoja1', df1), ('Hoja2', df2)])
    """
    if not sheets:
        raise ValueError("No se han proporcionado hojas para exportar.")

    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for nombre_hoja, df in sheets:
            if not isinstance(df, pd.DataFrame):
                raise TypeError(f"El objeto para la hoja '{nombre_hoja}' no es un DataFrame.")
            df.to_excel(writer, sheet_name=nombre_hoja, index=False)

    print(f"Archivo '{file_path}' creado con {len(sheets)} hoja(s): {', '.join([n for n,_ in sheets])}.")


def describe_df(data):
    """
    Proporciona un resumen del DataFrame, incluyendo forma, tipos de datos, estadísticas básicas,
    conteo de valores nulos, valores únicos, mediana y rango de fechas para columnas tipo datetime.

    :param data: DataFrame de pandas.
    :return: DataFrame con el resumen del DataFrame dado.
    """
    # Crear base del resumen
    total = len(data)
    summary = pd.DataFrame({
        'Column': data.columns,
        'Data Type': data.dtypes.astype(str),
        'Non-null Count': data.count().values,
        '% Null Values': ((data.isnull().sum() / total) * 100).round(2).values,
        'Unique Values': data.nunique().values
    })

    summary['Shape'] = f"{data.shape[0]} rows, {data.shape[1]} columns"

    # Estadísticas para columnas numéricas
    numeric_cols = data.select_dtypes(include=['number']).columns
    if not numeric_cols.empty:
        describe_stats = data[numeric_cols].describe().T
        describe_stats = describe_stats.rename(columns={'50%': 'median'})[
            ['mean', 'median', 'std', 'min', '25%',  '75%', 'max']
        ]
        describe_stats.reset_index(inplace=True)
        describe_stats.rename(columns={'index': 'Column'}, inplace=True)

        summary = pd.merge(summary, describe_stats, on='Column', how='left')

    # Rango de fechas para columnas datetime
    datetime_cols = data.select_dtypes(include=['datetime', 'datetime64[ns]']).columns
    if not datetime_cols.empty:
        date_ranges = pd.DataFrame({
            'Column': datetime_cols,
            'Min Date': data[datetime_cols].min().values,
            'Max Date': data[datetime_cols].max().values
        })
        summary = pd.merge(summary, date_ranges, on='Column', how='left')

    return summary


def resumir_metricas(df, niveles, columnas_metricas, metricas, orden=None, ascendente=True, incluir_total=False):
    """
    Agrupa el DataFrame según los niveles dados, aplica métricas a columnas seleccionadas y permite ordenar el resultado.

    Args:
        df (pd.DataFrame): El DataFrame de entrada.
        niveles (list): Columnas por las cuales agrupar.
        columnas_metricas (list): Columnas numéricas sobre las que se aplicarán las métricas.
        metricas (list or dict): Lista de métricas (como 'sum', 'mean') o diccionario tipo {'columna': ['sum', 'mean']}.
        orden (str or list, optional): Columna(s) por las cuales ordenar el resultado.
        ascendente (bool or list, optional): Orden ascendente o descendente.
        incluir_total (bool, optional): Si True, añade una fila con el sumatorio de las columnas numéricas.

    Returns:
        pd.DataFrame: DataFrame con métricas agregadas, ordenado si se especifica, y fila de total si se solicita.

    Ejemplo:
    resumir_metricas(df_grouped, ['Nacionalidad', 'CFR'], ['Peso Desembarque', 'CFR'], 
                 {'Peso Desembarque': ['sum', 'mean'], 
                  'CFR': 'nunique'}, 
                 orden='Peso Desembarque_sum', ascendente=False)

    """
    
    resumen = df.groupby(niveles, dropna=False)[columnas_metricas].agg(metricas).reset_index()

    # Si se pasa una sola métrica por columna, los nombres de columnas son simples.
    # Si hay múltiples, el resultado es un MultiIndex que se puede aplanar.
    if isinstance(resumen.columns, pd.MultiIndex):
        resumen.columns = ['_'.join(col).strip('_') for col in resumen.columns.values]

    if orden:
        resumen = resumen.sort_values(by=orden, ascending=ascendente)

    # Añadir fila de total si se solicita
    if incluir_total:
        # Crear fila de total
        fila_total = {}
        
        # Para las columnas de agrupación, solo la primera columna lleva 'TOTAL'
        for i, nivel in enumerate(niveles):
            if i == 0:
                fila_total[nivel] = 'TOTAL'
            else:
                fila_total[nivel] = ''
        
        # Para las columnas numéricas, calcular la suma
        for col in resumen.columns:
            if col not in niveles:
                # Verificar si la columna es numérica
                if pd.api.types.is_numeric_dtype(resumen[col]):
                    fila_total[col] = resumen[col].sum()
                else:
                    fila_total[col] = '-'
        
        # Crear DataFrame con la fila total y concatenar
        df_total = pd.DataFrame([fila_total])
        
        # Asegurar que las columnas estén en el mismo orden
        df_total = df_total.reindex(columns=resumen.columns)
        
        # Concatenar el resumen con la fila total
        resumen = pd.concat([resumen, df_total], ignore_index=True)

    return resumen

def detect_duplicates(df):
    """
    Detecta duplicados en un DataFrame y devuelve un nuevo DataFrame con los duplicados.

    :param df: DataFrame de pandas.
    :return: DataFrame con los duplicados detectados.
    """
    try:
        return df[df.duplicated(keep=False)]
    except Exception as e:
        print("Error detectando duplicados:", e)
        return None

def unique_df(df):
    """
    Imprime un resumen de las categorías únicas para las variables categóricas de un DataFrame.

    :param df: DataFrame de pandas.
    """
    categorical_columns = df.select_dtypes(include=['category', 'object']).columns

    if len(categorical_columns) == 0:
        print("No se encontraron columnas categóricas u objeto en el DataFrame.")
        return

    for column in categorical_columns:
        print(f"Resumen para la columna '{column}':\n{df[column].unique()}\n")


def merge_tables(
    table1, 
    table2, 
    left_index, 
    right_index, 
    columns_table1=None, 
    columns_table2=None, 
    how: 'MergeHow' = 'inner'
):
    """
    Realiza una unión (merge) entre dos DataFrames utilizando columnas clave diferentes y seleccionando columnas específicas.

    Esta función permite combinar dos tablas (DataFrames) especificando las columnas clave para cada una 
    (que pueden tener nombres distintos) y seleccionar las columnas deseadas de cada tabla antes del merge.

    Parámetros:
    ----------
    table1 : pd.DataFrame
        Primer DataFrame a unir.
    table2 : pd.DataFrame
        Segundo DataFrame a unir.
    left_index : str
        Nombre de la columna clave en la primera tabla.
    right_index : str
        Nombre de la columna clave en la segunda tabla.
    columns_table1 : list[str], opcional
        Columnas a conservar de la primera tabla. Si es None, se usan todas.
    columns_table2 : list[str], opcional
        Columnas a conservar de la segunda tabla. Si es None, se usan todas.
    how : str, opcional
        Tipo de unión a realizar: 'left', 'right', 'outer' o 'inner'. Por defecto es 'inner'.

    Retorna:
    -------
    pd.DataFrame
        Un nuevo DataFrame resultante de unir las dos tablas.

    Ejemplo:
    -------
    df1 = pd.DataFrame({'id_a': [1, 2], 'nombre': ['Ana', 'Luis']})
    df2 = pd.DataFrame({'id_b': [1, 2], 'edad': [30, 25]})
    merge_tables(df1, df2, 'id_a', 'id_b')
       id_a nombre  id_b  edad
    0     1    Ana     1    30
    1     2   Luis     2    25
    """

    if not isinstance(table1, pd.DataFrame) or not isinstance(table2, pd.DataFrame):
        raise TypeError("Ambos argumentos table1 y table2 deben ser DataFrames de pandas.")

    if left_index not in table1.columns:
        raise KeyError(f"La columna '{left_index}' no se encuentra en la primera tabla.")
    
    if right_index not in table2.columns:
        raise KeyError(f"La columna '{right_index}' no se encuentra en la segunda tabla.")

    if columns_table1:
        missing_cols1 = set(columns_table1) - set(table1.columns)
        if missing_cols1:
            raise KeyError(f"Columnas no encontradas en table1: {missing_cols1}")
        table1 = table1[columns_table1 + [left_index]] if left_index not in columns_table1 else table1[columns_table1]

    if columns_table2:
        missing_cols2 = set(columns_table2) - set(table2.columns)
        if missing_cols2:
            raise KeyError(f"Columnas no encontradas en table2: {missing_cols2}")
        table2 = table2[columns_table2 + [right_index]] if right_index not in columns_table2 else table2[columns_table2]

    merged_table = pd.merge(table1, table2, left_on=left_index, right_on=right_index, how=how)
    return merged_table

def diff_in_columns(df1, col1, df2, col2, encontrar_no_en_col2=True):
    """
    Encuentra los elementos únicos en la columna col1 de df1 que no están en la columna col2 de df2
    o los elementos únicos en col1 que sí están en col2.

    :param df1: Primer DataFrame.
    :param col1: Nombre de la columna en df1.
    :param df2: Segundo DataFrame.
    :param col2: Nombre de la columna en df2.
    :param encontrar_no_en_col2: Si es True, encuentra los elementos en col1 que no están en col2. Si es False, encuentra los elementos en col1 que sí están en col2.
    :return: Conjunto de elementos únicos según la condición especificada.
    """
    # Obtiene los valores únicos de la columna col1 en df1
    lista1 = df1[col1].unique()
    
    # Obtiene los valores únicos de la columna col2 en df2
    lista2 = df2[col2].unique()
    
    # Convierte las listas en conjuntos
    set_lista1 = set(lista1)
    set_lista2 = set(lista2)
    
    # Encuentra los elementos según la condición especificada
    if encontrar_no_en_col2:
        elementos_resultado = set_lista1 - set_lista2
    else:
        elementos_resultado = set_lista1.intersection(set_lista2)
    
    return elementos_resultado