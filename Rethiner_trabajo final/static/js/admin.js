const tablaProductos = document.getElementById('tabla-productos');
const tablaCitas = document.getElementById('tabla-citas');
const modalProducto = document.getElementById('modal-producto');
const formProducto = document.getElementById('form-producto');

let productosCache = [];

function formatoPrecio(valor) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  }).format(valor);
}

function formatoFecha(fecha) {
  if (!fecha) return '—';
  const [y, m, d] = fecha.split('-');
  return `${d}/${m}/${y}`;
}

document.querySelectorAll('.admin-tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.admin-tab').forEach((t) => t.classList.remove('active'));
    document.querySelectorAll('.admin-panel').forEach((p) => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(`panel-${tab.dataset.panel}`).classList.add('active');
  });
});

document.getElementById('btn-nuevo-producto').addEventListener('click', () => {
  abrirModalProducto();
});

document.getElementById('btn-cerrar-modal').addEventListener('click', cerrarModalProducto);
modalProducto.addEventListener('click', cerrarModalProducto);

document.getElementById('btn-refrescar-citas').addEventListener('click', cargarCitas);

formProducto.addEventListener('submit', async (e) => {
  e.preventDefault();
  await guardarProducto();
});

async function cargarProductos() {
  const res = await fetch('/admin/api/productos');
  const data = await res.json();

  if (data.status !== 'ok') {
    await rethinerAlert(data.mensaje || 'No se pudieron cargar los productos.', 'error');
    return;
  }

  productosCache = data.productos;
  renderProductos(productosCache);
  actualizarStats();
}

function renderProductos(productos) {
  tablaProductos.innerHTML = '';
  const empty = document.getElementById('productos-empty');
  empty.style.display = productos.length ? 'none' : 'block';

  productos.forEach((p) => {
    const tr = document.createElement('tr');
    const activo = p.estado === 'activo';
    tr.innerHTML = `
      <td>${p.id}</td>
      <td><strong>${p.nombre}</strong></td>
      <td>${p.tipo || '—'}</td>
      <td>${p.categoria}</td>
      <td>${formatoPrecio(p.precio)}</td>
      <td><code>${p.imagen}</code></td>
      <td>
        <span class="admin-badge ${activo ? 'admin-badge-activo' : 'admin-badge-suspendido'}">
          ${activo ? 'Activo' : 'Suspendido'}
        </span>
      </td>
      <td>
        <div class="admin-actions">
          <button type="button" class="admin-btn admin-btn-outline admin-btn-sm" data-editar="${p.id}">Editar</button>
          <button type="button" class="admin-btn ${activo ? 'admin-btn-warning' : 'admin-btn-success'} admin-btn-sm" data-estado="${p.id}" data-activo="${activo}">
            ${activo ? 'Suspender' : 'Activar'}
          </button>
        </div>
      </td>
    `;
    tablaProductos.appendChild(tr);
  });

  tablaProductos.querySelectorAll('[data-editar]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const id = Number(btn.dataset.editar);
      const producto = productosCache.find((x) => x.id === id);
      if (producto) abrirModalProducto(producto);
    });
  });

  tablaProductos.querySelectorAll('[data-estado]').forEach((btn) => {
    btn.addEventListener('click', () => cambiarEstadoProducto(Number(btn.dataset.estado), btn.dataset.activo === 'true'));
  });
}

async function cambiarEstadoProducto(id, estaActivo) {
  const nuevoEstado = estaActivo ? 'suspendido' : 'activo';
  const confirmar = await RethinerAlert.show({
    title: estaActivo ? '¿Suspender producto?' : '¿Activar producto?',
    text: estaActivo
      ? 'El producto dejará de mostrarse en la tienda.'
      : 'El producto volverá a estar visible en el catálogo.',
    type: 'warning',
    confirmText: 'Confirmar',
  });

  if (!confirmar) return;

  const res = await fetch(`/admin/api/productos/${id}/estado`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ estado: nuevoEstado }),
  });
  const data = await res.json();

  if (data.status === 'ok') {
    await rethinerAlert(data.mensaje, 'success');
    cargarProductos();
  } else {
    await rethinerAlert(data.mensaje || 'No se pudo actualizar.', 'error');
  }
}

function abrirModalProducto(producto = null) {
  document.getElementById('modal-titulo').textContent = producto ? 'Editar producto' : 'Nuevo producto';
  document.getElementById('producto-id').value = producto ? producto.id : '';
  document.getElementById('producto-nombre').value = producto ? producto.nombre : '';
  document.getElementById('producto-tipo').value = producto ? producto.tipo || '' : '';
  document.getElementById('producto-precio').value = producto ? producto.precio : '';
  document.getElementById('producto-categoria').value = producto ? producto.categoria : '';
  document.getElementById('producto-imagen').value = producto ? producto.imagen : '';
  modalProducto.classList.add('open');
}

function cerrarModalProducto() {
  modalProducto.classList.remove('open');
  formProducto.reset();
  document.getElementById('producto-id').value = '';
}

async function guardarProducto() {
  const id = document.getElementById('producto-id').value;
  const payload = {
    nombre: document.getElementById('producto-nombre').value.trim(),
    tipo: document.getElementById('producto-tipo').value.trim(),
    precio: document.getElementById('producto-precio').value,
    categoria: document.getElementById('producto-categoria').value,
    imagen: document.getElementById('producto-imagen').value.trim(),
  };

  const url = id ? `/admin/api/productos/${id}` : '/admin/api/productos';
  const method = id ? 'PUT' : 'POST';

  const res = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json();

  if (data.status === 'ok') {
    await rethinerAlert(data.mensaje, 'success');
    cerrarModalProducto();
    cargarProductos();
  } else {
    await rethinerAlert(data.mensaje || 'No se pudo guardar.', 'error');
  }
}

async function cargarCitas() {
  const res = await fetch('/admin/api/citas');
  const data = await res.json();

  if (data.status !== 'ok') {
    await rethinerAlert(data.mensaje || 'No se pudieron cargar las citas.', 'error');
    return;
  }

  renderCitas(data.citas);
  document.getElementById('stat-citas').textContent = data.citas.length;
}

function renderCitas(citas) {
  tablaCitas.innerHTML = '';
  const empty = document.getElementById('citas-empty');
  empty.style.display = citas.length ? 'none' : 'block';

  citas.forEach((c) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${c.nombre}</strong></td>
      <td>${c.identificacion ? `CC ${c.identificacion}` : '—'}</td>
      <td>${c.email}</td>
      <td>${formatoFecha(c.fecha)}</td>
      <td><strong>${c.hora}</strong></td>
      <td>${c.mensaje || '—'}</td>
    `;
    tablaCitas.appendChild(tr);
  });
}

function actualizarStats() {
  document.getElementById('stat-productos').textContent = productosCache.length;
  document.getElementById('stat-activos').textContent = productosCache.filter(
    (p) => p.estado === 'activo'
  ).length;
}

cargarProductos();
cargarCitas();
