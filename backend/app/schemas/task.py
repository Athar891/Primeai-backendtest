from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    status: TaskStatus = TaskStatus.todo

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"title": "Finish Assignment", "description": "Wrap up the backend intern task", "status": "todo"}
        }
    )


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    status: TaskStatus | None = None

    model_config = ConfigDict(
        json_schema_extra={"example": {"title": "Finish Assignment", "status": "in_progress"}}
    )


class TaskRead(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Finish Assignment",
                "description": "Wrap up the backend intern task",
                "status": "todo",
                "owner_id": 1,
                "created_at": "2026-07-01T12:00:00Z",
                "updated_at": "2026-07-01T12:00:00Z",
            }
        },
    )


class TaskListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[TaskRead]
