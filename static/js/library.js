const isDesktop = () => matchMedia('(min-width: 576px)').matches;

document.body.addEventListener('click', (e) => {
  const toggle = e.target.closest('a[data-submenu]');
  if (!toggle) return;
  e.preventDefault(); e.stopPropagation();

  const li = toggle.closest('.dropdown-submenu');
  const submenu = li.querySelector(':scope > .dropdown-menu');

  // close siblings
  li.closest('.dropdown-menu')
    .querySelectorAll('.dropdown-menu.show')
    .forEach(m => { if (m !== submenu) m.classList.remove('show'); });

  submenu.classList.toggle('show');
  toggle.setAttribute('aria-expanded', submenu.classList.contains('show'));

  // Only desktop needs horizontal overflow flip logic
  if (isDesktop()) {
    requestAnimationFrame(() => {
      const r = submenu.getBoundingClientRect();
      if (r.right > innerWidth) {
        li.classList.add('dropstart');
        submenu.style.left = 'auto';
        submenu.style.right = '100%';
      } else {
        li.classList.remove('dropstart');
        submenu.style.right = '';
        submenu.style.left = '';
      }
    });
  }
});
