"""
SADER - Sistema de Reportes Presupuestarios
Aplicacion Streamlit para procesar archivos MAP y SICOP
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import io
import base64

# Importar modulos propios
from config import (
    MONTH_NAMES_FULL, formatear_fecha, obtener_ultimo_dia_habil, get_config_by_year
)
from map_processor import procesar_map
from sicop_processor import procesar_sicop
from excel_map import generar_excel_map
from excel_sicop import generar_excel_sicop

# ============================================================================
# CONSTANTES DE COLORES
# ============================================================================
COLOR_AZUL = '#4472C4'      # Disponible, Por pagar
COLOR_NARANJA = '#ED7D31'   # Ejercido, Pagado
COLOR_VINO = '#9B2247'
COLOR_BEIGE = '#E6D194'
COLOR_GRIS = '#98989A'
COLOR_VERDE = '#002F2A'

# ============================================================================
# CONFIGURACION DE PAGINA
# ============================================================================

st.set_page_config(
    page_title="SADER - Reportes Presupuestarios",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ESTILOS CSS
# ============================================================================

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    
    .main-header {
        background: linear-gradient(135deg, #9B2247 0%, #7a1b38 100%);
        color: white; padding: 1.5rem 2rem; border-radius: 10px;
        margin-bottom: 2rem; text-align: center;
    }
    .main-header h1 { margin: 0; font-size: 2rem; font-weight: 600; color: white; }
    .main-header p { margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1rem; color: white; }
    
    .kpi-card {
        background: white; border-radius: 12px; padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid #9B2247;
    }
    .kpi-label { font-size: 0.85rem; color: #333; text-transform: uppercase; margin-bottom: 0.5rem; }
    .kpi-value { font-size: 1.8rem; font-weight: 700; color: #9B2247; }
    .kpi-subtitle { font-size: 0.8rem; color: #666; margin-top: 0.25rem; }
    
    .upload-zone {
        border: 2px dashed #E6D194; border-radius: 12px; padding: 2rem;
        text-align: center; background: #fafafa;
    }
    
    .instrucciones-box {
        background: #f8f8f8; border: 1px solid #E6D194;
        border-radius: 10px; padding: 1.5rem; margin-bottom: 1rem;
    }
    .instrucciones-box h4 { color: #9B2247; margin-top: 0; }
    
    /* Sidebar GRIS */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #98989A 0%, #787878 100%);
    }
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span { color: white !important; }
    
    /* Boton descarga VERDE */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #002F2A 0%, #004d40 100%);
        color: white; border: none; border-radius: 8px;
        padding: 0.75rem 2rem; font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] { background: #9B2247 !important; color: white !important; }
    h1, h2, h3, h4 { color: #9B2247; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def format_currency(value):
    if pd.isna(value) or value == 0:
        return "$0.00"
    return f"${value:,.2f}"

def format_currency_millions(value):
    if pd.isna(value) or value == 0:
        return "$0.00 M"
    return f"${value/1_000_000:,.2f} M"

def format_percentage(value):
    if pd.isna(value):
        return "0.00%"
    return f"{value*100:.2f}%"

def create_kpi_card(label, value, subtitle="", bg_color=None):
    if bg_color:
        if bg_color in [COLOR_GRIS, COLOR_BEIGE]:
            text_color = '#000'
        else:
            text_color = '#fff'
        return f"""
        <div style="background: {bg_color}; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;">
            <div style="font-size: 0.75rem; color: {text_color}; text-transform: uppercase; margin-bottom: 0.3rem;">{label}</div>
            <div style="font-size: 1.3rem; font-weight: 700; color: {text_color};">{value}</div>
            <div style="font-size: 0.7rem; color: {text_color}; opacity: 0.9;">{subtitle}</div>
        </div>
        """
    else:
        return f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-subtitle">{subtitle}</div>
        </div>
        """

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.2);">
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; color: white; font-weight: bold; font-size: 1.5rem;">
            SADER
        </div>
        <p style="color: rgba(255,255,255,0.8); font-size: 0.8rem; margin-top: 0.5rem;">Sistema de Reportes</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Tipo de Reporte")
    reporte_tipo = st.radio(
        "Selecciona el reporte a generar:",
        ["MAP - Cuadro de presupuesto", "SICOP - Estado del Ejercicio"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### Configuracion")
    hoy = date.today()
    ultimo_habil = obtener_ultimo_dia_habil(hoy)
    st.markdown(f"**Fecha actual:** {formatear_fecha(hoy)}")
    st.caption(f"Ultimo dia habil: {formatear_fecha(ultimo_habil)}")

# ============================================================================
# CONTENIDO PRINCIPAL
# ============================================================================

st.markdown("""
<div class="main-header">
    <h1>Sistema de Reportes Presupuestarios</h1>
    <p>Secretaria de Agricultura y Desarrollo Rural</p>
</div>
""", unsafe_allow_html=True)

es_map = "MAP" in reporte_tipo

# Layout: Upload e Instrucciones
col_upload, col_instrucciones = st.columns([2, 1])

with col_upload:
    st.markdown(f"### {'MAP' if es_map else 'SICOP'} - Cargar Archivo")
    uploaded_file = st.file_uploader(
        "Arrastra tu archivo CSV aqui o haz clic para seleccionar",
        type=['csv'],
        help="Sube el archivo CSV exportado del sistema correspondiente"
    )

with col_instrucciones:
    st.markdown("""
    <div class="instrucciones-box">
        <h4>Instrucciones</h4>
        <ol>
            <li>Selecciona el tipo de reporte en el menu lateral</li>
            <li>Sube el archivo CSV correspondiente</li>
            <li>Revisa los resultados</li>
            <li>Descarga el Excel</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='latin-1', low_memory=False)
        filename = uploaded_file.name
        
        st.success(f"Archivo cargado: **{filename}** ({len(df):,} registros)")
        
        with st.spinner("Procesando datos..."):
            if es_map:
                resultados = procesar_map(df, filename)
            else:
                resultados = procesar_sicop(df, filename)
        
        metadata = resultados['metadata']
        config = metadata['config']
        
        # Info del archivo
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.metric("Fecha del archivo", formatear_fecha(metadata['fecha_archivo']))
        with col_info2:
            st.metric("Mes", MONTH_NAMES_FULL[metadata['mes'] - 1])
        with col_info3:
            año_config = "2026 (Nuevos)" if config['usar_2026'] else "2025 (Anteriores)"
            st.metric("Configuracion", año_config)
        
        st.markdown("---")
        
        # ====================================================================
        # RESULTADOS MAP
        # ====================================================================
        
        if es_map:
            st.markdown("### Resumen Presupuestario")
            totales = resultados['totales']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(create_kpi_card("PEF Original", format_currency_millions(totales['Original']), "Presupuesto aprobado"), unsafe_allow_html=True)
            with col2:
                st.markdown(create_kpi_card("Modificado Anual", format_currency_millions(totales['ModificadoAnualNeto']), "Neto de congelados", COLOR_VINO), unsafe_allow_html=True)
            with col3:
                st.markdown(create_kpi_card("Modificado Periodo", format_currency_millions(totales['ModificadoPeriodoNeto']), f"Al mes de {MONTH_NAMES_FULL[metadata['mes'] - 1]}", COLOR_BEIGE), unsafe_allow_html=True)
            with col4:
                st.markdown(create_kpi_card("Ejercido", format_currency_millions(totales['Ejercido']), format_percentage(totales['Ejercido'] / totales['ModificadoPeriodoNeto'] if totales['ModificadoPeriodoNeto'] > 0 else 0) + " avance", COLOR_NARANJA), unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Tabs MAP
            tab1, tab2, tab3 = st.tabs(["Por Seccion", "Detalle Programas", "Graficas"])
            
            categorias = resultados['categorias']
            cat_data = []
            for cat_key, cat_name in [
                ('servicios_personales', 'Servicios Personales'),
                ('gasto_corriente', 'Gasto Corriente'),
                ('subsidios', 'Subsidios y Gastos asociados'),
                ('otros_programas', 'Otros programas'),
                ('bienes_muebles', 'Bienes muebles e intangibles')
            ]:
                if cat_key in categorias:
                    datos = categorias[cat_key]
                    disponible = datos['ModificadoPeriodoNeto'] - datos['Ejercido']
                    pct = datos['Ejercido'] / datos['ModificadoPeriodoNeto'] * 100 if datos['ModificadoPeriodoNeto'] > 0 else 0
                    cat_data.append({
                        'Categoria': cat_name, 'Original': datos['Original'],
                        'Mod. Anual': datos['ModificadoAnualNeto'], 'Mod. Periodo': datos['ModificadoPeriodoNeto'],
                        'Ejercido': datos['Ejercido'], 'Disponible': disponible, '% Avance': pct
                    })
            df_cat = pd.DataFrame(cat_data)
            
            with tab1:
                st.dataframe(df_cat.style.format({
                    'Original': '${:,.2f}', 'Mod. Anual': '${:,.2f}', 'Mod. Periodo': '${:,.2f}',
                    'Ejercido': '${:,.2f}', 'Disponible': '${:,.2f}', '% Avance': '{:.2f}%'
                }), use_container_width=True, hide_index=True)
            
            with tab2:
                programas = resultados['programas']
                prog_nombres = config['programas_nombres']
                prog_data = []
                for prog, datos in programas.items():
                    if datos['Original'] > 0 or datos['ModificadoAnualNeto'] > 0:
                        pct = datos['Ejercido'] / datos['ModificadoPeriodoNeto'] * 100 if datos['ModificadoPeriodoNeto'] > 0 else 0
                        prog_data.append({
                            'Programa': prog,
                            'Nombre': prog_nombres.get(prog, prog)[:50],
                            'Original': datos['Original'], 'Mod. Anual': datos['ModificadoAnualNeto'],
                            'Mod. Periodo': datos['ModificadoPeriodoNeto'], 'Ejercido': datos['Ejercido'], '% Avance': pct
                        })
                df_prog = pd.DataFrame(prog_data)
                st.dataframe(df_prog.style.format({
                    'Original': '${:,.2f}', 'Mod. Anual': '${:,.2f}', 'Mod. Periodo': '${:,.2f}',
                    'Ejercido': '${:,.2f}', '% Avance': '{:.2f}%'
                }), use_container_width=True, hide_index=True)
            
            with tab3:
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    fig_pie = px.pie(df_cat, values='Mod. Periodo', names='Categoria',
                        color_discrete_sequence=[COLOR_VINO, COLOR_BEIGE, COLOR_GRIS, COLOR_VERDE, '#4a4a4a'])
                    fig_pie.update_layout(showlegend=True, margin=dict(t=20, b=20, l=20, r=20))
                    st.plotly_chart(fig_pie, use_container_width=True, key="pie_map")
                with col_g2:
                    fig_bar = go.Figure()
                    fig_bar.add_trace(go.Bar(name='Ejercido', x=df_cat['Categoria'], y=df_cat['Ejercido'], marker_color=COLOR_NARANJA))
                    fig_bar.add_trace(go.Bar(name='Disponible', x=df_cat['Categoria'], y=df_cat['Disponible'], marker_color=COLOR_AZUL))
                    fig_bar.update_layout(barmode='stack', xaxis_tickangle=-45, margin=dict(t=20, b=100, l=20, r=20))
                    st.plotly_chart(fig_bar, use_container_width=True, key="bar_map")
        
        # ====================================================================
        # RESULTADOS SICOP
        # ====================================================================
        
        else:
            st.markdown("### Resumen por Unidad Responsable")
            totales = resultados['totales']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(create_kpi_card("Original", format_currency_millions(totales['Original']), "Presupuesto aprobado"), unsafe_allow_html=True)
            with col2:
                st.markdown(create_kpi_card("Modificado Anual", format_currency_millions(totales['Modificado_anual']), "Neto de congelados", COLOR_VINO), unsafe_allow_html=True)
            with col3:
                st.markdown(create_kpi_card("Ejercido Acumulado", format_currency_millions(totales['Ejercido_acumulado']), "Ejercido + Devengado + Tramite", COLOR_NARANJA), unsafe_allow_html=True)
            with col4:
                pct_avance = totales['Pct_avance_periodo'] * 100 if totales['Pct_avance_periodo'] else 0
                st.markdown(create_kpi_card("Avance al Periodo", f"{pct_avance:.2f}%", f"Meta: {metadata['mes'] / 12 * 100:.1f}%", COLOR_AZUL), unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Tabs SICOP con Dashboard Presupuesto y Austeridad
            tab1, tab2, tab3, tab4 = st.tabs(["Por Seccion", "Dashboard Presupuesto", "Dashboard Austeridad", "Graficas"])
            
            with tab1:
                subtotales = resultados['subtotales']
                seccion_data = []
                for seccion_key, seccion_name in [
                    ('sector_central', 'Sector Central'),
                    ('oficinas', 'Oficinas de Representacion'),
                    ('organos_desconcentrados', 'Organos Desconcentrados'),
                    ('entidades_paraestatales', 'Entidades Paraestatales')
                ]:
                    if seccion_key in subtotales:
                        datos = subtotales[seccion_key]
                        pct = datos['Pct_avance_periodo'] * 100 if datos.get('Pct_avance_periodo') else 0
                        seccion_data.append({
                            'Seccion': seccion_name, 'Original': datos['Original'],
                            'Mod. Anual': datos['Modificado_anual'], 'Mod. Periodo': datos['Modificado_periodo'],
                            'Ejercido': datos['Ejercido_acumulado'], 'Disponible': datos['Disponible_periodo'], '% Avance': pct
                        })
                df_seccion = pd.DataFrame(seccion_data)
                st.dataframe(df_seccion.style.format({
                    'Original': '${:,.2f}', 'Mod. Anual': '${:,.2f}', 'Mod. Periodo': '${:,.2f}',
                    'Ejercido': '${:,.2f}', 'Disponible': '${:,.2f}', '% Avance': '{:.2f}%'
                }), use_container_width=True, hide_index=True)
            
            # ================================================================
            # TAB 2: DASHBOARD PRESUPUESTO
            # ================================================================
            with tab2:
                resumen = resultados['resumen']
                denominaciones = config['denominaciones']
                
                urs_disponibles = resumen['UR'].tolist()
                urs_con_nombre = [f"{ur} - {denominaciones.get(ur, 'Sin nombre')[:40]}" for ur in urs_disponibles]
                
                ur_seleccionada = st.selectbox("Selecciona una Unidad Responsable:", options=urs_con_nombre, index=0, key="ur_pres")
                ur_codigo = ur_seleccionada.split(" - ")[0]
                datos_ur = resumen[resumen['UR'] == ur_codigo].iloc[0]
                
                st.markdown(f"### Dashboard Presupuesto - {denominaciones.get(ur_codigo, ur_codigo)}")
                
                # KPIs Fila 1
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(create_kpi_card("Original", format_currency(datos_ur['Original']), ""), unsafe_allow_html=True)
                with col2:
                    st.markdown(create_kpi_card("Modificado Anual", format_currency(datos_ur['Modificado_anual']), "", COLOR_VINO), unsafe_allow_html=True)
                with col3:
                    st.markdown(create_kpi_card("Modificado Periodo", format_currency(datos_ur['Modificado_periodo']), "", COLOR_BEIGE), unsafe_allow_html=True)
                with col4:
                    st.markdown(create_kpi_card("Ejercido", format_currency(datos_ur['Ejercido_acumulado']), "", COLOR_NARANJA), unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # KPIs Fila 2
                col5, col6, col7, col8 = st.columns(4)
                with col5:
                    st.markdown(create_kpi_card("Disponible Anual", format_currency(datos_ur['Disponible_anual']), "", COLOR_AZUL), unsafe_allow_html=True)
                with col6:
                    st.markdown(create_kpi_card("Disponible Periodo", format_currency(datos_ur['Disponible_periodo']), "", COLOR_AZUL), unsafe_allow_html=True)
                with col7:
                    st.markdown(create_kpi_card("Congelado Anual", "-", "", COLOR_GRIS), unsafe_allow_html=True)
                with col8:
                    st.markdown(create_kpi_card("Congelado Periodo", "-", "", COLOR_GRIS), unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Graficas y Pasivos
                col_izq, col_der = st.columns([1, 1])
                
                with col_izq:
                    # Graficas de avance
                    col_g1, col_g2 = st.columns(2)
                    pct_anual = datos_ur['Pct_avance_anual'] * 100 if datos_ur['Pct_avance_anual'] else 0
                    pct_periodo = datos_ur['Pct_avance_periodo'] * 100 if datos_ur['Pct_avance_periodo'] else 0
                    
                    with col_g1:
                        st.markdown("**Avance ejercicio anual**")
                        fig1 = go.Figure(go.Pie(values=[datos_ur['Ejercido_acumulado'], max(0, datos_ur['Disponible_anual'])],
                            labels=['Ejercido', 'Disponible'], hole=0.6, marker_colors=[COLOR_NARANJA, COLOR_AZUL], textinfo='none'))
                        fig1.add_annotation(text=f"{pct_anual:.2f}%", x=0.5, y=0.5, font_size=18, font_color=COLOR_VINO, showarrow=False)
                        fig1.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.2), margin=dict(t=10, b=30, l=10, r=10), height=200)
                        st.plotly_chart(fig1, use_container_width=True, key="fig_anual")
                    
                    with col_g2:
                        st.markdown("**Avance ejercicio periodo**")
                        fig2 = go.Figure(go.Pie(values=[datos_ur['Ejercido_acumulado'], max(0, datos_ur['Disponible_periodo'])],
                            labels=['Ejercido', 'Disponible'], hole=0.6, marker_colors=[COLOR_NARANJA, COLOR_AZUL], textinfo='none'))
                        fig2.add_annotation(text=f"{pct_periodo:.2f}%", x=0.5, y=0.5, font_size=18, font_color=COLOR_VINO, showarrow=False)
                        fig2.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.2), margin=dict(t=10, b=30, l=10, r=10), height=200)
                        st.plotly_chart(fig2, use_container_width=True, key="fig_periodo")
                    
                    # Seccion Pasivos
                    st.markdown("#### Pasivos con cargo al presupuesto")
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        st.markdown('<div style="border:1px solid #ddd; border-radius:8px; padding:1rem; text-align:center;"><div style="font-size:0.8rem; color:#666;">Pasivos reportados a la SHCP</div><div style="font-size:1.2rem; font-weight:bold;"></div></div>', unsafe_allow_html=True)
                    with col_p2:
                        st.markdown('<div style="border:1px solid #ddd; border-radius:8px; padding:1rem; text-align:center;"><div style="font-size:0.8rem; color:#666;">Pasivos pagados en COP 10</div><div style="font-size:1.2rem; font-weight:bold;"></div></div>', unsafe_allow_html=True)
                    
                    st.markdown("**Avance de pago de pasivos**")
                    fig3 = go.Figure(go.Pie(values=[1], labels=['Sin pasivos'], hole=0.6, marker_colors=['#e0e0e0'], textinfo='none'))
                    fig3.add_annotation(text="-", x=0.5, y=0.5, font_size=16, font_color=COLOR_VINO, showarrow=False)
                    fig3.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.2), margin=dict(t=10, b=30, l=10, r=10), height=180)
                    st.plotly_chart(fig3, use_container_width=True, key="fig_pasivos")
                
                with col_der:
                    # Tabla por capitulo
                    st.markdown("#### Estado del ejercicio por capitulo de gasto")
                    
                    caps_ur = resultados.get('capitulos_por_ur', {}).get(ur_codigo, {})
                    
                    cap_data = []
                    total_orig, total_mod_a, total_mod_p, total_eje = 0, 0, 0, 0
                    
                    for cap_num, cap_name in [('2', 'Materiales y suministros'), ('3', 'Servicios generales'), ('4', 'Transferencias, asignaciones, subsidios y otras ayudas')]:
                        cap_info = caps_ur.get(cap_num, {})
                        orig = cap_info.get('Original', 0)
                        mod_a = cap_info.get('Modificado_anual', 0)
                        mod_p = cap_info.get('Modificado_periodo', 0)
                        eje = cap_info.get('Ejercido_acumulado', 0)
                        disp = mod_p - eje
                        pct = eje / mod_p * 100 if mod_p > 0 else 0
                        
                        total_orig += orig
                        total_mod_a += mod_a
                        total_mod_p += mod_p
                        total_eje += eje
                        
                        cap_data.append({'Capitulo': f'{cap_num}000', 'Denominacion': cap_name, 'Original': orig, 'Mod. Anual': mod_a, 'Mod. Periodo': mod_p, 'Ejercido': eje, 'Disponible': disp, '% Avance': pct})
                    
                    # Fila total
                    total_disp = total_mod_p - total_eje
                    total_pct = total_eje / total_mod_p * 100 if total_mod_p > 0 else 0
                    cap_data.insert(0, {'Capitulo': 'Total', 'Denominacion': '', 'Original': total_orig, 'Mod. Anual': total_mod_a, 'Mod. Periodo': total_mod_p, 'Ejercido': total_eje, 'Disponible': total_disp, '% Avance': total_pct})
                    
                    df_cap = pd.DataFrame(cap_data)
                    st.dataframe(df_cap.style.format({
                        'Original': '${:,.2f}', 'Mod. Anual': '${:,.2f}', 'Mod. Periodo': '${:,.2f}',
                        'Ejercido': '${:,.2f}', 'Disponible': '${:,.2f}', '% Avance': '{:.2f}%'
                    }), use_container_width=True, hide_index=True)
                    
                    # Top 5 partidas
                    st.markdown("#### Cinco partidas con el mayor monto de disponible")
                    
                    partidas_ur = resultados.get('partidas_por_ur', {}).get(ur_codigo, [])
                    if partidas_ur:
                        total_disp_ur = datos_ur['Disponible_periodo']
                        part_data = []
                        for p in partidas_ur[:5]:
                            pct_resp = p['Disponible'] / total_disp_ur * 100 if total_disp_ur > 0 else 0
                            part_data.append({
                                'Partida': p['Partida'], 'Denominacion': p['Denominacion'],
                                'Programa': p['Programa'], 'Denom. Programa': p['Denom_Programa'],
                                'Disponible': p['Disponible'], '% del Total': pct_resp
                            })
                        df_part = pd.DataFrame(part_data)
                        st.dataframe(df_part.style.format({'Disponible': '${:,.2f}', '% del Total': '{:.2f}%'}), use_container_width=True, hide_index=True)
                    else:
                        st.info("No hay partidas con disponible para esta UR")
            
            # ================================================================
            # TAB 3: DASHBOARD AUSTERIDAD (Pendiente)
            # ================================================================
            with tab3:
                st.markdown("### Dashboard Austeridad")
                st.info("Este dashboard requiere el archivo de Cuenta Publica 2024 para comparar el ejercido. Cuando tengas el archivo, subelo y lo incorporamos.")
                
                # Selector de UR para cuando este listo
                ur_sel_aust = st.selectbox("Selecciona una Unidad Responsable:", options=urs_con_nombre, index=0, key="ur_aust")
                
                st.markdown("""
                **Datos que mostrara este dashboard:**
                - Partidas sujetas a Austeridad Republicana
                - Ejercido en 2024 vs 2025
                - Original, Modificado, Ejercido Real
                - Notas y alertas de solicitud de dictamen
                - Avance anual por partida
                """)
            
            # ================================================================
            # TAB 4: GRAFICAS
            # ================================================================
            with tab4:
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    st.markdown("#### Distribucion por Seccion")
                    fig_pie = px.pie(df_seccion, values='Mod. Periodo', names='Seccion',
                        color_discrete_sequence=[COLOR_VINO, COLOR_BEIGE, COLOR_GRIS, COLOR_VERDE])
                    fig_pie.update_layout(showlegend=True, margin=dict(t=20, b=20, l=20, r=20))
                    st.plotly_chart(fig_pie, use_container_width=True, key="pie_sicop_graf")
                with col_g2:
                    st.markdown("#### Avance por Seccion")
                    fig_bar = go.Figure()
                    fig_bar.add_trace(go.Bar(name='Ejercido', x=df_seccion['Seccion'], y=df_seccion['Ejercido'], marker_color=COLOR_NARANJA))
                    fig_bar.add_trace(go.Bar(name='Disponible', x=df_seccion['Seccion'], y=df_seccion['Disponible'], marker_color=COLOR_AZUL))
                    fig_bar.update_layout(barmode='stack', xaxis_tickangle=-45, margin=dict(t=20, b=100, l=20, r=20))
                    st.plotly_chart(fig_bar, use_container_width=True, key="bar_sicop_graf")
        
        # ====================================================================
        # DESCARGA
        # ====================================================================
        
        st.markdown("---")
        
        if es_map:
            excel_bytes = generar_excel_map(resultados)
            fecha_str = date.today().strftime('%d%b%Y').upper()
            config_str = "Prog2026" if config['usar_2026'] else "Prog2025"
            filename_excel = f'Cuadro_Presupuesto_{config_str}_{fecha_str}.xlsx'
        else:
            excel_bytes = generar_excel_sicop(resultados)
            fecha_str = date.today().strftime('%d%b%Y').upper()
            config_str = "URs2026" if config['usar_2026'] else "URs2025"
            filename_excel = f'Estado_Ejercicio_SICOP_{config_str}_{fecha_str}.xlsx'
        
        st.download_button(
            label="Descargar Excel",
            data=excel_bytes,
            file_name=filename_excel,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"Error al procesar el archivo: {str(e)}")
        st.exception(e)

else:
    st.markdown("""
    <div class="upload-zone">
        <h3>Sube tu archivo CSV</h3>
        <p style="color: #666;">Arrastra y suelta o haz clic en el boton de arriba</p>
        <p style="color: #888; font-size: 0.9rem; margin-top: 1rem;">Formatos soportados: CSV exportado de MAP o SICOP</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div style="text-align: center; color: #888; font-size: 0.8rem;"><p>SADER - Sistema de Reportes Presupuestarios | Unidad de Administracion y Finanzas</p></div>', unsafe_allow_html=True)
