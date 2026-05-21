const STORAGE_KEY = 'rethiner_user';

function getUsuarioSesion() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function guardarSesion(user) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
}

function cerrarSesion() {
  localStorage.removeItem(STORAGE_KEY);
}

async function apiPost(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || 'Error en la solicitud.');
  }
  return data;
}

function mostrarError(el, mensaje) {
  if (!el) {
    alert(mensaje);
    return;
  }
  el.textContent = mensaje;
  el.style.display = 'block';
  el.style.color = '#c0392b';
}

function mostrarExito(el, mensaje) {
  if (!el) {
    alert(mensaje);
    return;
  }
  el.textContent = mensaje;
  el.style.display = 'block';
  el.style.color = '#27ae60';
}
