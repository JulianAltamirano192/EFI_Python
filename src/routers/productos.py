from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import Session, select

from src.database import SessionDep, save_changes
from src.models import (
    Producto,
    ProductoCreate,
    ProductoNested,
    ProductoPublic,
    ProductoUpdate,
)
from src.routers.categorias import get_categoria_or_404
from src.routers.marcas import get_marca_or_404

router = APIRouter(prefix="/productos", tags=["Productos"])

NOT_FOUND_RESPONSE = {
    404: {
        "description": "Producto, marca o categoría no encontrada",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Producto no encontrado",
                }
            }
        },
    },
}

def get_producto_or_404(session: Session, producto_id: int) -> Producto:
    producto = session.get(Producto, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


def check_relations(session: Session, data: dict) -> None:
    # SQLite does not enforce foreign keys by default, so the referenced rows are checked here.
    if data.get("marca_id") is not None:
        get_marca_or_404(session, data["marca_id"])
    if data.get("categoria_id") is not None:
        get_categoria_or_404(session, data["categoria_id"])


@router.post(
    "",
    response_model=ProductoPublic,
    status_code=status.HTTP_201_CREATED,
    responses=NOT_FOUND_RESPONSE,
)
def create_producto(producto: ProductoCreate, session: SessionDep):
    check_relations(session, producto.model_dump())
    db_producto = Producto.model_validate(producto)
    session.add(db_producto)
    session.commit()
    session.refresh(db_producto)
    return db_producto


@router.get("", response_model=Page[ProductoPublic])
def list_productos(
    session: SessionDep,
    marca_id: Annotated[int | None, Query(description="Filtrar por marca_id")] = None,
    categoria_id: Annotated[int | None, Query(description="Filtrar por categoria_id")] = None,
):
    query = select(Producto).order_by(Producto.id)
    if marca_id is not None:
        query = query.where(Producto.marca_id == marca_id)
    if categoria_id is not None:
        query = query.where(Producto.categoria_id == categoria_id)
    return paginate(session, query)


@router.get(
    "/{producto_id}",
    response_model=ProductoNested,
    responses=NOT_FOUND_RESPONSE,
)
def read_producto(
    producto_id: Annotated[int, Path(gt=0, description="Id del producto. >0")],
    session: SessionDep,
):
    return get_producto_or_404(session, producto_id)


# PUT replaces the whole resource: omitted optional fields go back to their defaults.
@router.put("/{producto_id}", response_model=ProductoPublic, responses=NOT_FOUND_RESPONSE)
def replace_producto(
    producto_id: Annotated[int, Path(gt=0, description="Id del producto. >0")],
    producto: ProductoCreate,
    session: SessionDep,
):
    db_producto = get_producto_or_404(session, producto_id)
    data = producto.model_dump()
    check_relations(session, data)
    return save_changes(session, db_producto, data)


@router.patch("/{producto_id}", response_model=ProductoPublic, responses=NOT_FOUND_RESPONSE)
def update_producto(
    producto_id: Annotated[int, Path(gt=0, description="Id del producto. >0")],
    producto: ProductoUpdate,
    session: SessionDep,
):
    db_producto = get_producto_or_404(session, producto_id)
    data = producto.model_dump(exclude_unset=True)
    check_relations(session, data)
    return save_changes(session, db_producto, data)


@router.delete(
    "/{producto_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND_RESPONSE
)
def delete_producto(
    producto_id: Annotated[int, Path(gt=0, description="Id del producto. >0")],
    session: SessionDep,
):
    db_producto = get_producto_or_404(session, producto_id)
    session.delete(db_producto)
    session.commit()
