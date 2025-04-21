from pydantic import BaseModel
from typing import Optional

class Producto(BaseModel):
    nombre: str
    descripcion: str
    cantidad: int
    imagen_url: Optional[str] = None
    precio: float