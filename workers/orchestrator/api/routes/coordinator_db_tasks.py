import bson
from rq import Queue
from typing import Callable

from analysis_coordinator.api.coordinator_config import APIConfigBase


async def check_and_update_survey_status(survey_id: str, api_config: APIConfigBase) -> None:
    # we can now store the job in the db
    db_session = api_config.get_db_session()

    # get all the images associated with the survey
    # that have success flag still undefined
    all_images = await db_session.find(criteria={'surveyId': bson.ObjectId(survey_id)},
                                       collection='images',
                                       projection={'imageDetection.success': 1,
                                                   'imageRecommendation.success': 1})

    all_finished = True
    for img in all_images:
        if img['imageDetection']['success'] is not None and img['imageRecommendation']['success'] is not None:
            continue
        else:
            # we found an image that is not finished
            all_finished = False
            break

    if all_finished:
        # if all images have finished then the survey is turned
        # into PENDING_USER_REVIEW
        update_result = await db_session.update_one(criteria={'_id': bson.ObjectId(survey_id)},
                                                    data={'$set': {'status': 'PENDING_USER_REVIEW',
                                                                   'recommendations': ['No defects detected in the provided images']}},
                                                    collection='surveys')


async def schedule_summarization_task(survey_id: str,
                                      api_config: APIConfigBase,
                                      summarization_queue: Queue,
                                      summarizer: Callable) -> None:
    # we can now store the job in the db
    db_session = api_config.get_db_session()

    # get all the images associated with the survey
    # that have success flag still undefined
    all_images = await db_session.find(criteria={'surveyId': bson.ObjectId(survey_id)},
                                       collection='images',
                                       projection={'imageDetection.success': True,
                                                   #'imageRecommendation.success': ,
                                                   'imageRecommendation': True})

    all_finished = True
    for img in all_images:
        if img['imageDetection']['success'] is not None and img['imageRecommendation']['success'] is not None:
            continue
        else:
            # we found an image that is not finished
            all_finished = False
            break

    if all_finished:
        # if all images have finished then the survey is turned
        # into PENDING_USER_REVIEW

        recommendations = []
        for img in all_images:
            # a list of dicts
            img_recommendations = img['imageRecommendation']['recommendations']

            img_recommendations_list = []

            for rec in img_recommendations:
                img_recommendations_list.append(list(rec.values())[0])

            recommendations.extend(img_recommendations_list)
        job = summarization_queue.enqueue(summarizer,
                                          survey_id,
                                          recommendations)
