from pydantic import BaseModel
from datetime import datetime

# Esquema para crear una lectura (usado por crud)
class LecturaBase(BaseModel):
    valor: float

# Esquema para leer una lectura (devuelto por la API)
class Lectura(LecturaBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True # Permite que Pydantic lea desde el modelo de SQLAlchemy

# Esquema para el comando de riego
class ComandoRiego(BaseModel):
    accion: str # Ej: "ON", "OFF"