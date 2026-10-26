import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Producto, Usuario
from app.schemas import ProductoResponse
from app.core.security import obtener_usuario_actual

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.get("", response_model=List[ProductoResponse], summary="Listar Productos")
@router.get("/", response_model=List[ProductoResponse], include_in_schema=False)
def listar_productos(db: Session = Depends(get_db)):
    return db.query(Producto).all()

@router.get("/{producto_id}", response_model=ProductoResponse, summary="Obtener Producto")
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.post("", response_model=ProductoResponse, summary="Crear Producto")
@router.post("/", response_model=ProductoResponse, include_in_schema=False)
async def crear_producto(request: Request, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            data = await request.json()
        except Exception:
            data = {}
    else:
        try:
            form = await request.form()
            data = dict(form)
        except Exception:
            data = {}

    nombre = data.get("nombre") or data.get("title") or data.get("titulo") or "Nuevo Producto"
    descripcion = data.get("descripcion") or data.get("description") or ""
    
    # Extraer precio de cualquier campo posible (precio, precioFinal, price, valor)
    raw_precio = data.get("precio") if data.get("precio") is not None else (
        data.get("precioFinal") if data.get("precioFinal") is not None else (
            data.get("price") if data.get("price") is not None else data.get("valor", 0)
        )
    )
    try:
        precio = float(raw_precio)
    except (ValueError, TypeError):
        precio = 0.0

    # Extraer stock
    raw_stock = data.get("stock") if data.get("stock") is not None else (data.get("cantidad") or 0)
    try:
        stock = int(raw_stock)
    except (ValueError, TypeError):
        stock = 0

    imagen_url = data.get("imagen_url") or data.get("imagen") or data.get("image") or None

    nuevo_producto = Producto(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        stock=stock,
        imagen_url=imagen_url
    )
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto

@router.put("/{producto_id}", response_model=ProductoResponse, summary="Actualizar Producto")
async def actualizar_producto(producto_id: int, request: Request, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            data = await request.json()
        except Exception:
            data = {}
    else:
        try:
            form = await request.form()
            data = dict(form)
        except Exception:
            data = {}

    if "nombre" in data or "title" in data or "titulo" in data:
        producto.nombre = data.get("nombre") or data.get("title") or data.get("titulo") or producto.nombre
    if "descripcion" in data or "description" in data:
        producto.descripcion = data.get("descripcion") or data.get("description") or producto.descripcion
    
    raw_precio = data.get("precio") if "precio" in data else (
        data.get("precioFinal") if "precioFinal" in data else (
            data.get("price") if "price" in data else data.get("valor")
        )
    )
    if raw_precio is not None:
        try:
            producto.precio = float(raw_precio)
        except (ValueError, TypeError):
            pass

    raw_stock = data.get("stock") if "stock" in data else data.get("cantidad")
    if raw_stock is not None:
        try:
            producto.stock = int(raw_stock)
        except (ValueError, TypeError):
            pass

    if "imagen_url" in data or "imagen" in data or "image" in data:
        producto.imagen_url = data.get("imagen_url") or data.get("imagen") or data.get("image") or producto.imagen_url

    db.commit()
    db.refresh(producto)
    return producto

@router.delete("/{producto_id}", summary="Eliminar Producto")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(producto)
    db.commit()
    return {"mensaje": "Producto eliminado exitosamente"}

@router.post("/{producto_id}/imagen", summary="Subir Imagen de Producto")
def subir_imagen_producto(producto_id: int, imagen: UploadFile = File(...), db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
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