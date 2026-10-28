from src.models.categoria import CategoriaPublic
from src.models.marca import MarcaPublic
from src.models.producto import ProductoPublic


class MarcaNested(MarcaPublic):
    productos: list[ProductoPublic] = []


class CategoriaNested(CategoriaPublic):
    productos: list[ProductoPublic] = []


class ProductoNested(ProductoPublic):
    marca: MarcaPublic
    categoria: CategoriaPublic
