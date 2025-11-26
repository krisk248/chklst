"""Tests for WebSocket functionality"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import WebSocket
from fastapi.testclient import TestClient

from backend.websocket.manager import ConnectionManager, manager


class TestConnectionManager:
    """Test cases for ConnectionManager"""

    @pytest.mark.asyncio
    async def test_connection_manager_init(self):
        """Test ConnectionManager initialization"""
        conn_manager = ConnectionManager()
        assert isinstance(conn_manager.active_connections, set)
        assert len(conn_manager.active_connections) == 0

    @pytest.mark.asyncio
    async def test_connect_websocket(self):
        """Test connecting a WebSocket"""
        conn_manager = ConnectionManager()
        mock_ws = AsyncMock(spec=WebSocket)

        await conn_manager.connect(mock_ws)

        mock_ws.accept.assert_called_once()
        assert mock_ws in conn_manager.active_connections

    @pytest.mark.asyncio
    async def test_disconnect_websocket(self):
        """Test disconnecting a WebSocket"""
        conn_manager = ConnectionManager()
        mock_ws = AsyncMock(spec=WebSocket)

        await conn_manager.connect(mock_ws)
        assert mock_ws in conn_manager.active_connections

        conn_manager.disconnect(mock_ws)
        assert mock_ws not in conn_manager.active_connections

    @pytest.mark.asyncio
    async def test_disconnect_nonexistent_websocket(self):
        """Test disconnecting a WebSocket that doesn't exist"""
        conn_manager = ConnectionManager()
        mock_ws = AsyncMock(spec=WebSocket)

        # Should not raise an error
        conn_manager.disconnect(mock_ws)
        assert mock_ws not in conn_manager.active_connections

    @pytest.mark.asyncio
    async def test_broadcast_message(self):
        """Test broadcasting a message to all connections"""
        conn_manager = ConnectionManager()
        mock_ws1 = AsyncMock(spec=WebSocket)
        mock_ws2 = AsyncMock(spec=WebSocket)
        mock_ws3 = AsyncMock(spec=WebSocket)

        await conn_manager.connect(mock_ws1)
        await conn_manager.connect(mock_ws2)
        await conn_manager.connect(mock_ws3)

        message = {"type": "test", "data": "hello"}
        await conn_manager.broadcast(message)

        mock_ws1.send_json.assert_called_once_with(message)
        mock_ws2.send_json.assert_called_once_with(message)
        mock_ws3.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_removes_disconnected_clients(self):
        """Test that broadcast removes disconnected clients"""
        conn_manager = ConnectionManager()
        mock_ws1 = AsyncMock(spec=WebSocket)
        mock_ws2 = AsyncMock(spec=WebSocket)
        mock_ws3 = AsyncMock(spec=WebSocket)

        await conn_manager.connect(mock_ws1)
        await conn_manager.connect(mock_ws2)
        await conn_manager.connect(mock_ws3)

        # Make ws2 raise an exception when trying to send
        mock_ws2.send_json.side_effect = Exception("Connection closed")

        message = {"type": "test", "data": "hello"}
        await conn_manager.broadcast(message)

        # ws2 should be removed from active connections
        assert mock_ws2 not in conn_manager.active_connections
        assert mock_ws1 in conn_manager.active_connections
        assert mock_ws3 in conn_manager.active_connections

    @pytest.mark.asyncio
    async def test_broadcast_deployment_created(self):
        """Test broadcasting deployment created message"""
        conn_manager = ConnectionManager()
        mock_ws = AsyncMock(spec=WebSocket)
        await conn_manager.connect(mock_ws)

        deployment = {
            "id": 1,
            "jira_id": "JIRA-123",
            "project_id": 1,
            "build_status": "success"
        }

        await conn_manager.broadcast_deployment_created(deployment)

        expected_message = {
            "type": "deployment_created",
            "data": deployment
        }
        mock_ws.send_json.assert_called_once_with(expected_message)

    @pytest.mark.asyncio
    async def test_broadcast_deployment_updated(self):
        """Test broadcasting deployment updated message"""
        conn_manager = ConnectionManager()
        mock_ws = AsyncMock(spec=WebSocket)
        await conn_manager.connect(mock_ws)

        deployment = {
            "id": 1,
            "jira_id": "JIRA-123",
            "deploy_status": "success"
        }

        await conn_manager.broadcast_deployment_updated(deployment)

        expected_message = {
            "type": "deployment_updated",
            "data": deployment
        }
        mock_ws.send_json.assert_called_once_with(expected_message)

    @pytest.mark.asyncio
    async def test_broadcast_project_updated(self):
        """Test broadcasting project updated message"""
        conn_manager = ConnectionManager()
        mock_ws = AsyncMock(spec=WebSocket)
        await conn_manager.connect(mock_ws)

        project = {
            "id": 1,
            "name": "Test Project"
        }

        await conn_manager.broadcast_project_updated(project)

        expected_message = {
            "type": "project_updated",
            "data": project
        }
        mock_ws.send_json.assert_called_once_with(expected_message)

    @pytest.mark.asyncio
    async def test_broadcast_library_updated(self):
        """Test broadcasting library updated message"""
        conn_manager = ConnectionManager()
        mock_ws = AsyncMock(spec=WebSocket)
        await conn_manager.connect(mock_ws)

        await conn_manager.broadcast_library_updated()

        expected_message = {
            "type": "library_updated",
            "data": None
        }
        mock_ws.send_json.assert_called_once_with(expected_message)

    @pytest.mark.asyncio
    async def test_global_manager_instance(self):
        """Test that global manager instance exists"""
        assert manager is not None
        assert isinstance(manager, ConnectionManager)


class TestWebSocketEndpoint:
    """Test cases for WebSocket endpoint"""

    def test_websocket_endpoint_exists(self):
        """Test that WebSocket endpoint is registered in the app"""
        from backend.main import app

        # Check that the /ws endpoint exists
        routes = [route.path for route in app.routes]
        assert "/ws" in routes

    def test_websocket_manager_in_main(self):
        """Test that manager is imported in main.py"""
        from backend.main import manager as main_manager
        from backend.websocket.manager import manager as direct_manager

        # Should be the same global instance
        assert main_manager is direct_manager
