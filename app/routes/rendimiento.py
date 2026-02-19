import json
from fastapi import APIRouter
from app.database import supabase
from app.models.esquemas import RegistroEntrenamiento

router = APIRouter(prefix="/rendimiento", tags=["Rendimiento"])

@router.post("/")
def guardar_Marca(log: RegistroEntrenamiento):
    # Ya no necesitas try/except, el Global Handler de main.py captura errores de DB
    data = json.loads(log.model_dump_json(by_alias=True, exclude_none=True))
    
    # Si esto falla, el Middleware responde automáticamente con el error de Supabase
    supabase.table("Rendimiento").insert(data).execute()
    
    return {"status": "success"}

@router.get("/catalogo-ejercicios/")
def obtener_catalogo(page: int = 1):
    # La lógica se mantiene, pero sin el try/except manual
    limit_por_grupo = 20
    start = (page - 1) * limit_por_grupo
    end = start + limit_por_grupo - 1

    response = supabase.table("Ejercicios") \
        .select("nombre, categoria, peso_corporal") \
        .order("categoria", desc=False) \
        .order("nombre", desc=False) \
        .execute()

    conteo_por_categoria = {}
    lista_plana_final = []

    for ej in response.data:
        cat = ej.get('categoria', 'Sin Categoría')
        
        if cat not in conteo_por_categoria:
            conteo_por_categoria[cat] = 0

        actual = conteo_por_categoria[cat]
        if start <= actual <= end:
            lista_plana_final.append(ej)
        
        conteo_por_categoria[cat] += 1

    return {
        "status": "success",
        "metadata": {
            "pagina": page,
            "total_ejercicios_en_pagina": len(lista_plana_final)
        },
        "data": lista_plana_final
    }


    try:
        # 1. Traemos todo el historial ordenado por fecha (el más reciente primero)
        response = supabase.table("Rendimiento") \
            .select('*') \
            .eq("user_id", user_id) \
            .order("Fecha", desc=True) \
            .execute()

        if not response.data:
            return {"status": "success", "data": []}

        # 2. Agrupamos registros por ejercicio
        agrupados = {}
        for reg in response.data:
            ejercicio = reg["Ejercicio"]
            if ejercicio not in agrupados:
                agrupados[ejercicio] = []
            agrupados[ejercicio].append(reg)

        # 3. Aplicamos el filtro: mínimo 2, máximo 3
        resultado_final = []
        for ejercicio, registros in agrupados.items():
            # Solo si tiene 2 o más registros
            if len(registros) >= 2:
                # Nos quedamos solo con los 3 primeros (los más recientes)
                resultado_final.extend(registros[:3])

        return {
            "status": "success",
            "count": len(resultado_final),
            "data": resultado_final
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}