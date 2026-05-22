import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session, redirect

load_dotenv()
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta, time

from admin_panel import register_admin_routes

app = Flask(__name__)

PRODUCTOS_ACTIVOS = " AND (estado = 'activo' OR estado IS NULL) "


@app.context_processor
def inject_footer_year():
    return {"current_year": datetime.now().year}

# =========================
# CONFIGURACIÓN GENERAL
# =========================
app.secret_key = os.environ.get("SECRET_KEY", "rethiner_secret_key")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

bcrypt = Bcrypt(app)

# =========================
# CONFIGURACIÓN MYSQL
# =========================
app.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST", "localhost")
app.config["MYSQL_USER"] = os.environ.get("MYSQL_USER", "root")
app.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD", "")
app.config["MYSQL_DB"] = os.environ.get(
    "MYSQL_DATABASE", os.environ.get("MYSQL_DB", "optica_db")
)
app.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT", "3306"))

mysql = MySQL(app)

# =========================
# CONFIGURACIÓN EMAIL
# =========================
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", "587"))
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "")

mail = Mail(app)

ensure_admin_schema = register_admin_routes(app, mysql, bcrypt)


def normalizar_identificacion(valor):
    if valor is None:
        return None
    limpio = "".join(c for c in str(valor).strip() if c.isdigit())
    return limpio or None


def construir_identificacion(tipo, numero):
    tipo_limpio = (tipo or "").strip().upper()
    if tipo_limpio not in ("TI", "CC"):
        return None
    digitos = normalizar_identificacion(numero)
    if not digitos or len(digitos) < 6:
        return None
    return f"{tipo_limpio}{digitos}"


def ensure_usuario_schema():
    cursor = mysql.connection.cursor()
    try:
        cursor.execute(
            "ALTER TABLE usuarios ADD COLUMN identificacion VARCHAR(30) NULL UNIQUE"
        )
        mysql.connection.commit()
    except Exception:
        mysql.connection.rollback()

    try:
        cursor.execute(
            "ALTER TABLE citas ADD COLUMN usuario_id INT NULL"
        )
        mysql.connection.commit()
    except Exception:
        mysql.connection.rollback()

    cursor.execute(
        "SELECT identificacion FROM usuarios WHERE rol = 'admin' LIMIT 1"
    )
    admin = cursor.fetchone()
    if admin and not admin[0]:
        cursor.execute(
            "UPDATE usuarios SET identificacion = %s WHERE rol = 'admin' LIMIT 1",
            ("1000000001",),
        )
        mysql.connection.commit()

    cursor.close()


def establecer_sesion_usuario(usuario):
    session.permanent = True
    session["usuario_id"] = usuario[0]
    session["usuario_nombre"] = usuario[1]
    session["usuario_email"] = usuario[2]
    session["usuario_identificacion"] = usuario[4]


def usuario_a_json(usuario):
    return {
        "id": usuario[0],
        "nombre": usuario[1],
        "email": usuario[2],
        "identificacion": usuario[4],
    }


def fetch_productos_catalogo(categoria):
    cursor = mysql.connection.cursor()
    cursor.execute(
        f"""
        SELECT id, nombre, tipo, precio, imagen
        FROM productos
        WHERE categoria = %s{PRODUCTOS_ACTIVOS}
        """,
        (categoria,),
    )
    productos_db = cursor.fetchall()
    cursor.close()

    productos = []
    for producto in productos_db:
        productos.append({
            "id": producto[0],
            "nombre": producto[1],
            "tipo": producto[2],
            "precio": producto[3],
            "imagen": producto[4],
        })
    return productos


@app.before_request
def init_db_schema_once():
    if not app.config.get("SCHEMA_READY"):
        ensure_admin_schema()
        ensure_usuario_schema()
        app.config["SCHEMA_READY"] = True


