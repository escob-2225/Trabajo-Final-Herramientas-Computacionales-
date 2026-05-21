const express = require('express');
const path = require('path');
const bcrypt = require('bcryptjs');
const {
  crearUsuario,
  buscarUsuarioPorEmail,
  buscarUsuarioPorUsuario,
  crearCita,
  crearConsultoria,
  registrarRecuperacion,
} = require('./database');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(__dirname));

function usuarioPublico(row) {
  if (!row) return null;
  return { id: row.id, nombre: row.nombre, email: row.email, usuario: row.usuario };
}

app.post('/api/registro', async (req, res) => {
  try {
    const { nombre, email, usuario, password, confirmar } = req.body;

    if (!nombre?.trim() || !email?.trim() || !usuario?.trim() || !password) {
      return res.status(400).json({ ok: false, error: 'Completa todos los campos.' });
    }
    if (!email.includes('@')) {
      return res.status(400).json({ ok: false, error: 'Correo electrónico inválido.' });
    }
    if (password.length < 6) {
      return res.status(400).json({ ok: false, error: 'La contraseña debe tener al menos 6 caracteres.' });
    }
    if (password !== confirmar) {
      return res.status(400).json({ ok: false, error: 'Las contraseñas no coinciden.' });
    }
    if (buscarUsuarioPorEmail(email.trim().toLowerCase())) {
      return res.status(409).json({ ok: false, error: 'Este correo ya está registrado.' });
    }
    if (buscarUsuarioPorUsuario(usuario.trim())) {
      return res.status(409).json({ ok: false, error: 'Este nombre de usuario ya existe.' });
    }

    const passwordHash = await bcrypt.hash(password, 10);
    const result = crearUsuario({
      nombre: nombre.trim(),
      email: email.trim().toLowerCase(),
      usuario: usuario.trim(),
      passwordHash,
    });

    res.status(201).json({
      ok: true,
      message: 'Usuario creado exitosamente.',
      user: { id: result.lastInsertRowid, nombre: nombre.trim(), email: email.trim().toLowerCase(), usuario: usuario.trim() },
    });
  } catch (err) {
    console.error(err1);
    res.status(500).json({ ok: false, error: 'Error al crear la cuenta.' });
  }
});

app.post('/api/login', async (req, res) => {
  try {
    const { usuario, password } = req.body;

    if (!usuario?.trim() || !password) {
      return res.status(400).json({ ok: false, error: 'Ingresa usuario y contraseña.' });
    }

    const identificador = usuario.trim();
    let user =
      buscarUsuarioPorEmail(identificador.toLowerCase()) ||
      buscarUsuarioPorUsuario(identificador);

    if (!user) {
      return res.status(401).json({ ok: false, error: 'Usuario o contraseña incorrectos.' });
    }

    const valido = await bcrypt.compare(password, user.password_hash);
    if (!valido) {
      return res.status(401).json({ ok: false, error: 'Usuario o contraseña incorrectos.' });
    }

    res.json({ ok: true, user: usuarioPublico(user) });
  } catch (err) {
    console.error(err);
    res.status(500).json({ ok: false, error: 'Error al iniciar sesión.' });
  }
});

app.post('/api/recuperar', (req, res) => {
  try {
    const { email } = req.body;
    if (!email?.trim() || !email.includes('@')) {
      return res.status(400).json({ ok: false, error: 'Ingresa un correo válido.' });
    }

    registrarRecuperacion(email.trim().toLowerCase());
    res.json({
      ok: true,
      message: 'Solicitud registrada. Si el correo existe, recibirás instrucciones pronto.',
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ ok: false, error: 'Error al procesar la solicitud.' });
  }
});

app.post('/api/citas', (req, res) => {
  try {
    const { nombre, telefono, fecha, horario, usuarioId } = req.body;

    if (!nombre?.trim() || !telefono?.trim() || !fecha || !horario) {
      return res.status(400).json({ ok: false, error: 'Completa todos los campos de la cita.' });
    }

    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    const fechaCita = new Date(fecha + 'T00:00:00');
    if (fechaCita < hoy) {
      return res.status(400).json({ ok: false, error: 'La fecha debe ser hoy o posterior.' });
    }

    const result = crearCita({
      nombre: nombre.trim(),
      telefono: telefono.trim(),
      fecha,
      horario,
      usuarioId: usuarioId || null,
    });

    res.status(201).json({ ok: true, id: result.lastInsertRowid });
  } catch (err) {
    console.error(err);
    res.status(500).json({ ok: false, error: 'Error al guardar la cita.' });
  }
});

app.post('/api/consultorias', (req, res) => {
  try {
    const { nombre, email, consulta } = req.body;

    if (!nombre?.trim() || !email?.trim() || !consulta?.trim()) {
      return res.status(400).json({ ok: false, error: 'Completa todos los campos.' });
    }
    if (!email.includes('@')) {
      return res.status(400).json({ ok: false, error: 'Correo electrónico inválido.' });
    }

    const result = crearConsultoria({
      nombre: nombre.trim(),
      email: email.trim(),
      consulta: consulta.trim(),
    });

    res.status(201).json({ ok: true, id: result.lastInsertRowid });
  } catch (err) {
    console.error(err);
    res.status(500).json({ ok: false, error: 'Error al enviar la consulta.' });
  }
});

app.get('/api/health', (_req, res) => {
  res.json({ ok: true, message: 'Servidor y base de datos activos.' });
});

app.listen(PORT, () => {
  console.log(`Rethiner: http://localhost:${PORT}`);
  console.log(`Base de datos: ${path.join(__dirname, 'data', 'rethiner.db')}`);
});
