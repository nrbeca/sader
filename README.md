# SADER - Sistema de Reportes Presupuestarios

Aplicación web para automatizar la generación de reportes presupuestarios de la Secretaría de Agricultura y Desarrollo Rural (SADER).

## Características

- **MAP (Módulo de Adecuaciones Presupuestarias)**
  - Genera cuadro de presupuesto por programa presupuestario
  - Calcula congelados y modificados netos
  - Exporta a Excel con formato institucional

- **SICOP (Sistema de Contabilidad y Presupuesto)**
  - Genera estado del ejercicio por Unidad Responsable
  - Agrupa por Sector Central, Oficinas, Órganos Desconcentrados y Entidades Paraestatales
  - Calcula ejercido real (ejercido + devengado + en trámite)

## Instalación Local

```bash
# Clonar o descargar el proyecto
cd sader-reportes

# Crear entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
streamlit run app.py
```

La aplicación estará disponible en `http://localhost:8501`

## Despliegue en Streamlit Cloud (Gratis)

### Opción 1: Desde GitHub

1. Sube este proyecto a un repositorio de GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu cuenta de GitHub
4. Selecciona el repositorio y el archivo `app.py`
5. ¡Listo! Tu app estará disponible en una URL pública

### Opción 2: Desde la interfaz de Streamlit

1. Crea una cuenta en [streamlit.io](https://streamlit.io)
2. Haz clic en "New app"
3. Sube los archivos del proyecto
4. Streamlit detectará automáticamente `app.py`

## Estructura del Proyecto

```
sader-reportes/
├── app.py                 # Aplicación principal Streamlit
├── modules/
│   ├── __init__.py
│   ├── config.py          # Configuraciones y constantes
│   ├── map_processor.py   # Lógica de procesamiento MAP
│   └── sicop_processor.py # Lógica de procesamiento SICOP
├── requirements.txt       # Dependencias
└── README.md              # Este archivo
```

## Instrucciones

1. **Selecciona el tipo de reporte** en el menú lateral (MAP o SICOP)
2. **Sube el archivo CSV** exportado del sistema correspondiente
3. **Revisa los resultados** en las pestañas de visualización
4. **Descarga el reporte** en formato Excel o CSV

##  Configuración Automática

La aplicación detecta automáticamente:

- **Fecha del archivo** desde el nombre (ej: `19-FEB-2026_MAP.csv`)
- **Configuración de año** (2025 vs 2026) para usar los programas/URs correctos
- **Mes del periodo** para calcular modificados y congelados al periodo

##  Personalización

### Agregar nuevos programas (MAP)

Edita `modules/config.py` y agrega el programa en:
- `PROGRAMAS_NOMBRES_2026`
- `PROGRAMAS_ESPECIFICOS_2026` (si debe aparecer en la tabla)

### Agregar nuevas URs (SICOP)

Edita `modules/config.py` y agrega la UR en:
- `DENOMINACIONES_2026`
- La lista correspondiente: `SECTOR_CENTRAL_2026`, `OFICINAS_2026`, etc.

##  Notas

- Los archivos CSV deben tener codificación `latin-1` (ISO-8859-1)
- El formato del nombre de archivo esperado es `DD-MMM-YYYY_SISTEMA.csv`
- La aplicación maneja automáticamente el cierre de año anterior (enero/febrero)

##  Soporte

Para reportar problemas o sugerir mejoras, contacta al área de Presupuesto de la UAF.

---

**Desarrollado para la Secretaría de Agricultura y Desarrollo Rural**  
Unidad de Administración y Finanzas
