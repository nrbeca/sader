# ============================================================================
# PROCESADOR DE ARCHIVOS MAP
# ============================================================================

import pandas as pd
import numpy as np
from datetime import date
from config import (
    MONTH_NAMES, UR_MAP, round_like_excel, detectar_fecha_archivo,
    get_config_by_year, numero_a_letras_mx
)


def sum_columns(df, prefix, months_to_use):
    """Suma las columnas de un prefijo para los meses especificados"""
    cols = [f'{prefix}_{month}' for month in months_to_use if f'{prefix}_{month}' in df.columns]
    if not cols:
        return pd.Series([0] * len(df))
    result = df[cols].fillna(0).sum(axis=1)
    return result.apply(lambda x: round_like_excel(x, 2))


def procesar_map(df, filename):
    """
    Procesa el archivo MAP y devuelve los resultados calculados.
    
    Returns:
        dict con:
        - 'resumen': DataFrame con totales por concepto
        - 'programas': dict con datos por programa
        - 'congelados': dict con congelados por programa
        - 'totales': dict con totales generales
        - 'metadata': información del archivo
    """
    # Detectar fecha y configuración
    fecha_archivo, mes_archivo, año_archivo = detectar_fecha_archivo(filename)
    config = get_config_by_year(año_archivo)
    
    current_month_index = mes_archivo - 1
    months_up_to_current = MONTH_NAMES[0:current_month_index + 1]
    
    año_actual = date.today().year
    es_cierre_año_anterior = (mes_archivo in [1, 2]) and (año_archivo < año_actual)
    
    # Mapear URs
    df['NuevaUR'] = df['UNIDAD'].apply(
        lambda x: 811 if x == 'G00' else UR_MAP.get(int(x) if str(x).isdigit() else 0, int(x) if str(x).isdigit() else 0)
    )
    
    # Calcular Programa Presupuestario
    df['Pp_Original'] = df['IDEN_PROY'].astype(str) + df['PROYECTO'].astype(str).str.zfill(3)
    
    # Aplicar fusión de programas
    fusion = config['fusion_programas']
    df['Pp'] = df['Pp_Original'].apply(lambda pp: fusion.get(pp, pp))
    
    # Calcular Capítulo y Partida
    df['PARTIDA'] = pd.to_numeric(df['PARTIDA'], errors='coerce').fillna(0).astype(int)
    df['Capitulo'] = (df['PARTIDA'] // 10000) * 1000
    
    # Redondear valores base
    for prefix in ['ORI', 'AMP', 'RED', 'MOD', 'CONG', 'DESCONG', 'EJE']:
        for month in MONTH_NAMES:
            col = f'{prefix}_{month}'
            if col in df.columns:
                df[col] = df[col].fillna(0).apply(lambda x: round_like_excel(x, 2))
    
    # Calcular totales
    df['Original'] = sum_columns(df, 'ORI', MONTH_NAMES)
    df['OriginalPeriodo'] = sum_columns(df, 'ORI', months_up_to_current)
    
    # Modificado
    df['ModificadoAnualBruto'] = sum_columns(df, 'MOD', MONTH_NAMES)
    
    if es_cierre_año_anterior:
        df['ModificadoPeriodoBruto'] = sum_columns(df, 'MOD', MONTH_NAMES)
    else:
        df['ModificadoPeriodoBruto'] = sum_columns(df, 'MOD', months_up_to_current)
    
    # Congelados
    cong_anual = sum_columns(df, 'CONG', MONTH_NAMES)
    descong_anual = sum_columns(df, 'DESCONG', MONTH_NAMES)
    
    if es_cierre_año_anterior:
        cong_periodo = sum_columns(df, 'CONG', MONTH_NAMES)
        descong_periodo = sum_columns(df, 'DESCONG', MONTH_NAMES)
    else:
        cong_periodo = sum_columns(df, 'CONG', months_up_to_current)
        descong_periodo = sum_columns(df, 'DESCONG', months_up_to_current)
    
    df['CongeladoAnual'] = (cong_anual - descong_anual).apply(lambda x: round_like_excel(x, 2))
    df['CongeladoPeriodo'] = (cong_periodo - descong_periodo).apply(lambda x: round_like_excel(x, 2))
    
    # Modificado Neto
    mod_anual_sum = sum_columns(df, 'MOD', MONTH_NAMES)
    df['ModificadoAnualNeto'] = (mod_anual_sum - df['CongeladoAnual']).apply(lambda x: round_like_excel(x, 2))
    
    if es_cierre_año_anterior:
        df['ModificadoPeriodoNeto'] = df['ModificadoAnualNeto'].copy()
    else:
        mod_periodo_sum = sum_columns(df, 'MOD', months_up_to_current)
        df['ModificadoPeriodoNeto'] = (mod_periodo_sum - df['CongeladoPeriodo']).apply(lambda x: round_like_excel(x, 2))
    
    # Ejercido
    df['Ejercido'] = sum_columns(df, 'EJE', MONTH_NAMES)
    
    # Disponibles
    df['DisponibleAnualNeto'] = (df['ModificadoAnualNeto'] - df['Ejercido']).apply(lambda x: round_like_excel(x, 2))
    df['DisponiblePeriodoNeto'] = (df['ModificadoPeriodoNeto'] - df['Ejercido']).apply(lambda x: round_like_excel(x, 2))
    
    # Crear pivots
    programas_especificos = config['programas_especificos']
    
    def crear_pivot_suma(filtro_func):
        filtered = df[filtro_func(df)]
        if len(filtered) == 0:
            return {'Original': 0, 'ModificadoAnualNeto': 0, 'ModificadoPeriodoNeto': 0, 'Ejercido': 0}
        return {
            'Original': round(filtered['Original'].sum(), 2),
            'ModificadoAnualNeto': round(filtered['ModificadoAnualNeto'].sum(), 2),
            'ModificadoPeriodoNeto': round(filtered['ModificadoPeriodoNeto'].sum(), 2),
            'Ejercido': round(filtered['Ejercido'].sum(), 2)
        }
    
    # Pivots por categoría
    pivot_cap1000 = crear_pivot_suma(lambda d: (d['Capitulo'] == 1000) & (~d['Pp'].isin(programas_especificos)))
    pivot_cap2000_3000 = crear_pivot_suma(lambda d: (d['Capitulo'].isin([2000, 3000])) & (~d['Pp'].isin(programas_especificos)))
    pivot_cap4000 = crear_pivot_suma(lambda d: (d['Capitulo'] == 4000) & (~d['Pp'].isin(programas_especificos)))
    pivot_cap5000_7000 = crear_pivot_suma(lambda d: (d['Capitulo'].isin([5000, 7000])) & (~d['Pp'].isin(programas_especificos)))
    
    # Pivots por programa
    pivot_programas = {}
    for prog in programas_especificos:
        pivot_programas[prog] = crear_pivot_suma(lambda d, p=prog: d['Pp'] == p)
    
    # Congelados por programa (para notas)
    programas_con_congelados = ['S263', 'S293', 'S304']
    congelados_programas = {}
    textos_congelados = {}
    for prog in programas_con_congelados:
        df_prog = df[df['Pp'] == prog]
        congelados_programas[prog] = round_like_excel(df_prog['CongeladoAnual'].sum(), 2) if len(df_prog) > 0 else 0
        textos_congelados[prog] = numero_a_letras_mx(congelados_programas[prog])
    
    # Subtotal subsidios
    subtotal_subsidios = {
        'Original': sum(pivot_programas[p]['Original'] for p in programas_especificos),
        'ModificadoAnualNeto': sum(pivot_programas[p]['ModificadoAnualNeto'] for p in programas_especificos),
        'ModificadoPeriodoNeto': sum(pivot_programas[p]['ModificadoPeriodoNeto'] for p in programas_especificos),
        'Ejercido': sum(pivot_programas[p]['Ejercido'] for p in programas_especificos),
    }
    
    # Totales
    total_datos = {
        'Original': (pivot_cap1000['Original'] + pivot_cap2000_3000['Original'] +
                     subtotal_subsidios['Original'] +
                     pivot_cap4000['Original'] + pivot_cap5000_7000['Original']),
        'ModificadoAnualNeto': (pivot_cap1000['ModificadoAnualNeto'] + pivot_cap2000_3000['ModificadoAnualNeto'] +
                                subtotal_subsidios['ModificadoAnualNeto'] +
                                pivot_cap4000['ModificadoAnualNeto'] + pivot_cap5000_7000['ModificadoAnualNeto']),
        'ModificadoPeriodoNeto': (pivot_cap1000['ModificadoPeriodoNeto'] + pivot_cap2000_3000['ModificadoPeriodoNeto'] +
                                  subtotal_subsidios['ModificadoPeriodoNeto'] +
                                  pivot_cap4000['ModificadoPeriodoNeto'] + pivot_cap5000_7000['ModificadoPeriodoNeto']),
        'Ejercido': (pivot_cap1000['Ejercido'] + pivot_cap2000_3000['Ejercido'] +
                     subtotal_subsidios['Ejercido'] +
                     pivot_cap4000['Ejercido'] + pivot_cap5000_7000['Ejercido']),
    }
    
    return {
        'categorias': {
            'servicios_personales': pivot_cap1000,
            'gasto_corriente': pivot_cap2000_3000,
            'subsidios': subtotal_subsidios,
            'otros_programas': pivot_cap4000,
            'bienes_muebles': pivot_cap5000_7000,
        },
        'programas': pivot_programas,
        'congelados': {
            'valores': congelados_programas,
            'textos': textos_congelados,
        },
        'totales': total_datos,
        'metadata': {
            'fecha_archivo': fecha_archivo,
            'mes': mes_archivo,
            'año': año_archivo,
            'registros': len(df),
            'es_cierre': es_cierre_año_anterior,
            'config': config,
        },
        'df_procesado': df,
    }
