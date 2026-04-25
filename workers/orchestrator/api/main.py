from fastapi import FastAPI
from contextlib import asynccontextmanager

from analysis_coordinator.api.routes.routes import analysis_coordinator_router
from analysis_coordinator.api.routes.info_routes import info_router
from analysis_coordinator.api.routes.recommendation_routes import recommendations_router
from analysis_coordinator.api.routes.documents_routes import document_router
from analysis_coordinator.api.coordinator_config import get_api_config

DEBUG = True

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.
    Initializes resources and performs cleanup upon shutdown.
    """
    #_logger.info("Starting fine-tuning API...")
    #_logger.info("Loading API configuration...")

    # Access database session from configuration
    # in order to initialize it
    db_session = get_api_config().get_db_session()
    db_server_info = await db_session.connection.get_server_info()
    yield

# the mir-engine application instance
app = FastAPI(
    title="analysis-coordinator",
    debug=DEBUG,
    version="v0.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.include_router(info_router)
app.include_router(analysis_coordinator_router)
app.include_router(document_router)
app.include_router(recommendations_router)