# =========================
# TEST EMAIL
# =========================
@app.route("/test-email")
def test_email():

    try:

        msg = Message(
            subject="Prueba Rethiner",
            sender=app.config['MAIL_USERNAME'],
            recipients=["rethinerr@gmail.com"]
        )

        msg.body = "Correo de prueba desde Flask."

        mail.send(msg)

        return "CORREO ENVIADO"

    except Exception as e:

        return str(e)

# =========================
# RUTA PRINCIPAL
# =========================
@app.route("/")
def index():

    return render_template("index.html")

# =========================
# CATALOGO GENERAL
# =========================
@app.route("/catalogo")
def catalogo():

    return render_template("catalogo.html")

# =========================
# CATÁLOGO MUJER
# =========================
# =========================
# CATÁLOGO MUJER
# =========================
@app.route("/catalogo/mujer")
def catalogo_mujer():

    return render_template(
        "catalogo_mujer.html",
        productos=fetch_productos_catalogo("mujer"),
    )

# =========================
# CATÁLOGO HOMBRE
# =========================
@app.route("/catalogo/hombre")
def catalogo_hombre():

    return render_template(
        "catalogo_hombre.html",
        productos=fetch_productos_catalogo("hombre"),
    )
# =========================
# CATÁLOGO SOL
# =========================
@app.route("/catalogo/sol")
def catalogo_sol():

    return render_template(
        "catalogo_sol.html",
        productos=fetch_productos_catalogo("sol"),
    )
# =========================
# CATÁLOGO MARCOS
# =========================
@app.route("/catalogo/marcos")
def catalogo_marcos():

    return render_template(
        "catalogo_marcos.html",
        productos=fetch_productos_catalogo("marcos"),
    )# =========================
# CATÁLOGO LENTES CONTACTO
# =========================
@app.route("/catalogo/contacto")
def catalogo_contacto():

    return render_template(
        "catalogo_contacto.html",
        productos=fetch_productos_catalogo("contacto"),
    )
# =========================
# AGREGAR AL CARRITO
# =========================
@app.route("/agregar-carrito", methods=["POST"])
def agregar_carrito():

    # VALIDAR LOGIN
    if "usuario_id" not in session:

        return jsonify({
            "status": "error",
            "mensaje": "Debes iniciar sesión."
        })

    data = request.get_json()

    producto_id = data.get("producto_id")

    usuario_id = session["usuario_id"]

    cursor = mysql.connection.cursor()

    cursor.execute(
        f"""
        SELECT id FROM productos
        WHERE id = %s{PRODUCTOS_ACTIVOS}
        """,
        (producto_id,),
    )
    if not cursor.fetchone():
        cursor.close()
        return jsonify({
            "status": "error",
            "mensaje": "Este producto no está disponible.",
        })

    # VERIFICAR SI YA EXISTE
    cursor.execute("""
        SELECT id, cantidad
        FROM carrito
        WHERE usuario_id=%s
        AND producto_id=%s
    """, (
        usuario_id,
        producto_id
    ))

    producto = cursor.fetchone()

    # SI YA EXISTE
    if producto:

        nueva_cantidad = producto[1] + 1

        cursor.execute("""
            UPDATE carrito
            SET cantidad=%s
            WHERE id=%s
        """, (
            nueva_cantidad,
            producto[0]
        ))

    else:

        cursor.execute("""
            INSERT INTO carrito(
                usuario_id,
                producto_id,
                cantidad
            )
            VALUES(%s, %s, %s)
        """, (
            usuario_id,
            producto_id,
            1
        ))

    mysql.connection.commit()

    cursor.close()

    return jsonify({
        "status": "ok",
        "mensaje": "Producto agregado al carrito"
    })
