"""
===============================================================================
📊 MÓDULO DE REGRESIÓN LINEAL MÚLTIPLE
===============================================================================

TEORÍA MATEMÁTICA:
------------------
Objetivo: Predecir Tiempo_Real_Ofertado basándose en múltiples variables

Modelo matemático:
    Tiempo = β₀ + β₁·SPW + β₂·Peso + β₃·ANCHO_ASSY + β₄·ALTO_ASSY + ε

Donde:
    β₀     = Intercept (tiempo base sin variables)
    β₁...β₄ = Coeficientes (pesos) - PONDERACIÓN de cada variable
    ε     = Error residual (lo que el modelo no explica)

CÁLCULO:
    El algoritmo Mínimos Cuadrados Ordinarios (OLS) encuentra los β que 
    minimizan la suma de cuadrados del error:
    
    min Σ(yᵢ - ŷᵢ)²  para i=1 a n
    
    Solución (forma matricial):
    β = (X^T·X)⁻¹·X^T·y

MÉTRICAS DE CALIDAD:
    • R² (Coef. Determinación): 0-1. Qué % de varianza explica el modelo
    • RMSE: Error cuadrático medio. Unidades: segundos
    • MAE: Error absoluto medio. Unidades: segundos
    • p-value: Significancia estadística. <0.05 = significativo

INTERPRETACIÓN DE PESOS:
    Si β₁ = 0.8 (SPW):
        → Un punto SPW adicional aumenta el tiempo 0.8 segundos
    
    Si β₂ = 2.5 (Peso):
        → 1 kg adicional aumenta el tiempo 2.5 segundos
    
    Comparación de impacto:
    2.5 / 0.8 = 3.125 → El Peso es 3.125x más importante que SPW

===============================================================================
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pickle
import json
from pathlib import Path
import matplotlib.pyplot as plt

class ModeloRegresionLineal:
    """
    Modelo de regresión lineal múltiple para estimar tiempos de ciclo.
    
    Atributos:
        modelo: Objeto LinearRegression de sklearn
        scaler: StandardScaler para normalizar variables
        variables_entrada: Lista de variables usadas como entrada
        variable_salida: Nombre de la variable a predecir
        coeficientes: Dict con pesos de cada variable
        r2_score: Bondad del ajuste
        rmse: Error cuadrático medio
        historial_entrenamiento: Datos del entrenamiento
    """
    
    def __init__(self):
        self.modelo = None
        self.scaler = StandardScaler()
        self.variables_entrada = None
        self.variable_salida = 'Tiempo_Real_Ofertado'
        self.coeficientes = {}
        self.r2_score = None
        self.rmse = None
        self.mae = None
        self.historial_entrenamiento = {}
        self.datos_entrenamiento = None
        
    # ========================================================================
    # PASO 1: SELECCIONAR VARIABLES (Feature Selection)
    # ========================================================================
    
    def seleccionar_variables(self, df, umbral_correlacion=0.5):
        """
        Selecciona variables que tengan correlación significativa con el target.
        
        Args:
            df: DataFrame limpio
            umbral_correlacion: Mínimo R² (varianza explicada) para incluir
        
        Returns:
            Lista de variables seleccionadas
        """
        print("\n" + "="*80)
        print("🎯 PASO 1: SELECCIÓN DE VARIABLES")
        print("="*80)
        
        # Solo usar columnas numéricas (excluir Proyecto)
        df_numerico = df.select_dtypes(include=[np.number])
        correlaciones = df_numerico.corr()[self.variable_salida].drop(self.variable_salida)
        r_squared = correlaciones ** 2
        
        # Filtrar variables válidas (sin NaN y con correlación mínima)
        variables_validas = r_squared[
            (~r_squared.isna()) & (r_squared.abs() >= umbral_correlacion)
        ].sort_values(ascending=False)
        
        print(f"\n📌 Umbral de correlación (R²): {umbral_correlacion}")
        print(f"\n✅ Variables seleccionadas ({len(variables_validas)}):\n")
        
        for var, r2 in variables_validas.items():
            print(f"  • {var:20} → R² = {r2:.4f} (explica {r2*100:.1f}% de varianza)")
        
        self.variables_entrada = variables_validas.index.tolist()
        self.historial_entrenamiento['variables_seleccionadas'] = self.variables_entrada
        
        return self.variables_entrada
    
    # ========================================================================
    # PASO 2: ENTRENAR MODELO
    # ========================================================================
    
    def entrenar(self, df):
        """
        Entrena el modelo de regresión lineal.
        
        Args:
            df: DataFrame limpio con variables
        """
        print("\n" + "="*80)
        print("⚙️  PASO 2: ENTRENAMIENTO DEL MODELO")
        print("="*80)
        
        # Preparar datos
        X = df[self.variables_entrada].values
        y = df[self.variable_salida].values
        
        print(f"\n📊 Datos de entrenamiento:")
        print(f"   • Muestras: {len(df)}")
        print(f"   • Variables: {len(self.variables_entrada)}")
        print(f"   • Rango objetivo: [{y.min():.1f}s, {y.max():.1f}s]")
        
        # Entrenar modelo
        self.modelo = LinearRegression()
        self.modelo.fit(X, y)
        
        # Predecir sobre mismos datos
        y_pred = self.modelo.predict(X)
        
        # Calcular métricas
        self.r2_score = r2_score(y, y_pred)
        self.rmse = np.sqrt(mean_squared_error(y, y_pred))
        self.mae = mean_absolute_error(y, y_pred)
        
        print(f"\n📈 RESULTADOS DEL ENTRENAMIENTO:")
        print(f"   • R² score: {self.r2_score:.4f} ⟹ Explica {self.r2_score*100:.1f}% de varianza")
        print(f"   • RMSE: {self.rmse:.2f} segundos")
        print(f"   • MAE: {self.mae:.2f} segundos")
        
        # Calcular coeficientes (pesos)
        self._calcular_pesos()
        
        # Guardar datos
        self.datos_entrenamiento = df
        self.historial_entrenamiento['r2'] = self.r2_score
        self.historial_entrenamiento['rmse'] = self.rmse
        self.historial_entrenamiento['mae'] = self.mae
        
    # ========================================================================
    # PASO 3: CALCULAR Y MOSTRAR PESOS
    # ========================================================================
    
    def _calcular_pesos(self):
        """
        Calcula e interpreta los coeficientes (pesos) del modelo.
        Esto muestra la PONDERACIÓN de cada variable.
        """
        print(f"\n" + "="*80)
        print("⚖️  PONDERACIÓN DE VARIABLES (Coeficientes)")
        print("="*80)
        
        # Intercept
        intercept = self.modelo.intercept_
        print(f"\n📌 Tiempo Base (sin variables): {intercept:.2f} segundos")
        
        # Coeficientes
        coefs = self.modelo.coef_
        self.coeficientes = {var: coef for var, coef in zip(self.variables_entrada, coefs)}
        
        # Ordenar por magnitud
        coefs_ordenados = sorted(self.coeficientes.items(), key=lambda x: abs(x[1]), reverse=True)
        
        print(f"\n⚖️  PESOS (de más a menos importante):\n")
        print(f"  {'Variable':<20} | {'Coeficiente':>12} | Interpretación")
        print(f"  {'-'*70}")
        
        for var, coef in coefs_ordenados:
            # Interpretación
            if coef > 0:
                interp = f"↑ {abs(coef):.4f}s por unidad"
            else:
                interp = f"↓ {abs(coef):.4f}s por unidad"
            print(f"  {var:<20} | {coef:>12.4f} | {interp}")
        
        # Análisis de importancia relativa
        print(f"\n📊 IMPORTANCIA RELATIVA:")
        print(f"\n  (Comparado con la variable más influyente)\n")
        
        max_coef = max(abs(c) for c in coefs)
        for var, coef in coefs_ordenados:
            importancia = (abs(coef) / max_coef) * 100
            barra = "█" * int(importancia / 5) + "░" * (20 - int(importancia / 5))
            print(f"  {var:<20} | {barra} | {importancia:5.1f}%")
        
        # Información adicional
        print(f"\n💡 INTERPRETACIÓN:")
        print(f"   Si los coeficientes son similares → Variables igualmente importantes")
        print(f"   Si hay gran diferencia → Una o dos variables dominan el modelo")
    
    # ========================================================================
    # PASO 4: VALIDACIÓN CRUZADA (Cross-Validation)
    # ========================================================================
    
    def validacion_cruzada(self, df, n_folds=3):
        """
        Realiza validación cruzada k-fold para evaluar estabilidad del modelo.
        
        Args:
            df: DataFrame completo
            n_folds: Número de folds (con pocos datos, usar 3-5)
        """
        print(f"\n" + "="*80)
        print("🔄 PASO 4: VALIDACIÓN CRUZADA (K-Fold)")
        print("="*80)
        
        X = df[self.variables_entrada].values
        y = df[self.variable_salida].values
        
        # Configurar validación cruzada
        kfold = KFold(n_splits=n_folds, shuffle=True, random_state=42)
        scores_r2 = cross_val_score(self.modelo, X, y, cv=kfold, scoring='r2')
        scores_rmse = -cross_val_score(self.modelo, X, y, cv=kfold, scoring='neg_mean_squared_error')
        scores_rmse = np.sqrt(scores_rmse)
        
        print(f"\n📊 Resultados de {n_folds}-Fold Cross-Validation:\n")
        print(f"  R² Scores:")
        for i, score in enumerate(scores_r2, 1):
            print(f"    Fold {i}: {score:.4f}")
        print(f"    MEDIA: {scores_r2.mean():.4f} ± {scores_r2.std():.4f}")
        
        print(f"\n  RMSE Scores (segundos):")
        for i, score in enumerate(scores_rmse, 1):
            print(f"    Fold {i}: {score:.2f}s")
        print(f"    MEDIA: {scores_rmse.mean():.2f}s ± {scores_rmse.std():.2f}s")
        
        self.historial_entrenamiento['cv_r2'] = {
            'media': scores_r2.mean(),
            'std': scores_r2.std(),
            'scores': scores_r2.tolist()
        }
        self.historial_entrenamiento['cv_rmse'] = {
            'media': scores_rmse.mean(),
            'std': scores_rmse.std(),
            'scores': scores_rmse.tolist()
        }
        
        # Interpretación
        if scores_r2.std() < 0.1:
            print(f"\n  ✅ Modelo estable (baja varianza entre folds)")
        else:
            print(f"\n  ⚠️  Modelo inestable (varianza alta entre folds)")
            print(f"     → Puede haber sobrefitting o datos muy variados")
    
    # ========================================================================
    # PASO 5: ANÁLISIS DE RESIDUOS
    # ========================================================================
    
    def analizar_residuos(self, df):
        """
        Analiza los residuos (errores) del modelo.
        Los residuos deben ser aleatorios y normalmente distribuidos.
        """
        print(f"\n" + "="*80)
        print("📉 PASO 5: ANÁLISIS DE RESIDUOS")
        print("="*80)
        
        X = df[self.variables_entrada].values
        y = df[self.variable_salida].values
        y_pred = self.modelo.predict(X)
        residuos = y - y_pred
        
        print(f"\n📊 Estadísticas de residuos:\n")
        print(f"   Media: {residuos.mean():.4f} (debe ser ≈ 0)")
        print(f"   Std Dev: {residuos.std():.4f}")
        print(f"   Min: {residuos.min():.4f}")
        print(f"   Max: {residuos.max():.4f}")
        
        # Mostrar predicciones vs reales
        print(f"\n📋 Comparación Predicho vs Real:\n")
        print(f"  {'Proyecto':<20} | {'Real':>8} | {'Predicho':>8} | {'Error':>8} | {'% Error':>8}")
        print(f"  {'-'*70}")
        
        for i, proyecto in enumerate(df['Proyecto'].values):
            error = residuos[i]
            pct_error = (error / y[i]) * 100
            print(f"  {proyecto:<20} | {y[i]:>8.1f}s | {y_pred[i]:>8.1f}s | {error:>8.2f}s | {pct_error:>7.1f}%")
        
        self.historial_entrenamiento['residuos'] = residuos.tolist()
    
    # ========================================================================
    # PREDICCIÓN
    # ========================================================================
    
    def predecir(self, datos_entrada):
        """
        Realiza predicción con un conjunto de variables.
        
        Args:
            datos_entrada: Dict con {variable: valor}
            
        Returns:
            Tiempo predicho y explicación del cálculo
        """
        if self.modelo is None:
            raise ValueError("Modelo no entrenado. Ejecuta .entrenar() primero.")
        
        # Validar entrada
        for var in self.variables_entrada:
            if var not in datos_entrada:
                raise ValueError(f"Falta variable: {var}")
        
        # Preparar datos
        X = np.array([[datos_entrada[var] for var in self.variables_entrada]])
        tiempo_predicho = self.modelo.predict(X)[0]
        
        # Explicación detallada del cálculo
        explicacion = {
            'tiempo_base': float(self.modelo.intercept_),
            'aportaciones': {},
            'tiempo_total': float(tiempo_predicho)
        }
        
        for var, coef in self.coeficientes.items():
            aportacion = coef * datos_entrada[var]
            explicacion['aportaciones'][var] = {
                'valor': float(datos_entrada[var]),
                'coeficiente': float(coef),
                'aportacion': float(aportacion)
            }
        
        return tiempo_predicho, explicacion
    
    # ========================================================================
    # ANÁLISIS DE SENSIBILIDAD
    # ========================================================================
    
    def analisis_sensibilidad(self, datos_base, variable_ajuste, rango=(-20, 20), pasos=11):
        """
        Analiza cómo cambia el tiempo predicho al variar una variable.
        
        Args:
            datos_base: Dict con configuración base
            variable_ajuste: Variable a variar
            rango: Tupla (min%, max%) para variar
            pasos: Número de puntos a calcular
            
        Returns:
            Lista de predicciones con variaciones
        """
        resultado = []
        valor_base = datos_base[variable_ajuste]
        
        variaciones = np.linspace(rango[0], rango[1], pasos)
        
        for pct in variaciones:
            datos_mod = datos_base.copy()
            datos_mod[variable_ajuste] = valor_base * (1 + pct/100)
            tiempo, _ = self.predecir(datos_mod)
            
            resultado.append({
                'variacion_pct': float(pct),
                'valor': float(datos_mod[variable_ajuste]),
                'tiempo_predicho': float(tiempo),
                'cambio_tiempo': float(tiempo - resultado[0]['tiempo_predicho']) if resultado else 0.0
            })
        
        return resultado
    
    # ========================================================================
    # GUARDAR/CARGAR MODELO
    # ========================================================================
    
    def guardar(self, ruta_modelo='modelo_regresion.pkl', ruta_config='config_modelo.json'):
        """Guarda el modelo entrenado"""
        with open(ruta_modelo, 'wb') as f:
            pickle.dump(self.modelo, f)
        
        config = {
            'variables_entrada': self.variables_entrada,
            'variable_salida': self.variable_salida,
            'coeficientes': self.coeficientes,
            'r2_score': float(self.r2_score),
            'rmse': float(self.rmse),
            'mae': float(self.mae),
            'intercept': float(self.modelo.intercept_)
        }
        
        with open(ruta_config, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"✅ Modelo guardado: {ruta_modelo}")
        print(f"✅ Configuración guardada: {ruta_config}")
    
    def cargar(self, ruta_modelo='modelo_regresion.pkl', ruta_config='config_modelo.json'):
        """Carga el modelo entrenado"""
        with open(ruta_modelo, 'rb') as f:
            self.modelo = pickle.load(f)
        
        with open(ruta_config, 'r') as f:
            config = json.load(f)
        
        self.variables_entrada = config['variables_entrada']
        self.coeficientes = config['coeficientes']
        self.r2_score = config['r2_score']
        self.rmse = config['rmse']
        self.mae = config['mae']
        
        print(f"✅ Modelo cargado: {ruta_modelo}")
        print(f"✅ Configuración cargada: {ruta_config}")
    
    # ========================================================================
    # REPORTE COMPLETO
    # ========================================================================
    
    def generar_reporte(self, ruta_archivo='reporte_modelo.txt'):
        """Genera reporte completo del modelo"""
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("REPORTE COMPLETO DEL MODELO DE REGRESIÓN LINEAL\n")
            f.write("="*80 + "\n\n")
            
            f.write("MÉTRICAS DE CALIDAD:\n")
            f.write(f"  R² Score: {self.r2_score:.4f}\n")
            f.write(f"  RMSE: {self.rmse:.2f} segundos\n")
            f.write(f"  MAE: {self.mae:.2f} segundos\n\n")
            
            f.write("COEFICIENTES:\n")
            f.write(f"  Intercept: {self.modelo.intercept_:.4f}\n")
            for var, coef in sorted(self.coeficientes.items(), key=lambda x: abs(x[1]), reverse=True):
                f.write(f"  {var}: {coef:.4f}\n")
            
            f.write("\n" + "="*80 + "\n")
        
        print(f"✅ Reporte guardado: {ruta_archivo}")


# ============================================================================
# SCRIPT DE DEMOSTRACIÓN
# ============================================================================

if __name__ == "__main__":
    
    # Cargar datos limpios
    df = pd.read_csv('base_datos_limpia.csv')
    
    # Crear y entrenar modelo
    modelo = ModeloRegresionLineal()
    
    # Paso 1: Seleccionar variables
    modelo.seleccionar_variables(df, umbral_correlacion=0.5)
    
    # Paso 2: Entrenar
    modelo.entrenar(df)
    
    # Paso 3: Pesos (automático en entrenar)
    
    # Paso 4: Validación cruzada
    modelo.validacion_cruzada(df, n_folds=3)
    
    # Paso 5: Análisis de residuos
    modelo.analizar_residuos(df)
    
    # Guardar modelo
    modelo.guardar()
    
    # Generar reporte
    modelo.generar_reporte()
    
    print("\n" + "="*80)
    print("✅ ENTRENAMIENTO COMPLETADO")
    print("="*80)
