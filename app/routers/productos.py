import os
import json
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Producto

router = APIRouter(prefix="/productos", tags=["Productos"])

def adaptar_producto_response(p: Producto):
    desc = getattr(p, "descripcion", "") or getattr(p, "description", "") or ""

    # Resolver precio numérico
    precio_val = getattr(p, "precio", None)
    if precio_val is None or precio_val == 0.0:
        precio_val = getattr(p, "precio_final", 0.0) or 0.0
    try:
        precio_num = float(precio_val)
    except Exception:
        precio_num = 0.0

    cuotas_cant = getattr(p, "cuotas_cantidad", 1) or 1
    try:
        cuotas_cant = max(1, int(cuotas_cant))
    except Exception:
        cuotas_cant = 1

    cuotas_val = getattr(p, "cuotas_valor", None)
    if cuotas_val is None or cuotas_val == 0.0:
        cuotas_val = round(precio_num / cuotas_cant, 2) if cuotas_cant > 0 else 0.0
    else:
        try:
            cuotas_val = float(cuotas_val)
        except Exception:
            cuotas_val = 0.0

    garantia = getattr(p, "garantia_meses", 0) or 0
    try:
        garantia = int(garantia)
    except Exception:
        garantia = 0

    stock_val = getattr(p, "stock", 0) or 0
    try:
        stock_val = int(stock_val)
    except Exception:
        stock_val = 0

    img = getattr(p, "imagen_url", "") or getattr(p, "imagen", "") or ""

    return {
        "id": p.id,
        "nombre": getattr(p, "nombre", "Producto") or "Producto",
        "descripcion": desc,
        "description": desc,
        "precio": precio_num,
        "precio_final": precio_num,
        "precioFinal": precio_num,
        "cuotas": cuotas_cant,
        "cuotas_cantidad": cuotas_cant,
        "cuotas_valor": cuotas_val,
        "garantia_meses": garantia,
        "stock": stock_val,
        "imagen": img,
        "imagen_url": img,
        "image": img,
    }

@router.get("", summary="Listar Productos")
@router.get("/", include_in_schema=False)
def listar_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()
    return [adaptar_producto_response(p) for p in productos]

@router.get("/{producto_id}", summary="Obtener Producto")
@router.get("/{producto_id}/", include_in_schema=False)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return adaptar_producto_response(producto)

