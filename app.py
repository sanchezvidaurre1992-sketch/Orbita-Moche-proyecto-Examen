import os
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from data_processor import obtener_datos_sector, SECTORES
from database import init_db, get_db_connection

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "orbita_moche_nasa_2026_secret_key")

# Inicializar SQLite al arrancar (vital para Render)
init_db()

# --- DECORADORES DE SEGURIDAD Y ROLES ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión para acceder a la plataforma de monitoreo.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session or session.get("user_rol") != "admin":
            flash("Acceso denegado: Se requieren permisos de Administrador.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated_function

# --- RUTAS PÚBLICAS ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_nombre"] = user["nombre"]
            session["user_email"] = user["email"]
            session["user_rol"] = user["rol"]
            flash(f"Bienvenido, {user['nombre']} ({user['rol'].upper()}).", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Correo electrónico o contraseña incorrectos.", "danger")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        rol = request.form.get("rol", "investigador")

        if rol not in ("investigador", "admin"):
            rol = "investigador"

        if not nombre or not email or not password:
            flash("Todos los campos son obligatorios.", "warning")
            return render_template("register.html")

        conn = get_db_connection()
        existente = conn.execute("SELECT id FROM usuarios WHERE email = ?", (email,)).fetchone()
        if existente:
            conn.close()
            flash("Este correo electrónico ya está registrado.", "danger")
            return render_template("register.html")

        ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn.execute(
            "INSERT INTO usuarios (nombre, email, password_hash, rol, fecha_registro) VALUES (?, ?, ?, ?, ?)",
            (nombre, email, generate_password_hash(password), rol, ahora)
        )
        conn.commit()
        conn.close()

        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for("index"))

# --- DASHBOARD Y OPERACIONES CRUD ---
@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db_connection()
    reportes = conn.execute('''
        SELECT r.*, u.nombre AS autor_nombre, u.rol AS autor_rol
        FROM reportes_campo r
        JOIN usuarios u ON r.usuario_id = u.id
        ORDER BY r.id DESC
    ''').fetchall()
    
    usuarios = []
    if session.get("user_rol") == "admin":
        usuarios = conn.execute("SELECT id, nombre, email, rol, fecha_registro FROM usuarios ORDER BY id ASC").fetchall()
    conn.close()

    return render_template("dashboard.html", sectores=SECTORES, reportes=reportes, usuarios=usuarios)

# CREATE: Crear nuevo reporte de monitoreo en campo
@app.route("/reportes/crear", methods=["POST"])
@login_required
def crear_reporte():
    sector_id = request.form.get("sector_id")
    tipo_pozo = request.form.get("tipo_pozo", "").strip()
    salinidad_ppm = float(request.form.get("salinidad_ppm", 0))
    observaciones = request.form.get("observaciones", "").strip()

    # Clasificación automática de alerta según salinidad (ppm)
    if salinidad_ppm >= 2000:
        nivel_alerta = "Alto"
    elif salinidad_ppm >= 1000:
        nivel_alerta = "Moderado"
    else:
        nivel_alerta = "Bajo"

    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO reportes_campo (sector_id, tipo_pozo, salinidad_ppm, nivel_alerta, observaciones, fecha_reporte, usuario_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (sector_id, tipo_pozo, salinidad_ppm, nivel_alerta, observaciones, ahora, session["user_id"]))
    conn.commit()
    conn.close()

    flash("Reporte de monitoreo en campo registrado en SQLite.", "success")
    return redirect(url_for("dashboard"))

# UPDATE: Editar reporte existente
@app.route("/reportes/editar/<int:reporte_id>", methods=["GET", "POST"])
@login_required
def editar_reporte(reporte_id):
    conn = get_db_connection()
    reporte = conn.execute("SELECT * FROM reportes_campo WHERE id = ?", (reporte_id,)).fetchone()

    if not reporte:
        conn.close()
        flash("Reporte no encontrado.", "danger")
        return redirect(url_for("dashboard"))

    # Control de permisos: solo el dueño o un admin puede editar
    if session.get("user_rol") != "admin" and reporte["usuario_id"] != session["user_id"]:
        conn.close()
        flash("No tienes permiso para editar reportes de otros usuarios.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        sector_id = request.form.get("sector_id")
        tipo_pozo = request.form.get("tipo_pozo", "").strip()
        salinidad_ppm = float(request.form.get("salinidad_ppm", 0))
        observaciones = request.form.get("observaciones", "").strip()

        if salinidad_ppm >= 2000:
            nivel_alerta = "Alto"
        elif salinidad_ppm >= 1000:
            nivel_alerta = "Moderado"
        else:
            nivel_alerta = "Bajo"

        conn.execute('''
            UPDATE reportes_campo
            SET sector_id = ?, tipo_pozo = ?, salinidad_ppm = ?, nivel_alerta = ?, observaciones = ?
            WHERE id = ?
        ''', (sector_id, tipo_pozo, salinidad_ppm, nivel_alerta, observaciones, reporte_id))
        conn.commit()
        conn.close()

        flash("Reporte actualizado correctamente.", "success")
        return redirect(url_for("dashboard"))

    conn.close()
    return render_template("editar_reporte.html", reporte=reporte, sectores=SECTORES)

# DELETE: Eliminar reporte
@app.route("/reportes/eliminar/<int:reporte_id>", methods=["POST"])
@login_required
def eliminar_reporte(reporte_id):
    conn = get_db_connection()
    reporte = conn.execute("SELECT * FROM reportes_campo WHERE id = ?", (reporte_id,)).fetchone()

    if not reporte:
        conn.close()
        flash("Reporte no encontrado.", "danger")
        return redirect(url_for("dashboard"))

    # Control de permisos: solo el dueño o un admin puede eliminar
    if session.get("user_rol") != "admin" and reporte["usuario_id"] != session["user_id"]:
        conn.close()
        flash("Solo el administrador o el autor pueden eliminar este reporte.", "danger")
        return redirect(url_for("dashboard"))

    conn.execute("DELETE FROM reportes_campo WHERE id = ?", (reporte_id,))
    conn.commit()
    conn.close()

    flash("Reporte eliminado de la base de datos.", "info")
    return redirect(url_for("dashboard"))

# ADMIN: Cambiar rol de usuario
@app.route("/usuarios/rol/<int:user_id>", methods=["POST"])
@admin_required
def cambiar_rol(user_id):
    nuevo_rol = request.form.get("rol")
    if nuevo_rol in ("admin", "investigador") and user_id != session["user_id"]:
        conn = get_db_connection()
        conn.execute("UPDATE usuarios SET rol = ? WHERE id = ?", (nuevo_rol, user_id))
        conn.commit()
        conn.close()
        flash("Rol de usuario actualizado.", "success")
    return redirect(url_for("dashboard"))

# --- API DE DATOS SATELITALES NASA (EXISTENTE) ---
@app.route("/api/datos-zona", methods=["GET"])
def api_datos_zona():
    sector_id = request.args.get("sector", "morrope_san_jose_tinajones")
    resultado = obtener_datos_sector(sector_id)
    return jsonify(resultado)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)