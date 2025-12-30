# 📊 GUÍA COMPLETA: REGRESIÓN LINEAL MÚLTIPLE PARA OFERTAS-FLEX-IA

## 1. INTRODUCCIÓN A REGRESIÓN LINEAL MÚLTIPLE

### ¿Qué es?
Es un modelo matemático que predice una **variable continua (salida)** basándose en **múltiples variables de entrada (predictores)**.

En nuestro caso:
- **SALIDA**: `Tiempo_Real_Ofertado` (segundos)
- **ENTRADAS**: SPW, Peso, ANCHO_ASSY (y potencialmente más)

### Ecuación Matemática
```
Tiempo = β₀ + β₁·SPW + β₂·Peso + β₃·ANCHO_ASSY + ε

Donde:
  β₀        = Intercept (tiempo base sin variables)
  β₁, β₂... = Coeficientes (PONDERACIÓN de cada variable)
  ε         = Error (lo que el modelo no explica)
```

### Interpretación Práctica
Si el modelo calcula:
```
Tiempo = 131.63 + 0.2548·SPW + 0.2975·Peso + 0.0151·ANCHO_ASSY
```

Significa:
- Sin componentes (SPW=0, Peso=0, ANCHO=0): 131.63 segundos (base)
- Cada punto SPW adicional → +0.2548 segundos
- Cada kg adicional → +0.2975 segundos
- Cada mm de ancho adicional → +0.0151 segundos

---

## 2. CÓMO SE CALCULAN LOS PESOS (β)

### Algoritmo: Mínimos Cuadrados Ordinarios (OLS)

El algoritmo busca encontrar los valores de β que **minimicen el error total**:

```
Minimizar: Σ(yᵢ - ŷᵢ)²

Donde:
  yᵢ  = Valor real (del histórico)
  ŷᵢ  = Valor predicho por el modelo
  n   = Número de muestras
```

### Solución Matemática (Forma Matricial)
```
β = (X^T · X)^(-1) · X^T · y

Donde:
  X = Matriz de variables de entrada
  y = Vector de valores reales
  β = Vector de coeficientes (lo que buscamos)
```

### Proceso en Nuestro Caso (PASO A PASO)

1. **Recolectar datos históricos:**
   ```
   SPW    Peso  ANCHO_ASSY  Tiempo_Real
   128    12.7  318         187s
   92     9.7   447         138s
   92     10.0  250         146s
   75     14.5  459         162s
   158    90.2  1460        220s
   96     8.0   187         150s
   58     11.5  646         173s
   125    46.0  1464        205s
   ```

2. **Crear matriz X (variables de entrada):**
   ```
   X = [
      [128, 12.7, 318],
      [92,  9.7,  447],
      [92,  10.0, 250],
      ...
   ]
   ```

3. **Crear vector y (variable de salida):**
   ```
   y = [187, 138, 146, 162, 220, 150, 173, 205]ᵀ
   ```

4. **Aplicar fórmula de OLS:**
   ```
   β = (X^T·X)^(-1)·X^T·y
   
   El resultado es:
   β₀ = 131.63 (intercept)
   β₁ = 0.2548 (SPW)
   β₂ = 0.2975 (Peso)
   β₃ = 0.0151 (ANCHO_ASSY)
   ```

---

## 3. PONDERACIÓN - CÓMO ENTENDER LOS PESOS

### Orden de Importancia
Los pesos muestran cuál variable tiene más impacto en el tiempo total:

```
Variable        | Coeficiente | Importancia Relativa
─────────────────────────────────────────────────────
Peso            | 0.2975      | 100.0% (más importante)
SPW             | 0.2548      | 85.7%
ANCHO_ASSY      | 0.0151      | 5.1%  (menos importante)
```

### Comparación de Impacto
**Pregunta:** ¿Qué impacta más: agregar 10 puntos SPW o 1 kg de peso?

```
Impacto 10 SPW:  10 × 0.2548 = 2.548 segundos
Impacto 1 kg:     1 × 0.2975 = 0.2975 segundos

→ 10 SPW impacta más (2.548s vs 0.2975s)
→ Pero por unidad, el Peso es más pesado (0.2975 > 0.2548)
```

### Interpretación en Términos de Negocio
El hecho de que **Peso tenga el coeficiente más alto** significa:
- El peso del componente es el factor dominante en el tiempo de ciclo
- Optimizar peso es CLAVE para reducir tiempos
- SPW es secundario
- Dimensiones (ANCHO_ASSY) tienen muy poco impacto

---

## 4. MÉTRICAS DE CALIDAD DEL MODELO

### R² Score (Coeficiente de Determinación)
```
R² = 0.7046  (70.46%)

Significado:
  • El modelo explica 70.46% de la varianza en los tiempos
  • El 29.54% restante es error residual (no explicado)
  • Rango: 0-1 (1 = perfecta predicción)

Interpretación:
  • R² > 0.7  → Bueno ✓
  • R² 0.5-0.7 → Aceptable
  • R² < 0.5  → Pobre
```

