// Modo escuro com persistência em localStorage (item 9)
(function () {
  const body = document.body;
  const toggleBtn = document.getElementById('darkModeToggle');

  function aplicarModo(escuro) {
    body.classList.toggle('dark-mode', escuro);
    if (toggleBtn) {
      const icon = toggleBtn.querySelector('i');
      if (icon) {
        icon.className = escuro ? 'bi bi-sun' : 'bi bi-moon-stars';
      }
    }
  }

  const preferenciaSalva = localStorage.getItem('modoEscuro') === 'true';
  aplicarModo(preferenciaSalva);

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const novoEstado = !body.classList.contains('dark-mode');
      aplicarModo(novoEstado);
      localStorage.setItem('modoEscuro', novoEstado);
    });
  }
})();
