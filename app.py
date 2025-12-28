import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="OFERTAS FLEX IA 1.3.2", layout="wide")
st.title("🚗 FACTORY 21 - Lógica de Procesos Avanzada")

# --- INPUTS EN SIDEBAR ---
st.sidebar.header("📥 Datos de Entrada")

# Tecnologías Robot Manipulador
tuercas = st.sidebar.number_input("Nº Tuercas Soldadas", value=0)
tuckers = st.sidebar.number_input("Nº Tuckers", value=0)
marcado = st.sidebar.checkbox("¿Lleva Marcado Láser?", value=False)

# Tecnologías Robots Soldadores
spw = st.sidebar.number_input("Puntos SPW", value=0)
mastico_mm = st.sidebar.number_input("Mastico (mm)", value=0)
tox = st.sidebar.number_input("Nº Tox (Clinchado)", value=0)
roll_hemming_mm = st.sidebar.number_input("Roll Hemming (mm)", value=0)

# --- MOTOR DE CÁLCULO (Lógica Híbrida) ---

def calcular_tiempo_v132(tuercas, tuckers, marcado, spw, mastico, tox, rh):
    # 1. TRABAJO DEL ROBOT MANIPULADOR (Robot 4)
    # ------------------------------------------
    t_manipulacion_base = 16.0
    t_tuercas = tuercas * 8.0
    t_tuckers = tuckers * 7.0
    t_marcado = 14.0 if marcado else 0.0 # 10s fijo + 2s entrada + 2s salida
    
    t_total_manipulador = t_manipulacion_base + t_tuercas + t_tuckers + t_marcado

    # 2. TRABAJO DE LOS ROBOTS SOLDADORES (Robots 1, 2, 3)
    # ---------------------------------------------------
    # Calculamos tiempo de proceso puro
    t_spw_puro = spw * (3.5 + 3.0) # Tiempo punto + vuelo
    t_mastico_puro = mastico / 10.0
    t_tox_puro = tox * 5.0
    t_rh_puro = rh / 10.0
    
    t_proceso_total = t_spw_puro + t_mastico_puro + t_tox_puro + t_rh_puro
    
    # Aplicamos penalizaciones por cambios de herramienta o procesos no solapables
    t_penalizaciones = 0
    if mastico > 0:
        t_penalizaciones += 16.0 + 25.0 # Cogida/dejada extra + cambio herramienta
    if tox > 0:
        t_penalizaciones += 25.0 # Cambio herramienta
        
    # Balanceo entre 3 robots (eficiencia 80%)
    robots_efectivos = 3 * 0.8
    t_total_soldadores = (t_proceso_total / robots_efectivos) + t_penalizaciones

    # 3. RESULTADO FINAL (El cuello de botella)
    # En automoción, el tiempo de ciclo es el que más tarda de los dos grupos
    tiempo_ciclo_final = max(t_total_manipulador, t_total_soldadores)
    
    return {
        "Ciclo Final": tiempo_ciclo_final,
        "Carga Manipulador": t_total_manipulador,
        "Carga Soldadores": t_total_soldadores,
        "Diferencia": abs(t_total_manipulador - t_total_soldadores)
    }

# --- EJECUCIÓN Y MOSTRAR RESULTADOS ---

if st.button("CALCULAR TIEMPO DE CICLO"):
    res = calcular_tiempo_v132(tuercas, tuckers, marcado, spw, mastico_mm, tox, roll_hemming_mm)
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("TIEMPO DE CICLO FINAL", f"{res['Ciclo Final']:.2f} s")
    c2.metric("Uso Robot Manipulador", f"{res['Carga Manipulador']:.1f} s")
    c3.metric("Uso Robots Soldadores", f"{res['Carga Soldadores']:.1f} s")

    # Explicación del cuello de botella
    if res['Carga Manipulador'] > res['Carga Soldadores']:
        st.info("⚠️ El cuello de botella está en el **Robot Manipulador** (Carga/Tuercas/Marcado).")
    else:
        st.info("🤖 El cuello de botella está en los **Robots Soldadores** (Uniones/Proceso).")

    # Tabla técnica de salidas para tu Excel
    st.subheader("Salidas Estimadas")
    salidas = {
        "Parámetro": ["CELDA 1-TIEMPO DE CICLO", "CUELLO DE BOTELLA", "CAMBIO HERRAMIENTA", "PINZAS/GARRAS"],
        "Valor": [f"{res['Ciclo Final']:.2f} s", 
                  "Manipulador" if res['Carga Manipulador'] > res['Carga Soldadores'] else "Soldadores",
                  "SÍ" if (mastico_mm > 0 or tox > 0) else "NO",
                  "1 Garra / 3 Pinzas" if mastico_mm > 0 else "4 Pinzas"]
    }
    st.table(pd.DataFrame(salidas))
    