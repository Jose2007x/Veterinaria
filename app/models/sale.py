from pydantic import BaseModel
from typing import List

class Producto(BaseModel):
    nombre: str
    cantidad: int
    precio: float

class Venta(BaseModel):
    cliente_nombre: str
    productos: List[Producto]
    total: float