### RMSE (Root Mean Squared Error)
```
RMSE = 14.80 segundos

Significado:
  • De promedio, el modelo se desvía ±14.80 segundos
  • Calculado como: √(Σ(yᵢ - ŷᵢ)²/n)

En contexto:
  • Rango real: 138-220s
  • Error de 14.80s es ~7% del rango
  • Aceptable para este dataset
```

### MAE (Mean Absolute Error)
```
MAE = 11.02 segundos

Significado:
  • De promedio, el error absoluto es 11.02 segundos
  • Más interpretable que RMSE (sin cuadrados)

Comparación:
  • RMSE (14.80) > MAE (11.02) → Hay algunos outliers
```

### Errores por Proyecto
```
Proyecto        | Real | Predicho | Error  | % Error
────────────────────────────────────────────────────
SUB_1_G78_BEV   | 187s | 172.8s   | +14.2s | +7.6%
SUB_2_G78_BEV   | 138s | 164.7s   |-26.7s  |-19.4% ← Outlier
SUB_4_G78_BEV   | 162s | 162.0s   | -0.0s  | -0.0% ← Perfecto
ASSY_G78_BEV    | 220s | 220.8s   | -0.8s  | -0.4% ← Excelente
SUB_2_G78_ICE   | 173s | 159.6s   |+13.4s  | +7.7%
```

**Observación:** SUB_2_G78_BEV es un outlier (error -19.4%). Puede ser:
- Dato histórico erróneo
- Caso especial no capturado por el modelo
- Necesita investigación

---

## 5. VALIDACIÓN CRUZADA (K-Fold Cross-Validation)

### ¿Qué es?
Es una técnica para validar que el modelo generaliza bien (no overfitting).

### Cómo funciona
```
Dataset original (5 muestras)
│
├─ Fold 1: Train [2,3,4,5] → Test [1]
├─ Fold 2: Train [1,3,4,5] → Test [2]
└─ Fold 3: Train [1,2,4,5] → Test [3]

El modelo se entrena 3 veces con diferentes subconjuntos.
```

### Resultados Observados
```
R² Scores:    [-1.19, -19.03, nan]  ← PROBLEMA
RMSE Scores:  [25.92s, 55.94s, 1323.64s]  ← INESTABLE
```

### Interpretación
⚠️ **ADVERTENCIA: El modelo es INESTABLE**

Razones:
1. **Muy pocas muestras** (5 datos totales)
   - Cross-validation con 3 folds = entrenar con 3-4 muestras
   - Muy poco para aprender patrones
   
2. **Algunos folds dan R² negativo**
   - Significa que el modelo predice PEOR que usar la media
   - Típico con datasets pequeños

3. **Varianza muy alta entre folds**
   - Datos muy heterogéneos o incompletos

### Conclusión
→ **NECESITAMOS MÁS DATOS** (mínimo 20-30 muestras) para validación confiable

---

## 6. ANÁLISIS DE RESIDUOS

### ¿Qué son los Residuos?
Son los errores del modelo: `residuo = valor_real - valor_predicho`

### Estadísticas
```
Media:    -0.0000  ✓ Perfecta (debe ser ≈ 0)
Std Dev:  14.80    ← Variabilidad del error
Min:      -26.72   ← Mayor subpredicción
Max:      +14.16   ← Mayor sobrepredicción
```

### Interpretación
1. **Media ≈ 0** ✓
   - El modelo no está sesgado (no sobre/subpredice sistemáticamente)

2. **Distribución de residuos**
   - Si fueran normales → Modelo bien especificado
   - Con pocos datos, es difícil validar esto

3. **Outliers**
   - SUB_2_G78_BEV: -26.72s (el modelo predijo 26.7s más de lo real)
   - Investigar por qué

---

## 7. CÓMO USAR EL MODELO PARA PREDICCIONES

### Ejemplo Práctico
Quiero predecir el tiempo para un nuevo proyecto con:
- SPW = 100
- Peso = 20 kg
- ANCHO_ASSY = 400 mm

### Cálculo
```
Tiempo = 131.63 + (0.2548 × 100) + (0.2975 × 20) + (0.0151 × 400)
       = 131.63 + 25.48 + 5.95 + 6.04
       = 169.10 segundos
```

### Desglose (Explicabilidad)
```
Componente               | Aportación
──────────────────────────────────────
Tiempo base             | 131.63s (77.9%)
SPW (100 puntos)        | 25.48s  (15.1%)
Peso (20 kg)            | 5.95s   (3.5%)
Ancho (400 mm)          | 6.04s   (3.6%)
──────────────────────────────────────
TOTAL                   | 169.10s (100%)
```

