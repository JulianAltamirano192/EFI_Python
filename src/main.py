from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from src.routers import categorias, marcas, productos

app = FastAPI(
    title="API de Joyería y Relojería",
    description="Gestión de marcas, categorías y productos de una tienda de joyería y relojería.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(marcas.router)
app.include_router(categorias.router)
app.include_router(productos.router)

add_pagination(app)
