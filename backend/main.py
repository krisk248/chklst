"""FastAPI application entry point"""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import settings
from backend.database import init_db, Base
from backend.api.routes import deployments, projects, library, reports, settings as settings_routes, migration
from backend.websocket.manager import manager
from backend.services.migration_service import MigrationService

# Import models to register them with SQLAlchemy
from backend import models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    print("Starting up...")
    await init_db()
    print("Database initialized")

    # Check if migration is needed and run it
    migration_service = MigrationService()
    if migration_service.check_migration_needed():
        print("Running data migration from existing files...")
        try:
            results = await migration_service.run_full_migration()
            if not results["errors"]:
                migration_service.mark_migration_complete()
                print(f"Migration completed successfully:")
                print(f"  - Projects: {results['projects']}")
                print(f"  - Components: {results['components']}")
                print(f"  - Deployments: {results['deployments']}")
                print(f"  - Library: {results['library_imported']}")
                print(f"  - Settings: {results['settings_imported']}")
            else:
                print(f"Migration completed with errors:")
                for error in results["errors"]:
                    print(f"  - {error}")
                print(f"Results:")
                print(f"  - Projects: {results['projects']}")
                print(f"  - Components: {results['components']}")
                print(f"  - Deployments: {results['deployments']}")
        except Exception as e:
            print(f"Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("Migration already completed. Skipping.")

    yield

    # Shutdown
    print("Shutting down...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title=settings.APP_NAME,
        description="Deployment tracking web application",
        version=settings.VERSION,
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )

    # Include routers
    app.include_router(
        deployments.router,
        prefix=settings.API_V1_PREFIX,
    )
    app.include_router(
        projects.router,
        prefix=settings.API_V1_PREFIX,
    )
    app.include_router(
        library.router,
        prefix=settings.API_V1_PREFIX,
    )
    app.include_router(
        reports.router,
        prefix=settings.API_V1_PREFIX,
    )
    app.include_router(
        settings_routes.router,
        prefix=settings.API_V1_PREFIX,
    )
    app.include_router(
        migration.router,
        prefix=settings.API_V1_PREFIX,
    )

    # WebSocket endpoint for real-time updates
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time updates"""
        await manager.connect(websocket)
        try:
            while True:
                # Keep connection alive, handle incoming messages if needed
                data = await websocket.receive_text()
                # Could handle client-to-server messages here if needed
        except WebSocketDisconnect:
            manager.disconnect(websocket)

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "ok", "app": settings.APP_NAME}

    # Mount static assets for production frontend serving
    frontend_dist_path = Path(__file__).parent.parent / "frontend" / "dist" / "assets"
    if frontend_dist_path.exists():
        app.mount("/assets", StaticFiles(directory=str(frontend_dist_path)), name="assets")

    # SPA fallback route - serves index.html for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve Vue SPA index.html as fallback for client-side routing"""
        frontend_index = Path(__file__).parent.parent / "frontend" / "dist" / "index.html"
        if frontend_index.exists():
            return FileResponse(frontend_index)
        # If index.html doesn't exist, show a helpful message
        return {"error": "Frontend not built. Run 'npm run build' in frontend directory."}

    # Root endpoint (only reached if no static files or API routes match)
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.VERSION,
            "api_version": "v1",
            "docs": "/docs",
            "openapi_schema": "/openapi.json",
        }

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
