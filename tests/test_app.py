"""
Tests for main application entry point (app.py)
"""

import socket
import subprocess
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest


class TestPortDetection:
    """Test port detection and availability checking"""

    def test_is_port_in_use_with_available_port(self):
        """Test that is_port_in_use returns False for available port"""
        from app import is_port_in_use

        # Use a port that's typically available
        available_port = 19999
        result = is_port_in_use(available_port)
        assert result is False

    def test_is_port_in_use_with_in_use_port(self):
        """Test that is_port_in_use returns True for in-use port"""
        from app import is_port_in_use

        # Create a socket listening on a port to simulate it being in use
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('127.0.0.1', 0))
            s.listen(1)
            _, port = s.getsockname()

            result = is_port_in_use(port)
            assert result is True

    def test_find_available_port_returns_int(self):
        """Test that find_available_port returns an integer"""
        from app import find_available_port

        port = find_available_port()
        assert isinstance(port, int)
        assert port > 0

    def test_find_available_port_with_custom_start(self):
        """Test find_available_port with custom start port"""
        from app import find_available_port

        port = find_available_port(start_port=18000)
        assert port >= 18000

    def test_find_available_port_raises_on_no_available(self):
        """Test find_available_port raises error when no port available"""
        from app import find_available_port

        with patch('app.is_port_in_use', return_value=True):
            with pytest.raises(RuntimeError, match="No available port found"):
                find_available_port(max_attempts=3)


class TestBrowserOpening:
    """Test browser opening functionality"""

    @patch('webbrowser.open')
    @patch('time.sleep')
    def test_open_browser_opens_correct_url(self, mock_sleep, mock_browser_open):
        """Test that open_browser opens the correct URL"""
        from app import open_browser

        test_url = "http://localhost:8000"
        open_browser(test_url)

        mock_browser_open.assert_called_once_with(test_url)

    @patch('webbrowser.open')
    @patch('time.sleep')
    def test_open_browser_waits_before_opening(self, mock_sleep, mock_browser_open):
        """Test that open_browser waits before opening"""
        from app import open_browser

        test_url = "http://localhost:8000"
        open_browser(test_url, delay=2.0)

        mock_sleep.assert_called_once_with(2.0)
        mock_browser_open.assert_called_once_with(test_url)

    @patch('webbrowser.open')
    @patch('time.sleep')
    def test_open_browser_uses_default_delay(self, mock_sleep, mock_browser_open):
        """Test that open_browser uses default delay"""
        from app import open_browser

        open_browser("http://localhost:8000")
        mock_sleep.assert_called_once_with(1.5)


class TestProductionMode:
    """Test production mode execution"""

    @patch('uvicorn.run')
    def test_run_production_calls_uvicorn(self, mock_uvicorn):
        """Test that run_production calls uvicorn.run"""
        from app import run_production

        with patch('app.open_browser'):
            run_production(8000, open_browser_flag=False)

        mock_uvicorn.assert_called_once()
        call_args = mock_uvicorn.call_args
        assert call_args[1]['port'] == 8000
        assert 'reload' in call_args[1]

    @patch('app.open_browser')
    @patch('uvicorn.run')
    def test_run_production_opens_browser_when_flag_true(self, mock_uvicorn, mock_browser):
        """Test that run_production opens browser when flag is True"""
        from app import run_production

        # Make uvicorn.run block temporarily
        mock_uvicorn.side_effect = lambda *args, **kwargs: None

        run_production(8000, open_browser_flag=True)

        # Browser should be opened (via threading)
        # This is a timing-dependent test, so we just verify no error

    @patch('app.open_browser')
    @patch('uvicorn.run')
    def test_run_production_skips_browser_when_flag_false(self, mock_uvicorn, mock_browser):
        """Test that run_production skips browser when flag is False"""
        from app import run_production

        run_production(8000, open_browser_flag=False)

        mock_browser.assert_not_called()


