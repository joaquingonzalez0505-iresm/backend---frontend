import sqlite3
import os

def migrate_database(db_path: str):
    if not os.path.exists(db_path):
        print(f"[SKIP] DB {db_path} does not exist.")
        return
    
    print(f"[MIGRATE] Processing {db_path}...")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 1. Check if 'productos' table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productos'")
    if not c.fetchone():
        print(f"[SKIP] Table 'productos' does not exist in {db_path}.")
        conn.close()
        return

    # Check columns
    c.execute("PRAGMA table_info(productos)")
    cols = {row[1]: row for row in c.fetchall()}
    print(f"Existing columns in productos: {list(cols.keys())}")

    # Disable foreign keys during migration
    c.execute("PRAGMA foreign_keys = OFF")

    # Create new table with all desired columns and nullable/default constraints
    c.execute("""
    CREATE TABLE productos_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR NOT NULL DEFAULT 'Producto',
        descripcion VARCHAR DEFAULT '',
        precio FLOAT DEFAULT 0.0,
        precio_final FLOAT DEFAULT 0.0,
        cuotas_cantidad INTEGER DEFAULT 1,
        cuotas_valor FLOAT DEFAULT 0.0,
        garantia_meses INTEGER DEFAULT 0,
        stock INTEGER DEFAULT 0,
        imagen VARCHAR DEFAULT '',
        imagen_url VARCHAR DEFAULT ''
    )
    """)

    # Build dynamic select from old table
    col_nombre = "nombre" if "nombre" in cols else "'Producto'"
    col_desc = "descripcion" if "descripcion" in cols else "''"
    col_precio = "precio" if "precio" in cols else ("precio_final" if "precio_final" in cols else "0.0")
    col_pf = "precio_final" if "precio_final" in cols else ("precio" if "precio" in cols else "0.0")
    col_cq = "cuotas_cantidad" if "cuotas_cantidad" in cols else "1"
    col_cv = "cuotas_valor" if "cuotas_valor" in cols else "0.0"
    col_gm = "garantia_meses" if "garantia_meses" in cols else "0"
    col_stk = "stock" if "stock" in cols else "0"
    col_img = "imagen" if "imagen" in cols else "''"
    col_img_url = "imagen_url" if "imagen_url" in cols else "''"

    query_copy = f"""
    INSERT INTO productos_new (id, nombre, descripcion, precio, precio_final, cuotas_cantidad, cuotas_valor, garantia_meses, stock, imagen, imagen_url)
    SELECT 
        id,
        COALESCE({col_nombre}, 'Producto'),
        COALESCE({col_desc}, ''),
        COALESCE({col_precio}, 0.0),
        COALESCE({col_pf}, 0.0),
        COALESCE({col_cq}, 1),
        COALESCE({col_cv}, 0.0),
        COALESCE({col_gm}, 0),
        COALESCE({col_stk}, 0),
        COALESCE({col_img}, ''),
        COALESCE({col_img_url}, '')
    FROM productos
    """
    c.execute(query_copy)
    c.execute("DROP TABLE productos")
    c.execute("ALTER TABLE productos_new RENAME TO productos")
    c.execute("CREATE INDEX IF NOT EXISTS ix_productos_id ON productos (id)")
    c.execute("PRAGMA foreign_keys = ON")
    conn.commit()

    # Verify
    c.execute("PRAGMA table_info(productos)")
    new_cols = c.fetchall()
    print("New columns in productos:")
    for col in new_cols:
        print(f"  {col}")

    c.execute("SELECT count(*) FROM productos")
    count = c.fetchone()[0]
    print(f"Total productos in migrated table: {count}")
    conn.close()

if __name__ == "__main__":
    for db in ["sql_app.db", "stickerlab.db"]:
        migrate_database(db)
