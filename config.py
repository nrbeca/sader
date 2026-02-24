# ============================================================================
# CONFIGURACIÓN GLOBAL PARA SADER REPORTES
# ============================================================================

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta, MO
from decimal import Decimal, ROUND_HALF_UP
try:
    from num2words import num2words
except ImportError:
    def num2words(n, lang='es'):
        return str(n)

# ============================================================================
# LOGO BASE64
# ============================================================================

LOGO_BASE64 = """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"""

# ============================================================================
# MESES Y MAPEOS
# ============================================================================

MONTH_NAMES = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']
MONTH_NAMES_FULL = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

MONTH_MAP = {name: idx + 1 for idx, name in enumerate(MONTH_NAMES)}

# ============================================================================
# MAPEO DE URs (compartido entre MAP y SICOP)
# ============================================================================

UR_MAP = {
    121: 260, 122: 261, 123: 262, 124: 263, 125: 264, 126: 265, 127: 266, 128: 267,
    129: 268, 130: 269, 131: 270, 132: 271, 133: 272, 134: 273, 135: 274, 136: 275,
    137: 276, 138: 277, 139: 278, 140: 279, 141: 280, 142: 281, 143: 282, 144: 283,
    145: 284, 146: 285, 147: 286, 148: 287, 149: 288, 150: 289, 151: 290, 152: 291,
    153: 292, 108: 810, 215: 220, 300: 225, 310: 226, 700: 227, 600: 230, 612: 231,
    312: 232, 315: 233, 400: 235, 311: 237, 314: 245, 113: 250
}

# ============================================================================
# CONFIGURACIÓN MAP - PROGRAMAS 2025
# ============================================================================

PROGRAMAS_NOMBRES_2025 = {
    'B004': 'Adquisición de leche nacional',
    'S052': 'Programa de Abasto Social de Leche a cargo de Liconsa, S.A. de C.V.',
    'S053': 'Programa de Abasto Rural a cargo de Diconsa, S.A. de C.V.',
    'S263': 'Sanidad e Inocuidad Agroalimentaria',
    'S290': 'Precios de Garantía a Productos Alimentarios Básicos',
    'S292': 'Fertilizantes',
    'S293': 'Producción para el Bienestar',
    'S304': 'Programa de Fomento a la Agricultura, Ganadería, Pesca y Acuicultura',
    'P001': 'Diseño y Aplicación de la Política Agropecuaria',
    'E001': 'Desarrollo, aplicación de programas educativos e investigación en materia agroalimentaria',
    'E006': 'Generación de Proyectos de Investigación',
    'G001': 'Regulación, supervisión y aplicación de las políticas públicas en materia agropecuaria',
    'O001': 'Actividades de apoyo a la función pública y buen gobierno',
    'M001': 'Actividades de apoyo administrativo',
    'U027': 'Cosechando Soberanía',
    'W001': 'Operaciones ajenas',
}

PROGRAMAS_ESPECIFICOS_2025 = ['B004', 'S052', 'S053', 'S263', 'S290', 'S292', 'S293', 'S304']

NOMBRES_ESPECIALES_2025 = {
    'S263': 'Sanidad e Inocuidad Agroalimentaria 3/',
    'S293': 'Producción para el Bienestar 4/',
    'S304': 'Programa de Fomento a la Agricultura, Ganadería, Pesca y Acuicultura 5/',
}

FUSION_PROGRAMAS_2025 = {}

# ============================================================================
# CONFIGURACIÓN MAP - PROGRAMAS 2026
# ============================================================================

PROGRAMAS_NOMBRES_2026 = {
    'S052': 'Programa de Abasto Social y Precios de Garantía a cargo de Leche para el Bienestar, S.A. de C.V.',
    'S053': 'Programa de Abasto Rural',
    'S263': 'Sanidad e Inocuidad Agroalimentaria',
    'S290': 'Acopio para el Bienestar',
    'S292': 'Fertilizantes para el Bienestar',
    'S293': 'Producción para el Bienestar',
    'S304': 'Pesca y Acuacultura Sustentables',
    'B006': 'Adquisición, industrialización y comercialización de productos agroalimentarios',
    'B004': 'Adquisición de leche nacional',
    'P001': 'Diseño y Aplicación de la Política Agropecuaria',
    'E001': 'Desarrollo, aplicación de programas educativos e investigación en materia agroalimentaria',
    'E006': 'Generación de Proyectos de Investigación',
    'G001': 'Regulación, supervisión y aplicación de las políticas públicas',
    'M001': 'Actividades de apoyo administrativo',
    'O001': 'Actividades de apoyo a la función pública y buen gobierno',
    'W001': 'Operaciones ajenas',
}

