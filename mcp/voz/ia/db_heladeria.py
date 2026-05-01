"""
mcp/voz/ia/db_heladeria.py
──────────────────────────
Módulo centralizado de acceso directo a la BD SQLite para el agente de IA.
Usa exactamente la estructura definida en db/database.py:
  - sabores (id_sabor, nombre, descripcion, activo)
  - productos (id_producto, id_sabor, nombre_producto, volumen_litros, precio_unitario, activo)
  - inventario (id_inventario, id_producto, cantidad_unidades, stock_minimo, ultima_actualizacion)
  - ventas (id_venta, fecha, total, metodo_pago)
  - detalle_venta (id_detalle, id_venta, id_producto, cantidad, precio_unitario, subtotal)
  - movimientos_inventario (id_movimiento, id_producto, tipo, cantidad, fecha, motivo)
"""

import sqlite3
from datetime import datetime
from pathlib import Path

# Ruta absoluta a la BD — siempre relativa a este mismo archivo
DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "db" / "heladeria.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# ──────────────────────────────────────────────
# CATÁLOGO (productos + sabor + stock)
# ──────────────────────────────────────────────

def obtener_catalogo() -> list[dict]:
    """
    Devuelve la lista de productos activos con sabor y stock real.
    JOIN: productos → sabores → inventario
    """
    conn = _get_conn()
    try:
        rows = conn.execute("""
            SELECT
                p.id_producto,
                p.nombre_producto,
                s.nombre        AS sabor,
                p.precio_unitario,
                i.cantidad_unidades AS stock
            FROM productos p
            JOIN sabores    s ON p.id_sabor   = s.id_sabor
            JOIN inventario i ON p.id_producto = i.id_producto
            WHERE p.activo = 1
            ORDER BY p.id_producto
        """).fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[db_heladeria] ERROR obtener_catalogo: {e}")
        return []
    finally:
        conn.close()


# ──────────────────────────────────────────────
# REGISTRAR VENTA (igual que VentasService del backend)
# ──────────────────────────────────────────────

def registrar_venta(items: list[dict], metodo_pago: str) -> dict:
    """
    Registra una venta en la BD. items = [{"id_producto": int, "cantidad": int}, ...]
    Hace exactamente lo mismo que VentasService.realizar_venta():
      1. Verifica precio y stock para cada item.
      2. INSERT en ventas.
      3. INSERT en detalle_venta por cada item.
      4. UPDATE inventario (reduce cantidad_unidades).
      5. INSERT en movimientos_inventario tipo='salida'.
    Devuelve {"ok": True, "id_venta": int, "total": float} o {"ok": False, "error": str}
    """
    conn = _get_conn()
    cursor = conn.cursor()
    fecha_actual = datetime.now().isoformat()
    total = 0.0
    items_procesados = []

    try:
        for item in items:
            id_prod = int(item.get("id_producto", 0))
            cantidad = int(item.get("cantidad", 1))

            row = cursor.execute("""
                SELECT p.precio_unitario, i.cantidad_unidades
                FROM productos p
                JOIN inventario i ON p.id_producto = i.id_producto
                WHERE p.id_producto = ? AND p.activo = 1
            """, (id_prod,)).fetchone()

            if not row:
                conn.rollback()
                return {"ok": False, "error": f"Producto {id_prod} no encontrado o inactivo"}

            precio_unit  = row["precio_unitario"]
            stock_actual = row["cantidad_unidades"]

            if stock_actual < cantidad:
                conn.rollback()
                return {"ok": False, "error": f"Stock insuficiente para producto {id_prod} (hay {stock_actual})"}

            subtotal = precio_unit * cantidad
            total += subtotal
            items_procesados.append({
                "id_producto": id_prod,
                "cantidad": cantidad,
                "precio_unitario": precio_unit,
                "subtotal": subtotal,
            })

        # 1. INSERT ventas
        cursor.execute(
            "INSERT INTO ventas (fecha, total, metodo_pago) VALUES (?, ?, ?)",
            (fecha_actual, total, metodo_pago)
        )
        id_venta = cursor.lastrowid

        for ip in items_procesados:
            # 2. INSERT detalle_venta
            cursor.execute("""
                INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (id_venta, ip["id_producto"], ip["cantidad"], ip["precio_unitario"], ip["subtotal"]))

            # 3. UPDATE inventario
            cursor.execute("""
                UPDATE inventario
                SET cantidad_unidades = cantidad_unidades - ?,
                    ultima_actualizacion = ?
                WHERE id_producto = ?
            """, (ip["cantidad"], fecha_actual, ip["id_producto"]))

            # 4. INSERT movimientos_inventario
            cursor.execute("""
                INSERT INTO movimientos_inventario (id_producto, tipo, cantidad, fecha, motivo)
                VALUES (?, 'salida', ?, ?, 'Venta registrada por IA')
            """, (ip["id_producto"], ip["cantidad"], fecha_actual))

        conn.commit()
        print(f"[db_heladeria] Venta #{id_venta} registrada | total={total} | metodo={metodo_pago}")
        return {"ok": True, "id_venta": id_venta, "total": total}

    except Exception as e:
        conn.rollback()
        print(f"[db_heladeria] ERROR registrar_venta: {e}")
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()
