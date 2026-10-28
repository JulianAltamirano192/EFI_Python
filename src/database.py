import os
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

# Production (Coolify) points DATABASE_URL at a SQLite file inside a persistent volume.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./joyeria.db")

# SQLite only allows one thread per connection by default; FastAPI serves requests from several.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


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