PROGRAMAS_ESPECIFICOS_2026 = ['S052', 'S053', 'S263', 'S290', 'S292', 'S293', 'S304', 'B006']

NOMBRES_ESPECIALES_2026 = {
    'S263': 'Sanidad e Inocuidad Agroalimentaria 3/',
    'S293': 'Producción para el Bienestar 4/',
    'S304': 'Pesca y Acuacultura Sustentables 5/',
}

FUSION_PROGRAMAS_2026 = {
    'B004': 'B006',
}

# ============================================================================
# CONFIGURACIÓN SICOP - DENOMINACIONES URs 2025
# ============================================================================

DENOMINACIONES_2025 = {
    '100': 'Secretaría',
    '109': 'Dirección General de Normalización Agroalimentaria',
    '110': 'Unidad de Asuntos Jurídicos, Derechos Humanos y Normalización',
    '111': 'Dirección General de Comunicación Social',
    '112': 'Dirección General de Enlace Legislativo',
    '117': 'Coordinación General de Asuntos Internacionales',
    '200': 'Subsecretaría de Agricultura y Desarrollo Rural',
    '212': 'Dirección General de Organización para la Productividad',
    '214': 'Dirección General de la Autosuficiencia Alimentaria',
    '220': 'Coordinación General de Bienestar para el Campo',
    '221': 'Dirección General de Fertilizantes para el Bienestar',
    '222': 'Dirección General de Producción para el Bienestar',
    '225': 'Coordinación General de Producción Agrícola y Ganadera',
    '226': 'Dirección General de Producción Agrícola',
    '227': 'Dirección General de Producción Ganadera',
    '228': 'Dirección General de Implementación de Acuerdos Sectoriales',
    '230': 'Coordinación General de Comercialización y Financiamiento',
    '231': 'Dirección General de Precios y Ordenamiento Comercial',
    '232': 'Dirección General de Financiamiento y Gestión de Riesgos',
    '233': 'Dirección General de Agregación de Valor y Comercialización',
    '235': 'Coordinación General de Eficiencia Hídrica Agroalimentaria',
    '236': 'Dirección General de Eficiencia Hídrica en el Riego',
    '237': 'Dirección General de Eficiencia Hídrica en el Temporal',
    '240': 'Coordinación General de Innovación y Transición Agroecológica',
    '241': 'Dirección General de Innovación',
    '242': 'Dirección General de Transición Agroecológica',
    '245': 'Coordinación General de Sustentabilidad y Resiliencia Climática',
    '246': 'Dirección General de Sustentabilidad',
    '247': 'Dirección General de Financiamiento Verde',
    '250': 'Coordinación General de Operación Territorial',
    '251': 'Dirección General de Integración Territorial de Programas',
    '252': 'Dirección General de Intervención Territorial Estratégica',
    '260': 'Oficina de Representación en Aguascalientes',
    '261': 'Oficina de Representación en Baja California',
    '262': 'Oficina de Representación en Baja California Sur',
    '263': 'Oficina de Representación en Campeche',
    '264': 'Oficina de Representación en Coahuila',
    '265': 'Oficina de Representación en Colima',
    '266': 'Oficina de Representación en Chiapas',
    '267': 'Oficina de Representación en Chihuahua',
    '268': 'Oficina de Representación en la Ciudad de México',
    '269': 'Oficina de Representación en Durango',
    '270': 'Oficina de Representación en Guanajuato',
    '271': 'Oficina de Representación en Guerrero',
    '272': 'Oficina de Representación en Hidalgo',
    '273': 'Oficina de Representación en Jalisco',
    '274': 'Oficina de Representación en el Estado de México',
    '275': 'Oficina de Representación en Michoacán',
    '276': 'Oficina de Representación en Morelos',
    '277': 'Oficina de Representación en Nayarit',
    '278': 'Oficina de Representación en Nuevo León',
    '279': 'Oficina de Representación en Oaxaca',
    '280': 'Oficina de Representación en Puebla',
    '281': 'Oficina de Representación en Querétaro',
    '282': 'Oficina de Representación en Quintana Roo',
    '283': 'Oficina de Representación en San Luis Potosí',
    '284': 'Oficina de Representación en Sinaloa',
    '285': 'Oficina de Representación en Sonora',
    '286': 'Oficina de Representación en Tabasco',
    '287': 'Oficina de Representación en Tamaulipas',
    '288': 'Oficina de Representación en Tlaxcala',
    '289': 'Oficina de Representación en Veracruz',
    '290': 'Oficina de Representación en Yucatán',
    '291': 'Oficina de Representación en Zacatecas',
    '292': 'Oficina de Representación en la Región Lagunera',
    '410': 'Dirección General de Fortalecimiento a la Agricultura Familiar',
    '411': 'Dirección General de Integración Económica',
    '413': 'Dirección General de Investigación, Desarrollo Tecnológico y Extensionismo',
    '500': 'Unidad de Administración y Finanzas',
    '510': 'Dirección General de Programación, Presupuesto y Finanzas',
    '511': 'Dirección General de Capital Humano y Desarrollo Organizacional',
    '512': 'Dirección General de Recursos Materiales, Inmuebles y Servicios',
    '513': 'Dirección General de Tecnologías de la Información y Comunicaciones',
    '610': 'Dirección General de Comercialización',
    '611': 'Dirección General de Administración de Riesgos de Precios',
    '710': 'Dirección General de Repoblamiento Ganadero',
    '711': 'Dirección General de Sustentabilidad de Tierras de Uso Ganadero',
    '800': 'Coordinación General de Información, Inteligencia y Evaluación',
    '810': 'Dirección General de Evaluación, Políticas y Programas',
    '811': 'Dirección General del Servicio de Información Agroalimentaria y Pesquera',
    '812': 'Dirección General de Planeación',
    'B00': 'Servicio Nacional de Sanidad, Inocuidad y Calidad Agroalimentaria',
    'C00': 'Servicio Nacional de Inspección y Certificación de Semillas',
    'D00': 'Colegio Superior Agropecuario del Estado de Guerrero',
    'I00': 'Comisión Nacional de Acuacultura y Pesca',
    'A1I': 'Universidad Autónoma Chapingo',
    'AFU': 'Comité Nacional para el Desarrollo Sustentable de la Caña de Azúcar',
    'I6L': 'Fideicomiso de Riesgo Compartido',
    'I9H': 'Instituto Nacional para el Desarrollo de Capacidades del Sector Rural, A.C.',
    'IZC': 'Colegio de Postgraduados',
    'IZI': 'Comisión Nacional de las Zonas Áridas',
    'JAG': 'Instituto Nacional de Investigaciones Forestales, Agrícolas y Pecuarias',
    'JBP': 'Seguridad Alimentaria Mexicana',
    'RJL': 'Instituto Mexicano de Investigación en Pesca y Acuacultura Sustentables',
    'VSS': 'Alimentación para el Bienestar, S.A de C.V.',
    'VST': 'Leche para el Bienestar, S.A. de C.V.',
}

