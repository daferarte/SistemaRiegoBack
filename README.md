# 🌱 Sistema deRiego IoT con FastAPI y ESP32

Este proyecto es un backend completo construido con **FastAPI** para gestionar un sistema de riego automático e inteligente. Está diseñado para recibir datos de humedad de un microcontrolador (como un **ESP32**) vía **MQTT**, almacenar estos datos en **SQLite**, y enviar comandos de control de vuelta al dispositivo.

Además, expone los datos en tiempo real a un dashboard (no incluido) a través de **WebSockets**.

## ✨ Características Principales

* **Recepción de Datos en Tiempo Real:** Escucha un broker MQTT (Mosquitto) para recibir lecturas de humedad del ESP32.
* **Almacenamiento Persistente:** Guarda cada lectura en una base de datos **SQLite** para análisis histórico.
* **Dashboard en Vivo:** Envía automáticamente cada nueva lectura a todos los dashboards conectados mediante **WebSockets**.
* **Control Bidireccional:** Expone una API REST para que el dashboard pueda enviar comandos (ej. "Activar Riego") que se publican en MQTT para el ESP32.
* **Documentación Automática:** Gracias a FastAPI, la documentación de la API está disponible al instante en `/docs`.

---

## 🏗️ Arquitectura del Sistema

El flujo de datos está diseñado para ser eficiente y desacoplado.

### Flujo de Datos (Sensor -> Dashboard)

1.  **ESP32** lee el sensor de humedad.
2.  Publica un mensaje JSON en el topic MQTT `esp32/humedad` (Ej: `{"valor": 65.5}`).
3.  **FastAPI** (suscrito a ese topic) recibe el mensaje.
4.  Guarda el valor `65.5` en la base de datos **SQLite**.
5.  Envía el nuevo dato a todos los clientes conectados al **WebSocket** (`/ws`).
6.  El **Dashboard** (cliente) recibe el dato y actualiza la gráfica/indicador.

### Flujo de Control (Dashboard -> Riego)

1.  El usuario presiona "Activar Riego" en el **Dashboard**.
2.  El Dashboard envía una petición `POST` al endpoint `/api/control/riego` de **FastAPI** (Ej: `{"accion": "ON"}`).
3.  **FastAPI** recibe la petición y publica un mensaje en el topic MQTT `esp32/control/riego` (Ej: `ON`).
4.  El **ESP32** (suscrito a ese topic) recibe el mensaje `ON` y activa el relé de la bomba de agua.

---

## 🔧 Instalación y Puesta en Marcha

### Prerrequisitos

* Python 3.8+
* Un broker **Mosquitto** (o cualquier broker MQTT) corriendo.
* Un **ESP32** programado para publicar y suscribirse a los topics (ver [código de ejemplo](#-código-del-esp32)).

### Pasos de Instalación

1.  **Clona o descarga este repositorio:**
    ```bash
    git clone [URL_DEL_REPO]
    cd proyecto_riego
    ```

2.  **Crea un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instala las dependencias:**
    El archivo `requirements.txt` debe contener:
    ```txt
    fastapi
    uvicorn[standard]
    sqlalchemy
    fastapi-mqtt
    paho-mqtt
    ```
    Ejecuta:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configura tu Broker MQTT:**
    Abre el archivo `app/main.py` y edita la configuración de `mqtt_config` para que apunte a la IP y puerto de tu broker Mosquitto:

    ```python
    mqtt_config = MQTTConfig(
        host="localhost", # <-- CAMBIA ESTO por la IP de tu broker
        port=1883,
        keepalive=60
    )
    ```

### 🚀 Ejecutar el Servidor

Desde la carpeta raíz del proyecto (`proyecto_riego`), ejecuta:

```bash
uvicorn app.main:app --reload