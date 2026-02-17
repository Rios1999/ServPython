from fastapi import APIRouter
from app.database import supabase # Si vas a usar la base de datos

# ESTA ES LA LÍNEA QUE TE FALTA:
router = APIRouter(prefix="/analisis", tags=["Análisis"])

@router.get("/")
def obtener_resumen():
    return {"mensaje": "Hola desde análisis"}