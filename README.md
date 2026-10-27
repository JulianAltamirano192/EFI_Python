# EFI Python - API de Joyería y Relojería

API REST construida con FastAPI y SQLModel para una tienda de joyería y relojería. Gestiona marcas, categorías y productos, y es la API que consume el frontend en React del EFI de JavaScript.

## Integrantes

- Altamirano, Julian
- Sosa Zabala, Rodrigo Ezequiel

## Modelos

| Modelo | Campos | Relación |
| --- | --- | --- |
| `Marca` | nombre, país | Una marca tiene muchos productos |
| `Categoria` | nombre, descripción | Una categoría tiene muchos productos |
| `Producto` | nombre, descripción, material, precio, stock, imagen | Pertenece a una marca (`marca_id`) y a una categoría (`categoria_id`) |

## Cómo correrlo

Requiere [uv](https://docs.astral.sh/uv/).

```bash
uv sync                      # instala las dependencias
uv run alembic upgrade head  # crea la base joyeria.db con las tablas
uv run python -m src.seed    # carga marcas, categorías y productos de ejemplo
uv run fastapi dev src/main.py
```

La API queda en `http://localhost:8000` y la documentación interactiva en `http://localhost:8000/docs`.

Sin uv: `pip install -r requirements.txt` y los mismos comandos sin `uv run`.

## Endpoints

Cada modelo tiene cinco endpoints: `marcas`, `categorias` y `productos`.

| Método | Ruta | Descripción |
| --- | --- | --- |
| `POST` | `/productos` | Crea un producto (201) |
| `GET` | `/productos?page=1&size=50` | Lista paginada |
| `GET` | `/productos/{id}` | Detalle con datos anidados |
| `PATCH` | `/productos/{id}` | Actualiza solo los campos enviados |
| `DELETE` | `/productos/{id}` | Elimina (204, sin cuerpo) |

- El listado devuelve `{ items, total, page, size, pages }`.
- `GET /productos` acepta además los filtros `marca_id` y `categoria_id`.
- El detalle de un producto incluye su `marca` y su `categoria`; el de una marca o categoría incluye sus `productos`.
- Si el id no existe se responde 404. Crear o editar un producto con una marca o categoría inexistente también da 404.
- No se puede borrar una marca o categoría que todavía tiene productos: se responde 409.
- El `precio` viaja como texto (`"10500.00"`) para no perder decimales.

## Migraciones

Las migraciones están en `alembic/versions/`. Si se cambia un modelo:

```bash
uv run alembic revision --autogenerate -m "descripcion del cambio"
uv run alembic upgrade head
```

## Estructura

```
├── alembic/            # migraciones
├── alembic.ini
├── requirements.txt
└── src/
    ├── main.py         # app, CORS, routers y paginación
    ├── database.py     # engine de SQLite y sesión
    ├── seed.py         # datos de ejemplo
    ├── models/         # modelos y schemas de cada entidad
    └── routers/        # endpoints de cada entidad
```

## Captura de /docs

![Documentación interactiva en /docs](docs/endpoints.png)
