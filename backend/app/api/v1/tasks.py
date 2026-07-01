from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.crud.task import create_task, delete_task, get_task, list_tasks, update_task
from app.models.task import TaskStatus
from app.models.user import User, UserRole
from app.schemas.task import TaskCreate, TaskListResponse, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def _ensure_can_access(task, current_user: User) -> None:
    if current_user.role != UserRole.admin and task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this task")


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task_endpoint(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_task(db, task_in, owner_id=current_user.id)


@router.get("", response_model=TaskListResponse)
async def list_tasks_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None, max_length=255),
    sort: str = Query(default="created_at"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await list_tasks(
        db, current_user, skip=skip, limit=limit, status_filter=status_filter, search=search, sort=sort
    )
    return TaskListResponse(total=total, skip=skip, limit=limit, items=items)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task_endpoint(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    _ensure_can_access(task, current_user)
    return task


@router.put("/{task_id}", response_model=TaskRead)
async def update_task_endpoint(
    task_id: int,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    _ensure_can_access(task, current_user)
    return await update_task(db, task, task_in)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_endpoint(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    _ensure_can_access(task, current_user)
    await delete_task(db, task)
