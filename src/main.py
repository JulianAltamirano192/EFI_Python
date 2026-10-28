import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from src.routers import categorias, marcas, productos

app = FastAPI(
    title="API de Joyería y Relojería",
    description="Gestión de marcas, categorías y productos de una tienda de joyería y relojería.",
    version="1.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5500",  # Live Server (entorno de pruebas del docente)
        # Deployed frontend, e.g. https://efi-javascript.vercel.app
        *filter(None, [os.getenv("FRONTEND_URL")]),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(marcas.router)
app.include_router(categorias.router)
app.include_router(productos.router)

add_pagination(app)
