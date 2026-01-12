from loguru import logger

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException


auth_route = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

#----------------------
#      REGISTER
#----------------------
@auth_route.post('/register')
async def register():
    return