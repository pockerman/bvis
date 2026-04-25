import bson
import datetime
import os
import requests

from fastapi import (Depends,
                     HTTPException,
                     status, APIRouter,
                     BackgroundTasks,
                     Header,
                     BackgroundTasks)
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from analysis_coordinator.pdf_generation_utils.pdf_generation_job import pdf_generation_task
from analysis_coordinator.api.coordinator_config import get_api_config
from .redis_connection import (
    get_pdf_generation_work_queue,
    get_summarization_work_queue)

logger.remove()
logger.add(sys.stdout)

DEFECT_DETECTION_SERVICE_CONTAINER_NAME = os.getenv("DEFECT_DETECTION_SERVICE_CONTAINER_NAME",
                                                    'exact-marine-defect-detection-container')
DEFECT_DETECTION_SERVICE_CONTAINER_PORT = int(os.getenv("DEFECT_DETECTION_SERVICE_CONTAINER_PORT", 8002))

RECOMMENDATION_SERVICE_CONTAINER_NAME = os.getenv("RECOMMENDATION_SERVICE_CONTAINER_NAME",
                                                  "exact-marine-recommendation-container")
RECOMMENDATION_SERVICE_CONTAINER_PORT = int(os.getenv("RECOMMENDATION_SERVICE_CONTAINER_PORT", 8005))

document_router = APIRouter(prefix="/api", tags=["Analysis Coordinator API"])


@document_router.post("/pdf-generation-tasks/{survey_id}")
async def new_pdf_generation_request(survey_id: str,
                                     work_queue=Depends(get_pdf_generation_work_queue),
                                     api_config=Depends(get_api_config),
                                     api_version: str = Header()) -> JSONResponse:
    if api_version != api_config.api_version:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid api version. Current version={api_config.api_version}")

    if api_config.DEBUG:
        logger.debug(f"Received survey id {survey_id}")

    db = api_config.get_db_session()
    survey = await db.find_one(collection="surveys",
                               criteria={'_id': bson.ObjectId(survey_id)},
                               projection={})

    logger.debug(f"Survey details {survey}")

    if not survey:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"survey {survey_id} was not found")

    images = await db.find(collection='images',
                           criteria={'surveyId': bson.ObjectId(survey_id)},
                           projection={'createdAt': False, 'updatedAt': False})

    logger.info(f"Survey images {images}")

    created_at = datetime.datetime.fromtimestamp(survey["createdAt"] / 1000, tz=datetime.timezone.utc)
    survey_data = {
        "survey_id": survey_id,
        "owner_name": "Alex",
        "owner_surname": "Giavaras",
        "vessel_data": survey["vesselDetails"],
        "executive_summary": "this is the executive summary",
        "recommendations_summary": survey["recommendations"],
        "created_at": str(created_at),
        "images": images,
        "submitted_at": str(datetime.datetime.now(datetime.UTC))
    }
    job = work_queue.enqueue(pdf_generation_task, survey_id, survey_data)

    # we can now store the job in the db
    # db_session = api_config.get_db_session()
    # survey = await db_session.find_one(criteria={'_id': bson.ObjectId(survey_id)}, collection='surveys')

    if api_config.DEBUG:
        logger.debug(f"Enqueued 1 job for PDF creation job id={job}")

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "OK"})