SECTOR_CENTRAL_2025 = ['100', '109', '110', '111', '112', '117', '200', '212', '214',
                       '220', '221', '222', '225', '226', '227', '228', '230', '231', '232', '233',
                       '235', '236', '237', '240', '241', '242', '245', '246', '247', '250', '251', '252',
                       '410', '411', '413', '500', '510', '511', '512', '513',
                       '610', '611', '710', '711', '800', '810', '811', '812']

OFICINAS_2025 = ['260', '261', '262', '263', '264', '265', '266', '267', '268', '269',
                 '270', '271', '272', '273', '274', '275', '276', '277', '278', '279',
                 '280', '281', '282', '283', '284', '285', '286', '287', '288', '289',
                 '290', '291', '292']

ORGANOS_DESCONCENTRADOS_2025 = ['B00', 'C00', 'D00', 'I00']

ENTIDADES_PARAESTATALES_2025 = ['A1I', 'AFU', 'I6L', 'I9H', 'IZC', 'IZI', 'JAG', 'JBP', 'RJL', 'VSS', 'VST']

MAPEO_UR_2025 = {
    'G00': '811', 108: '810', 113: '250',
    121: '260', 122: '261', 123: '262', 124: '263', 125: '264', 126: '265', 127: '266', 128: '267', 129: '268', 130: '269',
    131: '270', 132: '271', 133: '272', 134: '273', 135: '274', 136: '275', 137: '276', 138: '277', 139: '278', 140: '279',
    141: '280', 142: '281', 143: '282', 144: '283', 145: '284', 146: '285', 147: '286', 148: '287', 149: '288', 150: '289',
    151: '290', 152: '291', 153: '292',
    215: '220', 300: '225', 310: '226', 700: '227', 600: '230', 612: '231', 312: '232', 315: '233', 400: '235', 311: '237', 314: '245',
}

