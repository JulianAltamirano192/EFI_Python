"""Loads sample data. Run after `alembic upgrade head` with `python -m src.seed`."""

from decimal import Decimal

from sqlmodel import Session, select

from src.database import engine
from src.models import Categoria, Marca, Producto

MARCAS = [
    ("Rolex", "Suiza"),
    ("Cartier", "Francia"),
    ("Tiffany & Co.", "Estados Unidos"),
    ("Pandora", "Dinamarca"),
    ("Casio", "Japón"),
]

CATEGORIAS = [
    ("Anillos", "Anillos de compromiso, alianzas y anillos de moda."),
    ("Collares", "Collares, cadenas y colgantes."),
    ("Relojes de pulsera", "Relojes analógicos, automáticos y digitales."),
    ("Pulseras", "Pulseras rígidas, de eslabones y de dijes."),
    ("Aros", "Aros abridores, argollas y colgantes."),
]

# (nombre, descripcion, material, precio, stock, marca, categoria)
PRODUCTOS = [
    ("Submariner Date", "Reloj de buceo automático, resistente a 300 m.", "Acero", "10500.00", 3, "Rolex", "Relojes de pulsera"),
    ("Datejust 36", "Clásico con fecha y bisel estriado.", "Acero y oro", "9800.00", 2, "Rolex", "Relojes de pulsera"),
    ("Love Bracelet", "Pulsera rígida con tornillos grabados.", "Oro amarillo", "7200.00", 4, "Cartier", "Pulseras"),
    ("Trinity Ring", "Tres aros entrelazados en tres tonos de oro.", "Oro", "1850.00", 6, "Cartier", "Anillos"),
    ("Tank Must", "Reloj rectangular de cuarzo con correa de cuero.", "Acero", "3100.00", 5, "Cartier", "Relojes de pulsera"),
    ("Solitario Tiffany Setting", "Anillo de compromiso con diamante de 0,5 ct.", "Platino", "12500.00", 1, "Tiffany & Co.", "Anillos"),
    ("Return to Tiffany Heart Tag", "Collar con dije de corazón grabado.", "Plata 925", "420.00", 10, "Tiffany & Co.", "Collares"),
    ("Aros HardWear", "Aros de eslabones gruesos.", "Plata 925", "850.00", 7, "Tiffany & Co.", "Aros"),
    ("Pulsera Moments", "Pulsera de cadena con cierre de corazón para dijes.", "Plata 925", "95.00", 20, "Pandora", "Pulseras"),
    ("Collar Corazón Brillante", "Cadena con colgante de corazón y circonitas.", "Plata 925", "110.00", 15, "Pandora", "Collares"),
    ("Aros Estrella", "Aros abridores con forma de estrella.", "Plata 925", "65.00", 25, "Pandora", "Aros"),
    ("G-Shock GA-2100", "Reloj digital y analógico, resistente a golpes.", "Resina", "120.00", 12, "Casio", "Relojes de pulsera"),
    ("Vintage A168", "Reloj digital retro con luz y alarma.", "Acero", "60.00", 18, "Casio", "Relojes de pulsera"),
]


def seed(session: Session) -> bool:
    """Inserts the sample data once. Returns False if the database already had marcas."""
    if session.exec(select(Marca)).first():
        return False

    marcas = {nombre: Marca(nombre=nombre, pais=pais) for nombre, pais in MARCAS}
    categorias = {nombre: Categoria(nombre=nombre, descripcion=d) for nombre, d in CATEGORIAS}
    session.add_all([*marcas.values(), *categorias.values()])

    for nombre, descripcion, material, precio, stock, marca, categoria in PRODUCTOS:
        slug = nombre.lower().replace(" ", "-")
        session.add(
            Producto(
                nombre=nombre,
                descripcion=descripcion,
                material=material,
                precio=Decimal(precio),
                stock=stock,
                imagen=f"https://picsum.photos/seed/{slug}/600/600",
                marca=marcas[marca],
                categoria=categorias[categoria],
            )
        )
    session.commit()
    return True


if __name__ == "__main__":
    with Session(engine) as session:
        if seed(session):
            print(f"Cargados {len(MARCAS)} marcas, {len(CATEGORIAS)} categorías y {len(PRODUCTOS)} productos.")
        else:
            print("La base ya tiene datos, no se cargó nada.")