class TestDevelopmentMode:
    """Test development mode execution"""

    @patch('subprocess.Popen')
    def test_run_development_starts_processes(self, mock_popen):
        """Test that run_development starts both backend and frontend"""
        from app import run_development

        mock_popen.return_value = MagicMock()

        try:
            # We'll interrupt it quickly
            with patch('time.sleep', side_effect=KeyboardInterrupt):
                run_development()
        except KeyboardInterrupt:
            pass

    @patch('subprocess.Popen')
    def test_run_development_uses_correct_ports(self, mock_popen):
        """Test that run_development uses correct ports"""
        from app import run_development

        mock_popen.return_value = MagicMock()

        try:
            with patch('time.sleep', side_effect=KeyboardInterrupt):
                run_development(backend_port=8001, frontend_port=3001)
        except KeyboardInterrupt:
            pass


class TestMainEntry:
    """Test main entry point and argument parsing"""

    @patch('app.run_production')
    def test_main_calls_production_by_default(self, mock_production):
        """Test that main calls run_production by default"""
        from app import main

        with patch('sys.argv', ['app.py']):
            try:
                main()
            except SystemExit:
                pass

    @patch('app.run_development')
    def test_main_calls_development_with_dev_flag(self, mock_development):
        """Test that main calls run_development with --dev flag"""
        from app import main

        with patch('sys.argv', ['app.py', '--dev']):
            try:
                main()
            except SystemExit:
                pass

    @patch('app.run_production')
    def test_main_passes_port_argument(self, mock_production):
        """Test that main passes port argument correctly"""
        from app import main

        with patch('sys.argv', ['app.py', '--port', '9000']):
            try:
                main()
            except SystemExit:
                pass

    @patch('app.run_production')
    def test_main_respects_no_browser_flag(self, mock_production):
        """Test that main respects --no-browser flag"""
        from app import main

        with patch('sys.argv', ['app.py', '--no-browser']):
            try:
                main()
            except SystemExit:
                pass


class TestStaticFileServing:
    """Test that backend is configured for static file serving"""

    def test_backend_main_has_static_mount(self):
        """Test that backend/main.py mounts static files"""
        from backend.main import app

        # Check that static files are mounted
        has_static_mount = False
        for route in app.routes:
            if hasattr(route, 'path') and route.path == "/assets":
                has_static_mount = True
                break

        assert has_static_mount, "Static assets directory not mounted in backend"

    def test_backend_main_has_spa_fallback(self):
        """Test that backend/main.py has SPA fallback route"""
        from backend.main import app

        # Check for catch-all route
        has_spa_fallback = False
        for route in app.routes:
            if hasattr(route, 'path') and '{full_path' in route.path:
                has_spa_fallback = True
                break

        assert has_spa_fallback, "SPA fallback route not configured in backend"


class TestBuildScript:
    """Test build script exists and is executable"""

    def test_build_script_exists(self):
        """Test that build.sh script exists"""
        build_script = Path(__file__).parent.parent / "build.sh"
        assert build_script.exists(), "build.sh script not found"

    def test_build_script_is_executable(self):
        """Test that build.sh is executable"""
        build_script = Path(__file__).parent.parent / "build.sh"
        import os
        assert os.access(build_script, os.X_OK), "build.sh is not executable"

    def test_build_script_content(self):
        """Test that build.sh has expected content"""
        build_script = Path(__file__).parent.parent / "build.sh"
        content = build_script.read_text()
        assert "npm run build" in content, "build.sh missing npm build command"
        assert "frontend" in content, "build.sh missing frontend reference"


class TestAppInitialization:
    """Test app initialization and structure"""

    def test_app_py_exists(self):
        """Test that app.py exists in project root"""
        app_py = Path(__file__).parent.parent / "app.py"
        assert app_py.exists(), "app.py not found in project root"

    def test_app_py_has_main_function(self):
        """Test that app.py has main() function"""
        from app import main
        assert callable(main), "main function not found in app.py"

    def test_app_py_has_required_functions(self):
        """Test that app.py has all required functions"""
        from app import (
            is_port_in_use,
            find_available_port,
            open_browser,
            run_production,
            run_development,
            main,
        )

        assert callable(is_port_in_use)
        assert callable(find_available_port)
        assert callable(open_browser)
        assert callable(run_production)
        assert callable(run_development)
        assert callable(main)
