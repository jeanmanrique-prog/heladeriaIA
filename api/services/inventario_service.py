import sqlite3
from api.core.config import DB_PATH
from datetime import datetime

class InventarioService:
    @staticmethod
    def get_db_conn():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    @classmethod
    def listar_sabores(cls):
        conn = cls.get_db_conn()
        sabores = conn.execute("SELECT * FROM sabores WHERE activo = 1").fetchall()
        conn.close()
        return [dict(s) for s in sabores]

    @classmethod
    def obtener_sabor(cls, id_sabor: int):
        conn = cls.get_db_conn()
        sabor = conn.execute("SELECT * FROM sabores WHERE id_sabor = ?", (id_sabor,)).fetchone()
        conn.close()
        return dict(sabor) if sabor else None

    @classmethod
    def listar_productos(cls):
        conn = cls.get_db_conn()
        productos = conn.execute("""
            SELECT p.id_producto, p.nombre_producto, p.precio_unitario,
                   p.volumen_litros, s.nombre AS sabor,
                   i.cantidad_unidades AS stock, i.stock_minimo
            FROM productos p
            JOIN sabores s ON p.id_sabor = s.id_sabor
            JOIN inventario i ON p.id_producto = i.id_producto
            WHERE p.activo = 1
        """).fetchall()
        conn.close()
        return [dict(p) for p in productos]

    @classmethod
    def obtener_producto(cls, id_producto: int):
        conn = cls.get_db_conn()
        producto = conn.execute("""
            SELECT p.*, s.nombre AS sabor, i.cantidad_unidades AS stock
            FROM productos p
            JOIN sabores s ON p.id_sabor = s.id_sabor
            JOIN inventario i ON p.id_producto = i.id_producto
            WHERE p.id_producto = ?
        """, (id_producto,)).fetchone()
        conn.close()
        return dict(producto) if producto else None

    @classmethod
    def ver_inventario(cls):
        conn = cls.get_db_conn()
        inventario = conn.execute("""
            SELECT p.nombre_producto, s.nombre AS sabor,
                   i.cantidad_unidades AS stock, i.stock_minimo,
                   i.ultima_actualizacion,
                   CASE WHEN i.cantidad_unidades <= i.stock_minimo
                        THEN 1 ELSE 0 END AS alerta_stock
            FROM inventario i
            JOIN productos p ON i.id_producto = p.id_producto
            JOIN sabores s ON p.id_sabor = s.id_sabor
            ORDER BY alerta_stock DESC
        """).fetchall()
        conn.close()
        return [dict(i) for i in inventario]

    @classmethod
    def alertas_stock(cls):
        conn = cls.get_db_conn()
        alertas = conn.execute("""
            SELECT p.nombre_producto, i.cantidad_unidades AS stock, i.stock_minimo
            FROM inventario i
            JOIN productos p ON i.id_producto = p.id_producto
            WHERE i.cantidad_unidades <= i.stock_minimo
        """).fetchall()
        conn.close()
        return [dict(a) for a in alertas]

    @classmethod
    def entrada_inventario(cls, id_producto: int, cantidad: int, motivo: str):
        conn = cls.get_db_conn()
        cursor = conn.cursor()
        fecha_actual = datetime.now().isoformat()

        producto = cursor.execute(
            "SELECT * FROM inventario WHERE id_producto = ?", (id_producto,)
        ).fetchone()

        if not producto:
            conn.close()
            return False, "Producto no encontrado"

        cursor.execute("""
            UPDATE inventario
            SET cantidad_unidades = cantidad_unidades + ?,
                ultima_actualizacion = ?
            WHERE id_producto = ?
        """, (cantidad, fecha_actual, id_producto))

        cursor.execute("""
            INSERT INTO movimientos_inventario (id_producto, tipo, cantidad, fecha, motivo)
            VALUES (?, 'entrada', ?, ?, ?)
        """, (id_producto, cantidad, fecha_actual, motivo))

        conn.commit()
        conn.close()
        return True, f"Se agregaron {cantidad} unidades"

    @classmethod
    def listar_movimientos(cls):
        conn = cls.get_db_conn()
        movimientos = conn.execute("""
            SELECT m.*, p.nombre_producto
            FROM movimientos_inventario m
            JOIN productos p ON m.id_producto = p.id_producto
            ORDER BY m.fecha DESC
        """).fetchall()
        conn.close()
        return [dict(m) for m in movimientos]
