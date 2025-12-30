import streamlit as st
import pandas as pd
import os
from logic import calcular_ciclo_completo, calcular_capacidad_y_mod
from report_gen import generar_reporte_pptx

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestamp Factory 21 v3.0", layout="wide")
DB_FILE = "base_datos_experta.csv"
LOGO_TU_EMPRESA = "https://cdn-icons-png.flaticon.com/512/2823/2823528.png"

# --- CARGA DE DATOS SEGURA (Blindada contra KeyErrors) ---
def obtener_factor_ia():
    if os.path.exists(DB_FILE):
        try:
            df_temp = pd.read_csv(DB_FILE)
            if not df_temp.empty and "Factor_Calculado" in df_temp.columns:
                return df_temp["Factor_Calculado"].mean()
        except Exception:
            pass # Si el archivo está corrupto, ignoramos y devolvemos 1.0
    return 1.0

factor_ia = obtener_factor_ia()

# --- INTERFAZ ---
st.image(LOGO_TU_EMPRESA, width=80)
st.title("Gestamp - Estimador Modular 3.0")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Configuración Técnica")
    proyecto = st.text_input("Nombre Proyecto", "Nuevo F21")
    oem = st.selectbox("OEM", ["Toyota", "VW", "Stellantis", "Ford", "BMW", "Mercedes"])
    img_p = st.file_uploader("Foto Producto", type=["jpg", "png"])
    spw = st.number_input("Puntos SPW", value=40)
    mastico = st.number_input("Mastico (mm)", value=0)
    tox = st.number_input("Nº Tox", value=0)
    tuercas = st.number_input("Tuercas", value=0)
    tuckers = st.number_input("Tuckers", value=0)
    marcado = st.checkbox("Marcado Láser")

with col2:
    st.subheader("Capacidad y Logística")
    dias = st.number_input("Días/Año", value=220)
    turnos = st.number_input("Turnos/Día", value=2)
    horas = st.number_input("Horas/Turno", value=7.5)
    v1 = st.number_input("Volumen Año 1", value=100000)
    p_kit = st.number_input("Piezas Kit", value=1)
    p_rack = st.number_input("Piezas Rack", value=1)
    peso = st.number_input("Peso (kg)", value=5.0)

if st.button("🚀 GENERAR ANÁLISIS"):
    # 1. Llamada a Lógica
    res_f1 = calcular_ciclo_completo(spw, mastico, tox, 0, tuercas, tuckers, marcado, factor_ia)
    t_man, n_mod, sat, cap_max, res_anual = calcular_capacidad_y_mod(res_f1['t_ciclo'], dias, turnos, horas, [v1], p_kit, p_rack, peso)
    
    # 2. Mostrar Resultados
    st.success(f"Tiempo Ciclo: {res_f1['t_ciclo']:.2f}s | MOD: {n_mod} | Líneas: {res_anual[0]['Instalaciones']}")
    
    # 3. Preparar Reporte
    datos_reporte = {
        "proyecto": proyecto, "oem": oem, "version": "3.0", 
        "factor_ia": factor_ia, "t_ciclo": res_f1['t_ciclo'],
        "saturacion": sat * 100, "n_mod": n_mod
    }
    pptx_bytes = generar_reporte_pptx(datos_reporte, img_p)
    
    st.download_button("📥 DESCARGAR REPORTE GESTAMP", pptx_bytes, f"Oferta_{proyecto}.pptx")