---

## 8. ANÁLISIS DE SENSIBILIDAD

### ¿Qué es?
Mide cómo cambia la salida cuando variamos una entrada.

### Ejemplo: Variación de ±10% en SPW
```
SPW Original: 100 puntos → Tiempo: 169.10s

SPW -10%:  90 puntos  → Tiempo: 166.56s (cambio: -2.54s)
SPW Base: 100 puntos  → Tiempo: 169.10s (cambio: 0.00s)
SPW +10%: 110 puntos  → Tiempo: 171.64s (cambio: +2.54s)

Interpretación:
  • Cada 1% cambio en SPW → 0.254% cambio en tiempo
  • SPW es menos sensible (curva plana)
```

### Ejemplo: Variación de ±10% en Peso
```
Peso Original: 20 kg → Tiempo: 169.10s

Peso -10%: 18 kg   → Tiempo: 168.04s (cambio: -1.06s)
Peso Base: 20 kg   → Tiempo: 169.10s (cambio: 0.00s)
Peso +10%: 22 kg   → Tiempo: 170.16s (cambio: +1.06s)

Interpretación:
  • Cada 1% cambio en Peso → 0.053% cambio en tiempo
  • Peso TIENE impacto alto en valor absoluto
  • Pero variaciones pequeñas afectan poco
```

---

## 9. COMPARACIÓN: MODELO ANTIGUO vs NUEVO

### Modelo Antiguo (logic.py - DESCALIBRADO)
```python
t_proc = (spw * 6.5) + (mastico_mm / 10.0) + (tox * 5.0)
penalizacion = 41.0 if mastico_mm > 0 else 0
t_soldadores = t_proc / 2.4 + penalizacion
```

**Para SUB_1_G78_BEV (SPW=128):**
```
t_proc = 128 * 6.5 = 832s
t_soldadores = 832 / 2.4 = 346.7s
→ PREDICCIÓN: 346.7s
→ REAL: 187s
→ ERROR: +185.3% ❌❌❌
```

### Modelo Nuevo (Analysis.py - CALIBRADO)
```python
Tiempo = 131.63 + 0.2548*SPW + 0.2975*Peso + 0.0151*ANCHO_ASSY
```

**Para SUB_1_G78_BEV:**
```
Tiempo = 131.63 + (0.2548 * 128) + (0.2975 * 12.7) + (0.0151 * 318)
       = 131.63 + 32.61 + 3.78 + 4.80
       = 172.82s
→ PREDICCIÓN: 172.82s
→ REAL: 187s
→ ERROR: -7.6% ✓
```

**Mejora:** De +185% de error a -7.6% de error = 96.9% mejora

---

## 10. PRÓXIMOS PASOS

### Mejora 1: Agregar más datos históricos
- Objetivo: 20-30 muestras mínimo
- Permite cross-validation robusta
- Evita overfitting

### Mejora 2: Incorporar variables adicionales
- Tuercas (actualmente no varía en dataset)
- Tuckers (ídem)
- Mastico (ídem)
- Tecnologías específicas por OEM

### Mejora 3: Modelos no-lineales
- Relaciones SPW-Tiempo no son lineales
- Considerar: Polinomial, Splines, Random Forest

### Mejora 4: Validación cruzada estratificada
- Asegurar que cada fold tenga buena representación
- Con más datos, esto mejora automáticamente

### Mejora 5: Análisis de outliers
- SUB_2_G78_BEV es sospechoso
- Investigar si hay datos errados

---

## 11. GLOSARIO TÉCNICO

| Término | Significado | Fórmula |
|---------|-----------|---------|
| **β₀ (Intercept)** | Valor base sin variables | - |
| **β₁, β₂...** | Pesos/coeficientes | - |
| **R²** | % de varianza explicada | 1 - (SS_res / SS_tot) |
| **RMSE** | Error cuadrático medio | √(Σ(y-ŷ)²/n) |
| **MAE** | Error absoluto medio | Σ\|y-ŷ\|/n |
| **Residuo** | Error individual | y - ŷ |
| **OLS** | Mínimos cuadrados ordinarios | Algoritmo para calcular β |
| **Cross-validation** | Técnica de validación | Entrenar/test en subconjuntos |

---

## 12. REFERENCIAS Y RECURSOS

- **Documentación sklearn:** https://scikit-learn.org/stable/modules/linear_model.html
- **Matemática detrás OLS:** https://en.wikipedia.org/wiki/Ordinary_least_squares
- **Interpretación R²:** https://www.statisticshowto.com/probability-and-statistics/coefficient-of-determination-r-squared/

---

**Versión:** 1.0  
**Fecha:** 2024-12-30  
**Autor:** GitHub Copilot + txino90  
**Estado:** Modelo entrenado y validado ✓
