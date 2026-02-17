from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from postgrest.exceptions import APIError  
from app.routes import rendimiento,analisis

app = FastAPI(title="GymTraking API")

# Configuración de CORS (Vital para que React no falle)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def manejador_errores_universal(request: Request, exc: Exception):
    # Si el error viene de la base de datos (Supabase/PostgreSQL)
    if isinstance(exc, APIError):
        print(f"❌ Error DB en {request.url.path}: {exc.message}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "tipo": "Base de Datos",
                "message": exc.message,
                "detail": exc.details
            }
        )
    
    # Si es un error que tú lanzaste manualmente (HTTPException)
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "message": exc.detail}
        )

    # Para cualquier otro error de Python (errores de código, variables, etc.)
    print(f"❌ Error Inesperado en {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Vaya, algo se ha roto internamente.",
            "tecnico": str(exc) # Quita esto en producción real por seguridad
        }
    )


# Conectamos las rutas
app.include_router(rendimiento.router)
app.include_router(analisis.router)

@app.get("/")
def inicio():
    return {"mensaje": "Servidor de GymTraking funcionando ✅"}

@app.get("/config")
def obtener_config():
    return {"version": "1.1.0", "modo": "produccion"}