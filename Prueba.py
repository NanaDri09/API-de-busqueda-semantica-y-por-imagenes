import numpy as np
import pandas as pd
from scipy import stats

# Datos de la tabla (tiempos de búsqueda - menor es mejor)
data = {
    'Hibrida_por_texto': [3749.473333, 2214.913368, 3869.554996, 2807.627439, 1624.725342, 
                          2039.379358, 2330.715656, 2085.193157, 2102.631092, 1650.941849,
                          2971.431255, 2403.391838, 2044.250488, 1986.176014, 1742.789268,
                          3571.40255, 2339.571476, 1405.966759, 2284.058332, 2205.309868],
    
    'Semantica': [2337.920427, 1658.061743, 4039.673605, 2367.377996, 1789.17551, 
                  2636.481285, 1812.305212, 1597.095966, 2872.093916, 4479.354858,
                  2617.270708, 2243.708611, 3050.181866, 2424.010038, 8115.447521,
                  18457.8526, 7480.99494, 9878.285408, 1859.395268, 10758.85224],
    
    'BM25': [122.3797798, 2.673625946, 3.871679306, 1.789331436, 1.755952835, 
             2.00343132, 2.145528793, 1.321315765, 0.980615616, 2.007246017,
             1.580476761, 2.014636993, 1.721658978, 2.403497696, 1.106262207,
             1.721382141, 2.175331116, 1.029014587, 2.647399902, 2.128839493],
    
    'RRF': [1402.699947, 2111.261129, 2217.890978, 1703.918219, 9855.326414, 
            5229.185581, 7195.784388, 6723.694324, 2601.258039, 3962.195158,
            4762.002945, 4020.727634, 3040.581942, 4118.658304, 2721.284151,
            2912.617922, 3022.968531, 2169.899702, 1900.454521, 3149.855137],
    
    'Multi-stage': [3233.920813, 2866.203547, 1738.847733, 2547.052383, 2239.471912, 
                    2268.9116, 2692.039967, 5466.775417, 2291.193485, 2642.454147,
                    4815.944433, 1914.433718, 3484.424101, 2400.858164, 2498.087168,
                    3907.11689, 1980.561018, 1867.308817, 1750.705481, 2179.200172],
    
    'Imagenes': [1530.201912, 381.465435, 311.2781048, 295.5157757, 1208.086729, 
                 279.0541649, 257.4284077, 305.9773445, 244.3420887, 252.4869442,
                 374.2022514, 259.0768337, 258.7718964, 339.621067, 262.3782158,
                 226.690144, 245.9828854, 303.9262295, 351.8538475, 251.0898113],
    
    'Caption': [188880.6095, 71476.57037, 19895.19167, 21935.70185, 199133.5418, 
                23470.89958, 104580.9388, 207400.4743, 70574.78571, 74568.52245,
                24858.48951, 24891.2518, 24502.27904, 103683.2569, 24858.48951,
                147458.554, 32781.34966, 55995.0428, 19140.43689, 28092.94891],
    
    'Descripciones': [166551.9416, 101589.1635, 27747.83874, 184265.1687, 196371.4902, 
                      26384.30572, 63209.64932, 152247.7508, 22864.74085, 23067.90018,
                      21905.48801, 25928.41077, 13928.01077, 120574.8222, 29237.1569,
                      186551.8254, 122466.9645, 547555.4242, 100525.8923, 132474.9673],
    
    'Hibrida_por_imagenes': [161669.683, 132950.402, 40401.89695, 37486.2299, 213091.3808, 
                             46794.27028, 176359.9777, 50401.89695, 186029.0542, 98090.7228,
                             59431.82595, 52620.73159, 186200.9439, 110259.3064, 77286.2299,
                             117383.0194, 121972.5568, 77843.3795, 40255.86009, 52959.84387]
}

# Crear DataFrame
df = pd.DataFrame(data)

print("=" * 100)
print("ESTADÍSTICAS DESCRIPTIVAS COMPLETAS - TIEMPOS DE BÚSQUEDA")
print("=" * 100)

# Función para calcular todas las estadísticas descriptivas
def calcular_estadisticas_descriptivas(serie, nombre):
    stats_dict = {
        'Método': nombre,
        'n': len(serie),
        'Media': serie.mean(),
        'Mediana': serie.median(),
        'Moda': serie.mode().iloc[0] if not serie.mode().empty else np.nan,
        'Desv. Estándar': serie.std(),
        'Varianza': serie.var(),
        'Mínimo': serie.min(),
        'Máximo': serie.max(),
        'Rango': serie.max() - serie.min(),
        'Q1 (25%)': serie.quantile(0.25),
        'Q3 (75%)': serie.quantile(0.75),
        'Rango Intercuartílico (IQR)': serie.quantile(0.75) - serie.quantile(0.25),
        'Coef. Variación': (serie.std() / serie.mean()) * 100,
        'Asimetría (Skewness)': serie.skew(),
        'Curtosis': serie.kurtosis(),
        'Suma': serie.sum()
    }
    return stats_dict

# Calcular estadísticas para cada método
estadisticas_completas = []
for columna in df.columns:
    stats_metodo = calcular_estadisticas_descriptivas(df[columna], columna)
    estadisticas_completas.append(stats_metodo)

