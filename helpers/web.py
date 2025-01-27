#!/usr/bin/env python3
"""HTTP session utilities with retry, timeout, and logging capabilities."""

from typing import Optional, Set
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# -- Constants -----------------------------------------------------------------------------
DEFAULT_TIMEOUT = 5
DEFAULT_RETRIES = 3
DEFAULT_STATUS_CODES = frozenset([403, 413, 429, 500, 502, 503, 504])
DEFAULT_HTTP_METHODS = frozenset(['GET', 'POST', 'PUT', 'DELETE', 'HEAD'])

# -- Exceptions ---------------------------------------------------------------------------
class SessionConfigError(Exception):
    """Raised when session configuration parameters are invalid."""
    pass

# -- SessionManager ------------------------------------------------------------------------
class SessionManager:
    """Manages HTTP sessions with retry and timeout capabilities."""
    
    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        retry: int = DEFAULT_RETRIES,
        status_codes: Optional[Set[int]] = None,
        http_methods: Optional[Set[str]] = None
    ) -> None:
        """Initialize the session manager.
        
        Args:
            timeout: Request timeout in seconds
            retry: Number of retry attempts
            status_codes: Set of status codes to retry on
            http_methods: Set of HTTP methods to retry
            
        Raises:
            SessionConfigError: If any parameters are invalid
        """
        self._validate_params(timeout, retry)
        self.timeout = timeout
        self.retry = retry
        self.status_codes = status_codes or DEFAULT_STATUS_CODES
        self.http_methods = http_methods or DEFAULT_HTTP_METHODS
        
    @staticmethod
    def _validate_params(timeout: int, retry: int) -> None:
        """Validate initialization parameters.
        
        Args:
            timeout: Request timeout in seconds
            retry: Number of retry attempts
            
        Raises:
            SessionConfigError: If parameters are invalid
        """
        if not isinstance(timeout, int) or timeout <= 0:
            raise SessionConfigError(f"Timeout must be a positive integer, got {timeout}")
        if not isinstance(retry, int) or retry < 0:
            raise SessionConfigError(f"Retry must be a positive integer, got {retry}")

    def create_session(self) -> requests.Session:
        """Create a requests Session with retry and timeout capabilities.
        
        Returns:
            requests.Session: Configured session object
            
        Raises:
            SessionConfigError: If session configuration fails
        """
        try:
            session = requests.Session()
            session.request = lambda method, url, **kwargs: requests.request(method, url, timeout=self.timeout, **kwargs)
            
            max_retries = Retry(
                total=self.retry,
                backoff_factor=0.1,
                allowed_methods=frozenset(self.http_methods),
                status_forcelist=frozenset(self.status_codes),
                respect_retry_after_header=False
            )

            adapter = HTTPAdapter(
                max_retries=max_retries
                )
            
            session.mount('https://', adapter)
            session.mount('http://', adapter)
            
            session.hooks['response'] = [lambda response, *args, **kwargs: response.raise_for_status()]
            return session
        except SessionConfigError as e:
            raise