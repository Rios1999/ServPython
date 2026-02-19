from fastapi import APIRouter, Query
from app.database import supabase

router = APIRouter(prefix="/analisis", tags=["Progreso"])

@router.get("/ver_records")
def obtener_records(user_id: str):
    # 1. Traemos todo el histórico del usuario
    response = supabase.table("Rendimiento") \
        .select('Ejercicio, "Peso (kg)", Repeticiones, RPE, Fecha, RM, Musculo') \
        .eq("user_id", user_id) \
        .execute()

    # 2. Estructura: { "Sentadilla": { 10: registro, 9: registro }, "Banca": {...} }
    records_map = {}

    for reg in response.data:
        ejercicio = reg["Ejercicio"]
        rpe = reg["RPE"]
        rm_actual = reg["RM"]

        if ejercicio not in records_map:
            records_map[ejercicio] = {}

        # Si para ese ejercicio y ese RPE específico no hay registro, 
        # o el RM actual es mejor que el que teníamos guardado:
        if rpe not in records_map[ejercicio] or rm_actual > records_map[ejercicio][rpe]["RM"]:
            records_map[ejercicio][rpe] = reg

    # 3. Formateamos para que el Frontend lo lea fácil
    resultado_final = []
    for nombre_ejercicio, rpes in records_map.items():
        resultado_final.append({
            "ejercicio": nombre_ejercicio,
            "records_por_rpe": sorted(
                [datos for rpe, datos in rpes.items()],
                key=lambda x: x["RPE"], 
                reverse=True
            )
        })

    return {
        "status": "success",
        "data": resultado_final
    }

@router.get("/ultimo_peso_corporal")
def obtener_ultimo_peso_corporal(user_id: str):
    response = supabase.table("Rendimiento") \
        .select("Peso_Corporal, Fecha") \
        .eq("user_id", user_id) \
        .neq("Peso_Corporal", 0) \
        .order("Fecha", desc=True) \
        .limit(1) \
        .execute()

    if not response.data:
        return {
            "status": "success",
            "peso_corporal": None,
            "mensaje": "No hay registros de peso corporal"
        }

    # Extraemos el valor del primer (y único) registro
    ultimo_registro = response.data[0]
    
    return {
        "status": "success",
        "peso_corporal": ultimo_registro["Peso_Corporal"],
        "fecha": ultimo_registro["Fecha"]
    }
        
@router.get("/historial_ejercicio")
def historial_ejercicio_rpe(user_id: str, ejercicio: str, rpe_target: float,page: int = 1):
    start = (page - 1) * 20
    end = start + 20 - 1

    # 1. Consultamos con filtros y rango de paginación
    response = supabase.table("Rendimiento") \
        .select('Fecha, "Peso (kg)", Repeticiones, RM', count="exact") \
        .eq("user_id", user_id) \
        .eq("Ejercicio", ejercicio) \
        .eq("RPE", rpe_target) \
        .order("Fecha", desc=True) \
        .range(start, end) \
        .execute()

    total_registros = response.count if response.count else 0

    return {
        "status": "success",
        "metadata": {
            "total_total": total_registros,
            "pagina_actual": page,
        },
        "ejercicio": ejercicio,
        "rpe_consultado": rpe_target,
        "data": response.data
    }
        

@router.get("/progreso")
@router.get("/obtener_progreso")
def obtener_progreso(user_id: str):
    response = supabase.table("Rendimiento") \
        .select('*') \
        .eq("user_id", user_id) \
        .order("Fecha", desc=True) \
        .execute()

    if not response.data:
        return {"status": "success", "records": [], "analisis": []}

    # 1. Agrupamos registros por ejercicio
    agrupados = {}
    for reg in response.data:
        ej = reg.get("Ejercicio")
        if ej not in agrupados:
            agrupados[ej] = []
        agrupados[ej].append(reg)

    records_procesados = []
    analisis_procesados = []

    # 2. Procesamos cada ejercicio para generar 'records' y 'analisis'
    for ej, registros in agrupados.items():
        # Filtro: Solo ejercicios con al menos 2 registros
        if len(registros) >= 2:
            
            # Formateamos los registros para la prop 'records' (máximo 3)
            for r in registros[:3]:
                records_procesados.append({
                    "ejercicio": r.get("Ejercicio"),
                    "fecha": r.get("Fecha"),
                    "puntosFuerza": float(r.get("RM", 0)), # El valor para la línea
                    "peso": r.get("Peso_Corporal") or r.get("Peso (kg)", 0),
                    "repeticiones": r.get("Repeticiones", 0),
                    "rpe": r.get("RPE", 0)
                })

            # Calculamos la tendencia para la prop 'analisis'
            # (Último registro vs el anterior)
            actual = float(registros[0].get("RM", 0))
            anterior = float(registros[1].get("RM", 0))
            
            if anterior > 0:
                dif = ((actual - anterior) / anterior) * 100
                valor_numerico = round(dif, 2)
                porcentaje_str = f"{'+' if dif >= 0 else ''}{valor_numerico}%"
            else:
                valor_numerico = 0
                porcentaje_str = "0%"

            analisis_procesados.append({
                "ejercicio": ej,
                "porcentaje": porcentaje_str,
                "valor_numerico": valor_numerico
            })

    return {
        "status": "success",
        "records": records_procesados,
        "analisis": analisis_procesados
    }