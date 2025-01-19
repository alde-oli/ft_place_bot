import logging
import sys
from typing import Any, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util import Retry

from ft_place_bot.config import APIConfig, APIEndpoints, HTTPStatus
from ft_place_bot.core import TokenError, UserProfile


class AuthenticationError(Exception):
    pass


class FTPlaceAPI:
    def __init__(self, config: APIConfig):
        self.config = config
        self.logger = self._setup_logger()
        self.max_token_retries = 3
        self.session: Optional[requests.Session] = None
        self.session = self._setup_session()  # Then create the session

    def _setup_session(self) -> requests.Session:
        session = requests.Session()
        retry_strategy = Retry(
            total=self.config.retry_attempts, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        session.cookies.set("token", self.config.access_token)
        session.cookies.set("refresh", self.config.refresh_token)

        return session

    def _update_session_tokens(self, access_token: str, refresh_token: str) -> None:
        """Update both tokens in session cookies"""
        if self.session is None:
            raise RuntimeError("Session not initialized")

        self.session.cookies.set("token", access_token)
        self.session.cookies.set("refresh", refresh_token)
        self.config.access_token = access_token
        self.config.refresh_token = refresh_token

    def _extract_tokens_from_headers(self, headers: Any) -> Tuple[Optional[str], Optional[str]]:
        """Extract new tokens from Set-Cookie headers"""
        new_access = None
        new_refresh = None

        cookies = headers.get("Set-Cookie", "").split(", ")
        for cookie in cookies:
            if cookie.startswith("token="):
                new_access = cookie.split(";")[0][6:]  # Remove "token=" prefix
            elif cookie.startswith("refresh="):
                new_refresh = cookie.split(";")[0][8:]  # Remove "refresh=" prefix

        return new_access, new_refresh

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def handle_response(self, response: requests.Response, retry_count: int = 0) -> Tuple[requests.Response, bool]:
        """
        Handle API response with token refresh logic.
        Returns (response, needs_retry)
        """
        if response.status_code == HTTPStatus.TOKEN_EXPIRED.value:  # Token needs refresh
            if retry_count >= self.max_token_retries:
                raise AuthenticationError("Max token refresh attempts reached")

            self.logger.info("Token refresh required")

            # Extract new tokens from Set-Cookie headers
            new_access, new_refresh = self._extract_tokens_from_headers(response.headers)

            if new_access and new_refresh:
                self._update_session_tokens(new_access, new_refresh)
                return response, True  # Indicate that request should be retried
            raise AuthenticationError("Failed to get new tokens from response")

        response.raise_for_status()
        return response, False

    def _make_request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        """Make a request with retry logic for token refresh"""
        if self.session is None:
            raise RuntimeError("Session not initialized")
        retry_count = 0
        while retry_count < self.max_token_retries:
            response = self.session.request(method, url, **kwargs)
            try:
                response, needs_retry = self.handle_response(response, retry_count)
                if not needs_retry:
                    return response
                retry_count += 1
            except AuthenticationError as e:
                raise AuthenticationError(f"Authentication failed: {str(e)}") from e
            except RequestException as e:
                raise RequestException(f"Request failed: {str(e)}") from e

        raise AuthenticationError("Max token refresh attempts reached")

    def get_profile(self) -> Optional[UserProfile]:
        """Fetches and returns the user profile."""
        try:
            response = self._make_request("GET", f"{self.config.base_url}{APIEndpoints.PROFILE.value}")
            return UserProfile.from_api_response(response.json())

        except AuthenticationError:
            self.logger.critical("Authentication failed - unable to refresh tokens. Exiting program...")
            sys.exit(1)
        except (RequestException, TokenError, ValueError) as e:
            self.logger.error("Failed to get profile: %s", str(e))
            return None

    def get_board(self) -> Optional[Any]:
        """Fetches and returns the current board state."""
        try:
            response = self._make_request(
                "GET", f"{self.config.base_url}{APIEndpoints.BOARD.value}", params={"type": "board"}
            )
            return response.json()

        except AuthenticationError:
            self.logger.critical("Authentication failed - unable to refresh tokens. Exiting program...")
            sys.exit(1)
        except (RequestException, TokenError, ValueError) as e:
            self.logger.error("Failed to get board: %s", str(e))
            return None
