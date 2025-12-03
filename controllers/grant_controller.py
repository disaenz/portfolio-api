import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.grant import GrantCreate, GrantUpdate, GrantResponse, GrantCreateResponse, GrantUpdateResponse
from schemas.error import APIError
from services.grant_service import fetch_grant, fetch_all, add_grant, change_grant

logger = logging.getLogger(__name__)

router = APIRouter(
  tags=["Grant Service"],
  responses={ 
    422: {"model": APIError},
    404: {"model": APIError},
  }
)

@router.get("/", response_model=list[GrantResponse])
async def list_all_grants(db: AsyncSession = Depends(get_db)):
    logger.info("Endpoint list_all_grants called")
    grants = await fetch_all(db)
    logger.info("Fetched %d grants", len(grants))
    return grants


@router.get("/{grant_id}", response_model=GrantResponse)
async def get_one_grant(grant_id: int, db: AsyncSession = Depends(get_db)):
    logger.info("Endpoint get_one_grant called with grant_id=%d", grant_id)
    grant = await fetch_grant(db, grant_id)
    if not grant:
        logger.info("Grant %d not found", grant_id)
        api_err = APIError(error=f"Grant {grant_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=api_err.model_dump())
    logger.info("Returning grant: %s", grant)
    return grant


@router.post("/", response_model=GrantCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_new_grant( grant_in: GrantCreate, db: AsyncSession = Depends(get_db)):
    logger.info("Endpoint create_new_grant called with payload: %s", grant_in.model_dump())
    new_id = await add_grant(db, grant_in)
    logger.info("Created grant with id=%d", new_id)
    return GrantCreateResponse(success=True, id=new_id)


@router.patch("/{grant_id}", response_model=GrantUpdateResponse)
async def update_existing_grant(grant_id: int, grant_in: GrantUpdate, db: AsyncSession = Depends(get_db)):
    logger.info("Endpoint update_existing_grant called with grant_id=%d payload=%s", grant_id, grant_in.model_dump(exclude_unset=True),)
    existing = await fetch_grant(db, grant_id)
    if not existing:
        logger.info("Grant %d not found for update", grant_id)
        api_err = APIError(error=f"Grant {grant_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=api_err.model_dump())
    updated_id = await change_grant(db, grant_id, grant_in)
    logger.info("Updated grant %d", grant_id)
    return GrantUpdateResponse(success=True, id=updated_id)