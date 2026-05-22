(function (global) {
  const ICONS = {
    success: `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M5 13l4 4L19 7"/>
      </svg>`,
    error: `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true">
        <path d="M6 6l12 12M18 6L6 18"/>
      </svg>`,
    warning: `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M12 9v4M12 17h.01"/>
        <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
      </svg>`,
    info: `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true">
        <circle cx="12" cy="12" r="10"/>
        <path d="M12 16v-4M12 8h.01"/>
      </svg>`,
  };

  let overlay = null;
  let resolvePromise = null;

  function ensureDom() {
    if (overlay) return overlay;

    overlay = document.createElement('div');
    overlay.id = 'rethiner-alert-overlay';
    overlay.className = 'rethiner-alert-overlay';
    overlay.innerHTML = `
      <div class="rethiner-alert-box" role="alertdialog" aria-modal="true" aria-labelledby="rethiner-alert-title" aria-describedby="rethiner-alert-text">
        <div class="rethiner-alert-icon-wrap">
          <span class="rethiner-alert-sparkle rethiner-alert-sparkle--tl" aria-hidden="true">✦</span>
          <span class="rethiner-alert-sparkle rethiner-alert-sparkle--tr" aria-hidden="true">✦</span>
          <span class="rethiner-alert-sparkle rethiner-alert-sparkle--bl" aria-hidden="true">✦</span>
          <div class="rethiner-alert-icon rethiner-alert-icon--success" id="rethiner-alert-icon"></div>
        </div>
        <h2 class="rethiner-alert-title" id="rethiner-alert-title"></h2>
        <p class="rethiner-alert-text" id="rethiner-alert-text"></p>
        <button type="button" class="rethiner-alert-btn" id="rethiner-alert-btn">OK</button>
      </div>
    `;

    document.body.appendChild(overlay);

    overlay.querySelector('#rethiner-alert-btn').addEventListener('click', close);
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) close();
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && overlay.classList.contains('is-open')) close();
    });

    return overlay;
  }

  function close() {
    if (!overlay) return;
    overlay.classList.remove('is-open');
    document.body.style.overflow = '';
    const fn = resolvePromise;
    resolvePromise = null;
    if (fn) fn();
  }

  function inferType(message) {
    const m = String(message || '').toLowerCase();
    if (/correctamente|agendada|éxito|exito|bienvenido|agregado|recibid|gracias|listo/.test(m)) {
      return 'success';
    }
    if (/error|incorrect|inválid|invalid|no se pudo|falló|fallo|denegad/.test(m)) {
      return 'error';
    }
    if (/completa|ingresa|por favor|describe|válid/.test(m)) {
      return 'warning';
    }
    return 'info';
  }

  function defaultTitle(type) {
    const titles = {
      success: '¡Listo!',
      error: '¡Ups!',
      warning: 'Atención',
      info: 'Aviso',
    };
    return titles[type] || titles.info;
  }

  function show(options) {
    const opts = typeof options === 'string' ? { text: options } : { ...options };
    const type = opts.type || inferType(opts.text);
    const title = opts.title || defaultTitle(type);
    const text = opts.text || '';
    const confirmText = opts.confirmText || 'OK';

    ensureDom();

    const iconEl = overlay.querySelector('#rethiner-alert-icon');
    const sparkles = overlay.querySelectorAll('.rethiner-alert-sparkle');

    iconEl.className = `rethiner-alert-icon rethiner-alert-icon--${type}`;
    iconEl.innerHTML = ICONS[type] || ICONS.info;

    sparkles.forEach((el) => {
      el.style.display = type === 'success' ? '' : 'none';
    });

    overlay.querySelector('#rethiner-alert-title').textContent = title;
    overlay.querySelector('#rethiner-alert-text').textContent = text;
    overlay.querySelector('#rethiner-alert-btn').textContent = confirmText;

    document.body.style.overflow = 'hidden';
    overlay.classList.add('is-open');

    return new Promise((resolve) => {
      resolvePromise = resolve;
    });
  }

  function alertMessage(message, type) {
    return show({ text: message, type: type || inferType(message) });
  }

  const RethinerAlert = { show, alert: alertMessage };

  global.RethinerAlert = RethinerAlert;
  global.rethinerAlert = alertMessage;
})(typeof window !== 'undefined' ? window : globalThis);
