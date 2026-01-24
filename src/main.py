"""
===============================================================================
GESTAMP FACTORY 21 - ESTIMADOR MODULAR 3.1 (GUI Desktop)
Modelo de Regresión Lineal + Análisis de Sensibilidad
===============================================================================
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import os
import sys
import json
import numpy as np
from pathlib import Path
from PIL import Image, ImageTk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Importar módulos locales (ajustar para el ejecutable)
if getattr(sys, 'frozen', False):
    # Si está ejecutando como ejecutable empaquetado
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Si está ejecutando como script Python
    BASE_DIR = Path(__file__).parent.parent

sys.path.insert(0, str(BASE_DIR))

from logic import calcular_ciclo_completo, calcular_capacidad_y_mod
from report_gen import generar_reporte_pptx_mejorado

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

DB_FILE = BASE_DIR / "base_datos_experta.csv"
DB_LIMPIA = BASE_DIR / "base_datos_limpia.csv"
CONFIG_FILE = BASE_DIR / "config_modelo.json"

# ============================================================================
# CLASE PRINCIPAL DE LA APLICACIÓN
# ============================================================================

class GestampEstimadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestamp Factory 21 v3.1 - Estimador Modular")
        self.root.geometry("1400x900")
        
        # Cargar configuración del modelo
        self.config_modelo = self.cargar_config_modelo()
        self.factor_ia = self.obtener_factor_ia()
        
        # Variables para almacenar foto del producto
        self.img_producto = None
        
        # Crear interfaz
        self.crear_interfaz()
        
    def cargar_config_modelo(self):
        """Carga la configuración del modelo de regresión"""
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def obtener_factor_ia(self):
        """Obtener factor IA basado en el R² del modelo"""
        if DB_LIMPIA.exists():
            try:
                df_temp = pd.read_csv(DB_LIMPIA)
                if not df_temp.empty:
                    if self.config_modelo:
                        return 1.0 + (self.config_modelo.get('r2_score', 0.7) - 0.7) * 0.1
            except Exception as e:
                print(f"⚠️ Error cargando factor IA: {e}")
        return 1.0
    
    def crear_interfaz(self):
        """Crear toda la interfaz gráfica"""
        
        # ====================================================================
        # ENCABEZADO
        # ====================================================================
        frame_header = tk.Frame(self.root, bg="#1E3A5F", height=80)
        frame_header.pack(fill=tk.X, side=tk.TOP)
        
        tk.Label(
            frame_header,
            text="🏭 Gestamp - Estimador Modular 3.1",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="#1E3A5F"
        ).pack(pady=20)
        
        # ====================================================================
        # NOTEBOOK (PESTAÑAS)
        # ====================================================================
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña 1: Configuración y Cálculo
        self.tab_config = tk.Frame(self.notebook)
        self.notebook.add(self.tab_config, text="⚙️ Configuración")
        
        # Pestaña 2: Análisis de Sensibilidad
        self.tab_sensibilidad = tk.Frame(self.notebook)
        self.notebook.add(self.tab_sensibilidad, text="📈 Sensibilidad")
        
        # Pestaña 3: Histórico
        self.tab_historico = tk.Frame(self.notebook)
        self.notebook.add(self.tab_historico, text="📋 Histórico")
        
        # Pestaña 4: Información del Modelo
        self.tab_modelo = tk.Frame(self.notebook)
        self.notebook.add(self.tab_modelo, text="🤖 Modelo IA")
        
        # Crear contenido de cada pestaña
        self.crear_tab_configuracion()
        self.crear_tab_sensibilidad()
        self.crear_tab_historico()
        self.crear_tab_modelo()
    
    def crear_tab_configuracion(self):
        """Crear la pestaña de configuración y cálculo"""
        
        # Frame principal con scroll
        canvas = tk.Canvas(self.tab_config)
        scrollbar = ttk.Scrollbar(self.tab_config, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ====================================================================
        # SECCIÓN 1: CONFIGURACIÓN TÉCNICA
        # ====================================================================
        frame_tecnico = tk.LabelFrame(scrollable_frame, text="⚙️ Configuración Técnica", 
                                       font=("Arial", 12, "bold"), padx=20, pady=20)
        frame_tecnico.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Identificación del proyecto
        tk.Label(frame_tecnico, text="Nombre Proyecto:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_proyecto = tk.Entry(frame_tecnico, width=30, font=("Arial", 10))
        self.entry_proyecto.insert(0, "G78_BEV_001")
        self.entry_proyecto.grid(row=0, column=1, pady=5)
        
        tk.Label(frame_tecnico, text="OEM:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.combo_oem = ttk.Combobox(frame_tecnico, width=28, font=("Arial", 10),
                                       values=["Toyota", "VW", "Stellantis", "Ford", "BMW", "Mercedes"])
        self.combo_oem.current(0)
        self.combo_oem.grid(row=1, column=1, pady=5)
        
        # Foto del producto
        tk.Button(frame_tecnico, text="📷 Cargar Foto Producto", 
                 command=self.cargar_foto_producto, 
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Tecnologías de unión
        tk.Label(frame_tecnico, text="Puntos SPW:", font=("Arial", 10)).grid(row=3, column=0, sticky="w", pady=5)
        self.spin_spw = tk.Spinbox(frame_tecnico, from_=0, to=500, width=28, font=("Arial", 10))
        self.spin_spw.delete(0, tk.END)
        self.spin_spw.insert(0, "100")
        self.spin_spw.grid(row=3, column=1, pady=5)
        
        tk.Label(frame_tecnico, text="Mastico (mm):", font=("Arial", 10)).grid(row=4, column=0, sticky="w", pady=5)
        self.spin_mastico = tk.Spinbox(frame_tecnico, from_=0, to=100, width=28, font=("Arial", 10))
        self.spin_mastico.delete(0, tk.END)
        self.spin_mastico.insert(0, "0")
        self.spin_mastico.grid(row=4, column=1, pady=5)
        
        tk.Label(frame_tecnico, text="Nº Tox:", font=("Arial", 10)).grid(row=5, column=0, sticky="w", pady=5)
        self.spin_tox = tk.Spinbox(frame_tecnico, from_=0, to=20, width=28, font=("Arial", 10))
        self.spin_tox.delete(0, tk.END)
        self.spin_tox.insert(0, "0")
        self.spin_tox.grid(row=5, column=1, pady=5)
        
        tk.Label(frame_tecnico, text="Tuercas Remachadas:", font=("Arial", 10)).grid(row=6, column=0, sticky="w", pady=5)
        self.spin_tuercas = tk.Spinbox(frame_tecnico, from_=0, to=50, width=28, font=("Arial", 10))
        self.spin_tuercas.delete(0, tk.END)
        self.spin_tuercas.insert(0, "0")
        self.spin_tuercas.grid(row=6, column=1, pady=5)
        
        tk.Label(frame_tecnico, text="Tuckers:", font=("Arial", 10)).grid(row=7, column=0, sticky="w", pady=5)
        self.spin_tuckers = tk.Spinbox(frame_tecnico, from_=0, to=50, width=28, font=("Arial", 10))
        self.spin_tuckers.delete(0, tk.END)
        self.spin_tuckers.insert(0, "0")
        self.spin_tuckers.grid(row=7, column=1, pady=5)
        
        # Procesos adicionales
        self.check_marcado_var = tk.BooleanVar()
        tk.Checkbutton(frame_tecnico, text="Marcado Láser", variable=self.check_marcado_var, 
                      font=("Arial", 10)).grid(row=8, column=0, columnspan=2, pady=5)
        
        # ====================================================================
        # SECCIÓN 2: CAPACIDAD Y LOGÍSTICA
        # ====================================================================
        frame_capacidad = tk.LabelFrame(scrollable_frame, text="📊 Capacidad y Logística", 
                                        font=("Arial", 12, "bold"), padx=20, pady=20)
        frame_capacidad.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        tk.Label(frame_capacidad, text="Días/Año:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.spin_dias = tk.Spinbox(frame_capacidad, from_=200, to=250, width=28, font=("Arial", 10))
        self.spin_dias.delete(0, tk.END)
        self.spin_dias.insert(0, "220")
        self.spin_dias.grid(row=0, column=1, pady=5)
        
        tk.Label(frame_capacidad, text="Turnos/Día:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.spin_turnos = tk.Spinbox(frame_capacidad, from_=1, to=3, width=28, font=("Arial", 10))
        self.spin_turnos.delete(0, tk.END)
        self.spin_turnos.insert(0, "2")
        self.spin_turnos.grid(row=1, column=1, pady=5)
        
        tk.Label(frame_capacidad, text="Horas/Turno:", font=("Arial", 10)).grid(row=2, column=0, sticky="w", pady=5)
        self.spin_horas = tk.Spinbox(frame_capacidad, from_=6.0, to=8.0, increment=0.5, width=28, font=("Arial", 10))
        self.spin_horas.delete(0, tk.END)
        self.spin_horas.insert(0, "7.5")
        self.spin_horas.grid(row=2, column=1, pady=5)
        
        # Volúmenes
        tk.Label(frame_capacidad, text="Volumen Año 1:", font=("Arial", 10)).grid(row=3, column=0, sticky="w", pady=5)
        self.entry_v1 = tk.Entry(frame_capacidad, width=30, font=("Arial", 10))
        self.entry_v1.insert(0, "100000")
        self.entry_v1.grid(row=3, column=1, pady=5)
        
        tk.Label(frame_capacidad, text="Volumen Año 2:", font=("Arial", 10)).grid(row=4, column=0, sticky="w", pady=5)
        self.entry_v2 = tk.Entry(frame_capacidad, width=30, font=("Arial", 10))
        self.entry_v2.insert(0, "100000")
        self.entry_v2.grid(row=4, column=1, pady=5)
        
        tk.Label(frame_capacidad, text="Volumen Año 3:", font=("Arial", 10)).grid(row=5, column=0, sticky="w", pady=5)
        self.entry_v3 = tk.Entry(frame_capacidad, width=30, font=("Arial", 10))
        self.entry_v3.insert(0, "100000")
        self.entry_v3.grid(row=5, column=1, pady=5)
        
        # Logística
        tk.Label(frame_capacidad, text="Piezas/Kit:", font=("Arial", 10)).grid(row=6, column=0, sticky="w", pady=5)
        self.spin_p_kit = tk.Spinbox(frame_capacidad, from_=1, to=10, width=28, font=("Arial", 10))
        self.spin_p_kit.delete(0, tk.END)
        self.spin_p_kit.insert(0, "1")
        self.spin_p_kit.grid(row=6, column=1, pady=5)
        
        tk.Label(frame_capacidad, text="Piezas/Rack:", font=("Arial", 10)).grid(row=7, column=0, sticky="w", pady=5)
        self.spin_p_rack = tk.Spinbox(frame_capacidad, from_=1, to=20, width=28, font=("Arial", 10))
        self.spin_p_rack.delete(0, tk.END)
        self.spin_p_rack.insert(0, "1")
        self.spin_p_rack.grid(row=7, column=1, pady=5)
        
        tk.Label(frame_capacidad, text="Peso (kg):", font=("Arial", 10)).grid(row=8, column=0, sticky="w", pady=5)
        self.entry_peso = tk.Entry(frame_capacidad, width=30, font=("Arial", 10))
        self.entry_peso.insert(0, "20.0")
        self.entry_peso.grid(row=8, column=1, pady=5)
        
        # ====================================================================
        # BOTÓN DE CÁLCULO
        # ====================================================================
        frame_botones = tk.Frame(scrollable_frame)
        frame_botones.grid(row=1, column=0, columnspan=2, pady=20)
        
        tk.Button(frame_botones, text="🚀 GENERAR ANÁLISIS COMPLETO", 
                 command=self.generar_analisis,
                 bg="#2196F3", fg="white", font=("Arial", 14, "bold"),
                 width=40, height=2).pack(pady=10)
        
        tk.Button(frame_botones, text="📥 GENERAR Y DESCARGAR REPORTE PPTX", 
                 command=self.generar_reporte,
                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                 width=40).pack(pady=5)
        
        # ====================================================================
        # ÁREA DE RESULTADOS
        # ====================================================================
        self.frame_resultados = tk.LabelFrame(scrollable_frame, text="📊 RESULTADOS", 
                                              font=("Arial", 12, "bold"), padx=20, pady=20)
        self.frame_resultados.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.text_resultados = scrolledtext.ScrolledText(self.frame_resultados, 
                                                         width=150, height=20,
                                                         font=("Courier New", 10))
        self.text_resultados.pack(fill=tk.BOTH, expand=True)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def crear_tab_sensibilidad(self):
        """Crear la pestaña de análisis de sensibilidad"""
        
        tk.Label(self.tab_sensibilidad, text="📈 Análisis de Sensibilidad", 
                font=("Arial", 16, "bold")).pack(pady=20)
        
        tk.Label(self.tab_sensibilidad, 
                text="Este análisis muestra cómo cambia el tiempo de ciclo al variar cada parámetro (±20%)",
                font=("Arial", 11)).pack(pady=10)
        
        tk.Button(self.tab_sensibilidad, text="🔄 EJECUTAR ANÁLISIS DE SENSIBILIDAD",
                 command=self.ejecutar_sensibilidad,
                 bg="#FF9800", fg="white", font=("Arial", 12, "bold"),
                 width=40, height=2).pack(pady=20)
        
        # Frame para gráficos
        self.frame_graficos_sensibilidad = tk.Frame(self.tab_sensibilidad)
        self.frame_graficos_sensibilidad.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    def crear_tab_historico(self):
        """Crear la pestaña de datos históricos"""
        
        tk.Label(self.tab_historico, text="📋 Base de Datos Histórica", 
                font=("Arial", 16, "bold")).pack(pady=20)
        
        tk.Button(self.tab_historico, text="🔄 CARGAR DATOS HISTÓRICOS",
                 command=self.cargar_historico,
                 bg="#9C27B0", fg="white", font=("Arial", 12, "bold"),
                 width=40, height=2).pack(pady=10)
        
        # Frame para tabla
        self.frame_tabla_historico = tk.Frame(self.tab_historico)
        self.frame_tabla_historico.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    def crear_tab_modelo(self):
        """Crear la pestaña de información del modelo"""
        
        tk.Label(self.tab_modelo, text="🤖 Información del Modelo de Regresión", 
                font=("Arial", 16, "bold")).pack(pady=20)
        
        info_text = scrolledtext.ScrolledText(self.tab_modelo, width=120, height=30,
                                              font=("Courier New", 10))
        info_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        if self.config_modelo:
            info_text.insert(tk.END, "✅ MODELO DE REGRESIÓN ENTRENADO\n\n")
            info_text.insert(tk.END, "="*80 + "\n")
            info_text.insert(tk.END, "MÉTRICAS DE CALIDAD:\n")
            info_text.insert(tk.END, "="*80 + "\n\n")
            
            info_text.insert(tk.END, f"• R² Score: {self.config_modelo['r2_score']:.2%}\n")
            info_text.insert(tk.END, f"  (Varianza explicada por el modelo)\n\n")
            
            info_text.insert(tk.END, f"• RMSE: {self.config_modelo['rmse']:.2f} segundos\n")
            info_text.insert(tk.END, f"  (Error cuadrático medio)\n\n")
            
            info_text.insert(tk.END, f"• MAE: {self.config_modelo['mae']:.2f} segundos\n")
            info_text.insert(tk.END, f"  (Error absoluto medio)\n\n")
            
            info_text.insert(tk.END, "\n" + "="*80 + "\n")
            info_text.insert(tk.END, "VARIABLES Y COEFICIENTES:\n")
            info_text.insert(tk.END, "="*80 + "\n\n")
            
            for var in self.config_modelo['variables_entrada']:
                coef = self.config_modelo['coeficientes'][var]
                info_text.insert(tk.END, f"• {var}: {coef:.4f}\n")
            
            info_text.insert(tk.END, f"\n• Intercept (Base): {self.config_modelo['intercept']:.2f} segundos\n")
            
            info_text.insert(tk.END, "\n\n" + "="*80 + "\n")
            info_text.insert(tk.END, "INFORMACIÓN ADICIONAL:\n")
            info_text.insert(tk.END, "="*80 + "\n\n")
            info_text.insert(tk.END, "ℹ️ El modelo fue entrenado con datos históricos reales de\n")
            info_text.insert(tk.END, "   procesos similares. Proporciona estimaciones más precisas\n")
            info_text.insert(tk.END, "   que modelos heurísticos tradicionales.\n\n")
            info_text.insert(tk.END, f"ℹ️ Factor IA actual: {self.factor_ia:.4f}\n")
        else:
            info_text.insert(tk.END, "⚠️ MODELO DE REGRESIÓN NO ENCONTRADO\n\n")
            info_text.insert(tk.END, "Por favor, ejecuta 'python analysis.py' para entrenar el modelo.\n")
            info_text.insert(tk.END, "El sistema utilizará un modelo de fallback basado en reglas.\n")
        
        info_text.config(state=tk.DISABLED)
    
    def cargar_foto_producto(self):
        """Cargar foto del producto"""
        filepath = filedialog.askopenfilename(
            title="Seleccionar foto del producto",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png"), ("Todos los archivos", "*.*")]
        )
        
        if filepath:
            self.img_producto = filepath
            messagebox.showinfo("Éxito", f"Foto cargada: {Path(filepath).name}")
    
    def generar_analisis(self):
        """Generar análisis completo"""
        try:
            # Obtener valores
            spw = int(self.spin_spw.get())
            mastico = float(self.spin_mastico.get())
            tox = int(self.spin_tox.get())
            tuercas = int(self.spin_tuercas.get())
            tuckers = int(self.spin_tuckers.get())
            marcado = self.check_marcado_var.get()
            
            dias = int(self.spin_dias.get())
            turnos = int(self.spin_turnos.get())
            horas = float(self.spin_horas.get())
            
            v1 = int(self.entry_v1.get())
            v2 = int(self.entry_v2.get()) if self.entry_v2.get() else 0
            v3 = int(self.entry_v3.get()) if self.entry_v3.get() else 0
            
            volumenes = [v1]
            if v2 > 0:
                volumenes.append(v2)
            if v3 > 0:
                volumenes.append(v3)
            
            p_kit = int(self.spin_p_kit.get())
            p_rack = int(self.spin_p_rack.get())
            peso = float(self.entry_peso.get())
            
            # Calcular
            res_f1 = calcular_ciclo_completo(spw, mastico, tox, 0, tuercas, tuckers, marcado, self.factor_ia)
            t_man, n_mod, sat, cap_max, res_anual = calcular_capacidad_y_mod(
                res_f1['t_ciclo'], dias, turnos, horas, volumenes, p_kit, p_rack, peso
            )
            
            # Mostrar resultados
            self.text_resultados.config(state=tk.NORMAL)
            self.text_resultados.delete(1.0, tk.END)
            
            self.text_resultados.insert(tk.END, "="*100 + "\n")
            self.text_resultados.insert(tk.END, "📊 RESULTADOS DEL ANÁLISIS\n")
            self.text_resultados.insert(tk.END, "="*100 + "\n\n")
            
            self.text_resultados.insert(tk.END, "MÉTRICAS PRINCIPALES:\n")
            self.text_resultados.insert(tk.END, "-"*100 + "\n")
            self.text_resultados.insert(tk.END, f"⏱️  Tiempo de Ciclo:     {res_f1['t_ciclo']:.2f} segundos\n")
            self.text_resultados.insert(tk.END, f"🤖 MOD:                  {n_mod} módulos\n")
            self.text_resultados.insert(tk.END, f"📊 Saturación:           {sat*100:.1f}%\n")
            self.text_resultados.insert(tk.END, f"📈 Capacidad Máxima:     {cap_max:,.0f} piezas/año\n")
            self.text_resultados.insert(tk.END, f"🤖 Factor IA:            {self.factor_ia:.4f}\n\n")
            
            self.text_resultados.insert(tk.END, "PLAN DE CAPACIDAD POR AÑOS:\n")
            self.text_resultados.insert(tk.END, "-"*100 + "\n")
            
            df_capacidad = pd.DataFrame(res_anual)
            self.text_resultados.insert(tk.END, df_capacidad.to_string(index=False) + "\n\n")
            
            self.text_resultados.insert(tk.END, "RECOMENDACIONES:\n")
            self.text_resultados.insert(tk.END, "-"*100 + "\n")
            
            if sat < 0.5:
                self.text_resultados.insert(tk.END, "✅ Saturación <50%: Instalar 1 MOD (1 operario)\n")
            elif sat <= 1.0:
                self.text_resultados.insert(tk.END, "⚠️  Saturación 50-100%: Instalar 1 MOD (1 operario + buffer)\n")
            else:
                self.text_resultados.insert(tk.END, f"🔴 Saturación >100%: Instalar {n_mod} MOD o más\n")
            
            self.text_resultados.insert(tk.END, f"\n• Líneas necesarias: {res_anual[0]['Instalaciones']} instalación(es)\n")
            self.text_resultados.insert(tk.END, f"• Operarios por turno: {res_anual[0]['Operarios_Turno']} personas/turno\n")
            
            self.text_resultados.config(state=tk.DISABLED)
            
            # Guardar resultados para reporte
            self.ultimo_resultado = {
                "proyecto": self.entry_proyecto.get(),
                "oem": self.combo_oem.get(),
                "version": "3.1",
                "factor_ia": self.factor_ia,
                "t_ciclo": res_f1['t_ciclo'],
                "saturacion": sat * 100,
                "n_mod": n_mod,
                "spw": spw,
                "peso": peso,
                "cap_max": cap_max,
                "res_anual": res_anual
            }
            
            messagebox.showinfo("Éxito", "Análisis completado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar análisis:\n{str(e)}")
    
    def generar_reporte(self):
        """Generar y descargar reporte PPTX"""
        try:
            if not hasattr(self, 'ultimo_resultado'):
                messagebox.showwarning("Advertencia", 
                                      "Primero debes generar un análisis antes de crear el reporte")
                return
            
            # Generar reporte
            img_file = None
            if self.img_producto:
                img_file = open(self.img_producto, 'rb')
            
            pptx_bytes = generar_reporte_pptx_mejorado(self.ultimo_resultado, img_file)
            
            if img_file:
                img_file.close()
            
            # Guardar archivo
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pptx",
                filetypes=[("PowerPoint", "*.pptx"), ("Todos los archivos", "*.*")],
                initialfile=f"Oferta_{self.ultimo_resultado['proyecto']}_v3.1.pptx"
            )
            
            if filepath:
                with open(filepath, 'wb') as f:
                    f.write(pptx_bytes.getvalue())
                
                messagebox.showinfo("Éxito", f"Reporte guardado en:\n{filepath}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte:\n{str(e)}")
    
    def ejecutar_sensibilidad(self):
        """Ejecutar análisis de sensibilidad"""
        try:
            # Limpiar frame anterior
            for widget in self.frame_graficos_sensibilidad.winfo_children():
                widget.destroy()
            
            # Obtener valores actuales
            spw = int(self.spin_spw.get())
            mastico = float(self.spin_mastico.get())
            tox = int(self.spin_tox.get())
            tuercas = int(self.spin_tuercas.get())
            tuckers = int(self.spin_tuckers.get())
            marcado = self.check_marcado_var.get()
            peso = float(self.entry_peso.get())
            
            # Calcular tiempo base
            res_base = calcular_ciclo_completo(spw, mastico, tox, 0, tuercas, tuckers, marcado, self.factor_ia)
            t_base = res_base['t_ciclo']
            
            # Análisis para SPW
            variaciones_pct = np.linspace(-20, 20, 9)
            tiempos_spw = []
            
            for pct in variaciones_pct:
                spw_temp = spw * (1 + pct/100)
                res_temp = calcular_ciclo_completo(spw_temp, mastico, tox, 0, tuercas, tuckers, marcado, self.factor_ia)
                tiempos_spw.append(res_temp['t_ciclo'])
            
            # Crear gráfico para SPW
            fig1, ax1 = plt.subplots(figsize=(8, 5))
            ax1.plot(variaciones_pct, tiempos_spw, marker='o', linewidth=2, markersize=8, color='#FF6B6B')
            ax1.axvline(x=0, color='green', linestyle='--', alpha=0.5, label='Base')
            ax1.axhline(y=t_base, color='green', linestyle='--', alpha=0.5)
            ax1.set_xlabel('Variación (%)', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Tiempo de Ciclo (s)', fontsize=12, fontweight='bold')
            ax1.set_title(f'Sensibilidad: Puntos SPW\nBase: {spw} puntos', fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            canvas1 = FigureCanvasTkAgg(fig1, master=self.frame_graficos_sensibilidad)
            canvas1.draw()
            canvas1.get_tk_widget().pack(side=tk.LEFT, padx=10, pady=10)
            
            messagebox.showinfo("Éxito", "Análisis de sensibilidad completado")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis de sensibilidad:\n{str(e)}")
    
    def cargar_historico(self):
        """Cargar y mostrar datos históricos"""
        try:
            # Limpiar frame anterior
            for widget in self.frame_tabla_historico.winfo_children():
                widget.destroy()
            
            if not DB_LIMPIA.exists():
                messagebox.showwarning("Advertencia", 
                                      "Base de datos histórica limpia no encontrada")
                return
            
            df_historico = pd.read_csv(DB_LIMPIA)
            
            # Crear treeview
            tree = ttk.Treeview(self.frame_tabla_historico, show='headings')
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Scrollbars
            vsb = ttk.Scrollbar(self.frame_tabla_historico, orient="vertical", command=tree.yview)
            vsb.pack(side=tk.RIGHT, fill=tk.Y)
            hsb = ttk.Scrollbar(self.frame_tabla_historico, orient="horizontal", command=tree.xview)
            hsb.pack(side=tk.BOTTOM, fill=tk.X)
            
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            
            # Configurar columnas
            tree['columns'] = list(df_historico.columns)
            for col in df_historico.columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            
            # Insertar datos
            for idx, row in df_historico.iterrows():
                tree.insert('', tk.END, values=list(row))
            
            messagebox.showinfo("Éxito", f"Cargados {len(df_historico)} registros históricos")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar histórico:\n{str(e)}")

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    root = tk.Tk()
    app = GestampEstimadorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
