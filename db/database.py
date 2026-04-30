import sqlite3
from datetime import datetime
from pathlib import Path

# Conexión a la base de datos (si no existe, la crea)
DB_PATH = Path(__file__).resolve().parent / "heladeria.db"
conexion = sqlite3.connect(str(DB_PATH))
cursor = conexion.cursor()

# Activar llaves foráneas en SQLite
cursor.execute("PRAGMA foreign_keys = ON;")


# ==========================================
# TABLA SABORES
# ==========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS sabores (
    id_sabor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    activo INTEGER NOT NULL DEFAULT 1
);
""")

# Insertar sabores base
cursor.executemany("""
INSERT OR IGNORE INTO sabores (nombre, descripcion)
VALUES (?, ?)
""", [
    ("Fresa", "Helado sabor fresa natural"),
    ("Chocolate", "Helado sabor chocolate clásico"),
    ("Vainilla", "Helado sabor vainilla tradicional"),
    ("Mango", "Helado sabor mango tropical"),
    ("Limón", "Helado sabor limón refrescante")
])



# ==========================================
# TABLA PRODUCTOS
# ==========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS productos (
    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
    id_sabor INTEGER NOT NULL,
    nombre_producto TEXT NOT NULL,
    volumen_litros REAL NOT NULL CHECK(volumen_litros > 0),
    precio_unitario REAL NOT NULL CHECK(precio_unitario > 0),
    activo INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_sabor) REFERENCES sabores(id_sabor)
);
""")

# Insertar productos (tarros de 1 litro)
cursor.executemany("""
INSERT OR IGNORE INTO productos (id_sabor, nombre_producto, volumen_litros, precio_unitario)
VALUES (?, ?, ?, ?)
""", [
    (1, "Tarro 1L Fresa", 1.0, 18000.0),
    (2, "Tarro 1L Chocolate", 1.0, 18000.0),
    (3, "Tarro 1L Vainilla", 1.0, 16000.0),
    (4, "Tarro 1L Mango", 1.0, 19000.0),
    (5, "Tarro 1L Limón", 1.0, 17000.0)
])



# ==========================================
# TABLA INVENTARIO
# ==========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventario (
    id_inventario INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto INTEGER NOT NULL UNIQUE,
    cantidad_unidades INTEGER NOT NULL CHECK(cantidad_unidades >= 0),
    stock_minimo INTEGER NOT NULL DEFAULT 0,
    ultima_actualizacion TEXT NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);
""")

fecha_actual = datetime.now().isoformat()

# Inventario inicial
cursor.executemany("""
INSERT OR IGNORE INTO inventario (id_producto, cantidad_unidades, stock_minimo, ultima_actualizacion)
VALUES (?, ?, ?, ?)
""", [
    (1, 20, 5, fecha_actual),
    (2, 15, 5, fecha_actual),
    (3, 10, 3, fecha_actual),
    (4, 8, 2, fecha_actual),
    (5, 12, 3, fecha_actual)
])



# ==========================================
# TABLA VENTAS
# ==========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS ventas (
    id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    total REAL NOT NULL CHECK(total >= 0),
    metodo_pago TEXT NOT NULL CHECK(metodo_pago IN ('efectivo','tarjeta'))
);
""")


# ==========================================
# TABLA DETALLE_VENTA
# ==========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS detalle_venta (
    id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
    id_venta INTEGER NOT NULL,
    id_producto INTEGER NOT NULL,
    cantidad INTEGER NOT NULL CHECK(cantidad > 0),
    precio_unitario REAL NOT NULL CHECK(precio_unitario > 0),
    subtotal REAL NOT NULL CHECK(subtotal >= 0),
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);
""")


# ==========================================
# TABLA MOVIMIENTOS INVENTARIO
# ==========================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS movimientos_inventario (
    id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('entrada','salida')),
    cantidad INTEGER NOT NULL CHECK(cantidad > 0),
    fecha TEXT NOT NULL,
    motivo TEXT NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);
""")


# Registrar movimientos iniciales de inventario
cursor.executemany("""
INSERT INTO movimientos_inventario (id_producto, tipo, cantidad, fecha, motivo)
VALUES (?, ?, ?, ?, ?)
""", [
    (1, "entrada", 20, fecha_actual, "Carga inicial inventario"),
    (2, "entrada", 15, fecha_actual, "Carga inicial inventario"),
    (3, "entrada", 10, fecha_actual, "Carga inicial inventario"),
    (4, "entrada", 8, fecha_actual, "Carga inicial inventario"),
    (5, "entrada", 12, fecha_actual, "Carga inicial inventario")
])


# Guardar cambios
conexion.commit()

# Cerrar conexión
conexion.close()

print("Base de datos creada y datos iniciales insertados correctamente.")