class FTPlaceError(Exception):
    """Base exception for FTPlace errors"""
    pass

class TokenError(FTPlaceError):
    """Raised when there's an issue with authentication tokens"""
    pass

class RateLimitError(FTPlaceError):
    """Raised when hitting rate limits"""
    pass