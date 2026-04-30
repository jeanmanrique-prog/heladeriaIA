import sqlite3
from api.core.config import DB_PATH
from datetime import datetime

class VentasService:
    @staticmethod
    def get_db_conn():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    @classmethod
    def realizar_venta(cls, metodo_pago: str, items: list):
        conn = cls.get_db_conn()
        cursor = conn.cursor()
        fecha_actual = datetime.now().isoformat()
        total = 0.0
        items_procesados = []

        try:
            for item in items:
                datos = cursor.execute("""
                    SELECT p.precio_unitario, i.cantidad_unidades
                    FROM productos p
                    JOIN inventario i ON p.id_producto = i.id_producto
                    WHERE p.id_producto = ? AND p.activo = 1
                """, (item.id_producto,)).fetchone()

                if not datos:
                    conn.close()
                    return False, f"Producto {item.id_producto} no encontrado", None

                if datos["cantidad_unidades"] < item.cantidad:
                    conn.close()
                    return False, f"Stock insuficiente para producto {item.id_producto}", None

                subtotal = datos["precio_unitario"] * item.cantidad
                total += subtotal
                items_procesados.append({
                    "id_producto": item.id_producto,
                    "cantidad": item.cantidad,
                    "precio_unitario": datos["precio_unitario"],
                    "subtotal": subtotal
                })

            cursor.execute("""
                INSERT INTO ventas (fecha, total, metodo_pago)
                VALUES (?, ?, ?)
            """, (fecha_actual, total, metodo_pago))
            id_venta = cursor.lastrowid

            for item in items_procesados:
                cursor.execute("""
                    INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """, (id_venta, item["id_producto"], item["cantidad"], item["precio_unitario"], item["subtotal"]))

                cursor.execute("""
                    UPDATE inventario
                    SET cantidad_unidades = cantidad_unidades - ?,
                        ultima_actualizacion = ?
                    WHERE id_producto = ?
                """, (item["cantidad"], fecha_actual, item["id_producto"]))

                cursor.execute("""
                    INSERT INTO movimientos_inventario (id_producto, tipo, cantidad, fecha, motivo)
                    VALUES (?, 'salida', ?, ?, 'Venta registrada')
                """, (item["id_producto"], item["cantidad"], fecha_actual))

            conn.commit()
            return True, "Venta exitosa", {
                "id_venta": id_venta,
                "total": total,
                "items": items_procesados
            }
        except Exception as e:
            conn.rollback()
            return False, f"Error: {e}", None
        finally:
            conn.close()

    @classmethod
    def listar_ventas(cls):
        conn = cls.get_db_conn()
        ventas = conn.execute("SELECT * FROM ventas ORDER BY fecha DESC").fetchall()
        conn.close()
        return [dict(v) for v in ventas]

    @classmethod
    def obtener_detalle_venta(cls, id_venta: int):
        conn = cls.get_db_conn()
        venta = conn.execute("SELECT * FROM ventas WHERE id_venta = ?", (id_venta,)).fetchone()
        if not venta:
            conn.close()
            return None, None
        
        detalles = conn.execute("""
            SELECT d.*, p.nombre_producto
            FROM detalle_venta d
            JOIN productos p ON d.id_producto = p.id_producto
            WHERE d.id_venta = ?
        """, (id_venta,)).fetchall()
        conn.close()
        return dict(venta), [dict(d) for d in detalles]
