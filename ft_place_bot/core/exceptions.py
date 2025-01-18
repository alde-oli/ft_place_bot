class FTPlaceError(Exception):
    """Base exception for FTPlace errors"""


class TokenError(FTPlaceError):
    """Raised when there's an issue with authentication tokens"""


class RateLimitError(FTPlaceError):
    """Raised when hitting rate limits"""
