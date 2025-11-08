from sqlalchemy.orm import Session
from . import models, schemas

def crear_lectura(db: Session, lectura: schemas.LecturaBase):
    """
    Guarda una nueva lectura de humedad en la base de datos.
    """
    db_lectura = models.LecturaHumedad(valor=lectura.valor)
    db.add(db_lectura)
    db.commit()
    db.refresh(db_lectura)
    return db_lectura

def get_ultimas_lecturas(db: Session, skip: int = 0, limit: int = 20):
    """
    Obtiene las 'limit' últimas lecturas de la base de datos.
    """
    return db.query(models.LecturaHumedad).order_by(
        models.LecturaHumedad.timestamp.desc()
    ).offset(skip).limit(limit).all()