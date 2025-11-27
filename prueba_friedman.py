import numpy as np
import pandas as pd
from scipy import stats
import scikit_posthocs as sp

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

print("=" * 80)
print("PRUEBA DE FRIEDMAN - COMPARACIÓN DE TIEMPOS DE BÚSQUEDA")
print("=" * 80)
print("SUPUESTO: MENOR valor = MEJOR rendimiento (tiempos más bajos)")

# 1. Calcular rankings por fila (MENOR valor = mejor = rango 1)
ranked_data = df.rank(axis=1, ascending=True, method='average')

print("\n" + "=" * 50)
print("RANKINGS POR FILA (1 = mejor tiempo, 9 = peor tiempo)")
print("=" * 50)

# 2. Calcular suma de rangos por método
rank_sums = ranked_data.sum()
average_ranks = rank_sums / len(df)

print("\nSUMA DE RANGOS POR MÉTODO:")
print("-" * 50)
for method, sum_rank in rank_sums.items():
    print(f"{method:25s}: {sum_rank:8.2f} (Promedio: {average_ranks[method]:.2f})")

# 3. Prueba de Friedman usando scipy
print("\n" + "=" * 50)
print("PRUEBA DE FRIEDMAN - RESULTADOS")
print("=" * 50)

friedman_stat, p_value = stats.friedmanchisquare(*[df[col] for col in df.columns])

print(f"Estadístico de Friedman (χ²): {friedman_stat:.6f}")
print(f"Valor p: {p_value:.20f}")

# 4. Interpretación
alpha = 0.05
print(f"\nNivel de significancia (α): {alpha}")

if p_value < alpha:
    print("✓ RESULTADO: Se rechaza la hipótesis nula")
    print("  → Existen diferencias SIGNIFICATIVAS entre los métodos")
    print("  → Los tiempos de búsqueda NO son iguales entre todos los métodos")
else:
    print("✓ RESULTADO: No se rechaza la hipótesis nula")  
    print("  → NO existen diferencias significativas entre los métodos")

# 5. Prueba post-hoc de Nemenyi
print("\n" + "=" * 50)
print("PRUEBA POST-HOC DE NEMENYI")
print("=" * 50)

try:
    nemenyi_result = sp.posthoc_nemenyi_friedman(df)
    print("Matriz de valores p (Nemenyi):")
    print(nemenyi_result.round(6))
    
    # Identificar diferencias significativas
    print(f"\nDIFERENCIAS SIGNIFICATIVAS (p < {alpha}):")
    print("-" * 60)
    
    significant_pairs = []
    methods = df.columns
    
    for i in range(len(methods)):
        for j in range(i+1, len(methods)):
            p_val = nemenyi_result.iloc[i, j]
            if p_val < alpha:
                significant_pairs.append((methods[i], methods[j], p_val, 
                                        average_ranks[i], average_ranks[j]))
    
    if significant_pairs:
        print(f"Se encontraron {len(significant_pairs)} pares significativos:")
        print()
        for pair in significant_pairs:
            metodo1, metodo2, p_val, rank1, rank2 = pair
            print(f"  {metodo1:20s} vs {metodo2:20s}: p = {p_val:.15f}")
    else:
        print("  No se encontraron pares significativos con Nemenyi")
        
except ImportError:
    print("Para la prueba post-hoc, instala: pip install scikit-posthocs")

# 6. Resumen de rendimiento
print("\n" + "=" * 50)
print("RESUMEN DE RENDIMIENTO (ordenado por eficiencia)")
print("=" * 50)

performance_summary = pd.DataFrame({
    'Método': df.columns,
    'Suma_Rangos': rank_sums,
    'Ranking_Promedio': average_ranks,
    'Mediana_Tiempo': df.median(),
    'Media_Tiempo': df.mean()
})

# Ordenar de MEJOR a PEOR (ranking promedio más bajo = mejor)
performance_summary = performance_summary.sort_values('Ranking_Promedio', ascending=True)

print("\nCLASIFICACIÓN DE MÉTODOS (de más rápido a más lento):")
print("-" * 70)
for idx, row in performance_summary.iterrows():
    print(f"{row['Método']:25s}: Ranking {row['Ranking_Promedio']:4.2f} | "
          f"Mediana: {row['Mediana_Tiempo']:8.1f}")

# 7. Análisis de grupos
print("\n" + "=" * 50)
print("ANÁLISIS DE GRUPOS DE RENDIMIENTO")
print("=" * 50)

# Identificar grupos naturales basados en diferencias en rankings
ranking_groups = {
    "Grupo 1 - Muy rápidos": [],
    "Grupo 2 - Rápidos": [],
    "Grupo 3 - Moderados": [],
    "Grupo 4 - Lentos": [],
    "Grupo 5 - Muy lentos": []
}

for idx, row in performance_summary.iterrows():
    rank = row['Ranking_Promedio']
    if rank <= 2:
        ranking_groups["Grupo 1 - Muy rápidos"].append(row['Método'])
    elif rank <= 4:
        ranking_groups["Grupo 2 - Rápidos"].append(row['Método'])
    elif rank <= 6:
        ranking_groups["Grupo 3 - Moderados"].append(row['Método'])
    elif rank <= 8:
        ranking_groups["Grupo 4 - Lentos"].append(row['Método'])
    else:
        ranking_groups["Grupo 5 - Muy lentos"].append(row['Método'])

for group_name, methods in ranking_groups.items():
    if methods:
        print(f"{group_name}: {', '.join(methods)}")

print("\n" + "=" * 80)
print("CONCLUSIÓN FINAL")
print("=" * 80)

if p_value < alpha:
    best_method = performance_summary.iloc[0]['Método']
    worst_method = performance_summary.iloc[-1]['Método']
    best_median = performance_summary.iloc[0]['Mediana_Tiempo']
    worst_median = performance_summary.iloc[-1]['Mediana_Tiempo']
    
    print(f"✓ RESULTADO ESTADÍSTICAMENTE SIGNIFICATIVO")
    print(f"✓ Se rechaza H0: Los métodos tienen tiempos de búsqueda diferentes")
    print(f"✓ Método MÁS RÁPIDO: {best_method} (mediana: {best_median:.1f})")
    print(f"✓ Método MÁS LENTO: {worst_method} (mediana: {worst_median:.1f})")
    print(f"✓ Diferencia: {worst_median/best_median:.0f}x más lento")
    print(f"✓ Número de comparaciones significativas: {len(significant_pairs)}")
    
else:
    print("✓ No hay diferencias estadísticamente significativas entre los métodos")
    print("✓ Todos los métodos tienen tiempos de búsqueda similares")

print("\n" + "=" * 80)