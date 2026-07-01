from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models here so Alembic's autogenerate can discover them via Base.metadata
from app.models import user, task  # noqa: E402,F401
