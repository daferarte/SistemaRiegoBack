from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from fastapi_mqtt import FastMQTT, MQTTConfig
import json

# Importamos todos nuestros módulos locales
from . import models, crud, schemas
from .database import SessionLocal, engine
from .websocket_manager import manager

# --- Configuración de la Base de Datos ---
# Crea las tablas en la base de datos (si no existen)
models.Base.metadata.create_all(bind=engine)

# Dependencia de FastAPI para obtener la sesión de la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Configuración de MQTT ---
# Asegúrate de que tu broker Mosquitto esté corriendo en esta IP/puerto
mqtt_config = MQTTConfig(
    host="localhost", # Cambia a la IP de tu broker Mosquitto
    port=1883,
    keepalive=60
)

# Creamos la instancia de la app FastAPI
app = FastAPI(title="API de Riego IoT")

# Inicializamos el cliente MQTT
fast_mqtt = FastMQTT(config=mqtt_config)
fast_mqtt.init_app(app)


# --- Lógica de MQTT (Recepción de datos) ---

# Tema para recibir la humedad del ESP32
TOPIC_HUMEDAD = "esp32/humedad"
# Tema para enviar comandos al ESP32
TOPIC_CONTROL_RIEGO = "esp32/control/riego"

@fast_mqtt.on_connect()
def on_mqtt_connect(client, flags, rc, properties):
    print("Conectado al broker MQTT.")
    # Nos suscribimos al tema de humedad al conectar
    client.subscribe(TOPIC_HUMEDAD)
    print(f"Suscrito al tema: {TOPIC_HUMEDAD}")

@fast_mqtt.on_message()
async def on_mqtt_message(client, topic, payload, qos, properties):
    """
    Este es el corazón de la app. Se activa cuando llega un mensaje MQTT.
    """
    print(f"Mensaje recibido en {topic}: {payload.decode()}")
    
    try:
        # 1. Decodificar el mensaje (asumimos JSON, ej: {"valor": 55.2})
        data = json.loads(payload.decode())
        valor_humedad = data.get("valor")

        if valor_humedad is None:
            print("Error: El JSON no tiene la clave 'valor'")
            return

        # 2. Guardar en la Base de Datos (SQLite)
        # Creamos un esquema Pydantic y una sesión de DB
        lectura_schema = schemas.LecturaBase(valor=valor_humedad)
        db = SessionLocal()
        try:
            crud.crear_lectura(db, lectura=lectura_schema)
            print(f"Dato guardado en DB: {valor_humedad}")
        finally:
            db.close()

        # 3. Enviar a Dashboards (WebSockets)
        # Preparamos el dato para el dashboard
        data_para_dashboard = {
            "timestamp": "ahora", # Idealmente, usar el timestamp de la DB
            "valor": valor_humedad
        }
        await manager.broadcast(data_para_dashboard)
        print("Dato enviado a WebSockets.")

    except Exception as e:
        print(f"Error procesando mensaje MQTT: {e}")

# --- Endpoints de la API ---

@app.post("/api/control/riego")
async def controlar_riego(comando: schemas.ComandoRiego):
    """
    Endpoint para que el Dashboard envíe comandos al ESP32.
    """
    print(f"Recibido comando de riego: {comando.accion}")
    
    # 5. Enviar Comando por MQTT
    fast_mqtt.publish(TOPIC_CONTROL_RIEGO, comando.accion, qos=1)
    
    return {"status": "comando_enviado", "accion": comando.accion}

@app.get("/api/datos/humedad", response_model=list[schemas.Lectura])
def obtener_historial_humedad(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    Endpoint para que el Dashboard obtenga el historial de datos.
    """
    lecturas = crud.get_ultimas_lecturas(db, skip=skip, limit=limit)
    return lecturas

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Punto de entrada para que los Dashboards se conecten.
    """
    await manager.connect(websocket)
    print("Nuevo Dashboard conectado.")
    try:
        while True:
            # Mantenemos la conexión abierta
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Dashboard desconectado.")