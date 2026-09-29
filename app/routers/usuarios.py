import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Response, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models import Usuario, Pedido
from app.schemas.usuario import UsuarioOut, PerfilUpdate
from app.core.security import get_password_hash

router = APIRouter(tags=["Usuarios"])

@router.get("/usuarios/me", response_model=UsuarioOut)
@router.get("/usuarios/me/", response_model=UsuarioOut)
@router.get("/usuarios/me/datos", response_model=UsuarioOut)
@router.get("/usuarios/me/datos/", response_model=UsuarioOut)
def obtener_mis_datos(current_user: Usuario = Depends(get_current_user)):
    return current_user

@router.get("/perfil", response_model=UsuarioOut)
@router.get("/perfil/", response_model=UsuarioOut)
def obtener_perfil(current_user: Usuario = Depends(get_current_user)):
    return current_user

@router.put("/perfil", response_model=UsuarioOut)
@router.put("/perfil/", response_model=UsuarioOut)
def actualizar_perfil(
    datos: PerfilUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if datos.nombre is not None:
        current_user.nombre = datos.nombre
    if datos.email is not None and datos.email != current_user.email:
        existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está en uso."
            )
        current_user.email = datos.email
    if datos.password:
        current_user.hashed_password = get_password_hash(datos.password)

    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/usuarios/exportar")
@router.get("/usuarios/exportar/")
@router.get("/usuarios/me/exportar")
@router.get("/usuarios/me/exportar/")
def exportar_mis_datos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    pedidos = (
        db.query(Pedido)
        .filter(Pedido.usuario_id == current_user.id)
        .order_by(Pedido.fecha_creacion.desc())
        .all()
    )

    historial_pedidos = []
    for p in pedidos:
        items_data = []
        for item in p.items:
            items_data.append({
                "producto_id": item.producto_id,
                "producto_nombre": item.producto.nombre if item.producto else None,
                "cantidad": item.cantidad,
                "precio_unitario": float(item.precio_unitario),
            })
        
        historial_pedidos.append({
            "id": p.id,
            "estado": p.estado,
            "total": float(p.total),
            "fecha_creacion": p.fecha_creacion.isoformat(),
            "codigo_solicitud_revocacion": p.solicitud_revocacion.codigo if p.solicitud_revocacion else None,
            "items": items_data
        })

    datos_exportados = {
        "usuario": {
            "id": current_user.id,
            "nombre": current_user.nombre,
            "email": current_user.email,
            "rol": current_user.rol,
            "acepto_tratamiento": current_user.acepto_tratamiento,
            "fecha_consentimiento": current_user.fecha_consentimiento.isoformat() if current_user.fecha_consentimiento else None,
            "activo": current_user.activo,
            "fecha_baja": current_user.fecha_baja.isoformat() if current_user.fecha_baja else None
        },
        "historial_pedidos": historial_pedidos,
        "exportado_el": datetime.now(timezone.utc).isoformat()
    }

    content_json = json.dumps(datos_exportados, indent=2, ensure_ascii=False)
    return Response(
        content=content_json,
        media_type="application/json",
        headers={
            "Content-Disposition": "attachment; filename=mis_datos.json"
        }
    )

@router.delete("/usuarios/me", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/usuarios/me/", status_code=status.HTTP_204_NO_CONTENT)
def anonimizar_mi_cuenta(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    current_user.nombre = "Usuario Anonimizado"
    current_user.email = f"anonymized_{current_user.id}_{uuid.uuid4().hex[:8]}@deleted.local"
    current_user.hashed_password = get_password_hash(uuid.uuid4().hex)
    current_user.activo = False
    current_user.fecha_baja = datetime.now(timezone.utc)

    db.commit()
    return None
