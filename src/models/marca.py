from typing import TYPE_CHECKING, Annotated

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.producto import Producto


class MarcaBase(SQLModel):
    nombre: Annotated[str, Field(min_length=1, max_length=100, index=True)]
    pais: Annotated[str | None, Field(max_length=60)] = None


class Marca(MarcaBase, table=True):
    id: Annotated[int | None, Field(primary_key=True)] = None
    productos: list["Producto"] = Relationship(back_populates="marca")


class MarcaPublic(MarcaBase):
    id: int


class MarcaCreate(MarcaBase):
    pass


class MarcaUpdate(SQLModel):
    nombre: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    pais: Annotated[str | None, Field(max_length=60)] = None