@router.post("", summary="Crear Producto")
@router.post("/", include_in_schema=False)
async def crear_producto(request: Request, db: Session = Depends(get_db)):
    data = {}
    try:
        body_bytes = await request.body()
        if body_bytes:
            try:
                data = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                try:
                    form = await request.form()
                    data = dict(form)
                except Exception:
                    data = {}
    except Exception:
        data = {}

    nombre = data.get("nombre") or data.get("title") or data.get("titulo") or "Nuevo Producto"
    descripcion = data.get("descripcion") or data.get("description") or ""

    # Si la petición trae 'precio', asigna ese valor tanto a 'precio' como a 'precio_final'
    raw_precio = None
    for k in ("precio", "precio_final", "precioFinal", "price", "valor"):
        if k in data and data[k] is not None and str(data[k]).strip() != "":
            raw_precio = data[k]
            break

    try:
        precio_val = float(str(raw_precio).replace(",", ".").strip()) if raw_precio is not None else 0.0
    except Exception:
        precio_val = 0.0

    # Si trae 'cuotas' o 'cuotas_cantidad', asígnalo; de lo contrario asigna 1 por defecto
    raw_cuotas = None
    for k in ("cuotas", "cuotas_cantidad", "installments"):
        if k in data and data[k] is not None and str(data[k]).strip() != "":
            raw_cuotas = data[k]
            break

    try:
        cuotas_cant = max(1, int(raw_cuotas)) if raw_cuotas is not None else 1
    except Exception:
        cuotas_cant = 1

    # Completa 'cuotas_valor', 'garantia_meses', 'imagen' y 'imagen_url' con valores por defecto válidos (nunca None)
    raw_cv = data.get("cuotas_valor") or data.get("cuota_valor") or data.get("installment_value")
    try:
        cuotas_val = float(str(raw_cv).replace(",", ".").strip()) if raw_cv is not None else (round(precio_val / cuotas_cant, 2) if cuotas_cant > 0 else 0.0)
    except Exception:
        cuotas_val = round(precio_val / cuotas_cant, 2) if cuotas_cant > 0 else 0.0

    raw_garantia = data.get("garantia_meses") or data.get("garantia") or data.get("warranty")
    try:
        garantia_meses = int(raw_garantia) if raw_garantia is not None else 0
    except Exception:
        garantia_meses = 0

    raw_stock = data.get("stock") if data.get("stock") is not None else (data.get("cantidad") if data.get("cantidad") is not None else 0)
    try:
        stock_val = int(raw_stock)
    except Exception:
        stock_val = 0

    img_raw = data.get("imagen_url") or data.get("imagen") or data.get("image") or data.get("url") or ""
    imagen_str = str(img_raw).strip() if img_raw else ""

    kwargs = {}
    if hasattr(Producto, "nombre"): kwargs["nombre"] = str(nombre)
    if hasattr(Producto, "descripcion"): kwargs["descripcion"] = str(descripcion)
    if hasattr(Producto, "description"): kwargs["description"] = str(descripcion)
    if hasattr(Producto, "precio"): kwargs["precio"] = float(precio_val)
    if hasattr(Producto, "precio_final"): kwargs["precio_final"] = float(precio_val)
    if hasattr(Producto, "cuotas_cantidad"): kwargs["cuotas_cantidad"] = int(cuotas_cant)
    if hasattr(Producto, "cuotas_valor"): kwargs["cuotas_valor"] = float(cuotas_val)
    if hasattr(Producto, "garantia_meses"): kwargs["garantia_meses"] = int(garantia_meses)
    if hasattr(Producto, "stock"): kwargs["stock"] = int(stock_val)
    if hasattr(Producto, "imagen"): kwargs["imagen"] = str(imagen_str)
    if hasattr(Producto, "imagen_url"): kwargs["imagen_url"] = str(imagen_str)

    try:
        nuevo_producto = Producto(**kwargs)
        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)
        return adaptar_producto_response(nuevo_producto)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error guardando producto: {str(e)}")

