from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from bson.objectid import ObjectId
from app.database import db
from app.utils.pdf_generator import create_invoice_pdf
import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

carrito = []

@router.get("/productos", response_class=HTMLResponse)
async def listar_productos(request: Request):
    prods = await db.productos.find().to_list(100)
    user = None
    user_id = request.session.get("user")
    if user_id:
        u = await db.usuarios.find_one({"_id": ObjectId(user_id)})
        if u:
            user = {"full_name": u.get("full_name"), "rol": u.get("rol")}
    return templates.TemplateResponse("productos.html", {
        "request": request,
        "productos": prods,
        "user": user
    })

@router.get("/productos/agregar", response_class=HTMLResponse)
async def form_agregar_producto(request: Request):
    return templates.TemplateResponse("agregar_producto.html", {"request": request})

@router.post("/productos/agregar")
async def agregar_producto(request: Request, nombre: str = Form(...), descripcion: str = Form(...),
                           valor_unitario: float = Form(...), imagen: str = Form(...), stock: int = Form(...)):
    if stock > 30:
        return templates.TemplateResponse("agregar_producto.html", {
            "request": request,
            "error": "El stock no puede ser mayor a 30 unidades."
        })

    await db.productos.insert_one({
        "nombre": nombre,
        "descripcion": descripcion,
        "valor_unitario": valor_unitario,
        "imagen": imagen,
        "stock": stock
    })
    return RedirectResponse("/productos", status_code=303)

@router.get("/productos/editar/{id}", response_class=HTMLResponse)
async def form_editar_producto(id: str, request: Request):
    producto = await db.productos.find_one({"_id": ObjectId(id)})
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return templates.TemplateResponse("editar_producto.html", {"request": request, "producto": producto})

@router.post("/productos/editar/{id}")
async def editar_producto(id: str, nombre: str = Form(...), descripcion: str = Form(...),
                          valor_unitario: float = Form(...), imagen: str = Form(...), stock: int = Form(...)):
    if stock > 30:
        raise HTTPException(status_code=400, detail="El stock no puede ser mayor a 30 unidades.")

    await db.productos.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "nombre": nombre,
            "descripcion": descripcion,
            "valor_unitario": valor_unitario,
            "imagen": imagen,
            "stock": stock
        }}
    )
    return RedirectResponse("/productos", status_code=303)

@router.post("/productos/eliminar/{id}")
async def eliminar_producto(id: str):
    await db.productos.delete_one({"_id": ObjectId(id)})
    return RedirectResponse("/productos", status_code=303)

@router.post("/carrito/agregar")
async def agregar_al_carrito(id: str = Form(...), cantidad: int = Form(...)):
    prod = await db.productos.find_one({"_id": ObjectId(id)})
    if prod:
        stock_disponible = prod.get("stock", 0)
        if stock_disponible >= cantidad:
            for item in carrito:
                if item["_id"] == prod["_id"]:
                    if item["cantidad"] + cantidad <= stock_disponible:
                        item["cantidad"] += cantidad
                    break
            else:
                carrito.append({**prod, "cantidad": cantidad})
    return RedirectResponse("/productos", status_code=303)

@router.post("/carrito/eliminar")
async def eliminar_del_carrito(id: str = Form(...)):
    global carrito
    carrito = [item for item in carrito if str(item["_id"]) != id]
    return RedirectResponse("/carrito", status_code=303)

@router.get("/carrito", response_class=HTMLResponse)
async def ver_carrito(request: Request):
    total = sum(item["cantidad"] * item["valor_unitario"] for item in carrito)
    user = None
    user_id = request.session.get("user")
    if user_id:
        u = await db.usuarios.find_one({"_id": ObjectId(user_id)})
        if u:
            user = {"full_name": u.get("full_name")}
    return templates.TemplateResponse("carrito.html", {
        "request": request,
        "carrito": carrito,
        "total": total,
        "user": user,
        "user_id": user_id
    })

@router.post("/comprar")
async def comprar(request: Request, cliente_id: str = Form(...)):
    venta_items = []
    for item in carrito:
        producto_id = item["_id"]
        cantidad_vendida = item["cantidad"]
        producto_actual = await db.productos.find_one({"_id": ObjectId(producto_id)})
        if producto_actual and producto_actual.get("stock", 0) >= cantidad_vendida:
            nuevo_stock = producto_actual["stock"] - cantidad_vendida
            await db.productos.update_one({"_id": ObjectId(producto_id)}, {"$set": {"stock": nuevo_stock}})
            venta_items.append({
                "producto_id": producto_id,
                "nombre": item["nombre"],
                "cantidad": cantidad_vendida,
                "valor_unitario": item["valor_unitario"],
                "subtotal": item["cantidad"] * item["valor_unitario"]
            })
        else:
            return templates.TemplateResponse("carrito.html", {
                "request": request,
                "carrito": carrito,
                "total": sum(i["cantidad"] * i["valor_unitario"] for i in carrito),
                "error": f"No hay suficiente stock para el producto: {item['nombre']}"
            })

    venta = {
        "cliente_id": ObjectId(cliente_id),
        "items": venta_items,
        "total": sum(i["subtotal"] for i in venta_items),
        "fecha": datetime.datetime.now()
    }
    result = await db.ventas.insert_one(venta)
    carrito.clear()
    pdf_path = await create_invoice_pdf(venta, result.inserted_id)
    return FileResponse(pdf_path, filename="factura.pdf", media_type="application/pdf")

@router.get("/inventario", response_class=HTMLResponse)
async def reporte_inventario(request: Request):
    user_id = request.session.get("user")
    if not user_id:
        return RedirectResponse("/", status_code=303)

    usuario = await db.usuarios.find_one({"_id": ObjectId(user_id)})
    if not usuario or usuario.get("rol") != "admin":
        raise HTTPException(status_code=403, detail="Acceso no autorizado")

    productos = await db.productos.find().to_list(100)
    return templates.TemplateResponse("reporte_inventario.html", {
        "request": request,
        "productos": productos,
        "user": {
            "full_name": usuario.get("full_name"),
            "rol": usuario.get("rol")
        }
    })