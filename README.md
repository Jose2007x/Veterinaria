# Veterinaria Yoyo

## Setup
1. `python -m venv venv && source venv/bin/activate`  
2. `pip install -r requirements.txt`   
3. `uvicorn app.main:app --reload`  

## Funcionalidades
- Registro e inicio de sesión de usuarios  
- Roles (cliente/admin)  
- CRUD de productos (solo admin)  
- Carrito de compras  
- Generación y descarga de factura en PDF  