# ============================================================================
# CONFIGURACIÓN SICOP - DENOMINACIONES URs 2026
# ============================================================================

DENOMINACIONES_2026 = {
    '100': 'Secretaría',
    '110': 'Unidad de Asuntos Jurídicos',
    '106': 'Coordinación de Legislación y Consulta',
    '107': 'Coordinación de lo Contencioso',
    '111': 'Dirección General de Comunicación Social',
    '112': 'Coordinación de Atención Legislativa',
    '117': 'Coordinación de Asuntos Internacionales',
    '119': 'Dirección General de Planeación y Evaluación de Políticas y Programas',
    '120': 'Dirección General del Servicio de Información Agroalimentaria y Pesquera',
    '200': 'Subsecretaría de Agricultura y Desarrollo Rural',
    '220': 'Unidad de Bienestar para el Campo',
    '221': 'Dirección General de Fertilizantes para el Bienestar',
    '222': 'Dirección General de Producción para el Bienestar',
    '250': 'Unidad de Operación Territorial y Eficiencia Hídrica Agroalimentaria',
    '252': 'Dirección General de Intervención Territorial Estratégica',
    '253': 'Dirección General de Eficacia Hídrica en Riego y Temporal',
    '260': 'Oficina de Representación en Aguascalientes',
    '261': 'Oficina de Representación en Baja California',
    '262': 'Oficina de Representación en Baja California Sur',
    '263': 'Oficina de Representación en Campeche',
    '264': 'Oficina de Representación en Coahuila',
    '265': 'Oficina de Representación en Colima',
    '266': 'Oficina de Representación en Chiapas',
    '267': 'Oficina de Representación en Chihuahua',
    '268': 'Oficina de Representación en la Ciudad de México',
    '269': 'Oficina de Representación en Durango',
    '270': 'Oficina de Representación en Guanajuato',
    '271': 'Oficina de Representación en Guerrero',
    '272': 'Oficina de Representación en Hidalgo',
    '273': 'Oficina de Representación en Jalisco',
    '274': 'Oficina de Representación en el Estado de México',
    '275': 'Oficina de Representación en Michoacán',
    '276': 'Oficina de Representación en Morelos',
    '277': 'Oficina de Representación en Nayarit',
    '278': 'Oficina de Representación en Nuevo León',
    '279': 'Oficina de Representación en Oaxaca',
    '280': 'Oficina de Representación en Puebla',
    '281': 'Oficina de Representación en Querétaro',
    '282': 'Oficina de Representación en Quintana Roo',
    '283': 'Oficina de Representación en San Luis Potosí',
    '284': 'Oficina de Representación en Sinaloa',
    '285': 'Oficina de Representación en Sonora',
    '286': 'Oficina de Representación en Tabasco',
    '287': 'Oficina de Representación en Tamaulipas',
    '288': 'Oficina de Representación en Tlaxcala',
    '289': 'Oficina de Representación en Veracruz',
    '290': 'Oficina de Representación en Yucatán',
    '291': 'Oficina de Representación en Zacatecas',
    '292': 'Oficina de Representación en la Región Lagunera',
    '500': 'Unidad de Administración y Finanzas',
    '510': 'Dirección General de Programación, Presupuesto y Finanzas',
    '511': 'Dirección General de Capital Humano y Desarrollo Organizacional',
    '512': 'Dirección General de Recursos Materiales, Inmuebles y Servicios',
    '513': 'Dirección General de Tecnologías de la Información y Comunicaciones',
    '900': 'Coordinación General de Producción, Comercialización, Sustentabilidad e Innovación',
    '910': 'Unidad de Innovación, Sustentabilidad y Resiliencia Climática',
    '911': 'Dirección General de Desarrollo e Innovación',
    '912': 'Dirección General de Sustentabilidad y Resiliencia Climática',
    '920': 'Unidad de Producción, Comercialización y Financiamiento',
    '921': 'Dirección General de Producción Agrícola',
    '922': 'Dirección General de Producción Ganadera, Pesquera y Acuícola',
    '923': 'Dirección General de Precios, Ordenamiento Comercial y Valor Agregado',
    '924': 'Dirección General de Financiamiento y Gestión de Riesgos',
    'B00': 'Servicio Nacional de Sanidad, Inocuidad y Calidad Agroalimentaria',
    'C00': 'Servicio Nacional de Inspección y Certificación de Semillas',
    'D00': 'Colegio Superior Agropecuario del Estado de Guerrero',
    'I00': 'Comisión Nacional de Acuacultura y Pesca',
    'A1I': 'Universidad Autónoma Chapingo',
    'AFU': 'Comité Nacional para el Desarrollo Sustentable de la Caña de Azúcar',
    'I6L': 'Fideicomiso de Riesgo Compartido',
    'I9H': 'Instituto Nacional para el Desarrollo de Capacidades del Sector Rural, A.C.',
    'IZC': 'Colegio de Postgraduados',
    'IZI': 'Comisión Nacional de las Zonas Áridas',
    'JAG': 'Instituto Nacional de Investigaciones Forestales, Agrícolas y Pecuarias',
    'JAL': 'Productora de Semillas para el Bienestar',
    'JBK': 'Productora Nacional de Biológicos Veterinarios',
    'RJL': 'Instituto Mexicano de Investigación en Pesca y Acuacultura Sustentables',
    'VSS': 'Alimentación para el Bienestar, S.A de C.V.',
    'VST': 'Leche para el Bienestar, S.A. de C.V.',
}

