import os
import sqlite3
import hashlib
import secrets

DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DB_DIR, 'rethiner.db')


def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL,
            fecha TEXT NOT NULL,
            horario TEXT NOT NULL,
            usuario_id INTEGER,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );

        CREATE TABLE IF NOT EXISTS consultorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            consulta TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS recuperaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest_hex = stored.split('$', 1)
        digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return secrets.compare_digest(digest.hex(), digest_hex)
    except ValueError:
        return False


def crear_usuario(nombre, email, usuario, password):
    conn = get_connection()
    try:
        cur = conn.execute(
            'INSERT INTO usuarios (nombre, email, usuario, password_hash) VALUES (?, ?, ?, ?)',
            (nombre, email, usuario, hash_password(password)),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def buscar_usuario_por_email(email):
    conn = get_connection()
    try:
        return conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
    finally:
        conn.close()


def buscar_usuario_por_usuario(usuario):
    conn = get_connection()
    try:
        return conn.execute('SELECT * FROM usuarios WHERE usuario = ?', (usuario,)).fetchone()
    finally:
        conn.close()


def crear_cita(nombre, telefono, fecha, horario, usuario_id=None):
    conn = get_connection()
    try:
        cur = conn.execute(
            'INSERT INTO citas (nombre, telefono, fecha, horario, usuario_id) VALUES (?, ?, ?, ?, ?)',
            (nombre, telefono, fecha, horario, usuario_id),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def crear_consultoria(nombre, email, consulta):
    conn = get_connection()
    try:
        cur = conn.execute(
            'INSERT INTO consultorias (nombre, email, consulta) VALUES (?, ?, ?)',
            (nombre, email, consulta),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def registrar_recuperacion(email):
    conn = get_connection()
    try:
        cur = conn.execute('INSERT INTO recuperaciones (email) VALUES (?)', (email,))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()