# =========================
# CARRITO
# =========================
@app.route("/carrito")
def carrito():

    # VALIDAR LOGIN
    if "usuario_id" not in session:

        return redirect("/login")

    usuario_id = session["usuario_id"]

    cursor = mysql.connection.cursor()

    # CONTADOR CARRITO
    cursor.execute("""
        SELECT SUM(cantidad)
        FROM carrito
        WHERE usuario_id=%s
    """, (
        usuario_id,
    ))

    contador = cursor.fetchone()[0]

    if contador is None:
        contador = 0

    # PRODUCTOS DEL CARRITO
    cursor.execute("""
        SELECT

        carrito.id,
        productos.nombre,
        productos.precio,
        productos.imagen,

        CASE

            WHEN productos.categoria='mujer'
            THEN 'gafas-mujer'

            WHEN productos.categoria='hombre'
            THEN 'gafas-hombre'

            WHEN productos.categoria='sol'
            THEN 'lentes-sol'

            WHEN productos.categoria='marcos'
            THEN 'marcos'

            WHEN productos.categoria='contacto'
            THEN 'lentes-contacto'

        END AS carpeta,

        carrito.cantidad,

        (
            productos.precio * carrito.cantidad
        ) AS subtotal

        FROM carrito

        INNER JOIN productos
        ON carrito.producto_id = productos.id

        WHERE carrito.usuario_id=%s
        AND (productos.estado = 'activo' OR productos.estado IS NULL)
    """, (
        usuario_id,
    ))

    productos = cursor.fetchall()

    total = 0

    for producto in productos:

        total += producto[6]

    cursor.close()

    return render_template(
        "carrito.html",
        productos=productos,
        total=total,
        contador=contador
    )