SECTOR_CENTRAL_2026 = ['100', '110', '106', '107', '111', '112', '117', '119', '120', '200',
                       '220', '221', '222', '250', '252', '253',
                       '500', '510', '511', '512', '513',
                       '900', '910', '911', '912', '920', '921', '922', '923', '924']

OFICINAS_2026 = ['260', '261', '262', '263', '264', '265', '266', '267', '268', '269',
                 '270', '271', '272', '273', '274', '275', '276', '277', '278', '279',
                 '280', '281', '282', '283', '284', '285', '286', '287', '288', '289',
                 '290', '291', '292']

ORGANOS_DESCONCENTRADOS_2026 = ['B00', 'C00', 'D00', 'I00']

ENTIDADES_PARAESTATALES_2026 = ['A1I', 'AFU', 'I6L', 'I9H', 'IZC', 'IZI', 'JAG', 'JAL', 'JBK', 'RJL', 'VSS', 'VST']

MAPEO_UR_2026_BASE = {
    'G00': '811', 108: '810', 113: '250',
    121: '260', 122: '261', 123: '262', 124: '263', 125: '264', 126: '265', 127: '266', 128: '267', 129: '268', 130: '269',
    131: '270', 132: '271', 133: '272', 134: '273', 135: '274', 136: '275', 137: '276', 138: '277', 139: '278', 140: '279',
    141: '280', 142: '281', 143: '282', 144: '283', 145: '284', 146: '285', 147: '286', 148: '287', 149: '288', 150: '289',
    151: '290', 152: '291', 153: '292',
    215: '220', 300: '225', 310: '226', 700: '227', 600: '230', 612: '231', 312: '232', 315: '233', 400: '235', 311: '237', 314: '245',
}

FUSION_URS_2026 = {
    '810': '119', '812': '119',
    '800': '120', '811': '120',
    '235': '250',
    '236': '253', '237': '253',
    '225': '900',
    '245': '910',
    '241': '911',
    '246': '912', '247': '912',
    '230': '920',
    '226': '921',
    '227': '922',
    '231': '923',
    '232': '924',
}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def round_like_excel(value, decimals=2):
    """Redondea como Excel (ROUND_HALF_UP)"""
    import pandas as pd
    if pd.isna(value):
        return 0
    d = Decimal(str(value))
    return float(d.quantize(Decimal(10) ** -decimals, rounding=ROUND_HALF_UP))


