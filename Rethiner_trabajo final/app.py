from flask import Flask, render_template, request, jsonify, session, redirect
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

app = Flask(__name__)

# =========================
# CONFIGURACIÓN GENERAL
# =========================
app.secret_key = 'rethiner_secret_key'

bcrypt = Bcrypt(app)

# =========================
# CONFIGURACIÓN MYSQL
# =========================
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'optica_db'

mysql = MySQL(app)

# =========================
# CONFIGURACIÓN EMAIL
# =========================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

app.config['MAIL_USERNAME'] = 'rethinerr@gmail.com'
app.config['MAIL_PASSWORD'] = 'opgskukucjhsmfqk'

mail = Mail(app)

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

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
        id,
        nombre,
        tipo,
        precio,
        imagen
        FROM productos
        WHERE categoria='mujer'
    """)

    productos_db = cursor.fetchall()

    cursor.close()

    productos = []

    for producto in productos_db:

        productos.append({

            "id": producto[0],
            "nombre": producto[1],
            "tipo": producto[2],
            "precio": producto[3],
            "imagen": producto[4]

        })

    return render_template(
        "catalogo_mujer.html",
        productos=productos
    )

# =========================
# CATÁLOGO HOMBRE
# =========================
@app.route("/catalogo/hombre")
def catalogo_hombre():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
        id,
        nombre,
        tipo,
        precio,
        imagen
        FROM productos
        WHERE categoria='hombre'
    """)

    productos_db = cursor.fetchall()

    cursor.close()

    productos = []

    for producto in productos_db:

        productos.append({

            "id": producto[0],
            "nombre": producto[1],
            "tipo": producto[2],
            "precio": producto[3],
            "imagen": producto[4]

        })

    return render_template(
        "catalogo_hombre.html",
        productos=productos
    )
# =========================
# CATÁLOGO SOL
# =========================
@app.route("/catalogo/sol")
def catalogo_sol():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
        id,
        nombre,
        tipo,
        precio,
        imagen
        FROM productos
        WHERE categoria='sol'
    """)

    productos_db = cursor.fetchall()

    cursor.close()

    productos = []

    for producto in productos_db:

        productos.append({

            "id": producto[0],
            "nombre": producto[1],
            "tipo": producto[2],
            "precio": producto[3],
            "imagen": producto[4]

        })

    return render_template(
        "catalogo_sol.html",
        productos=productos
    )
# =========================
# CATÁLOGO MARCOS
# =========================
@app.route("/catalogo/marcos")
def catalogo_marcos():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
        id,
        nombre,
        tipo,
        precio,
        imagen
        FROM productos
        WHERE categoria='marcos'
    """)

    productos_db = cursor.fetchall()

    cursor.close()

    productos = []

    for producto in productos_db:

        productos.append({

            "id": producto[0],
            "nombre": producto[1],
            "tipo": producto[2],
            "precio": producto[3],
            "imagen": producto[4]

        })

    return render_template(
        "catalogo_marcos.html",
        productos=productos
    )# =========================
# CATÁLOGO LENTES CONTACTO
# =========================
@app.route("/catalogo/contacto")
def catalogo_contacto():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
        id,
        nombre,
        tipo,
        precio,
        imagen
        FROM productos
        WHERE categoria='contacto'
    """)

    productos_db = cursor.fetchall()

    cursor.close()

    productos = []

    for producto in productos_db:

        productos.append({

            "id": producto[0],
            "nombre": producto[1],
            "tipo": producto[2],
            "precio": producto[3],
            "imagen": producto[4]

        })

    return render_template(
        "catalogo_contacto.html",
        productos=productos
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

    data = request.get_json()

    nombre = data.get("nombre")
    email = data.get("email")
    password = data.get("password")

    cursor = mysql.connection.cursor()

    # VERIFICAR SI YA EXISTE
    cursor.execute(
        "SELECT * FROM usuarios WHERE email=%s",
        (email,)
    )

    usuario = cursor.fetchone()

    if usuario:

        cursor.close()

        return jsonify({
            "status": "error",
            "mensaje": "El correo ya se encuentra registrado."
        })

    # ENCRIPTAR PASSWORD
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # GUARDAR USUARIO
    cursor.execute("""
        INSERT INTO usuarios(
            nombre,
            email,
            password
        )
        VALUES(%s, %s, %s)
    """, (
        nombre,
        email,
        password_hash
    ))

    mysql.connection.commit()

    cursor.close()

    return jsonify({
        "status": "ok",
        "mensaje": "Cuenta creada correctamente"
    })

# =========================
# LOGIN
# =========================
@app.route("/iniciar-sesion", methods=["POST"])
def iniciar_sesion():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    cursor = mysql.connection.cursor()

    cursor.execute(
        "SELECT * FROM usuarios WHERE email=%s",
        (email,)
    )

    usuario = cursor.fetchone()

    cursor.close()

    # USUARIO NO EXISTE
    if not usuario:

        return jsonify({
            "status": "error",
            "mensaje": "La cuenta ingresada no se encuentra registrada."
        })

    # VALIDAR CONTRASEÑA
    password_correcta = bcrypt.check_password_hash(
        usuario[3],
        password
    )

    if not password_correcta:

        return jsonify({
            "status": "error",
            "mensaje": "La contraseña ingresada es incorrecta."
        })

    # CREAR SESIÓN
    session["usuario_id"] = usuario[0]
    session["usuario_nombre"] = usuario[1]

    return jsonify({
        "status": "ok",
        "mensaje": f"Bienvenido {usuario[1]}",
        "nombre": usuario[1],
        "email": usuario[2]
    })

# =========================
# CERRAR SESIÓN
# =========================
@app.route("/cerrar-sesion")
def cerrar_sesion():

    session.pop("usuario_id", None)
    session.pop("usuario_nombre", None)

    return redirect("/")
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
        ocupadas.append(str(hora[0])[:5])

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

    data = request.get_json()

    nombre = data.get("nombre")
    email = data.get("email")
    mensaje = data.get("mensaje")
    fecha = data.get("fecha")
    hora = data.get("hora")

    cursor = mysql.connection.cursor()

    # VERIFICAR SI YA EXISTE
    cursor.execute(
        "SELECT * FROM citas WHERE fecha=%s AND hora=%s",
        (fecha, hora)
    )

    cita_existente = cursor.fetchone()

    if cita_existente:

        cursor.close()

        return jsonify({
            "status": "error",
            "mensaje": "Ese horario ya está ocupado."
        })

    # GUARDAR CITA
    cursor.execute("""
        INSERT INTO citas(
            nombre,
            email,
            fecha,
            hora,
            mensaje
        )
        VALUES(%s, %s, %s, %s, %s)
    """, (
        nombre,
        email,
        fecha,
        hora,
        mensaje
    ))

    mysql.connection.commit()

    # =========================
    # ENVIAR CORREO
    # =========================
    msg = Message(

        subject='Cita agendada correctamente',

        sender=app.config['MAIL_USERNAME'],

        recipients=[email]

    )

    msg.body = f'''

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
'''

    mail.send(msg)

    print("CORREO ENVIADO")

    cursor.close()

    return jsonify({
        "status": "ok",
        "mensaje": "Cita agendada correctamente"
    })

# =========================
# INICIAR SERVIDOR
# =========================
if __name__ == "__main__":

    app.run(debug=True)