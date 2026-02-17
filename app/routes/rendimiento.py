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
        .select("nombre, categoria") \
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