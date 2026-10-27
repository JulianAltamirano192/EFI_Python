from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import Session, select

from src.database import SessionDep
from src.models import Marca, MarcaCreate, MarcaNested, MarcaPublic, MarcaUpdate

router = APIRouter(prefix="/marcas", tags=["Marcas"])

NOT_FOUND_RESPONSE = {
    404: {
        "description": "Marca no encontrada",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Marca no encontrada",
                }
            }
        },
    },
}
NOT_FOUND = NOT_FOUND_RESPONSE


def get_marca_or_404(session: Session, marca_id: int) -> Marca:
    marca = session.get(Marca, marca_id)
    if not marca:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    return marca


@router.post("", response_model=MarcaPublic, status_code=status.HTTP_201_CREATED)
def create_marca(marca: MarcaCreate, session: SessionDep):
    db_marca = Marca.model_validate(marca)
    session.add(db_marca)
    session.commit()
    session.refresh(db_marca)
    return db_marca


@router.get("", response_model=Page[MarcaPublic])
def list_marcas(session: SessionDep):
    return paginate(session, select(Marca).order_by(Marca.id))


@router.get("/{marca_id}", response_model=MarcaNested, responses=NOT_FOUND_RESPONSE)
def read_marca(
    marca_id: Annotated[int, Path(gt=0, description="Id de la marca. >0")],
    session: SessionDep,
):
    return get_marca_or_404(session, marca_id)


@router.put("/{marca_id}", response_model=MarcaPublic, responses=NOT_FOUND_RESPONSE)
@router.patch("/{marca_id}", response_model=MarcaPublic, responses=NOT_FOUND_RESPONSE)
def update_marca(
    marca_id: Annotated[int, Path(gt=0, description="Id de la marca. >0")],
    marca: MarcaUpdate,
    session: SessionDep,
):
    db_marca = get_marca_or_404(session, marca_id)
    db_marca.sqlmodel_update(marca.model_dump(exclude_unset=True))
    session.add(db_marca)
    session.commit()
    session.refresh(db_marca)
    return db_marca


@router.delete(
    "/{marca_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**NOT_FOUND_RESPONSE, 409: {"description": "La marca tiene productos asociados"}},
)
def delete_marca(
    marca_id: Annotated[int, Path(gt=0, description="Id de la marca. >0")],
    session: SessionDep,
):
    db_marca = get_marca_or_404(session, marca_id)
    # SQLite does not enforce foreign keys by default, so orphaned productos must be prevented here.
    if db_marca.productos:
        raise HTTPException(status_code=409, detail="La marca tiene productos asociados")
    session.delete(db_marca)
    session.commit()
