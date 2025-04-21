from fpdf import FPDF
import os
from datetime import datetime
from bson.objectid import ObjectId
from app.database import db

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 16)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, "Veterinaria Yoyo - Factura de Venta", 0, 1, "C")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "C")

async def create_invoice_pdf(venta, venta_id):
    pdf = PDF()
    pdf.add_page()

    pdf.set_font("Arial", size=11)

    fecha_str = venta["fecha"].strftime("%Y-%m-%d")
    hora_str = venta["fecha"].strftime("%H:%M:%S")

    cliente_id = venta.get("cliente_id")
    cliente = await db.usuarios.find_one({"_id": ObjectId(cliente_id)})
    cliente_nombre = cliente.get("full_name") if cliente else "Cliente desconocido"

    pdf.set_text_color(50)
    pdf.cell(0, 10, f"Fecha: {fecha_str}    Hora: {hora_str}", ln=True)
    pdf.cell(0, 10, f"Cliente: {cliente_nombre}", ln=True)
    pdf.ln(8)

    pdf.set_fill_color(230, 230, 230)
    pdf.set_text_color(0)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(25, 10, "Cantidad", 1, 0, 'C', 1)
    pdf.cell(75, 10, "Producto", 1, 0, 'C', 1)
    pdf.cell(35, 10, "V. Unitario", 1, 0, 'C', 1)
    pdf.cell(35, 10, "Total", 1, 1, 'C', 1)

    pdf.set_font("Arial", '', 11)
    for item in venta["items"]:
        cantidad = item["cantidad"]
        nombre = item["nombre"][:40]
        valor_unitario = item["valor_unitario"]
        total = cantidad * valor_unitario

        pdf.cell(25, 10, str(cantidad), 1, 0, 'C')
        pdf.cell(75, 10, nombre, 1)
        pdf.cell(35, 10, f"${valor_unitario:.2f}", 1, 0, 'R')
        pdf.cell(35, 10, f"${total:.2f}", 1, 1, 'R')

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 100, 0)
    pdf.cell(0, 10, f"TOTAL FACTURA: ${venta['total']:.2f}", ln=True, align="R")

    path = f"app/static/facturas/factura_{venta_id}.pdf"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pdf.output(path)
    return path