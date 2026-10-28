import os
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

# Local development uses SQLite; production (Vercel) sets DATABASE_URL to Postgres.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./joyeria.db")
# Neon gives postgres:// or postgresql://; SQLAlchemy needs the psycopg (v3) driver named explicitly.
if DATABASE_URL.startswith(("postgres://", "postgresql://")):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL.split("://", 1)[1]

# SQLite only allows one thread per connection by default; FastAPI serves requests from several.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def save_changes(session: Session, db_obj, data: dict):
    db_obj.sqlmodel_update(data)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
