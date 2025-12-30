import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================================
# SCRIPT DE LIMPIEZA Y ANÁLISIS EXPLORATORIO
# ============================================================================

def limpiar_base_datos(ruta_csv):
    """
    Limpia la base de datos histórica:
    1. Normaliza decimales (comas → puntos)
    2. Convierte tipos de datos
    3. Identifica missing values
    4. Calcula estadísticas descriptivas
    """
    
    print("=" * 80)
    print("📊 ANÁLISIS EXPLORATORIO - BASE DE DATOS HISTÓRICA")
    print("=" * 80)
    
    # Leer CSV con flexibilidad decimal
    df = pd.read_csv(ruta_csv, decimal=',')
    print(f"\n✅ CSV cargada: {len(df)} registros\n")
    
    # Mostrar estructura
    print("📋 ESTRUCTURA INICIAL:")
    print(df.dtypes)
    print("\n")
    
    # Reemplazar valores problemáticos
    print("🔧 LIMPIEZA EN PROGRESO:")
    
    # Asegurar conversión numérica
    columnas_numericas = ['SPW', 'Mastico_mm', 'Tucker', 'Peso', 'LONGITUD ASSY', 
                          'ANCHO ASSY', 'ALTO ASSY', 'Tiempo_Real_Ofertado']
    
    for col in columnas_numericas:
        try:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            print(f"  ✓ {col:25} → Convertido a numérico")
        except Exception as e:
            print(f"  ✗ {col:25} → Error: {e}")
    
    # Mostrar valores faltantes
    print(f"\n❌ VALORES FALTANTES (NaN):")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(missing[missing > 0])
    else:
        print("  Ninguno encontrado ✓")
    
    # Estadísticas descriptivas
    print("\n📈 ESTADÍSTICAS DESCRIPTIVAS:")
    print(df[columnas_numericas].describe().round(2))
    
    # Correlación con variable objetivo
    print("\n🔗 CORRELACIÓN CON TIEMPO_REAL_OFERTADO:")
    correlaciones = df[columnas_numericas].corr()['Tiempo_Real_Ofertado'].sort_values(ascending=False)
    print(correlaciones.round(3))
    
    # Identificar outliers (método: IQR)
    print("\n⚠️  ANÁLISIS DE OUTLIERS (método IQR):")
    for col in columnas_numericas[:-1]:  # Excluir target
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)]
        if len(outliers) > 0:
            print(f"  {col}: {len(outliers)} outliers detectados")
            print(f"    Rango normal: [{Q1 - 1.5*IQR:.1f}, {Q3 + 1.5*IQR:.1f}]")
    
    # Dataset limpio
    df_clean = df.dropna()
    print(f"\n✅ DATASET LIMPIO: {len(df_clean)} registros (removidos {len(df) - len(df_clean)})")
    
    return df_clean

# ============================================================================
# PASO 2: ANÁLISIS DE VARIABLES
# ============================================================================

def analizar_variables(df):
    """
    Analiza qué variables son relevantes para el modelo
    """
    print("\n" + "=" * 80)
    print("🎯 SELECCIÓN DE VARIABLES PARA REGRESIÓN")
    print("=" * 80)
    
    # Variables de entrada potenciales
    variables_entrada = ['SPW', 'Mastico_mm', 'Tucker', 'Peso', 
                         'LONGITUD ASSY', 'ANCHO ASSY', 'ALTO ASSY']
    variable_salida = 'Tiempo_Real_Ofertado'
    
    print("\n📌 Variables candidatas (entrada):")
    for var in variables_entrada:
        corr = df[var].corr(df[variable_salida])
        r_squared = corr ** 2
        print(f"  • {var:20} | Correlación: {corr:7.3f} | R²: {r_squared:.3f}")
    
    # Detectar multicolinealidad (problemas)
    print("\n⚙️  MULTICOLINEALIDAD (Variables muy relacionadas entre sí):")
    print("    Esto reduce la estabilidad del modelo si ocurre.")
    
    matriz_corr = df[variables_entrada].corr()
    print("\n    Matriz de correlaciones (entrada vs entrada):")
    print(matriz_corr.round(2))
    
    # Identificar pares altamente correlacionados
    print("\n    ⚠️  Pares fuertemente correlacionados (|r| > 0.7):")
    encontrados = False
    for i in range(len(variables_entrada)):
        for j in range(i+1, len(variables_entrada)):
            corr_val = matriz_corr.iloc[i, j]
            if abs(corr_val) > 0.7:
                print(f"      {variables_entrada[i]} ↔ {variables_entrada[j]}: {corr_val:.3f}")
                encontrados = True
    if not encontrados:
        print("      Ninguno encontrado ✓")
    
    return variables_entrada, variable_salida

# ============================================================================
# PASO 3: VARIANZA Y COEFICIENTES DE VARIACIÓN
# ============================================================================

def analizar_varianza(df):
    """
    Calcula coeficiente de variación para identificar variables estables
    """
    print("\n" + "=" * 80)
    print("📊 ANÁLISIS DE VARIANZA (Variabilidad de cada variable)")
    print("=" * 80)
    
    variables_entrada = ['SPW', 'Mastico_mm', 'Tucker', 'Peso', 
                         'LONGITUD ASSY', 'ANCHO ASSY', 'ALTO ASSY']
    
    print("\nCoeficiente de Variación (CV = σ/μ) → Mide variabilidad relativa:\n")
    for var in variables_entrada:
        media = df[var].mean()
        std = df[var].std()
        cv = (std / media * 100) if media != 0 else 0
        print(f"  {var:20} | Media: {media:8.2f} | σ: {std:6.2f} | CV: {cv:6.1f}%")
    
    print("\n  Interpretación:")
    print("    • CV < 20%  → Variable relativamente estable")
    print("    • CV > 50%  → Variable muy volátil")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    ruta_csv = "base_datos_experta.csv"
    
    # Ejecutar análisis
    df_clean = limpiar_base_datos(ruta_csv)
    variables_entrada, variable_salida = analizar_variables(df_clean)
    analizar_varianza(df_clean)
    
    # Guardar CSV limpia
    df_clean.to_csv("base_datos_limpia.csv", index=False, decimal='.')
    print("\n" + "=" * 80)
    print("✅ CSV limpia guardada como: base_datos_limpia.csv")
    print("=" * 80)
