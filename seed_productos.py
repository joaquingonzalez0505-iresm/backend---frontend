"""
seed_productos.py
─────────────────
Limpia duplicados en la tabla productos y siembra un catálogo
variado y atractivo para la presentación del proyecto.

Uso:
    python seed_productos.py
"""

import sys
import os

# Asegura que el módulo `app` se resuelva desde el directorio del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import Producto, ItemPedido

# ── Catálogo a sembrar ────────────────────────────────────────────────────────
CATALOGO = [
    {
        "nombre": "Notebook Gamer Asus ROG Strix G16",
        "precio_final": 1_450_000.0,
        "cuotas_cantidad": 12,
        "cuotas_valor": 120_833.33,
        "garantia_meses": 24,
        "stock": 8,
        "imagen_url": "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=600&q=80",
    },
    {
        "nombre": "Monitor Gamer LG UltraGear 27\" 144Hz",
        "precio_final": 380_000.0,
        "cuotas_cantidad": 6,
        "cuotas_valor": 63_333.33,
        "garantia_meses": 12,
        "stock": 12,
        "imagen_url": "https://images.unsplash.com/photo-1547082299-de196ea013d6?w=600&q=80",
    },
    {
        "nombre": "Teclado Mecánico RGB Redragon Kumara",
        "precio_final": 65_000.0,
        "cuotas_cantidad": 3,
        "cuotas_valor": 21_666.67,
        "garantia_meses": 12,
        "stock": 20,
        "imagen_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&q=80",
    },
    {
        "nombre": "Mouse Inalámbrico Logitech G Pro X",
        "precio_final": 120_000.0,
        "cuotas_cantidad": 3,
        "cuotas_valor": 40_000.0,
        "garantia_meses": 12,
        "stock": 15,
        "imagen_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&q=80",
    },
    {
        "nombre": "Auriculares Gamer HyperX Cloud II",
        "precio_final": 95_000.0,
        "cuotas_cantidad": 3,
        "cuotas_valor": 31_666.67,
        "garantia_meses": 12,
        "stock": 10,
        "imagen_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80",
    },
    {
        "nombre": "Silla Gamer Ergonómica Premium",
        "precio_final": 290_000.0,
        "cuotas_cantidad": 6,
        "cuotas_valor": 48_333.33,
        "garantia_meses": 24,
        "stock": 5,
        "imagen_url": "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=600&q=80",
    },
]

def run_seed():
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("=" * 60)
        print("  SEED — Inicializando catálogo de productos")
        print("=" * 60)

        # ── 1. Limpiar duplicados ─────────────────────────────────────
        todos = db.query(Producto).order_by(Producto.id).all()
        print(f"\n[INFO] Productos actuales en DB: {len(todos)}")

        # Agrupar por nombre normalizado
        vistos: dict[str, int] = {}   # nombre → id a conservar
        ids_a_eliminar: list[int] = []

        for prod in todos:
            clave = prod.nombre.strip().lower()
            if clave not in vistos:
                vistos[clave] = prod.id
            else:
                ids_a_eliminar.append(prod.id)

        if ids_a_eliminar:
            print(f"[LIMPIEZA] Eliminando {len(ids_a_eliminar)} registros duplicados: {ids_a_eliminar}")
            # Primero desvincular items_pedido que apunten a estos ids
            for dup_id in ids_a_eliminar:
                afectados = db.query(ItemPedido).filter(ItemPedido.producto_id == dup_id).all()
                for item in afectados:
                    # Reasignar al producto original conservado
                    nombre_dup = db.query(Producto).filter(Producto.id == dup_id).first()
                    if nombre_dup:
                        original_id = vistos.get(nombre_dup.nombre.strip().lower())
                        if original_id:
                            item.producto_id = original_id
                db.query(Producto).filter(Producto.id == dup_id).delete()
            db.commit()
            print("[LIMPIEZA] Duplicados eliminados.")
        else:
            print("[LIMPIEZA] No hay duplicados que eliminar.")

        # ── 2. Sembrar / actualizar productos del catálogo ────────────
        print("\n[SEED] Procesando catálogo...")
        for datos in CATALOGO:
            nombre_clave = datos["nombre"].strip().lower()
            existente = db.query(Producto).filter(
                Producto.nombre.ilike(datos["nombre"].split("\"")[0].strip() + "%")
            ).first()

            if existente:
                # Actualizar datos existentes
                existente.precio_final   = datos["precio_final"]
                existente.cuotas_cantidad = datos["cuotas_cantidad"]
                existente.cuotas_valor   = datos["cuotas_valor"]
                existente.garantia_meses = datos["garantia_meses"]
                existente.stock          = datos["stock"]
                existente.imagen_url     = datos["imagen_url"]
                existente.imagen         = datos["imagen_url"]
                print(f"  [UPDATE] {existente.nombre} (id={existente.id})")
            else:
                # Insertar nuevo
                nuevo = Producto(
                    nombre         = datos["nombre"],
                    precio_final   = datos["precio_final"],
                    cuotas_cantidad = datos["cuotas_cantidad"],
                    cuotas_valor   = datos["cuotas_valor"],
                    garantia_meses = datos["garantia_meses"],
                    stock          = datos["stock"],
                    imagen_url     = datos["imagen_url"],
                    imagen         = datos["imagen_url"],
                )
                db.add(nuevo)
                print(f"  [INSERT] {datos['nombre']}")

        db.commit()

        # ── 3. Estado final ───────────────────────────────────────────
        final = db.query(Producto).order_by(Producto.id).all()
        print(f"\n[RESULTADO] {len(final)} productos en la base de datos:")
        print(f"  {'ID':>4}  {'Nombre':<45}  {'Precio':>12}  Stock")
        print(f"  {'-'*4}  {'-'*45}  {'-'*12}  -----")
        for p in final:
            print(f"  {p.id:>4}  {p.nombre:<45}  ${p.precio_final:>11,.0f}  {p.stock}")

        print("\n[OK] Seed completado exitosamente.")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
