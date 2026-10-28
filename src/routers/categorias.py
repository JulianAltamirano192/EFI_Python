from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import Session, select

from src.database import SessionDep, save_changes
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


# PUT replaces the whole resource: omitted optional fields go back to their defaults.
@router.put("/{categoria_id}", response_model=CategoriaPublic, responses=NOT_FOUND_RESPONSE)
def replace_categoria(
    categoria_id: Annotated[int, Path(gt=0, description="Id de la categoría. >0")],
    categoria: CategoriaCreate,
    session: SessionDep,
):
    return save_changes(session, get_categoria_or_404(session, categoria_id), categoria.model_dump())


@router.patch("/{categoria_id}", response_model=CategoriaPublic, responses=NOT_FOUND_RESPONSE)
def update_categoria(
    categoria_id: Annotated[int, Path(gt=0, description="Id de la categoría. >0")],
    categoria: CategoriaUpdate,
    session: SessionDep,
):
    return save_changes(session, get_categoria_or_404(session, categoria_id), categoria.model_dump(exclude_unset=True))


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
