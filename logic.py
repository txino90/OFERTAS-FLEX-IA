import math
import pickle
import json
import numpy as np
from pathlib import Path

# ============================================================================
# CARGAR MODELO DE REGRESIÓN ENTRENADO
# ============================================================================

_modelo = None
_config = None

def _cargar_modelo():
    """Carga el modelo de regresión entrenado (una sola vez)"""
    global _modelo, _config
    
    if _modelo is None:
        try:
            ruta_modelo = Path(__file__).parent / 'modelo_regresion.pkl'
            ruta_config = Path(__file__).parent / 'config_modelo.json'
            
            if ruta_modelo.exists() and ruta_config.exists():
                with open(ruta_modelo, 'rb') as f:
                    _modelo = pickle.load(f)
                
                with open(ruta_config, 'r') as f:
                    _config = json.load(f)
        except Exception as e:
            print(f"⚠️ Error cargando modelo: {e}")
            _modelo = None
            _config = None
    
    return _modelo, _config

def calcular_ciclo_completo(spw, mastico_mm, tox, rh_mm, tuercas, tuckers, marcado, factor_ia):
    """
    Calcula el tiempo de ciclo usando el modelo de regresión entrenado.
    
    VERSIÓN 2.0: Modelo matemático basado en datos históricos
    
    Args:
        spw: Puntos de soldadura
        mastico_mm: Mastico en mm
        tox: Número de Tox
        rh_mm: RH en mm
        tuercas: Número de tuercas
        tuckers: Número de tuckers
        marcado: Boolean si lleva marcado láser
        factor_ia: Factor de IA (actualmente no usado, para futuras mejoras)
    
    Returns:
        Dict con tiempo de ciclo y desglose
    """
    
    # Cargar modelo de regresión
    modelo, config = _cargar_modelo()
    
    # ====================================================================
    # OPCIÓN 1: Usar modelo de regresión (si está disponible)
    # ====================================================================
    if modelo is not None and config is not None:
        try:
            # Preparar datos según el modelo entrenado
            variables_entrada = config['variables_entrada']
            
            # Crear diccionario con valores
            datos_entrada = {
                'SPW': spw,
                'Peso': 0,  # No disponible en interfaz, usar estimación
                'ANCHO_ASSY': 0,  # No disponible, usar estimación
            }
            
            # Nota: El modelo fue entrenado con Peso y ANCHO_ASSY
            # Aquí estimamos basándonos en correlaciones
            # Peso ≈ SPW * 0.2 (aproximación del histórico)
            # ANCHO_ASSY ≈ SPW * 4.5 (aproximación del histórico)
            
            datos_entrada['Peso'] = spw * 0.2
            datos_entrada['ANCHO_ASSY'] = spw * 4.5
            
            # Hacer predicción
            X_entrada = np.array([[datos_entrada[var] for var in variables_entrada]])
            t_ciclo = modelo.predict(X_entrada)[0]
            
            # Ajustar por factor_ia si aplica
            t_ciclo = t_ciclo * factor_ia
            
            return {
                "t_ciclo": max(t_ciclo, 10.0),  # Mínimo 10 segundos
                "t_soldadores": t_ciclo * 0.7,  # Estimación
                "t_manipulador": t_ciclo * 0.3,  # Estimación
                "modelo": "REGRESIÓN_LINEAL",
                "r2": config['r2_score']
            }
        
        except Exception as e:
            print(f"⚠️ Error en predicción: {e}")
            # Fallback al modelo antiguo
            pass
    
    # ====================================================================
    # OPCIÓN 2: Modelo antiguo (fallback si regresión no funciona)
    # ====================================================================
    # Grupo Soldadores (Robots 1, 2, 3)
    t_proc = (spw * 6.5) + (mastico_mm / 10.0) + (tox * 5.0) + (rh_mm / 10.0)
    penalizacion = (41.0 if mastico_mm > 0 else 0) + (25.0 if tox > 0 else 0)
    t_soldadores = (t_proc / 2.4) + penalizacion
    
    # Grupo Manipulador (Robot 4)
    t_manipulador = 16.0 + (tuercas * 8.0) + (tuckers * 7.0) + (14.0 if marcado else 0.0)
    
    # Cuello de botella + IA
    t_base = max(t_soldadores, t_manipulador)
    t_final_ia = t_base * factor_ia
    
    return {
        "t_ciclo": t_final_ia,
        "t_soldadores": t_soldadores,
        "t_manipulador": t_manipulador,
        "modelo": "HARDCODED_FALLBACK",
        "r2": 0.0
    }

def calcular_capacidad_y_mod(t_ciclo, dias, turnos, horas, volumenes, p_kit, p_rack, peso):
    # Lógica MOD
    t_kit = p_kit * 5.0
    t_rack = (p_rack * 25.0) if peso >= 10 else (p_rack * 6.0 + peso * 0.5)
    t_manual = t_kit + t_rack
    sat = t_manual / t_ciclo if t_ciclo > 0 else 0
    n_mod_celda = 2 if sat > 1.0 else 1
    
    # Capacidad
    segundos_disponibles = dias * turnos * horas * 3600
    cap_max_linea = (segundos_disponibles * 0.80) / t_ciclo if t_ciclo > 0 else 0
    
    res_anual = []
    for i, vol in enumerate(volumenes):
        n_lineas = math.ceil(vol / cap_max_linea) if cap_max_linea > 0 else 0
        res_anual.append({
            "Año": i + 1,
            "Volumen": vol,
            "Instalaciones": n_lineas,
            "Operarios_Turno": n_lineas * n_mod_celda
        })
        
    return t_manual, n_mod_celda, sat, cap_max_linea, res_anual