# Crear DataFrame de resultados
df_estadisticas = pd.DataFrame(estadisticas_completas)

# Mostrar estadísticas principales
print("\n" + "=" * 80)
print("RESUMEN ESTADÍSTICO PRINCIPAL")
print("=" * 80)
columnas_principales = ['Método', 'n', 'Media', 'Mediana', 'Desv. Estándar', 'Mínimo', 'Máximo', 'Coef. Variación']
print(df_estadisticas[columnas_principales].round(4))

print("\n" + "=" * 80)
print("CUARTILES Y DISPERSIÓN")
print("=" * 80)
columnas_cuartiles = ['Método', 'Q1 (25%)', 'Mediana', 'Q3 (75%)', 'Rango Intercuartílico (IQR)']
print(df_estadisticas[columnas_cuartiles].round(4))

print("\n" + "=" * 80)
print("FORMA DE LA DISTRIBUCIÓN")
print("=" * 80)
columnas_forma = ['Método', 'Asimetría (Skewness)', 'Curtosis', 'Coef. Variación']
print(df_estadisticas[columnas_forma].round(4))

# Análisis adicional
print("\n" + "=" * 80)
print("ANÁLISIS COMPARATIVO")
print("=" * 80)

# Método más rápido y más lento (basado en mediana)
metodo_mas_rapido = df_estadisticas.loc[df_estadisticas['Mediana'].idxmin()]
metodo_mas_lento = df_estadisticas.loc[df_estadisticas['Mediana'].idxmax()]

print(f"Método MÁS RÁPIDO: {metodo_mas_rapido['Método']}")
print(f"  - Mediana: {metodo_mas_rapido['Mediana']:.2f}")
print(f"  - Media: {metodo_mas_rapido['Media']:.2f}")

print(f"\nMétodo MÁS LENTO: {metodo_mas_lento['Método']}")
print(f"  - Mediana: {metodo_mas_lento['Mediana']:.2f}")
print(f"  - Media: {metodo_mas_lento['Media']:.2f}")

print(f"\nDiferencia: {metodo_mas_lento['Mediana']/metodo_mas_rapido['Mediana']:.1f}x más lento")

# Métodos con mayor y menor variabilidad
metodo_mas_estable = df_estadisticas.loc[df_estadisticas['Coef. Variación'].idxmin()]
metodo_menos_estable = df_estadisticas.loc[df_estadisticas['Coef. Variación'].idxmax()]

print(f"\nMétodo MÁS ESTABLE (menor Coef. Variación): {metodo_mas_estable['Método']}")
print(f"  - Coef. Variación: {metodo_mas_estable['Coef. Variación']:.2f}%")

print(f"\nMétodo MENOS ESTABLE (mayor Coef. Variación): {metodo_menos_estable['Método']}")
print(f"  - Coef. Variación: {metodo_menos_estable['Coef. Variación']:.2f}%")

# Clasificación por velocidad (mediana)
print("\n" + "=" * 80)
print("CLASIFICACIÓN POR VELOCIDAD (de más rápido a más lento)")
print("=" * 80)
clasificacion = df_estadisticas[['Método', 'Mediana', 'Media']].sort_values('Mediana')
for i, (idx, fila) in enumerate(clasificacion.iterrows(), 1):
    print(f"{i:2d}. {fila['Método']:25s} Mediana: {fila['Mediana']:8.2f} | Media: {fila['Media']:8.2f}")

# Detección de outliers usando el criterio IQR
print("\n" + "=" * 80)
print("DETECCIÓN DE VALORES ATÍPICOS (Outliers)")
print("=" * 80)
for columna in df.columns:
    Q1 = df[columna].quantile(0.25)
    Q3 = df[columna].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    
    outliers = df[columna][(df[columna] < limite_inferior) | (df[columna] > limite_superior)]
    
    if len(outliers) > 0:
        print(f"{columna:25s}: {len(outliers)} outliers - Valores: {list(outliers.round(2))}")
    else:
        print(f"{columna:25s}: Sin outliers")

# Estadísticas resumidas para reporte
print("\n" + "=" * 80)
print("ESTADÍSTICAS PARA INFORME")
print("=" * 80)
print("Método               |   Media  |  Mediana |   DE    |   Mín   |   Máx   |  CV(%)  ")
print("-" * 80)
for _, fila in df_estadisticas.iterrows():
    print(f"{fila['Método']:20s} | {fila['Media']:8.1f} | {fila['Mediana']:8.1f} | {fila['Desv. Estándar']:6.1f} | {fila['Mínimo']:6.1f} | {fila['Máximo']:7.1f} | {fila['Coef. Variación']:6.1f}")

# Exportar a CSV si se desea
exportar = input("\n¿Deseas exportar los resultados a CSV? (s/n): ")
if exportar.lower() == 's':
    df_estadisticas.to_csv('estadisticas_busquedas.csv', index=False, encoding='utf-8')
    print("Archivo 'estadisticas_busquedas.csv' exportado correctamente.")

print("\n" + "=" * 100)
print("ANÁLISIS COMPLETADO")
print("=" * 100)