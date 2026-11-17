import requests
from datetime import datetime, timedelta

SECTORES = {
    "morrope_san_jose_tinajones": {
        "nombre_es": "Lambayeque - Mórrope y San José (Cola del Sistema Tinajones / Alta Salinidad)",
        "nombre_en": "Lambayeque - Mórrope & San José (Tinajones Tail-end / High Salinity)",
        "lat": -6.5417,
        "lon": -80.0111,
        "estado_actual_es": "Monitoreo de Estrés Hídrico & Alerta de Salinidad en Pozos",
        "estado_actual_en": "Water Stress & Groundwater Salinity Monitoring",
        "pendiente_srtm": "Plana / Árida (0.5%)",
        "sistema_hidrico_es": "Embalse de Tinajones / Valle de Chancay (Riesgo de agua salobre)",
        "sistema_hidrico_en": "Tinajones Reservoir / Chancay Valley (Brackish water risk)",
        "costo_agua_estimado": "S/ 18.00 - S/ 25.00 / hora + Riesgo de costo de desalinización"
    },
    "chancay_tinajones_medio": {
        "nombre_es": "Lambayeque - Túcume, Mochumí y Lambayeque (Valle Medio / Tinajones)",
        "nombre_en": "Lambayeque - Túcume, Mochumí & Lambayeque (Middle Valley / Tinajones)",
        "lat": -6.5108,
        "lon": -79.8583,
        "estado_actual_es": "Monitoreo de Humedad y Turnos de Riego Regulado",
        "estado_actual_en": "Soil Moisture & Regulated Irrigation Shift Monitoring",
        "pendiente_srtm": "Plana (0.7%)",
        "sistema_hidrico_es": "Sistema Hidráulico Valle Chancay y Tinajones (Regulado)",
        "sistema_hidrico_en": "Chancay Valley & Tinajones Regulated Hydraulic System",
        "costo_agua_estimado": "S/ 14.00 - S/ 18.00 / hora (Tarifa institucional por turno)"
    },
    "ferrenafe_cabecera": {
        "nombre_es": "Lambayeque - Ferreñafe (Cabecera de Cuenca / Canal Taymi)",
        "nombre_en": "Lambayeque - Ferreñafe (Basin Headwaters / Taymi Canal)",
        "lat": -6.6389,
        "lon": -79.7911,
        "estado_actual_es": "Control de Caudal y Derivación Principal (Canal Taymi)",
        "estado_actual_en": "Flow Control & Main Diversion (Taymi Canal)",
        "pendiente_srtm": "Plana (0.8%)",
        "sistema_hidrico_es": "Canal Taymi / Cabecera de distribución Tinajones",
        "sistema_hidrico_en": "Taymi Canal / Tinajones Distribution Headwaters",
        "costo_agua_estimado": "S/ 10.00 - S/ 13.00 / hora (Mayor caudal y menor costo)"
    },
    "valle_la_leche": {
        "nombre_es": "Lambayeque - Valle La Leche y Motupe (Jayanca, Pacora, Íllimo, Motupe, Olmos)",
        "nombre_en": "Lambayeque - La Leche & Motupe Valleys (Jayanca, Pacora, Íllimo, Motupe, Olmos)",
        "lat": -6.4833,
        "lon": -79.8833,
        "estado_actual_es": "Evaluación de Cuenca Independiente y Pozos Agrícolas",
        "estado_actual_en": "Independent Basin & Agricultural Wells Assessment",
        "pendiente_srtm": "Plana a Ondulada (0.9%)",
        "sistema_hidrico_es": "Cuencas Independientes (Valle La Leche / Motupe-Olmos)",
        "sistema_hidrico_en": "Independent Basins (La Leche / Motupe-Olmos Valleys)",
        "costo_agua_estimado": "Tarifa de Cuenca Independiente / Costo variable de pozos"
    },
    "moche_bajo_libertad": {
        "nombre_es": "La Libertad - Campiña de Moche (Valle Histórico)",
        "nombre_en": "La Libertad - Moche Countryside (Historic Valley)",
        "lat": -8.1519,
        "lon": -79.0094,
        "estado_actual_es": "Monitoreo de Agroexportación y Riego Tecnificado",
        "estado_actual_en": "Agro-export & Technified Irrigation Monitoring",
        "pendiente_srtm": "Plana (1.2%)",
        "sistema_hidrico_es": "Cuenca Baja Río Moche (Toma directa / Pozos tecnificados)",
        "sistema_hidrico_en": "Lower Moche River Basin (Direct intake / Technified wells)",
        "costo_agua_estimado": "Tarifa Junta de Usuarios Moche / Inversión privada"
    }
}

