from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

DATABASE_URL = "sqlite:///./joyeria.db"

# SQLite only allows one thread per connection by default; FastAPI serves requests from several.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
