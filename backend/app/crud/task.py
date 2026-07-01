from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus
from app.models.user import User, UserRole
from app.schemas.task import TaskCreate, TaskUpdate

SORTABLE_FIELDS = {
    "created_at": Task.created_at,
    "updated_at": Task.updated_at,
    "title": Task.title,
    "status": Task.status,
}


async def create_task(db: AsyncSession, task_in: TaskCreate, owner_id: int) -> Task:
    task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        owner_id=owner_id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_task(db: AsyncSession, task_id: int) -> Task | None:
    return await db.get(Task, task_id)


async def list_tasks(
    db: AsyncSession,
    current_user: User,
    skip: int = 0,
    limit: int = 20,
    status_filter: TaskStatus | None = None,
    search: str | None = None,
    sort: str = "created_at",
) -> tuple[list[Task], int]:
    query = select(Task)
    count_query = select(func.count()).select_from(Task)

    if current_user.role != UserRole.admin:
        query = query.where(Task.owner_id == current_user.id)
        count_query = count_query.where(Task.owner_id == current_user.id)

    if status_filter is not None:
        query = query.where(Task.status == status_filter)
        count_query = count_query.where(Task.status == status_filter)

    if search:
        pattern = f"%{search}%"
        clause = or_(Task.title.ilike(pattern), Task.description.ilike(pattern))
        query = query.where(clause)
        count_query = count_query.where(clause)

    sort_column = SORTABLE_FIELDS.get(sort, Task.created_at)
    query = query.order_by(sort_column.desc()).offset(skip).limit(limit)

    total = (await db.execute(count_query)).scalar_one()
    items = (await db.execute(query)).scalars().all()
    return list(items), total


async def update_task(db: AsyncSession, task: Task, task_in: TaskUpdate) -> Task:
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task: Task) -> None:
    await db.delete(task)
    await db.commit()