# =========================
# ELIMINAR PRODUCTO
# =========================
@app.route("/eliminar-carrito/<int:id>")
def eliminar_carrito(id):

    if "usuario_id" not in session:

        return redirect("/login")

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM carrito
        WHERE id=%s
    """, (
        id,
    ))

    mysql.connection.commit()

    cursor.close()

    return redirect("/carrito")
# =========================
# SUMAR CANTIDAD
# =========================
@app.route("/sumar-carrito/<int:id>")
def sumar_carrito(id):

    if "usuario_id" not in session:

        return redirect("/login")

    cursor = mysql.connection.cursor()

    cursor.execute("""
        UPDATE carrito
        SET cantidad = cantidad + 1
        WHERE id=%s
    """, (
        id,
    ))

    mysql.connection.commit()

    cursor.close()

    return redirect("/carrito")
# =========================
# RESTAR CANTIDAD
# =========================
@app.route("/restar-carrito/<int:id>")
def restar_carrito(id):

    if "usuario_id" not in session:

        return redirect("/login")

    cursor = mysql.connection.cursor()

    # OBTENER CANTIDAD
    cursor.execute("""
        SELECT cantidad
        FROM carrito
        WHERE id=%s
    """, (
        id,
    ))

    producto = cursor.fetchone()

    # SI ES MAYOR A 1
    if producto[0] > 1:

        cursor.execute("""
            UPDATE carrito
            SET cantidad = cantidad - 1
            WHERE id=%s
        """, (
            id,
        ))

    else:

        cursor.execute("""
            DELETE FROM carrito
            WHERE id=%s
        """, (
            id,
        ))

    mysql.connection.commit()

    cursor.close()

    return redirect("/carrito")
# =========================
# LOGIN PAGE
# =========================
@app.route("/login")
def login():

    return render_template("login.html")

# =========================
# REGISTRO PAGE
# =========================
@app.route("/crear-cuenta")
def registro_page():

    return render_template("crear-cuenta.html")

# =========================
# REGISTRO
# =========================
@app.route("/registro", methods=["POST"])
def registro():

    data = request.get_json() or {}

    nombre = (data.get("nombre") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    tipo_identificacion = (data.get("tipo_identificacion") or "").strip().upper()
    identificacion = construir_identificacion(
        tipo_identificacion,
        data.get("identificacion"),
    )

    if not nombre or not email or not password or not identificacion:
        return jsonify({
            "status": "error",
            "mensaje": "Completa nombre, tipo y número de documento, correo y contraseña.",
        })

    if tipo_identificacion not in ("TI", "CC"):
        return jsonify({
            "status": "error",
            "mensaje": "Selecciona un tipo de documento válido (CC o TI).",
        })

    cursor = mysql.connection.cursor()

    cursor.execute(
        "SELECT id FROM usuarios WHERE identificacion = %s",
        (identificacion,),
    )

    if cursor.fetchone():
        cursor.close()
        return jsonify({
            "status": "error",
            "mensaje": "Ya existe una cuenta registrada con esta identificación.",
        })

    cursor.execute(
        "SELECT id FROM usuarios WHERE LOWER(email) = %s",
        (email,),
    )

    if cursor.fetchone():
        cursor.close()
        return jsonify({
            "status": "error",
            "mensaje": "El correo ya se encuentra registrado.",
        })

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    cursor.execute(
        """
        INSERT INTO usuarios (nombre, email, password, identificacion, rol)
        VALUES (%s, %s, %s, %s, 'cliente')
        """,
        (nombre, email, password_hash, identificacion),
    )

    mysql.connection.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()

    return jsonify({
        "status": "ok",
        "mensaje": "Cuenta creada correctamente. Usa tu correo electrónico para iniciar sesión.",
        "usuario": {
            "id": nuevo_id,
            "nombre": nombre,
            "email": email,
            "identificacion": identificacion,
        },
    })

# =========================
# LOGIN
# =========================
@app.route("/iniciar-sesion", methods=["POST"])
def iniciar_sesion():

    data = request.get_json() or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({
            "status": "error",
            "mensaje": "Ingresa tu correo electrónico y contraseña.",
        })

    cursor = mysql.connection.cursor()

    cursor.execute(
        """
        SELECT id, nombre, email, password, identificacion
        FROM usuarios
        WHERE LOWER(email) = %s AND (rol IS NULL OR rol = 'cliente')
        """,
        (email,),
    )

    usuario = cursor.fetchone()
    cursor.close()

    if not usuario:
        return jsonify({
            "status": "error",
            "mensaje": "No existe una cuenta con este correo. Crea tu cuenta primero.",
        })

    if not bcrypt.check_password_hash(usuario[3], password):
        return jsonify({
            "status": "error",
            "mensaje": "La contraseña ingresada es incorrecta.",
        })

    establecer_sesion_usuario(usuario)
    perfil = usuario_a_json(usuario)

    return jsonify({
        "status": "ok",
        "mensaje": f"Bienvenido {perfil['nombre']}",
        **perfil,
    })


@app.route("/api/usuario-actual")
def usuario_actual():
    if "usuario_id" not in session:
        return jsonify({"status": "error", "mensaje": "Sin sesión"}), 401

    return jsonify({
        "status": "ok",
        "usuario": {
            "id": session["usuario_id"],
            "nombre": session.get("usuario_nombre"),
            "email": session.get("usuario_email"),
            "identificacion": session.get("usuario_identificacion"),
        },
    })

# =========================
# CERRAR SESIÓN
# =========================
@app.route("/cerrar-sesion")
def cerrar_sesion():

    session.pop("usuario_id", None)
    session.pop("usuario_nombre", None)
    session.pop("usuario_email", None)
    session.pop("usuario_identificacion", None)

    return redirect("/")
def normalizar_hora(hora):
    """Unifica formatos 06:00, 06:00:00, timedelta, etc."""
    if hora is None:
        return None
    if isinstance(hora, time):
        return f"{hora.hour:02d}:{hora.minute:02d}"
    if hasattr(hora, "seconds") and not isinstance(hora, str):
        total = int(hora.total_seconds())
        h = total // 3600
        m = (total % 3600) // 60
        return f"{h:02d}:{m:02d}"
    texto = str(hora).strip()
    if not texto:
        return None
    partes = texto.split(":")
    if len(partes) < 2:
        return texto
    return f"{int(partes[0]):02d}:{int(partes[1]):02d}"


# =========================
# HORARIOS DISPONIBLES
# =========================
@app.route("/horarios-disponibles/<fecha>")
def horarios_disponibles(fecha):

    cursor = mysql.connection.cursor()

    cursor.execute(
        "SELECT hora FROM citas WHERE fecha=%s",
        (fecha,)
    )

    horas_ocupadas = cursor.fetchall()

    ocupadas = []

    for hora in horas_ocupadas:
        hora_norm = normalizar_hora(hora[0])
        if hora_norm:
            ocupadas.append(hora_norm)

    horarios = []

    # MAÑANA
    inicio = datetime.strptime("06:00", "%H:%M")
    fin = datetime.strptime("12:00", "%H:%M")

    while inicio < fin:

        hora_str = inicio.strftime("%H:%M")

        if hora_str not in ocupadas:
            horarios.append(hora_str)

        inicio += timedelta(minutes=20)

    # TARDE
    inicio = datetime.strptime("14:00", "%H:%M")
    fin = datetime.strptime("18:00", "%H:%M")

    while inicio < fin:

        hora_str = inicio.strftime("%H:%M")

        if hora_str not in ocupadas:
            horarios.append(hora_str)

        inicio += timedelta(minutes=20)

    cursor.close()

    return jsonify(horarios)

# =========================
# AGENDAR CITA
# =========================
@app.route("/contacto", methods=["POST"])
def contacto():

    data = request.get_json() or {}

    nombre = (data.get("nombre") or "").strip()
    email = (data.get("email") or "").strip()
    mensaje = data.get("mensaje") or ""
    fecha = data.get("fecha")
    hora = normalizar_hora(data.get("hora"))
    usuario_id = session.get("usuario_id")

    if usuario_id:
        if not nombre:
            nombre = session.get("usuario_nombre") or nombre
        if not email:
            email = session.get("usuario_email") or email

    if not nombre or not email or not fecha or not hora:
        return jsonify({
            "status": "error",
            "mensaje": "Completa todos los campos de la cita."
        }), 400

    cursor = mysql.connection.cursor()

    try:
        cursor.execute(
            """
            SELECT id FROM citas
            WHERE fecha = %s AND TIME_FORMAT(hora, '%%H:%%i') = %s
            LIMIT 1
            """,
            (fecha, hora),
        )

        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "mensaje": "Ese horario ya está ocupado."
            })

        cursor.execute(
            """
            INSERT INTO citas (nombre, email, fecha, hora, mensaje, usuario_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (nombre, email, fecha, hora, mensaje, usuario_id),
        )

        mysql.connection.commit()

        try:
            msg = Message(
                subject="Cita agendada correctamente",
                sender=app.config["MAIL_USERNAME"],
                recipients=[email],
            )
            msg.body = f"""
Hola {nombre},

Tu cita fue agendada correctamente en Rethiner.

Fecha:
{fecha}

Hora:
{hora}

Duración aproximada:
20 minutos

Gracias por confiar en nosotros.

Rethiner Óptica y Oftalmología
"""
            mail.send(msg)
            print("CORREO ENVIADO")
        except Exception as mail_error:
            print(f"AVISO: cita guardada pero falló el correo: {mail_error}")

        return jsonify({
            "status": "ok",
            "mensaje": "Cita agendada correctamente",
        })

    except Exception as e:
        mysql.connection.rollback()
        print(f"ERROR al agendar cita: {e}")
        return jsonify({
            "status": "error",
            "mensaje": "No se pudo agendar la cita. Intenta de nuevo.",
        }), 500

    finally:
        cursor.close()

# =========================
# INICIAR SERVIDOR
# =========================
if __name__ == "__main__":

    app.run(debug=True)