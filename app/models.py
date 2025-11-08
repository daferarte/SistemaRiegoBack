from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from .database import Base

class LecturaHumedad(Base):
    __tablename__ = "lecturas"

    id = Column(Integer, primary_key=True, index=True)
    # Guardamos el tiempo de forma automática
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    valor = Column(Float) # Usamos Float para la humedad (ej. 55.5)