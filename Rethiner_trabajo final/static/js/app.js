// ===== CONSULTORÍA VISUAL =====
function abrirConsultoria() {
  document.getElementById('modalConsultoria').classList.add('open');
}

function cerrarConsultoria() {
  document.getElementById('modalConsultoria').classList.remove('open');
  document.getElementById('c-nombre').value = '';
  document.getElementById('c-email').value = '';
  document.getElementById('c-consulta').value = '';
}

async function enviarConsultoria() {
  const nombre = document.getElementById('c-nombre').value.trim();
  const email = document.getElementById('c-email').value.trim();
  const consulta = document.getElementById('c-consulta').value.trim();

  if (!nombre) {
    await rethinerAlert('Por favor ingresa tu nombre.');
    document.getElementById('c-nombre').focus();
    return;
  }
  if (!email || !email.includes('@')) {
    await rethinerAlert('Por favor ingresa un correo electrónico válido.');
    document.getElementById('c-email').focus();
    return;
  }
  if (!consulta) {
    await rethinerAlert('Por favor describe tu consulta.');
    document.getElementById('c-consulta').focus();
    return;
  }

  try {
    const res = await fetch('/api/consultorias', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre, email, consulta }),
    });
    const data = await res.json();
    if (!res.ok) {
      await rethinerAlert(data.error || 'No se pudo enviar la consulta.', 'error');
      return;
    }

    cerrarConsultoria();
    document.getElementById('modalMsg').textContent =
      `¡Gracias ${nombre}! Hemos recibido tu consulta visual. Un especialista te escribirá a ${email} en menos de 24 horas.`;
    document.getElementById('modalOverlay').classList.add('open');
  } catch {
    await rethinerAlert('No se pudo conectar con el servidor. Ejecuta "python3 server.py" y abre http://localhost:3000', 'error');
  }
}

function toggleMenu() {
  const menu = document.getElementById('mobileMenu');
  menu.classList.toggle('open');
}

// ===== SCROLL TO CITA =====
function scrollToCita() {
  document.getElementById('cita').scrollIntoView({ behavior: 'smooth' });
}

// ===== TIME SLOT SELECTION =====
let selectedSlot = null;

function selectSlot(btn) {
  document.querySelectorAll('.slot').forEach(s => s.classList.remove('selected'));
  btn.classList.add('selected');
  selectedSlot = btn.textContent;
}

function getUsuarioSesion() {
  try {
    const raw = localStorage.getItem('rethiner_user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

async function cerrarSesion() {
  await RethinerAlert.show({
    title: '¡Hasta pronto!',
    text: 'Has cerrado sesión correctamente.',
    type: 'success',
  });

  localStorage.removeItem('usuarioNombre');
  localStorage.removeItem('usuarioEmail');
  localStorage.removeItem('rethiner_user');

  try {
    await fetch('/cerrar-sesion', { credentials: 'same-origin' });
  } catch (_) {
    /* la red puede fallar; igual redirigimos */
  }

  window.location.href = '/login';
}

// ===== RESERVAR CITA =====
let reservandoCita = false;

async function reservarCita() {
  if (reservandoCita) return;

  const nombre = document.getElementById("nombre").value.trim();
  const email = document.getElementById("email").value.trim();
  const fecha = document.getElementById("fecha").value;
  const hora = document.getElementById("hora").value;
  const mensaje = document.getElementById("mensaje").value.trim();
  const btn = document.getElementById("btn-reservar-cita");

  if (!nombre || !email || !fecha || !hora) {
    await rethinerAlert("Completa todos los campos.");
    return;
  }

  if (!/^\d{2}:\d{2}$/.test(hora)) {
    await rethinerAlert("Selecciona un horario válido de la lista.", "warning");
    return;
  }

  reservandoCita = true;
  if (btn) {
    btn.disabled = true;
    btn.textContent = "Reservando...";
  }

  try {
    const res = await fetch("/contacto", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify({ nombre, email, fecha, hora, mensaje }),
    });

    const data = await res.json();

    if (data.status === "ok") {
      await RethinerAlert.show({
        title: "¡Cita agendada!",
        text: "La cita fue agendada correctamente.",
        type: "success",
      });

      document.getElementById("nombre").value = "";
      document.getElementById("email").value = "";
      document.getElementById("fecha").value = "";
      document.getElementById("mensaje").value = "";
      document.getElementById("hora").innerHTML = `
        <option value="">Selecciona una hora</option>
      `;
    } else {
      await rethinerAlert(data.mensaje || "No se pudo agendar la cita.", "error");
    }
  } catch {
    await rethinerAlert("Error al conectar con el servidor.", "error");
  } finally {
    reservandoCita = false;
    if (btn) {
      btn.disabled = false;
      btn.textContent = "Reservar Cita";
    }
  }
}
