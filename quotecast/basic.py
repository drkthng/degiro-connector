import logging
import quotecast.utilities as utilities
import urllib3

from quotecast.constants.headers import Headers
from quotecast.models.session_storage import SessionStorage
from quotecast.pb.quotecast_pb2 import Quotecast, Request
from typing import Union

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Basic:
    """ Tools to consume Degiro's QuoteCast API.
    
    Same operations then "utilities" but with automatic management of :
        * requests.Session
        * logging.Logger

    This class should be threadsafe.
    """

    @staticmethod
    def build_session_storage()->SessionStorage:
        return SessionStorage(
            headers=Headers.get_headers(),
            hooks=None,
        )

    @property
    def user_token(self)->int:
        return self._user_token

    @property
    def session_storage(self)->SessionStorage:
        return self._session_storage

    @session_storage.setter
    def session_storage(self, session_storage:SessionStorage):
        self._session_storage = session_storage

    def __init__(self, user_token:int, session_storage=None):
        if session_storage is None:
            session_storage = self.build_session_storage()

        self._logger = logging.getLogger(self.__module__)
        self._user_token = user_token
        self._session_storage = session_storage

    def fetch_data(self, session_id:str)->Quotecast:
        logger = self._logger
        session = self._session_storage.session

        return utilities.fetch_data(
            session_id=session_id,
            session=session,
            logger=logger,
        )

    def get_session_id(self)->str:
        logger = self._logger
        user_token = self._user_token
        session = self._session_storage.session

        return utilities.get_session_id(
            user_token=user_token,
            session=session,
            logger=logger
        )

    def subscribe(self, request:Request, session_id:str)->bool:
        logger = self._logger
        session = self._session_storage.session
        
        return utilities.subscribe(
            request=request,
            session_id=session_id,
            session=session,
            logger=logger,
        )

if __name__ == '__main__':
    # IMPORTATIONS
    import json
    import logging
    import time

    # SETUP LOGS
    logging.basicConfig(level=logging.DEBUG)

    # SETUP CREDENTIALS    
    with open('config/subscription_request.json') as config_file:
        config = json.load(config_file)
    user_token = config['user_token']

    # SETUP API
    basic = Basic(user_token=user_token)

    # SETUP REQUEST
    request = Request()
    request.subscriptions['360015751'].extend([
        'LastDate',
        'LastTime',
        'LastPrice',
        'LastVolume',
    ])

    # CONNECT
    session_id = basic.get_session_id()

    # SUBSCRIBE
    basic.subscribe(request=request, session_id=session_id)

    # FETCH DATA
    time.sleep(1)
    basic.fetch_data(session_id=session_id)