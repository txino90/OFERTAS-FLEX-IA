# Gestamp Factory 21 - Estimador Modular 3.1

## 🏭 Descripción

Sistema de estimación inteligente para procesos de fabricación en automoción, basado en **Regresión Lineal Múltiple** con datos históricos reales.

### Versiones disponibles:

- **Aplicación Web (Streamlit)**: `app.py` - Interfaz web interactiva
- **Aplicación Desktop (GUI)**: `src/main.py` - Ejecutable de escritorio con Tkinter

## 🚀 Instalación

### Opción 1: Ejecutable de Escritorio (Recomendado para usuarios)

1. Descarga el ejecutable desde [Releases](https://github.com/txino90/OFERTAS-FLEX-IA/releases)
2. Ejecuta el archivo:
   - **Windows**: `GestampEstimador.exe`
   - **Linux**: `./GestampEstimador` (dar permisos: `chmod +x GestampEstimador`)

### Opción 2: Ejecutar desde código fuente

#### Aplicación Desktop (GUI):

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación GUI
python src/main.py
```

#### Aplicación Web (Streamlit):

```bash
# Instalar streamlit adicional
pip install streamlit>=1.28.0

# Ejecutar aplicación web
streamlit run app.py
```

## 🔨 Compilar ejecutable localmente

### Windows:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="GestampEstimador" ^
  --add-data="base_datos_experta.csv;." ^
  --add-data="base_datos_limpia.csv;." ^
  --add-data="config_modelo.json;." ^
  --add-data="modelo_regresion.pkl;." ^
  --hidden-import=PIL ^
  --hidden-import=PIL._tkinter_finder ^
  --hidden-import=matplotlib.backends.backend_tkagg ^
  --collect-all matplotlib ^
  --collect-all sklearn ^
  src/main.py
```

### Linux/Mac:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="GestampEstimador" \
  --add-data="base_datos_experta.csv:." \
  --add-data="base_datos_limpia.csv:." \
  --add-data="config_modelo.json:." \
  --add-data="modelo_regresion.pkl:." \
  --hidden-import=PIL \
  --hidden-import=PIL._tkinter_finder \
  --hidden-import=matplotlib.backends.backend_tkagg \
  --collect-all matplotlib \
  --collect-all sklearn \
  src/main.py
```

El ejecutable se generará en la carpeta `dist/`.

## 📊 Características

### Aplicación Desktop (GUI):

✅ **Interfaz gráfica nativa** - No requiere navegador
✅ **Cálculo de tiempos de ciclo** - Modelo de regresión lineal
✅ **Análisis de capacidad** - Planificación multi-año
✅ **Análisis de sensibilidad** - Gráficos interactivos
✅ **Generación de reportes PPTX** - Exportación profesional
✅ **Base de datos histórica** - Visualización y análisis

### Pestañas disponibles:

1. **⚙️ Configuración** - Parámetros técnicos y cálculo
2. **📈 Sensibilidad** - Análisis de impacto de variables
3. **📋 Histórico** - Datos de proyectos anteriores
4. **🤖 Modelo IA** - Información del modelo de regresión

## 🤖 Modelo de IA

El sistema utiliza un modelo de **Regresión Lineal Múltiple** entrenado con datos históricos reales:

- **R² Score**: Mide la precisión del modelo (varianza explicada)
- **RMSE**: Error cuadrático medio en segundos
- **MAE**: Error absoluto medio en segundos

### Entrenar el modelo:

```bash
python analysis.py
```

Esto generará:
- `modelo_regresion.pkl` - Modelo entrenado
- `config_modelo.json` - Configuración y métricas

## 📁 Estructura del Proyecto

```
OFERTAS-FLEX-IA/
├── src/
│   └── main.py                 # Aplicación GUI Desktop
├── app.py                      # Aplicación Web (Streamlit)
├── logic.py                    # Lógica de cálculo
├── analysis.py                 # Entrenamiento del modelo
├── report_gen.py               # Generación de reportes
├── data_cleaning.py            # Limpieza de datos
├── requirements.txt            # Dependencias
├── base_datos_experta.csv      # Datos históricos
├── base_datos_limpia.csv       # Datos procesados
├── config_modelo.json          # Configuración del modelo
├── modelo_regresion.pkl        # Modelo entrenado
└── .github/workflows/
    └── build.yml               # CI/CD para compilar ejecutables
```

## 🔧 Desarrollo

### Variables de entrada:

- **SPW**: Puntos de soldadura
- **Peso**: Peso de la pieza (kg)
- **Mastico**: Mastico en mm
- **Tox**: Número de Tox
- **Tuercas**: Tuercas remachadas
- **Tuckers**: Número de tuckers
- **Marcado Láser**: Boolean

### Outputs:

- **Tiempo de ciclo**: Segundos por pieza
- **MOD**: Número de módulos necesarios
- **Saturación**: Porcentaje de uso
- **Capacidad máxima**: Piezas por año

## 📦 Dependencias

```
pandas>=2.0.0
openpyxl>=3.10.0
numpy>=1.24.0
python-pptx>=0.6.21
Pillow>=10.0.0
scikit-learn>=1.3.0
matplotlib>=3.8.0
```

Para la versión web, añadir:
```
streamlit>=1.28.0
```

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -am 'Añadir nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crea un Pull Request

## 📄 Licencia

Este proyecto es propiedad de Gestamp Factory 21.

## 📧 Contacto

automation@gestamp.com

---

**Gestamp Factory 21 v3.1** | Estimador Modular Inteligente
