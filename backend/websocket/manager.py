"""WebSocket connection manager for real-time updates"""

from typing import Dict, Set
from fastapi import WebSocket
import json


class ConnectionManager:
    """Manage WebSocket connections and broadcast messages"""

    def __init__(self):
        """Initialize the connection manager"""
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections.discard(conn)

    async def broadcast_deployment_created(self, deployment: dict):
        """Broadcast deployment created message"""
        await self.broadcast({
            "type": "deployment_created",
            "data": deployment
        })

    async def broadcast_deployment_updated(self, deployment: dict):
        """Broadcast deployment updated message"""
        await self.broadcast({
            "type": "deployment_updated",
            "data": deployment
        })

    async def broadcast_project_updated(self, project: dict):
        """Broadcast project updated message"""
        await self.broadcast({
            "type": "project_updated",
            "data": project
        })

    async def broadcast_library_updated(self):
        """Broadcast library updated message"""
        await self.broadcast({
            "type": "library_updated",
            "data": None
        })


# Global instance
manager = ConnectionManager()
