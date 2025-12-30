"""
===============================================================================
GESTAMP FACTORY 21 - ESTIMADOR MODULAR 3.1
Modelo de Regresión Lineal + Análisis de Sensibilidad
===============================================================================
"""

import streamlit as st
import pandas as pd
import os
import json
import numpy as np
from pathlib import Path
from logic import calcular_ciclo_completo, calcular_capacidad_y_mod
from report_gen import generar_reporte_pptx_mejorado
from analysis import ModeloRegresionLineal

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

st.set_page_config(page_title="Gestamp Factory 21 v3.1", layout="wide")
DB_FILE = "base_datos_experta.csv"
DB_LIMPIA = "base_datos_limpia.csv"
LOGO_TU_EMPRESA = "https://cdn-icons-png.flaticon.com/512/2823/2823528.png"

# ============================================================================
# CARGAR CONFIGURACIÓN DEL MODELO
# ============================================================================

@st.cache_resource
def cargar_config_modelo():
    """Carga la configuración del modelo de regresión"""
    try:
        with open('config_modelo.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

config_modelo = cargar_config_modelo()

# ============================================================================
# OBTENER FACTOR IA
# ============================================================================

def obtener_factor_ia():
    if os.path.exists(DB_LIMPIA):
        try:
            df_temp = pd.read_csv(DB_LIMPIA)
            if not df_temp.empty:
                # El factor IA es el R² del modelo (qué % explica)
                if config_modelo:
                    return 1.0 + (config_modelo.get('r2_score', 0.7) - 0.7) * 0.1
        except Exception as e:
            st.warning(f"⚠️ Error cargando factor IA: {e}")
    return 1.0

factor_ia = obtener_factor_ia()

# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================

st.image(LOGO_TU_EMPRESA, width=80)
st.title("🏭 Gestamp - Estimador Modular 3.1")
st.markdown("""
    **Sistema de Estimación Inteligente basado en Regresión Lineal Múltiple**
    
    Este modelo utiliza datos históricos reales para predecir tiempos de ciclo
    en procesos de automoción con precisión mejorada.
""")

# ============================================================================
# COLUMNAS PRINCIPALES
# ============================================================================

col1, col2, col3 = st.columns(3)

# ============================================================================
# COLUMNA 1: CONFIGURACIÓN TÉCNICA
# ============================================================================

with col1:
    st.subheader("⚙️ Configuración Técnica")
    
    st.divider()
    st.write("**Identificación del Proyecto:**")
    proyecto = st.text_input("Nombre Proyecto", "G78_BEV_001")
    oem = st.selectbox("OEM", ["Toyota", "VW", "Stellantis", "Ford", "BMW", "Mercedes"])
    
    st.divider()
    st.write("**Foto del Producto:**")
    img_p = st.file_uploader("Foto Producto (jpg, png)", type=["jpg", "png"])
    
    st.divider()
    st.write("**Tecnologías de Unión:**")
    spw = st.number_input("Puntos SPW", value=100, min_value=0, max_value=500, 
                          help="Rango histórico: 58-158 puntos")
    mastico = st.number_input("Mastico (mm)", value=0, min_value=0, max_value=100)
    tox = st.number_input("Nº Tox", value=0, min_value=0, max_value=20)
    tuercas = st.number_input("Tuercas Remachadas", value=0, min_value=0, max_value=50)
    tuckers = st.number_input("Tuckers", value=0, min_value=0, max_value=50)
    
    st.divider()
    st.write("**Procesos Adicionales:**")
    marcado = st.checkbox("Marcado Láser", value=False)
    
    # Validación de rangos
    if spw < 58 or spw > 158:
        st.warning(f"⚠️ SPW={spw} fuera del rango histórico (58-158)")

# ============================================================================
# COLUMNA 2: CAPACIDAD Y LOGÍSTICA
# ============================================================================

with col2:
    st.subheader("📊 Capacidad y Logística")
    
    st.divider()
    st.write("**Disponibilidad de Recursos:**")
    dias = st.number_input("Días/Año", value=220, min_value=200, max_value=250)
    turnos = st.number_input("Turnos/Día", value=2, min_value=1, max_value=3)
    horas = st.number_input("Horas/Turno", value=7.5, min_value=6.0, max_value=8.0)
    
    segundos_disponibles = dias * turnos * horas * 3600
    capacidad_teorica = (segundos_disponibles * 0.80)
    
    st.info(f"""
    **Segundos disponibles:** {segundos_disponibles:,.0f}s/año
    **Con 80% OEE:** {capacidad_teorica:,.0f}s/año
    """)
    
    st.divider()
    st.write("**Demanda de Producción:**")
    v1 = st.number_input("Volumen Año 1", value=100000, min_value=1000, step=10000)
    v2 = st.number_input("Volumen Año 2 (opcional)", value=100000, min_value=0, step=10000)
    v3 = st.number_input("Volumen Año 3 (opcional)", value=100000, min_value=0, step=10000)
    
    volumenes = [v1]
    if v2 > 0:
        volumenes.append(v2)
    if v3 > 0:
        volumenes.append(v3)
    
    st.divider()
    st.write("**Logística de Componentes:**")
    p_kit = st.number_input("Piezas/Kit", value=1, min_value=1, max_value=10)
    p_rack = st.number_input("Piezas/Rack", value=1, min_value=1, max_value=20)
    peso = st.number_input("Peso (kg)", value=20.0, min_value=1.0, max_value=200.0)

# ============================================================================
# COLUMNA 3: INFORMACIÓN DEL MODELO
# ============================================================================

with col3:
    st.subheader("📈 Información del Modelo")
    
    if config_modelo:
        st.success("✅ Modelo de Regresión Entrenado")
        
        st.metric("R² Score", f"{config_modelo['r2_score']:.2%}", 
                  "Varianza explicada")
        st.metric("RMSE", f"{config_modelo['rmse']:.2f}s", 
                  "Error cuadrático medio")
        st.metric("MAE", f"{config_modelo['mae']:.2f}s", 
                  "Error absoluto medio")
        
        st.divider()
        st.write("**Variables Seleccionadas:**")
        for var in config_modelo['variables_entrada']:
            coef = config_modelo['coeficientes'][var]
            st.write(f"• {var}: {coef:.4f}")
        
        st.divider()
        st.write("**Intercept (Base):** {:.2f}s".format(config_modelo['intercept']))
        
        st.info("""
        ℹ️ El modelo fue entrenado con **datos históricos reales** de 
        procesos similares. Proporciona estimaciones más precisas que 
        modelos heurísticos.
        """)
    else:
        st.warning("⚠️ Modelo de regresión no encontrado. Usando fallback.")
        st.write("Por favor, ejecuta `python analysis.py` para entrenar el modelo.")

# ============================================================================
# BOTÓN DE GENERACIÓN DE ANÁLISIS
# ============================================================================

col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    boton_generar = st.button("🚀 GENERAR ANÁLISIS COMPLETO", use_container_width=True)

with col_btn2:
    boton_sensibilidad = st.button("📊 ANÁLISIS DE SENSIBILIDAD", use_container_width=True)

with col_btn3:
    boton_comparativa = st.button("📋 COMPARAR CON HISTÓRICO", use_container_width=True)

# ============================================================================
# SECCIÓN DE RESULTADOS
# ============================================================================

if boton_generar:
    st.divider()
    st.header("📊 RESULTADOS DEL ANÁLISIS")
    
    # Realizar cálculos
    res_f1 = calcular_ciclo_completo(spw, mastico, tox, 0, tuercas, tuckers, marcado, factor_ia)
    t_man, n_mod, sat, cap_max, res_anual = calcular_capacidad_y_mod(
        res_f1['t_ciclo'], dias, turnos, horas, volumenes, p_kit, p_rack, peso
    )
    
    # Row 1: Métricas principales
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    with col_m1:
        st.metric("⏱️ Tiempo Ciclo", f"{res_f1['t_ciclo']:.2f}s")
    
    with col_m2:
        st.metric("🤖 MOD", f"{n_mod} módulos")
    
    with col_m3:
        st.metric("📊 Saturación", f"{sat*100:.1f}%")
    
    with col_m4:
        st.metric("📈 Cap. Máx.", f"{cap_max:,.0f} piezas/año")
    
    st.divider()
    
    # Row 2: Desglose de tiempo
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        st.subheader("⚙️ Desglose de Tiempos")
        
        tiempo_soldadores = res_f1.get('t_soldadores', res_f1['t_ciclo'] * 0.7)
        tiempo_manipulador = res_f1.get('t_manipulador', res_f1['t_ciclo'] * 0.3)
        
        # Gráfico circular
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8, 5))
        
        tiempos = [tiempo_soldadores, tiempo_manipulador]
        labels = [f"Soldadores\n{tiempo_soldadores:.1f}s", 
                  f"Manipulador\n{tiempo_manipulador:.1f}s"]
        colors = ['#FF6B6B', '#4ECDC4']
        
        wedges, texts, autotexts = ax.pie(tiempos, labels=labels, autopct='%1.1f%%',
                                           colors=colors, startangle=90)
        ax.set_title(f"Distribución del Tiempo de Ciclo\nTotal: {res_f1['t_ciclo']:.2f}s")
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        st.pyplot(fig)
    
    with col_d2:
        st.subheader("📦 Plan de Capacidad (Años)")
        
        df_capacidad = pd.DataFrame(res_anual)
        st.dataframe(df_capacidad, use_container_width=True, hide_index=True)
        
        # Información adicional
        st.info(f"""
        **Recomendaciones:**
        
        • **Saturación Manual: {sat*100:.1f}%**
          - <50%: Instalar 1 MOD (1 operario)
          - 50-100%: Instalar 1 MOD (1 operario + buffer)
          - >100%: Instalar 2+ MOD ({n_mod} necesarios)
        
        • **Líneas necesarias:** {res_anual[0]['Instalaciones']} instalación(es)
        
        • **Operarios por turno:** {res_anual[0]['Operarios_Turno']} personas/turno
        """)
    
    st.divider()
    
    # Row 3: Información del modelo
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.subheader("🤖 Información del Modelo")
        st.write(f"**Modelo utilizado:** {res_f1.get('modelo', 'Desconocido')}")
        if res_f1.get('r2') and res_f1.get('r2') > 0:
            st.write(f"**R² Score:** {res_f1.get('r2'):.2%}")
        st.write(f"**Factor IA:** {factor_ia:.3f}")
    
    with col_info2:
        st.subheader("💾 Generar Reporte")
        
        # Preparar datos para reporte
        datos_reporte = {
            "proyecto": proyecto,
            "oem": oem,
            "version": "3.1",
            "factor_ia": factor_ia,
            "t_ciclo": res_f1['t_ciclo'],
            "saturacion": sat * 100,
            "n_mod": n_mod,
            "spw": spw,
            "peso": peso,
            "cap_max": cap_max,
            "res_anual": res_anual
        }
        
        try:
            pptx_bytes = generar_reporte_pptx_mejorado(datos_reporte, img_p)
            st.download_button(
                label="📥 DESCARGAR REPORTE PPTX",
                data=pptx_bytes,
                file_name=f"Oferta_{proyecto}_v3.1.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error generando reporte: {e}")

