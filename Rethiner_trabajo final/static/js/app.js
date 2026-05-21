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
    alert('Por favor ingresa tu nombre.');
    document.getElementById('c-nombre').focus();
    return;
  }
  if (!email || !email.includes('@')) {
    alert('Por favor ingresa un correo electrónico válido.');
    document.getElementById('c-email').focus();
    return;
  }
  if (!consulta) {
    alert('Por favor describe tu consulta.');
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
      alert(data.error || 'No se pudo enviar la consulta.');
      return;
    }

    cerrarConsultoria();
    document.getElementById('modalMsg').textContent =
      `¡Gracias ${nombre}! Hemos recibido tu consulta visual. Un especialista te escribirá a ${email} en menos de 24 horas.`;
    document.getElementById('modalOverlay').classList.add('open');
  } catch {
    alert('No se pudo conectar con el servidor. Ejecuta "python3 server.py" y abre http://localhost:3000');
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

// ===== RESERVAR CITA =====

  // ===== RESERVAR CITA =====
async function reservarCita(){

    const nombre =
    document.getElementById("nombre").value;

    const email =
    document.getElementById("email").value;

    const fecha =
    document.getElementById("fecha").value;

    const hora =
    document.getElementById("hora").value;

    const mensaje =
    document.getElementById("mensaje").value;

    // VALIDAR
    if(
        !nombre ||
        !email ||
        !fecha ||
        !hora
    ){

        alert("Completa todos los campos.");

        return;
    }

    try{

        const res = await fetch("/contacto", {

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                nombre,
                email,
                fecha,
                hora,
                mensaje
            })

        });

        const data = await res.json();

        // =========================
        // CITA EXITOSA
        // =========================
        if(data.status === "ok"){

            alert("La cita fue agendada correctamente.");

            // LIMPIAR FORMULARIO
            document.getElementById("nombre").value = "";

            document.getElementById("email").value = "";

            document.getElementById("fecha").value = "";

            document.getElementById("mensaje").value = "";

            document.getElementById("hora").innerHTML = `
              <option value="">
                Selecciona una hora
              </option>
            `;

        }else{

            alert(data.mensaje);

        }

    }catch(error){

        alert("Error al conectar con el servidor.");

    }

}