from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        # Mantiene una lista de todas las conexiones activas
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Acepta una nueva conexión WebSocket."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Elimina una conexión WebSocket de la lista."""
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        """Envía un mensaje JSON a todas las conexiones activas."""
        # Convertimos el dict a JSON string
        message = json.dumps(data)
        for connection in self.active_connections:
            await connection.send_text(message)

# Creamos una instancia global para ser usada en la app
manager = ConnectionManager()