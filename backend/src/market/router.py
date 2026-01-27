from fastapi import APIRouter, Depends
from sqlalchemy import select

from src.core.config import settings
from src.core.database import SessionDep
from src.market.constants import AssetType
from src.market.models import Asset
from src.market.exceptions import *
from src.market.schemas import *


market_route = APIRouter(
    prefix="/market",
    tags=["Market Data Manipulation"]
)

#----------------------
#      
#----------------------