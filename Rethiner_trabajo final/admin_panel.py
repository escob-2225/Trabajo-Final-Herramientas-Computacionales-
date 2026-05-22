from datetime import datetime
from functools import wraps

from flask import jsonify, redirect, render_template, request, session, url_for


def register_admin_routes(app, mysql, bcrypt):
    _schema_ready = {"done": False}

    def ensure_schema():
        if _schema_ready["done"]:
            return
        cursor = mysql.connection.cursor()
        try:
            cursor.execute(
                "ALTER TABLE productos ADD COLUMN estado VARCHAR(20) DEFAULT 'activo'"
            )
            mysql.connection.commit()
        except Exception:
            mysql.connection.rollback()

        try:
            cursor.execute(
                "ALTER TABLE usuarios ADD COLUMN rol VARCHAR(20) DEFAULT 'cliente'"
            )
            mysql.connection.commit()
        except Exception:
            mysql.connection.rollback()

        cursor.execute("SELECT id FROM usuarios WHERE rol = 'admin' LIMIT 1")
        if not cursor.fetchone():
            password_hash = bcrypt.generate_password_hash("admin1234").decode("utf-8")
            cursor.execute(
                """
                INSERT INTO usuarios (nombre, email, password, rol, identificacion)
                VALUES (%s, %s, %s, 'admin', %s)
                """,
                (
                    "Administrador Rethiner",
                    "admin@rethiner.com",
                    password_hash,
                    "1000000001",
                ),
            )
            mysql.connection.commit()

        cursor.close()
        _schema_ready["done"] = True

    def admin_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            ensure_schema()
            if not session.get("admin_id"):
                if request.path.startswith("/admin/api/"):
                    return jsonify({"status": "error", "mensaje": "No autorizado"}), 401
                return redirect(url_for("admin_login"))
            return view(*args, **kwargs)

        return wrapped

    def normalizar_hora_cita(hora):
        if hora is None:
            return ""
        texto = str(hora).strip()
        if len(texto) >= 5 and ":" in texto:
            partes = texto.split(":")
            return f"{int(partes[0]):02d}:{int(partes[1]):02d}"
        return texto

    def producto_row_to_dict(row):
        return {
            "id": row[0],
            "nombre": row[1],
            "tipo": row[2],
            "precio": float(row[3]) if row[3] is not None else 0,
            "imagen": row[4],
            "categoria": row[5],
            "estado": row[6] if len(row) > 6 and row[6] else "activo",
        }

    @app.route("/admin/login")
    def admin_login():
        if session.get("admin_id"):
            return redirect(url_for("admin_dashboard"))
        return render_template("admin/login.html")

    @app.route("/admin/iniciar-sesion", methods=["POST"])
    def admin_iniciar_sesion():
        ensure_schema()
        data = request.get_json() or {}
        email = (data.get("email") or "").strip()
        password = data.get("password") or ""

        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT id, nombre, email, password, rol FROM usuarios WHERE email = %s",
            (email,),
        )
        usuario = cursor.fetchone()
        cursor.close()

        if not usuario or usuario[4] != "admin":
            return jsonify({
                "status": "error",
                "mensaje": "Credenciales de administrador incorrectas.",
            })

        if not bcrypt.check_password_hash(usuario[3], password):
            return jsonify({
                "status": "error",
                "mensaje": "Credenciales de administrador incorrectas.",
            })

        session["admin_id"] = usuario[0]
        session["admin_nombre"] = usuario[1]
        session["admin_email"] = usuario[2]

        return jsonify({
            "status": "ok",
            "mensaje": "Bienvenido al panel de administración.",
        })

    @app.route("/admin/cerrar-sesion")
    def admin_cerrar_sesion():
        session.pop("admin_id", None)
        session.pop("admin_nombre", None)
        session.pop("admin_email", None)
        return redirect(url_for("admin_login"))

    @app.route("/admin")
    @app.route("/admin/dashboard")
    @admin_required
    def admin_dashboard():
        return render_template(
            "admin/dashboard.html",
            admin_nombre=session.get("admin_nombre", "Administrador"),
        )

    @app.route("/admin/api/productos", methods=["GET"])
    @admin_required
    def admin_listar_productos():
        cursor = mysql.connection.cursor()
        cursor.execute(
            """
            SELECT id, nombre, tipo, precio, imagen, categoria, estado
            FROM productos
            ORDER BY categoria, nombre
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        return jsonify({
            "status": "ok",
            "productos": [producto_row_to_dict(r) for r in rows],
        })

    @app.route("/admin/api/productos", methods=["POST"])
    @admin_required
    def admin_crear_producto():
        data = request.get_json() or {}
        nombre = (data.get("nombre") or "").strip()
        tipo = (data.get("tipo") or "").strip()
        categoria = (data.get("categoria") or "").strip()
        imagen = (data.get("imagen") or "").strip()
        precio = data.get("precio")

        if not nombre or not categoria or not imagen:
            return jsonify({
                "status": "error",
                "mensaje": "Nombre, categoría e imagen son obligatorios.",
            }), 400

        try:
            precio = float(precio)
        except (TypeError, ValueError):
            return jsonify({
                "status": "error",
                "mensaje": "El precio debe ser un número válido.",
            }), 400

        categorias_validas = {"mujer", "hombre", "sol", "marcos", "contacto"}
        if categoria not in categorias_validas:
            return jsonify({
                "status": "error",
                "mensaje": "Categoría no válida.",
            }), 400

        cursor = mysql.connection.cursor()
        cursor.execute(
            """
            INSERT INTO productos (nombre, tipo, precio, imagen, categoria, estado)
            VALUES (%s, %s, %s, %s, %s, 'activo')
            """,
            (nombre, tipo, precio, imagen, categoria),
        )
        mysql.connection.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()

        return jsonify({
            "status": "ok",
            "mensaje": "Producto creado correctamente.",
            "id": nuevo_id,
        })

    @app.route("/admin/api/productos/<int:producto_id>", methods=["PUT"])
    @admin_required
    def admin_editar_producto(producto_id):
        data = request.get_json() or {}
        nombre = (data.get("nombre") or "").strip()
        tipo = (data.get("tipo") or "").strip()
        categoria = (data.get("categoria") or "").strip()
        imagen = (data.get("imagen") or "").strip()
        precio = data.get("precio")

        if not nombre or not categoria or not imagen:
            return jsonify({
                "status": "error",
                "mensaje": "Nombre, categoría e imagen son obligatorios.",
            }), 400

        try:
            precio = float(precio)
        except (TypeError, ValueError):
            return jsonify({
                "status": "error",
                "mensaje": "El precio debe ser un número válido.",
            }), 400

        cursor = mysql.connection.cursor()
        cursor.execute(
            """
            UPDATE productos
            SET nombre = %s, tipo = %s, precio = %s, imagen = %s, categoria = %s
            WHERE id = %s
            """,
            (nombre, tipo, precio, imagen, categoria, producto_id),
        )
        afectados = cursor.rowcount
        mysql.connection.commit()
        cursor.close()

        if afectados == 0:
            return jsonify({
                "status": "error",
                "mensaje": "Producto no encontrado.",
            }), 404

        return jsonify({
            "status": "ok",
            "mensaje": "Producto actualizado correctamente.",
        })

    @app.route("/admin/api/productos/<int:producto_id>/estado", methods=["PATCH"])
    @admin_required
    def admin_cambiar_estado_producto(producto_id):
        data = request.get_json() or {}
        estado = (data.get("estado") or "").strip()

        if estado not in ("activo", "suspendido"):
            return jsonify({
                "status": "error",
                "mensaje": "Estado no válido.",
            }), 400

        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE productos SET estado = %s WHERE id = %s",
            (estado, producto_id),
        )
        mysql.connection.commit()
        afectados = cursor.rowcount
        cursor.close()

        if afectados == 0:
            return jsonify({
                "status": "error",
                "mensaje": "Producto no encontrado.",
            }), 404

        accion = "suspendido" if estado == "suspendido" else "reactivado"
        return jsonify({
            "status": "ok",
            "mensaje": f"Producto {accion} correctamente.",
        })

    @app.route("/admin/api/citas", methods=["GET"])
    @admin_required
    def admin_listar_citas():
        cursor = mysql.connection.cursor()
        cursor.execute(
            """
            SELECT c.id, c.nombre, c.email, c.fecha, c.hora, c.mensaje, u.identificacion
            FROM citas c
            LEFT JOIN usuarios u ON c.usuario_id = u.id
            ORDER BY c.fecha DESC, c.hora DESC
            """
        )
        rows = cursor.fetchall()
        cursor.close()

        citas = []
        for row in rows:
            fecha = row[3]
            if hasattr(fecha, "strftime"):
                fecha_str = fecha.strftime("%Y-%m-%d")
            else:
                fecha_str = str(fecha)[:10]

            citas.append({
                "id": row[0],
                "nombre": row[1],
                "email": row[2],
                "fecha": fecha_str,
                "hora": normalizar_hora_cita(row[4]),
                "mensaje": row[5] or "",
                "identificacion": row[6] or "",
            })

        return jsonify({"status": "ok", "citas": citas})

    return ensure_schema