RESPALDO_LOCAL = {
    "morrope_san_jose_tinajones": {
        "temp_promedio": 27.4, "precipitacion_total": 1.2, "radiacion_solar": 24.5,
        "ndvi": 0.34, "humedad_suelo_smap": 0.11,
        "serie_temp": [26.8, 27.1, 27.5, 27.9, 27.4, 27.2, 27.4],
        "fechas": ["D-6", "D-5", "D-4", "D-3", "D-2", "D-1", "Today"]
    },
    "chancay_tinajones_medio": {
        "temp_promedio": 26.9, "precipitacion_total": 2.5, "radiacion_solar": 24.1,
        "ndvi": 0.41, "humedad_suelo_smap": 0.14,
        "serie_temp": [26.2, 26.6, 27.0, 27.3, 26.9, 26.8, 26.9],
        "fechas": ["D-6", "D-5", "D-4", "D-3", "D-2", "D-1", "Today"]
    },
    "ferrenafe_cabecera": {
        "temp_promedio": 26.3, "precipitacion_total": 4.2, "radiacion_solar": 23.9,
        "ndvi": 0.46, "humedad_suelo_smap": 0.16,
        "serie_temp": [25.8, 26.1, 26.5, 26.8, 26.3, 26.2, 26.3],
        "fechas": ["D-6", "D-5", "D-4", "D-3", "D-2", "D-1", "Today"]
    },
    "valle_la_leche": {
        "temp_promedio": 26.5, "precipitacion_total": 3.0, "radiacion_solar": 24.0,
        "ndvi": 0.39, "humedad_suelo_smap": 0.13,
        "serie_temp": [26.0, 26.3, 26.7, 27.0, 26.5, 26.4, 26.5],
        "fechas": ["D-6", "D-5", "D-4", "D-3", "D-2", "D-1", "Today"]
    },
    "moche_bajo_libertad": {
        "temp_promedio": 21.2, "precipitacion_total": 3.1, "radiacion_solar": 22.4,
        "ndvi": 0.48, "humedad_suelo_smap": 0.18,
        "serie_temp": [20.9, 21.0, 21.4, 21.8, 21.1, 21.0, 21.2],
        "fechas": ["D-6", "D-5", "D-4", "D-3", "D-2", "D-1", "Today"]
    }
}

