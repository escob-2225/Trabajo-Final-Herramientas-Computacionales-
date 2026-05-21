const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

const dataDir = path.join(__dirname, 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

const db = new Database(path.join(dataDir, 'rethiner.db'));

db.exec(`
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
`);

function crearUsuario({ nombre, email, usuario, passwordHash }) {
  const stmt = db.prepare(`
    INSERT INTO usuarios (nombre, email, usuario, password_hash)
    VALUES (@nombre, @email, @usuario, @passwordHash)
  `);
  return stmt.run({ nombre, email, usuario, passwordHash });
}

function buscarUsuarioPorEmail(email) {
  return db.prepare('SELECT * FROM usuarios WHERE email = ?').get(email);
}

function buscarUsuarioPorUsuario(usuario) {
  return db.prepare('SELECT * FROM usuarios WHERE usuario = ?').get(usuario);
}

function buscarUsuarioPorId(id) {
  return db.prepare('SELECT id, nombre, email, usuario FROM usuarios WHERE id = ?').get(id);
}

function crearCita({ nombre, telefono, fecha, horario, usuarioId }) {
  const stmt = db.prepare(`
    INSERT INTO citas (nombre, telefono, fecha, horario, usuario_id)
    VALUES (@nombre, @telefono, @fecha, @horario, @usuarioId)
  `);
  return stmt.run({
    nombre,
    telefono,
    fecha,
    horario,
    usuarioId: usuarioId || null,
  });
}

function crearConsultoria({ nombre, email, consulta }) {
  const stmt = db.prepare(`
    INSERT INTO consultorias (nombre, email, consulta)
    VALUES (@nombre, @email, @consulta)
  `);
  return stmt.run({ nombre, email, consulta });
}

function registrarRecuperacion(email) {
  const stmt = db.prepare('INSERT INTO recuperaciones (email) VALUES (?)');
  return stmt.run(email);
}

module.exports = {
  db,
  crearUsuario,
  buscarUsuarioPorEmail,
  buscarUsuarioPorUsuario,
  buscarUsuarioPorId,
  crearCita,
  crearConsultoria,
  registrarRecuperacion,
};
