from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import Session, select

from src.database import SessionDep
from src.models import (
    Categoria,
    CategoriaCreate,
    CategoriaNested,
    CategoriaPublic,
    CategoriaUpdate,
)

router = APIRouter(prefix="/categorias", tags=["Categorías"])

NOT_FOUND_RESPONSE = {
    404: {
        "description": "Categoría no encontrada",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Categoría no encontrada",
                }
            }
        },
    },
}
NOT_FOUND = NOT_FOUND_RESPONSE


def get_categoria_or_404(session: Session, categoria_id: int) -> Categoria:
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria


@router.post("", response_model=CategoriaPublic, status_code=status.HTTP_201_CREATED)
def create_categoria(categoria: CategoriaCreate, session: SessionDep):
    db_categoria = Categoria.model_validate(categoria)
    session.add(db_categoria)
    session.commit()
    session.refresh(db_categoria)
    return db_categoria


@router.get("", response_model=Page[CategoriaPublic])
def list_categorias(session: SessionDep):
    return paginate(session, select(Categoria).order_by(Categoria.id))


@router.get(
    "/{categoria_id}", response_model=CategoriaNested, responses=NOT_FOUND_RESPONSE
)
def read_categoria(
    categoria_id: Annotated[int, Path(gt=0, description="Id de la categoría. >0")],
    session: SessionDep,
):
    return get_categoria_or_404(session, categoria_id)


@router.put("/{categoria_id}", response_model=CategoriaPublic, responses=NOT_FOUND_RESPONSE)
@router.patch("/{categoria_id}", response_model=CategoriaPublic, responses=NOT_FOUND_RESPONSE)
def update_categoria(
    categoria_id: Annotated[int, Path(gt=0, description="Id de la categoría. >0")],
    categoria: CategoriaUpdate,
    session: SessionDep,
):
    db_categoria = get_categoria_or_404(session, categoria_id)
    db_categoria.sqlmodel_update(categoria.model_dump(exclude_unset=True))
    session.add(db_categoria)
    session.commit()
    session.refresh(db_categoria)
    return db_categoria


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**NOT_FOUND_RESPONSE, 409: {"description": "La categoría tiene productos asociados"}},
)
def delete_categoria(
    categoria_id: Annotated[int, Path(gt=0, description="Id de la categoría. >0")],
    session: SessionDep,
):
    db_categoria = get_categoria_or_404(session, categoria_id)
    # SQLite does not enforce foreign keys by default, so orphaned productos must be prevented here.
    if db_categoria.productos:
        raise HTTPException(status_code=409, detail="La categoría tiene productos asociados")
    session.delete(db_categoria)
    session.commit()
