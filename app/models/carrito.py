from pydantic import BaseModel

class ProductoCarrito(BaseModel):
    id: int
    nombre: str
    precio: float
    cantidad: int
    total: float