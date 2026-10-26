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
    desc = getattr(p, "descripcion", None) or getattr(p, "description", "") or ""
    return {
        "id": p.id,
        "nombre": getattr(p, "nombre", "Producto"),
        "descripcion": desc,
        "description": desc,
        "precio": float(getattr(p, "precio", 0.0) or 0.0),
        "stock": int(getattr(p, "stock", 0) or 0),
        "imagen_url": getattr(p, "imagen_url", "") or ""
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
    except Exception as e:
        data = {}

    nombre = data.get("nombre") or data.get("title") or data.get("titulo") or "Nuevo Sticker"
    descripcion = data.get("descripcion") or data.get("description") or ""
    
    raw_precio = data.get("precio") if data.get("precio") is not None else (
        data.get("precioFinal") if data.get("precioFinal") is not None else (
            data.get("price") if data.get("price") is not None else data.get("valor", 0)
        )
    )
    try:
        precio = float(str(raw_precio).replace(",", "."))
    except Exception:
        precio = 0.0

    raw_stock = data.get("stock") if data.get("stock") is not None else (data.get("cantidad") or 0)
    try:
        stock = int(raw_stock)
    except Exception:
        stock = 0

    imagen_url = data.get("imagen_url") or data.get("imagen") or data.get("image") or data.get("url") or ""

    # Construcción dinámica para prevenir TypeError de atributos inexistentes en SQLAlchemy
    kwargs = {}
    if hasattr(Producto, "nombre"): kwargs["nombre"] = str(nombre)
    
    if hasattr(Producto, "descripcion"): kwargs["descripcion"] = str(descripcion)
    if hasattr(Producto, "description"): kwargs["description"] = str(descripcion)
    
    if hasattr(Producto, "precio"): kwargs["precio"] = precio
    if hasattr(Producto, "stock"): kwargs["stock"] = stock
    if hasattr(Producto, "imagen_url"): kwargs["imagen_url"] = str(imagen_url) if imagen_url else None

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

    if "nombre" in data or "title" in data or "titulo" in data:
        val = str(data.get("nombre") or data.get("title") or data.get("titulo") or "")
        if hasattr(producto, "nombre"): producto.nombre = val

    if "descripcion" in data or "description" in data:
        val = str(data.get("descripcion") or data.get("description") or "")
        if hasattr(producto, "descripcion"): producto.descripcion = val
        if hasattr(producto, "description"): producto.description = val
    
    raw_precio = data.get("precio") if "precio" in data else (
        data.get("precioFinal") if "precioFinal" in data else (
            data.get("price") if "price" in data else data.get("valor")
        )
    )
    if raw_precio is not None and hasattr(producto, "precio"):
        try:
            producto.precio = float(str(raw_precio).replace(",", "."))
        except Exception:
            pass

    raw_stock = data.get("stock") if "stock" in data else data.get("cantidad")
    if raw_stock is not None and hasattr(producto, "stock"):
        try:
            producto.stock = int(raw_stock)
        except Exception:
            pass

    if ("imagen_url" in data or "imagen" in data or "image" in data) and hasattr(producto, "imagen_url"):
        img = data.get("imagen_url") or data.get("imagen") or data.get("image")
        if img:
            producto.imagen_url = str(img)

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