@router.put("/{producto_id}", summary="Actualizar Producto")
@router.put("/{producto_id}/", include_in_schema=False)
async def actualizar_producto(producto_id: int, request: Request, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    data = {}
    try:
        body_bytes = await request.body()
        if body_bytes:
            try:
                data = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                try:
                    form = await request.form()
                    data = dict(form)
                except Exception:
                    data = {}
    except Exception:
        data = {}

    if any(k in data for k in ("nombre", "title", "titulo")):
        val = str(data.get("nombre") or data.get("title") or data.get("titulo") or "")
        if hasattr(producto, "nombre"):
            producto.nombre = val

    if any(k in data for k in ("descripcion", "description")):
        val = str(data.get("descripcion") or data.get("description") or "")
        if hasattr(producto, "descripcion"):
            producto.descripcion = val
        if hasattr(producto, "description"):
            producto.description = val

    # Si la petición trae 'precio', asigna ese valor tanto a 'precio' como a 'precio_final'
    raw_precio = None
    for k in ("precio", "precio_final", "precioFinal", "price", "valor"):
        if k in data and data[k] is not None and str(data[k]).strip() != "":
            raw_precio = data[k]
            break

    if raw_precio is not None:
        try:
            precio_val = float(str(raw_precio).replace(",", ".").strip())
            if hasattr(producto, "precio"):
                producto.precio = precio_val
            if hasattr(producto, "precio_final"):
                producto.precio_final = precio_val
        except Exception:
            pass

    # Si trae 'cuotas' o 'cuotas_cantidad', asígnalo; de lo contrario asigna 1 por defecto
    raw_cuotas = None
    for k in ("cuotas", "cuotas_cantidad", "installments"):
        if k in data and data[k] is not None and str(data[k]).strip() != "":
            raw_cuotas = data[k]
            break

    if raw_cuotas is not None:
        try:
            cuotas_cant = max(1, int(raw_cuotas))
            if hasattr(producto, "cuotas_cantidad"):
                producto.cuotas_cantidad = cuotas_cant
        except Exception:
            pass

    # Cuotas valor
    if any(k in data for k in ("cuotas_valor", "cuota_valor", "installment_value")):
        raw_cv = data.get("cuotas_valor") or data.get("cuota_valor") or data.get("installment_value")
        if raw_cv is not None:
            try:
                cv_val = float(str(raw_cv).replace(",", ".").strip())
                if hasattr(producto, "cuotas_valor"):
                    producto.cuotas_valor = cv_val
            except Exception:
                pass

    # Garantia meses
    if any(k in data for k in ("garantia_meses", "garantia", "warranty")):
        raw_g = data.get("garantia_meses") or data.get("garantia") or data.get("warranty")
        if raw_g is not None:
            try:
                g_val = int(raw_g)
                if hasattr(producto, "garantia_meses"):
                    producto.garantia_meses = g_val
            except Exception:
                pass

    # Stock
    raw_stock = None
    for k in ("stock", "cantidad"):
        if k in data and data[k] is not None and str(data[k]).strip() != "":
            raw_stock = data[k]
            break

    if raw_stock is not None:
        try:
            stk = int(raw_stock)
            if hasattr(producto, "stock"):
                producto.stock = stk
        except Exception:
            pass

    # Imagen
    if any(k in data for k in ("imagen_url", "imagen", "image", "url")):
        img_raw = data.get("imagen_url") or data.get("imagen") or data.get("image") or data.get("url") or ""
        img_str = str(img_raw).strip()
        if hasattr(producto, "imagen"):
            producto.imagen = img_str
        if hasattr(producto, "imagen_url"):
            producto.imagen_url = img_str

    # Completa 'cuotas_valor', 'garantia_meses', 'imagen' y 'imagen_url' con valores por defecto válidos (nunca None)
    if hasattr(producto, "cuotas_cantidad") and (producto.cuotas_cantidad is None or producto.cuotas_cantidad < 1):
        producto.cuotas_cantidad = 1
    if hasattr(producto, "cuotas_valor") and producto.cuotas_valor is None:
        actual_p = getattr(producto, "precio_final", 0.0) or getattr(producto, "precio", 0.0) or 0.0
        c_cant = getattr(producto, "cuotas_cantidad", 1) or 1
        producto.cuotas_valor = round(actual_p / c_cant, 2) if c_cant > 0 else 0.0
    if hasattr(producto, "garantia_meses") and producto.garantia_meses is None:
        producto.garantia_meses = 0
    if hasattr(producto, "stock") and producto.stock is None:
        producto.stock = 0
    if hasattr(producto, "imagen") and producto.imagen is None:
        producto.imagen = ""
    if hasattr(producto, "imagen_url") and producto.imagen_url is None:
        producto.imagen_url = ""
    if hasattr(producto, "precio_final") and producto.precio_final is None:
        producto.precio_final = getattr(producto, "precio", 0.0) or 0.0
    if hasattr(producto, "precio") and producto.precio is None:
        producto.precio = getattr(producto, "precio_final", 0.0) or 0.0

    try:
        db.commit()
        db.refresh(producto)
        return adaptar_producto_response(producto)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error actualizando producto: {str(e)}")

@router.delete("/{producto_id}", summary="Eliminar Producto")
@router.delete("/{producto_id}/", include_in_schema=False)
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    try:
        db.delete(producto)
        db.commit()
        return {"mensaje": "Producto eliminado exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))