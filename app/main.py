from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse
from bson.objectid import ObjectId

from app.routes import user_routes, product_routes
from app.database.connection import db

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="tu_clave_secreta_aqui")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(user_routes.router)
app.include_router(product_routes.router)

@app.on_event("startup")
async def startup_db_client():
    try:
        await db.command("ping")
        print(f"✅ Conectado a la base de datos: {db.name}")
    except Exception as e:
        print(f"❌ Error al conectar con MongoDB: {e}")

@app.get("/", tags=["Inicio"])
async def home(request: Request):
    user_data = None
    user_id = request.session.get("user")
    if user_id:
        user_doc = await db.usuarios.find_one({"_id": ObjectId(user_id)})
        if user_doc:
            user_data = {
                "full_name": user_doc.get("full_name"),
                "email": user_doc.get("email"),
                "rol": user_doc.get("rol")
            }
    return templates.TemplateResponse("home.html", {
        "request": request,
        "user": user_data
    })