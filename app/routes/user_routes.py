from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import db
from passlib.context import CryptContext
from bson.objectid import ObjectId

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/auth", response_class=HTMLResponse)
async def auth_page(request: Request):
    user_id = request.session.get("user")
    user = None
    if user_id:
        user = await db.usuarios.find_one({"_id": ObjectId(user_id)})
    return templates.TemplateResponse("auth.html", {"request": request, "user": user})

@router.post("/usuarios/registro")
async def registro(
    request: Request,
    tipo_doc: str = Form(...),
    num_doc: str = Form(...),
    full_name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    existing_user = await db.usuarios.find_one({"email": email})
    if existing_user:
        return RedirectResponse("/auth?error=usuario_ya_existe", status_code=303)

    hashed_password = pwd_context.hash(password)
    user = {
        "tipo_doc": tipo_doc,
        "num_doc": num_doc,
        "full_name": full_name,
        "phone": phone,
        "email": email,
        "password": hashed_password,
        "rol": "cliente"
    }
    await db.usuarios.insert_one(user)
    return RedirectResponse("/auth?success=cuenta_creada", status_code=303)

@router.post("/usuarios/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    user = await db.usuarios.find_one({"email": email})
    if user and pwd_context.verify(password, user["password"]):
        request.session["user"] = str(user["_id"])
        return RedirectResponse("/", status_code=303)
    return RedirectResponse("/auth?error=credenciales_invalidas", status_code=303)

@router.get("/usuarios/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)