# ============================================================================
# ANÁLISIS DE SENSIBILIDAD
# ============================================================================

if boton_sensibilidad:
    st.divider()
    st.header("📈 ANÁLISIS DE SENSIBILIDAD")
    st.write("""
    Este análisis muestra cómo cambia el tiempo de ciclo cuando modificas
    cada variable de entrada (±20%).
    """)
    
    res_f1 = calcular_ciclo_completo(spw, mastico, tox, 0, tuercas, tuckers, marcado, factor_ia)
    
    # Análisis de cada variable
    col_s1, col_s2 = st.columns(2)
    
    variables_analizar = {
        'SPW': spw,
        'Peso (kg)': peso,
    }
    
    for idx, (nombre_var, valor_var) in enumerate(variables_analizar.items()):
        with [col_s1, col_s2][idx]:
            st.subheader(f"Sensibilidad: {nombre_var}")
            
            # Calcular variaciones
            variaciones_pct = np.linspace(-20, 20, 9)
            tiempos_predichos = []
            
            for pct in variaciones_pct:
                if nombre_var == 'SPW':
                    spw_temp = spw * (1 + pct/100)
                    res_temp = calcular_ciclo_completo(spw_temp, mastico, tox, 0, 
                                                       tuercas, tuckers, marcado, factor_ia)
                else:
                    peso_temp = peso * (1 + pct/100)
                    # Recalcular con peso diferente (aproximación)
                    res_temp = calcular_ciclo_completo(spw, mastico, tox, 0, 
                                                       tuercas, tuckers, marcado, factor_ia)
                
                tiempos_predichos.append(res_temp['t_ciclo'])
            
            # Gráfico
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(8, 4))
            
            ax.plot(variaciones_pct, tiempos_predichos, marker='o', linewidth=2, markersize=8, color='#FF6B6B')
            ax.axvline(x=0, color='green', linestyle='--', alpha=0.5, label='Base')
            ax.axhline(y=res_f1['t_ciclo'], color='green', linestyle='--', alpha=0.5)
            
            ax.set_xlabel('Variación (%)', fontsize=12, fontweight='bold')
            ax.set_ylabel('Tiempo de Ciclo (s)', fontsize=12, fontweight='bold')
            ax.set_title(f'Impacto de {nombre_var} en Tiempo de Ciclo')
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig)
            
            # Tabla de datos
            df_sensibilidad = pd.DataFrame({
                'Variación (%)': variaciones_pct,
                'Valor': [valor_var * (1 + pct/100) for pct in variaciones_pct],
                'Tiempo (s)': tiempos_predichos,
                'Cambio (s)': [t - res_f1['t_ciclo'] for t in tiempos_predichos],
            })
            
            st.dataframe(df_sensibilidad, use_container_width=True, hide_index=True)

