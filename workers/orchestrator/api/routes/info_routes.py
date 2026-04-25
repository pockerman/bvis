

import os
from fastapi import (Depends,
                     HTTPException,
                     status, APIRouter,

                     Header,
                     )
from fastapi.responses import JSONResponse
from loguru import logger
import sys


from analysis_coordinator.api.coordinator_config import get_api_config


# removes the default logger to prevent duplication
logger.remove()
logger.add(sys.stdout)

DEFECT_DETECTION_SERVICE_CONTAINER_NAME = os.getenv("DEFECT_DETECTION_SERVICE_CONTAINER_NAME",
                                                    'exact-marine-defect-detection-container')
DEFECT_DETECTION_SERVICE_CONTAINER_PORT = int(os.getenv("DEFECT_DETECTION_SERVICE_CONTAINER_PORT", 8002))

RECOMMENDATION_SERVICE_CONTAINER_NAME = os.getenv("RECOMMENDATION_SERVICE_CONTAINER_NAME",
                                                  "exact-marine-recommendation-container")
RECOMMENDATION_SERVICE_CONTAINER_PORT = int(os.getenv("RECOMMENDATION_SERVICE_CONTAINER_PORT", 8005))

info_router = APIRouter(prefix="/api", tags=["Analysis Coordinator API"])


@info_router.get("/surveys-bucket-name")
async def get_surveys_bucket_name(api_config=Depends(get_api_config), api_version: str = Header()) -> JSONResponse:
    if api_version != api_config.api_version:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid api version. Current version={api_config.api_version}")

    return JSONResponse(status_code=status.HTTP_200_OK, content={"surveys_buck_name": "surveys-bucket"})


@info_router.get("/chats-bucket-name")
async def get_chats_bucket_name(api_config=Depends(get_api_config), api_version: str = Header()) -> JSONResponse:
    if api_version != api_config.api_version:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid api version. Current version={api_config.api_version}")

    return JSONResponse(status_code=status.HTTP_200_OK, content={"chats_buck_name": "chats-bucket"})


@info_router.get("/defects-images-repo")
async def get_defects_images_repo(embedder_name: str, api_config=Depends(get_api_config),
                                  api_version: str = Header()) -> JSONResponse:
    if api_version != api_config.api_version:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid api version. Current version={api_config.api_version}")

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"defects_images_repo": f"defects_images_{embedder_name}"})


@info_router.get("/defects-recommendations-repo")
async def get_defects_recommendations_repo(embedder_name: str, api_config=Depends(get_api_config),
                                           api_version: str = Header()) -> JSONResponse:
    if api_version != api_config.api_version:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid api version. Current version={api_config.api_version}")

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"defects_recommendations_repo": f"defects_recommendations_{embedder_name}"})
















