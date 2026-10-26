import os
import json
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Producto

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.get("", summary="Listar Productos")
@router.get("/", include_in_schema=False)
def listar_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()
    res = []
    for p in productos:
        res.append({
            "id": p.id,
            "nombre": p.nombre or "Producto",
            "descripcion": p.descripcion or "",
            "precio": float(p.precio) if p.precio is not None else 0.0,
            "stock": int(p.stock) if p.stock is not None else 0,
            "imagen_url": p.imagen_url or ""
        })
    return res

@router.get("/{producto_id}", summary="Obtener Producto")
@router.get("/{producto_id}/", include_in_schema=False)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {
        "id": producto.id,
        "nombre": producto.nombre or "Producto",
        "descripcion": producto.descripcion or "",
        "precio": float(producto.precio) if producto.precio is not None else 0.0,
        "stock": int(producto.stock) if producto.stock is not None else 0,
        "imagen_url": producto.imagen_url or ""
    }

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
        print(f"Error procesando body: {e}")
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

    try:
        nuevo_producto = Producto(
            nombre=str(nombre),
            descripcion=str(descripcion),
            precio=precio,
            stock=stock,
            imagen_url=str(imagen_url) if imagen_url else None
        )
        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)

        return {
            "id": nuevo_producto.id,
            "nombre": nuevo_producto.nombre,
            "descripcion": nuevo_producto.descripcion,
            "precio": nuevo_producto.precio,
            "stock": nuevo_producto.stock,
            "imagen_url": nuevo_producto.imagen_url
        }
    except Exception as e:
        db.rollback()
        print(f"Error en BD al guardar producto: {e}")
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
        producto.nombre = str(data.get("nombre") or data.get("title") or data.get("titulo") or producto.nombre)
    if "descripcion" in data or "description" in data:
        producto.descripcion = str(data.get("descripcion") or data.get("description") or producto.descripcion)
    
    raw_precio = data.get("precio") if "precio" in data else (
        data.get("precioFinal") if "precioFinal" in data else (
            data.get("price") if "price" in data else data.get("valor")
        )
    )
    if raw_precio is not None:
        try:
            producto.precio = float(str(raw_precio).replace(",", "."))
        except Exception:
            pass

    raw_stock = data.get("stock") if "stock" in data else data.get("cantidad")
    if raw_stock is not None:
        try:
            producto.stock = int(raw_stock)
        except Exception:
            pass

    if "imagen_url" in data or "imagen" in data or "image" in data:
        img = data.get("imagen_url") or data.get("imagen") or data.get("image")
        if img:
            producto.imagen_url = str(img)

    try:
        db.commit()
        db.refresh(producto)
        return {
            "id": producto.id,
            "nombre": producto.nombre,
            "descripcion": producto.descripcion,
            "precio": producto.precio,
            "stock": producto.stock,
            "imagen_url": producto.imagen_url
        }
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

@router.post("/{producto_id}/imagen", summary="Subir Imagen de Producto")
def subir_imagen_producto(producto_id: int, imagen: UploadFile = File(...), db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    directorio = "uploads/productos"
    os.makedirs(directorio, exist_ok=True)
    path_archivo = os.path.join(directorio, f"{producto_id}_{imagen.filename}")
    
    with open(path_archivo, "wb") as buffer:
        shutil.copyfileobj(imagen.file, buffer)
        
    producto.imagen_url = f"/static/productos/{producto_id}_{imagen.filename}"
    db.commit()
    return {"imagen_url": producto.imagen_url}