from typing import TYPE_CHECKING, Annotated

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.producto import Producto


class CategoriaBase(SQLModel):
    nombre: Annotated[str, Field(min_length=1, max_length=60, index=True)]
    descripcion: Annotated[str | None, Field(max_length=255)] = None


class Categoria(CategoriaBase, table=True):
    id: Annotated[int | None, Field(primary_key=True)] = None
    productos: list["Producto"] = Relationship(back_populates="categoria")


class CategoriaPublic(CategoriaBase):
    id: int


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(SQLModel):
    nombre: Annotated[str | None, Field(min_length=1, max_length=60)] = None
    descripcion: Annotated[str | None, Field(max_length=255)] = None

    # Omitted fields keep their value; an explicit null on a NOT NULL column is rejected.
    @field_validator("nombre")
    @classmethod
    def not_null(cls, value):
        if value is None:
            raise ValueError("no puede ser null")
        return value
