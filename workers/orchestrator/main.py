from fastapi import FastAPI
from contextlib import asynccontextmanager


from orchestrator.routes import orchestrator_router

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
    yield


# the mir-engine application instance
app = FastAPI(
    title="ai-orchestrator",
    debug=DEBUG,
    version="v0.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
)



app.include_router(orchestrator_router)




