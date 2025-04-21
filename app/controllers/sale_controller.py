from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from fastapi.responses import StreamingResponse
from app.models.sale import Venta, Producto

def generar_factura(venta: Venta):
    buffer = io.BytesIO()

    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.drawString(100, height - 100, f"Factura para {venta.cliente_nombre}")
    c.drawString(100, height - 120, "Productos comprados:")

    y_position = height - 140
    for producto in venta.productos:
        c.drawString(100, y_position, f"- {producto.nombre} (Cantidad: {producto.cantidad}) - ${producto.precio}")
        y_position -= 20

    c.drawString(100, y_position - 20, f"Total: ${venta.total}")
    
    c.save()

    buffer.seek(0)

    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": "inline; filename=factura.pdf"})