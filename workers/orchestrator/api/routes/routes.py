import bson

import os


from fastapi import (Depends, 
                     HTTPException, 
                     status, APIRouter, 

                     Header, 
                     BackgroundTasks)
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from analysis_coordinator.core_utils.survey_analysis_request import NewSurveyImageRequest
from analysis_coordinator.core_utils.image_defect_detector_response import ImageDefectDetectorResultPost
from analysis_coordinator.core_utils.recommendation_summarization_response import SurveySummarizationPost
from analysis_coordinator.api.coordinator_config import get_api_config

from .coordinator_db_tasks import check_and_update_survey_status, schedule_summarization_task
from .routest_helpers import send_post_request

# removes the default logger to prevent duplication
logger.remove()
logger.add(sys.stdout)


DEFECT_DETECTION_SERVICE_CONTAINER_NAME = os.getenv("DEFECT_DETECTION_SERVICE_CONTAINER_NAME",
                                                    'exact-marine-defect-detection-container')
DEFECT_DETECTION_SERVICE_CONTAINER_PORT = int(os.getenv("DEFECT_DETECTION_SERVICE_CONTAINER_PORT", 8002))

RECOMMENDATION_SERVICE_CONTAINER_NAME = os.getenv("RECOMMENDATION_SERVICE_CONTAINER_NAME",
                                                  "exact-marine-recommendation-container")
RECOMMENDATION_SERVICE_CONTAINER_PORT = int(os.getenv("RECOMMENDATION_SERVICE_CONTAINER_PORT", 8005))

analysis_coordinator_router = APIRouter(prefix="/api", tags=["Analysis Coordinator API"])


@analysis_coordinator_router.post("/analysis/{survey_id}")
async def new_analysis_request(survey_id: str, *,
                               image_request: NewSurveyImageRequest,
                               background_tasks: BackgroundTasks,
                               api_config=Depends(get_api_config),
                               api_version: str = Header()) -> JSONResponse:
    
    if api_version != api_config.api_version:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid api version. Current version={api_config.api_version}")

    if api_config.DEBUG:
        logger.debug(f"Received survey id {survey_id}")

    validation_result = NewSurveyImageRequest.is_valid(image_request)

    if validation_result != 'OK':
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail=validation_result)

    for img in image_request.images:

        # we send requests to the defect detection service
        data = {
            "image_id": img.image_id,
            "image_path": img.image_path
        }
        url = f"http://{DEFECT_DETECTION_SERVICE_CONTAINER_NAME}:{DEFECT_DETECTION_SERVICE_CONTAINER_PORT}"
        url = url + f"/api/defect-detection/detect/{survey_id}?request_type=survey"

        if api_config.DEBUG:
            logger.debug(f"Posting on url {url}")
            logger.debug(f"Sending data={data}")

        background_tasks.add_task(send_post_request,
                                  data=data,
                                  url=url,
                                  api_version=api_version)

    if api_config.DEBUG:
        logger.debug(f"Enqueued {len(image_request.images)} images for analysis")

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "OK"})


@analysis_coordinator_router.post("/defect-tasks/{task_id}")
async def defect_detection_task_result(task_id: str,
                                       img_results: ImageDefectDetectorResultPost,
                                       background_tasks: BackgroundTasks,
                                       api_config=Depends(get_api_config),
                                       api_version: str = Header()) -> JSONResponse:
    """Receives the image defect detection result. It updates
    the relevant image and if necessary schedules a recommendation task

    Args:
        task_id ():
        img_results ():
        background_tasks ():
        api_config ():
        work_queue ():
        api_version ():

    Returns:

    """

    if api_version != api_config.api_version:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid api version. Current version={api_config.api_version}")

    if api_config.DEBUG:
        logger.debug(f"Received defect task result {task_id}")
        logger.debug(img_results)

    # we can now store the job in the db
    db_session = api_config.get_db_session()

    # get the image and survey id
    image_id = img_results.image_id
    survey_id = img_results.survey_id

    image_result = img_results.result
    defects = image_result.defects

    # TODO: Leave this here for easy testing
    defects = [{
        "severity": "severe",
        "description": "Severe corrosion on a metalic plate",
        "label": "corrosion"
    }]

    image_detection_data = {
        # should always be true as it the flag to check
        # if the image defect detection has finished
        'success': True,  # img_results.success,
        'defects': defects
    }

    # there are defects found on this image
    if defects:

        if api_config.DEBUG:
            logger.debug(f"Defects detected updating DB and schedule a recommendation job...")

        recommendation_query = {
            "image_description": img_results.result.image_description,
            "hull_material": "steel",
            "defects": defects,
            "image_id": image_id
        }

        # update the image in the db about the result
        # and the image description
        update_result = await db_session.update_one(criteria={'_id': bson.ObjectId(image_id)},
                                                    data={'$set': {'imageDetection': image_detection_data,
                                                                   'imageSummary': img_results.result.image_description
                                                                   }
                                                          },
                                                    collection='images')

        # we need to trigger the recommendations service
        url = f"http://{RECOMMENDATION_SERVICE_CONTAINER_NAME}:{RECOMMENDATION_SERVICE_CONTAINER_PORT}"
        url = url + f"/api/recommendations/recommend/{survey_id}?request_type=survey"

        background_tasks.add_task(send_post_request,
                                  data=recommendation_query,
                                  url=url,
                                  api_version=api_version)

    else:

        if api_config.DEBUG:
            logger.debug(f"No defects detected...")

        # nothing to send to the recommendation engine
        update_result = await db_session.update_one(criteria={'_id': bson.ObjectId(image_id)},
                                                    data={'$set': {'imageDetection': image_detection_data,
                                                                   'imageSummary': img_results.result.image_description,
                                                                   'imageRecommendations.success': True,
                                                                   }},
                                                    collection='images')

        # let's check and update the survey status
        # above we know that this survey is not finished as we scheduled
        # a recommendation job
        await check_and_update_survey_status(survey_id=survey_id, api_config=api_config)

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "OK"})


@analysis_coordinator_router.post("/summarization-tasks/{task_id}")
async def summarization_task_result(task_id: str,
                                    summarization: SurveySummarizationPost,
                                    api_config=Depends(get_api_config),
                                    api_version: str = Header()
                                    ) -> JSONResponse:
    if api_version != api_config.api_version:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid api version. Current version={api_config.api_version}")

    # we can now store the job in the db
    db_session = api_config.get_db_session()

    survey_id = summarization.survey_id

    # we received the summarization for the survey and also
    # update the status of the survey
    await db_session.update_one(criteria={'_id': bson.ObjectId(survey_id)},
                                data={'$set': {'status': 'PENDING_USER_REVIEW',
                                               'recommendations': [summarization.recommendations_summary]}},
                                collection='surveys')

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": "OK"})



