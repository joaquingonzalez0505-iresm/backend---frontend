import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Producto, Usuario
from app.schemas import ProductoCreate, ProductoResponse
from app.core.security import obtener_usuario_actual

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.get("", response_model=List[ProductoResponse], summary="Listar Productos")
def listar_productos(db: Session = Depends(get_db)):
    return db.query(Producto).all()

@router.get("/{producto_id}", response_model=ProductoResponse, summary="Obtener Producto")
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.post("", response_model=ProductoResponse, summary="Crear Producto")
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    nuevo_producto = Producto(**producto.dict())
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto

@router.put("/{producto_id}", response_model=ProductoResponse, summary="Actualizar Producto")
def actualizar_producto(producto_id: int, datos: ProductoCreate, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for key, value in datos.dict().items():
        setattr(producto, key, value)
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