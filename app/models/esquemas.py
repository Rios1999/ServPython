from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date
from uuid import UUID

class RegistroEntrenamiento(BaseModel):
    # Forzamos que los nombres coincidan con los alias de tu imagen de Supabase
    ejercicio: str = Field(..., alias="Ejercicio")
    peso_kg: float = Field(..., alias="Peso (kg)")
    repeticiones: int = Field(..., alias="Repeticiones")
    
    # IMPORTANTE: En tu imagen ponía 'Peso_Corpora', asegúrate de que el alias sea idéntico
    peso_corporal: Optional[float] = Field(None, alias="Peso_Corporal")
    
    rm: Optional[float] = Field(None, alias="RM")
    fecha: date = Field(default_factory=date.today, alias="Fecha")
    
    # Cambiamos a UUID para mayor seguridad con Supabase
    user_id: Optional[UUID] = Field(None, alias="user_id")
    
    rpe: Optional[float] = Field(None, alias="RPE")
    musculo: Optional[str] = Field(None, alias="Musculo")
    tiene_carga: bool = Field(default=True, alias="Tiene_Carga")

    # ESTO ES LO QUE TE FALTA:
    model_config = ConfigDict(
        populate_by_name=True,  # Permite usar peso_kg en el JSON de Vite
        arbitrary_types_allowed=True
    )


class DeleteRecord(BaseModel):
    id: int