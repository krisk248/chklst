#!/usr/bin/env python3
"""
chklst - Deployment Tracking Web Application
Single command startup: pipenv run python app.py

This module provides the main entry point for running the chklst application
in either production or development mode.
"""

import subprocess
import sys
import threading
import time
import webbrowser
import socket
import os
from pathlib import Path
import signal
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def is_port_in_use(port: int) -> bool:
    """
    Check if a port is already in use.

    Args:
        port: Port number to check

    Returns:
        True if port is in use, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def find_available_port(start_port: int = 8000, max_attempts: int = 10) -> int:
    """
    Find an available port starting from start_port.

    Args:
        start_port: Starting port number (default 8000)
        max_attempts: Maximum number of attempts to find port (default 10)

    Returns:
        First available port number

    Raises:
        RuntimeError: If no available port found after max_attempts
    """
    for i in range(max_attempts):
        port = start_port + i
        if not is_port_in_use(port):
            return port

    raise RuntimeError(
        f"No available port found in range {start_port}-{start_port + max_attempts - 1}"
    )


def open_browser(url: str, delay: float = 1.5) -> None:
    """
    Open browser after a short delay to ensure server is ready.

    Args:
        url: URL to open in browser
        delay: Delay in seconds before opening browser (default 1.5)
    """
    time.sleep(delay)
    webbrowser.open(url)


def run_production(port: int = 8000, open_browser_flag: bool = True) -> None:
    """
    Run application in production mode.

    Serves pre-built Vue frontend from frontend/dist/ directory.
    FastAPI serves both API endpoints and static frontend files.

    Args:
        port: Port to run server on (default 8000)
        open_browser_flag: Whether to auto-open browser (default True)
    """
    import uvicorn

    # Check if port is available
    if is_port_in_use(port):
        logger.warning(f"Port {port} is in use, finding alternative...")
        port = find_available_port(start_port=port)

    # Open browser in a separate thread if requested
    if open_browser_flag:
        url = f"http://localhost:{port}"
        browser_thread = threading.Thread(
            target=open_browser,
            args=(url, 1.5),
            daemon=True
        )
        browser_thread.start()

    logger.info(f"Starting chklst in production mode on port {port}")
    logger.info(f"Open http://localhost:{port} in your browser")

    try:
        uvicorn.run(
            "backend.main:app",
            host="127.0.0.1",
            port=port,
            reload=False,
            log_level="info",
        )
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)


def run_development(backend_port: int = 8000, frontend_port: int = 3000) -> None:
    """
    Run application in development mode with hot reload.

    Runs FastAPI backend on backend_port and Vite frontend dev server
    on frontend_port. Frontend proxies API calls to backend.

    Args:
        backend_port: Port for FastAPI backend (default 8000)
        frontend_port: Port for Vite dev server (default 3000)
    """
    # Check port availability
    if is_port_in_use(backend_port):
        logger.warning(f"Backend port {backend_port} is in use, finding alternative...")
        backend_port = find_available_port(start_port=backend_port)

    if is_port_in_use(frontend_port):
        logger.warning(f"Frontend port {frontend_port} is in use, finding alternative...")
        frontend_port = find_available_port(start_port=frontend_port)

    logger.info("Starting chklst in development mode")
    logger.info(f"Backend:  http://localhost:{backend_port}")
    logger.info(f"Frontend: http://localhost:{frontend_port}")
    logger.info("Press Ctrl+C to stop both servers")

    frontend_dir = Path(__file__).parent / "frontend"

    # Start backend process
    backend_process = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--host", "127.0.0.1",
            "--port", str(backend_port),
            "--reload",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait a moment for backend to start
    time.sleep(2)

    # Start frontend development server
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    logger.info("Both backend and frontend servers started")

    # Handle Ctrl+C gracefully
    def signal_handler(signum, frame):
        logger.info("Stopping servers...")
        backend_process.terminate()
        frontend_process.terminate()
        try:
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("Force killing processes...")
            backend_process.kill()
            frontend_process.kill()
        logger.info("Servers stopped")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Wait for both processes
    try:
        while True:
            # Check if processes are still running
            backend_alive = backend_process.poll() is None
            frontend_alive = frontend_process.poll() is None

            if not (backend_alive and frontend_alive):
                logger.error("One of the servers crashed")
                signal_handler(None, None)
                break
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)


def main() -> None:
    """
    Main entry point for the application.

    Parses command line arguments and runs the application in
    production or development mode.
    """
    parser = argparse.ArgumentParser(
        description='chklst - Deployment Tracking Web Application',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pipenv run python app.py              # Production mode on port 8000
  pipenv run python app.py --port 9000  # Production mode on port 9000
  pipenv run python app.py --dev        # Development mode with hot reload
  pipenv run python app.py --no-browser # Production without auto-opening browser
        """
    )

    parser.add_argument(
        '--dev',
        action='store_true',
        help='Run in development mode with hot reload'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Server port (default: 8000)'
    )
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Do not auto-open browser in production mode'
    )

    args = parser.parse_args()

    try:
        if args.dev:
            run_development()
        else:
            run_production(args.port, not args.no_browser)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
