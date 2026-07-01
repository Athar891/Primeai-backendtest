from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.crud.user import list_users
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["Admin"])


@router.get("", response_model=list[UserRead])
async def list_users_endpoint(db: AsyncSession = Depends(get_db), _admin=Depends(require_admin)):
    return await list_users(db)
