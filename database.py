import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

DB_NAME = "orbita_moche.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'investigador',
            fecha_registro TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reportes_campo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sector_id TEXT NOT NULL,
            tipo_pozo TEXT NOT NULL,
            salinidad_ppm REAL NOT NULL,
            nivel_alerta TEXT NOT NULL,
            observaciones TEXT NOT NULL,
            fecha_reporte TEXT NOT NULL,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
        usuarios_iniciales = [
            ("Admin Órbita Moche", "admin@orbitamoche.pe", generate_password_hash("Admin2026*"), "admin", ahora),
            ("Alex Sánchez (Investigador)", "investigador@orbitamoche.pe", generate_password_hash("Investigador2026*"), "investigador", ahora)
        ]
        cursor.executemany(
            "INSERT INTO usuarios (nombre, email, password_hash, rol, fecha_registro) VALUES (?, ?, ?, ?, ?)",
            usuarios_iniciales
        )

    cursor.execute("SELECT COUNT(*) FROM reportes_campo")
    if cursor.fetchone()[0] == 0:
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
        reportes_iniciales = [
            ("morrope_san_jose_tinajones", "Pozo Tubular Artesanal", 2850.0, "Alto", "Agua con elevada conductividad eléctrica y sabor salobre en sector Cruz del Médano.", ahora, 2),
            ("chancay_tinajones_medio", "Canal Derivación / Pozo Mixto", 1120.0, "Moderado", "Turno de riego reducido; se recomienda alternar con cultivo tolerante.", ahora, 2),
            ("ferrenafe_cabecera", "Toma Directa Canal Taymi", 480.0, "Bajo", "Caudal estable y baja concentración salina en cabecera de valle.", ahora, 1)
        ]
        cursor.executemany(
            """INSERT INTO reportes_campo 
               (sector_id, tipo_pozo, salinidad_ppm, nivel_alerta, observaciones, fecha_reporte, usuario_id) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            reportes_iniciales
        )

    conn.commit()
    conn.close()