def generar_recomendacion(sector_id, temp, precip, ndvi, humedad_smap):
    rec_es = []
    rec_en = []
    nivel_es, nivel_en, codigo_riesgo = "Low", "Low", "Bajo"

    if humedad_smap < 0.12:
        nivel_es, nivel_en, codigo_riesgo = "High", "High", "Alto"
        rec_es.append("Alerta Crítica de Humedad (SMAP < 0.12): Suelo extremadamente seco. El uso intensivo de pozos tubulares en esta zona de cola incrementa drásticamente la extracción de agua salobre, deteriorando la estructura del suelo y afectando la salud humana y animal.")
        rec_en.append("Critical Moisture Alert (SMAP < 0.12): Extremely dry soil. Intensive well pumping in this tail-end zone drastically increases brackish water extraction, degrading soil structure and threatening health.")
    elif humedad_smap < 0.16:
        nivel_es, nivel_en, codigo_riesgo = "Moderate", "Moderate", "Moderado"
        rec_es.append("Alerta Moderada de Estrés Hídrico: Se recomienda optimizar los turnos de riego superficiales y evitar la inundación prolongada para prevenir el ascenso capilar de sales.")
        rec_en.append("Moderate Water Stress Alert: Recommended to optimize surface irrigation shifts and avoid prolonged flooding to prevent capillary salt rise.")
    else:
        rec_es.append("Condición Hídrica Estable: Niveles de humedad superficial dentro del rango aceptable para la red de canales.")
        rec_en.append("Stable Water Condition: Topsoil moisture levels within acceptable range for the canal network.")

    if temp >= 25.0:
        rec_es.append("Alerta Térmica (NASA POWER): Alta temperatura superficial que acelera la evaporación. Programar aplicaciones o riegos preferentemente en horario nocturno.")
        rec_en.append("Thermal Alert (NASA POWER): High surface temperature accelerating evaporation. Schedule irrigation preferably during nighttime shifts.")
    
    if ndvi < 0.38:
        rec_es.append("Vigor Vegetal Bajo (Landsat NDVI < 0.38): Posible presencia de estrés salino o déficit nutricional en las parcelas evaluadas.")
        rec_en.append("Low Crop Vigor (Landsat NDVI < 0.38): Potential salt stress or nutrient deficit in evaluated plots.")

    return {
        "codigo_riesgo": codigo_riesgo,
        "nivel_es": nivel_es,
        "nivel_en": nivel_en,
        "recomendaciones_es": rec_es,
        "recomendaciones_en": rec_en
    }

def obtener_datos_sector(sector_id):
    if sector_id not in SECTORES:
        sector_id = "morrope_san_jose_tinajones"

    info_sector = SECTORES[sector_id]
    fecha_fin = datetime.now() - timedelta(days=3)
    fecha_inicio = fecha_fin - timedelta(days=7)

    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"parameters=T2M,PRECTOTCORR,ALLSKY_SFC_SW_DWN&community=AG"
        f"&longitude={info_sector['lon']}&latitude={info_sector['lat']}"
        f"&start={fecha_inicio.strftime('%Y%m%d')}&end={fecha_fin.strftime('%Y%m%d')}&format=JSON"
    )

    try:
        response = requests.get(url, timeout=6)
        response.raise_for_status()
        data = response.json()["properties"]["parameter"]

        temps = [v for v in data["T2M"].values() if v != -999]
        precips = [v for v in data["PRECTOTCORR"].values() if v != -999]
        rads = [v for v in data["ALLSKY_SFC_SW_DWN"].values() if v != -999]
        fechas = [k for k, v in data["T2M"].items() if v != -999]

        if not temps:
            raise ValueError("Empty NASA POWER data")

        temp_prom = round(sum(temps) / len(temps), 1)
        precip_tot = round(sum(precips), 1)
        rad_prom = round(sum(rads) / len(rads), 1)
        ref = RESPALDO_LOCAL[sector_id]
        fuente_es = "NASA POWER API (En vivo) + Capas SMAP/Landsat"
        fuente_en = "NASA POWER API (Live) + SMAP/Landsat Layers"

    except Exception:
        ref = RESPALDO_LOCAL[sector_id]
        temp_prom = ref["temp_promedio"]
        precip_tot = ref["precipitacion_total"]
        rad_prom = ref["radiacion_solar"]
        temps = ref["serie_temp"]
        fechas = ref["fechas"]
        fuente_es = "Dataset Calibrado Local (Respaldo NASA POWER / SMAP)"
        fuente_en = "Calibrated Local Dataset (NASA POWER / SMAP Backup)"

    analisis = generar_recomendacion(
        sector_id, temp_prom, precip_tot, ref["ndvi"], ref["humedad_suelo_smap"]
    )

    return {
        "sector_id": sector_id,
        "meta": info_sector,
        "fuente_es": fuente_es,
        "fuente_en": fuente_en,
        "metricas": {
            "temperatura_c": temp_prom,
            "precipitacion_mm": precip_tot,
            "radiacion_mj": rad_prom,
            "ndvi": ref["ndvi"],
            "humedad_smap": ref["humedad_suelo_smap"]
        },
        "series": {
            "fechas": fechas,
            "temperaturas": temps
        },
        "analisis_agronomico": analisis
    }