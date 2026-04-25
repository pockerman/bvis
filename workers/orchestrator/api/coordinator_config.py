from pydantic_settings import BaseSettings
from enum import StrEnum
from abc import abstractmethod
import os

from analysis_coordinator.core_utils.mongodb_session import MongoDBConnection, MongoDBDataController

__all__ = ['APIConfigBase', 'APIConfigDev',
           'APIConfigDeploy', 'get_api_config', 'DBTypeEnum']

# the database session follows the MongoDBSessionProtocol
_db_session = None


class DBTypeEnum(StrEnum):
    DEPLOY = "mongodb-deploy"
    IN_MEMORY_DEV = "mongodb-in-memory-dev"
    REMOTE_DEV = "mongodb-remote-dev"


class APIConfigBase(BaseSettings):
    DEBUG: bool = False
    DB_TYPE: DBTypeEnum = DBTypeEnum.DEPLOY

    @staticmethod
    @abstractmethod
    def get_db_session():
        pass

    @staticmethod
    def nullify_db() -> None:
        global _db_session
        _db_session = None

    @property
    def api_version(self) -> str:
        return "v1.0.0"


class APIConfigDev(APIConfigBase):
    DEBUG: bool = True
    DB_TYPE: DBTypeEnum = DBTypeEnum.REMOTE_DEV

    @staticmethod
    def build_db_session(mongodb_url: str, mongodb_name: str) -> MongoDBDataController:
        global _db_session
        connection = MongoDBConnection(mongodb_url=mongodb_url,
                                       mongodb_name=mongodb_name,
                                       #     **{'directConnection': True}
                                       )
        _db_session = MongoDBDataController(connection)
        return _db_session

    @staticmethod
    def build_in_memory_session() -> MongoDBDataController:
        global _db_session
        from internal.controllers.in_memory_mongodb_session import InMemoryMongoDBDataController
        _db_session = InMemoryMongoDBDataController()
        return _db_session

    def get_db_session(self):

        mongodb_url = os.getenv("DBHOST", None)

        if mongodb_url is None:
            raise ValueError("Missing environment variable DBHOST")

        mongodb_name = os.getenv("DBNAME", None)

        if mongodb_name is None:
            raise ValueError("Missing environment variable DBNAME")

        global _db_session
        if _db_session is None:
            if DBTypeEnum(self.DB_TYPE) == DBTypeEnum.REMOTE_DEV:

                # use the name of the service as this is defined
                # in the docker-compose file. Use localhost:30001 for accessing
                # the mongodb container from outside the containers
                # mongodb_url = "mongodb://host.docker.internal:27017"  # "mongodb://db:27017"
                # mongodb_name = "mir-db"
                connection = MongoDBConnection(mongodb_url=mongodb_url,
                                               mongodb_name=mongodb_name,
                                               #     **{'directConnection': True}
                                               )
                _db_session = MongoDBDataController(connection)
                return _db_session
            else:
                # assume an in memory database keep it here so we don't have dependency in production
                APIConfigDev.build_in_memory_session()
                return _db_session
        else:
            return _db_session


class APIConfigDeploy(APIConfigBase):
    """API configuration settings for deployment
    Currently mirrors the APIConfigBase

    """

    @staticmethod
    def get_db_session():

        mongodb_url = os.getenv("DBHOST", None)

        if mongodb_url is None:
            raise ValueError("Missing environment variable DBHOST")

        mongodb_name = os.getenv("DBNAME", None)

        if mongodb_name is None:
            raise ValueError("Missing environment variable DBNAME")

        global _db_session

        if _db_session is None:
            # use the name of the service as this is defined
            # in the docker-compose file. Use localhost:30001 for accessing
            # the mongodb container from outside the containers
            # mongodb_url = "mongodb://host.docker.internal:27017"  # "mongodb://db:27017"
            # mongodb_name = "mir-db"
            connection = MongoDBConnection(mongodb_url=mongodb_url,
                                           mongodb_name=mongodb_name,
                                           #     **{'directConnection': True}
                                           )
            _db_session = MongoDBDataController(connection)
        return _db_session


# the instance to inject in the container
_api_config: APIConfigBase | None = None  # APIConfigDeploy()


# accessors
def get_api_config() -> APIConfigBase:
    global _api_config

    if _api_config:
        return _api_config
    else:

        debug = os.environ.get('DEBUG', None)

        if debug == '0' or not debug:
            _api_config = APIConfigDeploy()
        else:
            _api_config = APIConfigDev()

        return _api_config
