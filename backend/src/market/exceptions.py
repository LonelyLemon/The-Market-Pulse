"""HTTP exceptions for the market module."""

from fastapi import HTTPException, status


class AssetNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")


class AssetAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail="Asset with this symbol already exists")


class MarketDataUnavailable(HTTPException):
    def __init__(self, msg: str = "Market data unavailable"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=msg)


class InvalidTimeframe(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid timeframe. Valid: 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo",
        )
