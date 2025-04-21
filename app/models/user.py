from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    nombre: str
    correo: EmailStr
    contrasena: str
    rol: str = "cliente"

class UserLogin(BaseModel):
    correo: EmailStr
    contrasena: str