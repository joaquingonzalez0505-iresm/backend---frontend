import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin
from app.models import Producto, Usuario
from app.schemas.producto import ProductoCreate, ProductoOut
from app.utils.archivos import parece_imagen

router = APIRouter(prefix="/productos", tags=["Productos"])

UPLOAD_DIR = os.path.join("uploads", "productos")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

@router.get("", response_model=List[ProductoOut])
@router.get("/", response_model=List[ProductoOut])
def listar_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    nombre: Optional[str] = None,
    db: Session = Depends(get_db)
):
    from sqlalchemy import func, select

    # Subquery: el ID mínimo por nombre (evita duplicados en caso de seed repetido)
    min_ids = (
        select(func.min(Producto.id))
        .group_by(Producto.nombre)
        .scalar_subquery()
    )
    query = db.query(Producto).filter(Producto.id.in_(min_ids))

    if nombre and nombre.strip():
        query = query.filter(Producto.nombre.ilike(f"%{nombre.strip()}%"))

    return query.order_by(Producto.id).offset(skip).limit(limit).all()

@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return prod

@router.post("", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear_producto(
    prod_in: ProductoCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin)
):
    prod = Producto(**prod_in.model_dump())
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return prod

@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(
    producto_id: int,
    prod_in: ProductoCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin)
):
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    for key, value in prod_in.model_dump().items():
        setattr(prod, key, value)

    db.commit()
    db.refresh(prod)
    return prod

@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin)
):
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    db.delete(prod)
    db.commit()
    return None

@router.post("/{producto_id}/imagen", response_model=ProductoOut)
@router.post("/{producto_id}/imagen/", response_model=ProductoOut)
async def subir_imagen_producto(
    producto_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin)
):
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    filename_lower = (archivo.filename or "").lower()
    ext = os.path.splitext(filename_lower)[1]

    # 1. Validación de extensión permitida (HTTP 415)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Extensión de archivo no permitida. Formatos válidos: .jpg, .jpeg, .png, .webp"
        )

    contents = await archivo.read()

    # 2. Validación de tamaño máximo (2 MB) (HTTP 413)
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="El archivo excede el tamaño máximo permitido de 2 MB"
        )

    # 3. Validación de firma real de contenido / magic bytes (HTTP 415)
    if not parece_imagen(contents):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="El contenido del archivo no coincide con una imagen válida"
        )

    # Estructura del nombre: {id}-{token_hex}.{extension}
    token_hex = uuid.uuid4().hex[:8]
    nuevo_nombre = f"{prod.id}-{token_hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, nuevo_nombre)

    with open(filepath, "wb") as f:
        f.write(contents)

    imagen_url = f"/static/productos/{nuevo_nombre}"
    prod.imagen_url = imagen_url
    prod.imagen = imagen_url

    db.commit()
    db.refresh(prod)

    return prod
