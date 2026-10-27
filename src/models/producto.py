from decimal import Decimal
from typing import Annotated

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

from src.models.categoria import Categoria, CategoriaPublic
from src.models.marca import Marca, MarcaPublic


class ProductoBase(SQLModel):
    nombre: Annotated[str, Field(min_length=1, max_length=150, index=True)]
    descripcion: Annotated[str | None, Field(max_length=1000)] = None
    material: Annotated[str, Field(min_length=1, max_length=60)]
    precio: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
    stock: Annotated[int, Field(ge=0)] = 0
    imagen: Annotated[str | None, Field(max_length=500)] = None
    marca_id: Annotated[int, Field(foreign_key="marca.id")]
    categoria_id: Annotated[int, Field(foreign_key="categoria.id")]


class Producto(ProductoBase, table=True):
    id: Annotated[int | None, Field(primary_key=True)] = None
    marca: Marca = Relationship(back_populates="productos")
    categoria: Categoria = Relationship(back_populates="productos")


class ProductoPublic(ProductoBase):
    id: int


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(SQLModel):
    nombre: Annotated[str | None, Field(min_length=1, max_length=150)] = None
    descripcion: Annotated[str | None, Field(max_length=1000)] = None
    material: Annotated[str | None, Field(min_length=1, max_length=60)] = None
    precio: Annotated[Decimal | None, Field(gt=0, max_digits=10, decimal_places=2)] = None
    stock: Annotated[int | None, Field(ge=0)] = None
    imagen: Annotated[str | None, Field(max_length=500)] = None
    marca_id: int | None = None
    categoria_id: int | None = None

    # Omitted fields keep their value; an explicit null on a NOT NULL column is rejected.
    @field_validator("nombre", "material", "precio", "stock", "marca_id", "categoria_id")
    @classmethod
    def not_null(cls, value):
        if value is None:
            raise ValueError("no puede ser null")
        return value


# Nested schemas live here because they need ProductoPublic, and importing it
# from marca.py or categoria.py would create a circular import.
class ProductoPublicWithMarcaAndCategoria(ProductoPublic):
    marca: MarcaPublic
    categoria: CategoriaPublic


class MarcaPublicWithProductos(MarcaPublic):
    productos: list[ProductoPublic] = []


class CategoriaPublicWithProductos(CategoriaPublic):
    productos: list[ProductoPublic] = []
