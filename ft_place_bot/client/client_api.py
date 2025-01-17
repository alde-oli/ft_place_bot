import logging
import requests
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from ft_place_bot.config import APIEndpoints, HTTPStatus, APIConfig
from ft_place_bot.core.exceptions import TokenError
from ft_place_bot.core.models import UserProfile


class FTPlaceAPI:
    def __init__(self, config: APIConfig):
        self.config = config
        self.session = self._setup_session()
        self.logger = self._setup_logger()

    def _setup_session(self) -> requests.Session:
        session = requests.Session()
        retry_strategy = Retry(
            total=self.config.retry_attempts,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.cookies.set('refresh', self.config.refresh_token)
        session.cookies.set('token', self.config.access_token)
        return session

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            )
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _handle_response(self, response: requests.Response) -> requests.Response:
        if response.status_code == HTTPStatus.TOKEN_EXPIRED.value:
            new_token = response.cookies.get('token')
            if not new_token:
                raise TokenError("No new token in response cookies")
            
            self.config.access_token = new_token
            self.session.cookies.set('token', new_token)
            
            return self.session.send(
                response.request.copy(),
                timeout=response.elapsed.total_seconds() * 1.5
            )
        
        response.raise_for_status()
        return response

    def get_profile(self) -> Optional[UserProfile]:
        """Fetches and returns the user profile."""
        try:
            response = self.session.get(
                f"{self.config.base_url}{APIEndpoints.PROFILE.value}"
            )
            response = self._handle_response(response)
            return UserProfile.from_api_response(response.json())
        except Exception as e:
            self.logger.error(f"Failed to get profile: {e}")
            return None

    def get_board(self) -> Optional[Dict[str, Any]]:
        """Fetches and returns the current board state."""
        try:
            response = self.session.get(
                f"{self.config.base_url}{APIEndpoints.BOARD.value}",
                params={'type': 'board'}
            )
            response = self._handle_response(response)
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get board: {e}")
            return None