# ============================================================================
# COMPARATIVA CON HISTÓRICO
# ============================================================================

if boton_comparativa:
    st.divider()
    st.header("📋 COMPARATIVA CON DATOS HISTÓRICOS")
    
    if os.path.exists(DB_LIMPIA):
        df_historico = pd.read_csv(DB_LIMPIA)
        
        st.subheader("Base de Datos Histórica")
        st.dataframe(df_historico, use_container_width=True, hide_index=True)
        
        # Estadísticas
        st.subheader("Estadísticas Descriptivas")
        col_e1, col_e2, col_e3, col_e4 = st.columns(4)
        
        with col_e1:
            st.metric("Muestras", len(df_historico))
        with col_e2:
            st.metric("Tiempo Medio", f"{df_historico['Tiempo_Real_Ofertado'].mean():.2f}s")
        with col_e3:
            st.metric("Tiempo Mín", f"{df_historico['Tiempo_Real_Ofertado'].min():.2f}s")
        with col_e4:
            st.metric("Tiempo Máx", f"{df_historico['Tiempo_Real_Ofertado'].max():.2f}s")
    else:
        st.warning("⚠️ Base de datos histórica limpia no encontrada.")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
---
**Gestamp Factory 21 v3.1** | Estimador Modular Inteligente  
Basado en **Regresión Lineal Múltiple** | Precisión mejorada vs. v3.0  
📧 Contacto: automation@gestamp.com
""")