def numero_a_letras_mx(numero):
    """Convierte número a texto en español mexicano"""
    entero = int(numero)
    centavos = int(round((numero - entero) * 100))
    if entero == 0:
        texto_entero = "Cero"
    else:
        texto_entero = num2words(entero, lang='es').title()
        texto_entero = texto_entero.replace('Mil Millones', 'Mil millones')
        texto_entero = texto_entero.replace('Millones', 'millones')
        texto_entero = texto_entero.replace('Millón', 'millón')
        texto_entero = texto_entero.replace('Mil ', 'mil ')
    return f"{texto_entero} pesos {centavos:02d}/100 M.N."


def formatear_fecha(fecha):
    """Formatea fecha en español"""
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return f"{fecha.day} de {meses[fecha.month - 1]} de {fecha.year}"


def obtener_ultimo_dia_habil(fecha_referencia=None):
    """Obtiene el último día hábil antes de la fecha de referencia"""
    if fecha_referencia is None:
        fecha_referencia = date.today()
    año_actual = fecha_referencia.year
    festivos = [
        date(año_actual, 1, 1), date(año_actual, 5, 1), date(año_actual, 5, 5),
        date(año_actual, 9, 16), date(año_actual, 12, 25),
        date(año_actual, 2, 1) + relativedelta(weekday=MO(1)),
        date(año_actual, 3, 1) + relativedelta(weekday=MO(3)),
        date(año_actual, 11, 1) + relativedelta(weekday=MO(3))
    ]
    dia_analizado = fecha_referencia - timedelta(days=1)
    while True:
        if dia_analizado.weekday() < 5 and dia_analizado not in festivos:
            break
        dia_analizado -= timedelta(days=1)
    return dia_analizado


def detectar_fecha_archivo(filename):
    """Detecta la fecha del nombre del archivo"""
    import re
    month_match = re.search(
        r'(\d{2})[-_]?(ENE|FEB|MAR|ABR|MAY|JUN|JUL|AGO|SEP|OCT|NOV|DIC)[-_]?(\d{4})?',
        filename, re.IGNORECASE
    )
    if month_match:
        dia = int(month_match.group(1))
        mes_nombre = month_match.group(2).upper()
        año = int(month_match.group(3)) if month_match.group(3) else date.today().year
        mes = MONTH_MAP[mes_nombre]
        return date(año, mes, dia), mes, año
    return date.today(), date.today().month, date.today().year


def get_config_by_year(año):
    """Obtiene la configuración según el año"""
    if año <= 2025:
        return {
            'programas_nombres': PROGRAMAS_NOMBRES_2025,
            'programas_especificos': PROGRAMAS_ESPECIFICOS_2025,
            'nombres_especiales': NOMBRES_ESPECIALES_2025,
            'fusion_programas': FUSION_PROGRAMAS_2025,
            'denominaciones': DENOMINACIONES_2025,
            'sector_central': SECTOR_CENTRAL_2025,
            'oficinas': OFICINAS_2025,
            'organos_desconcentrados': ORGANOS_DESCONCENTRADOS_2025,
            'entidades_paraestatales': ENTIDADES_PARAESTATALES_2025,
            'mapeo_ur': MAPEO_UR_2025,
            'fusion_urs': {},
            'usar_2026': False,
        }
    else:
        return {
            'programas_nombres': PROGRAMAS_NOMBRES_2026,
            'programas_especificos': PROGRAMAS_ESPECIFICOS_2026,
            'nombres_especiales': NOMBRES_ESPECIALES_2026,
            'fusion_programas': FUSION_PROGRAMAS_2026,
            'denominaciones': DENOMINACIONES_2026,
            'sector_central': SECTOR_CENTRAL_2026,
            'oficinas': OFICINAS_2026,
            'organos_desconcentrados': ORGANOS_DESCONCENTRADOS_2026,
            'entidades_paraestatales': ENTIDADES_PARAESTATALES_2026,
            'mapeo_ur': MAPEO_UR_2026_BASE,
            'fusion_urs': FUSION_URS_2026,
            'usar_2026': True,
        }
