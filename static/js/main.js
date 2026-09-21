/**
 * Bhromonghuri Core JavaScript
 * Handles HTMX CSRF integration, navbar scroll effects, and mobile helpers.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Ensure HTMX sends CSRF Token with every request
  document.body.addEventListener('htmx:configRequest', (event) => {
    const csrfCookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    if (csrfCookie) {
      event.detail.headers['X-CSRFToken'] = csrfCookie.split('=')[1];
    }
  });

  // Sticky Navbar Glass effect on scroll (Passive listener + RAF for 60fps/120fps performance)
  const navbar = document.getElementById('main-navbar');
  if (navbar) {
    let ticking = false;
    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          if (window.scrollY > 40) {
            navbar.classList.add('bg-slate-900/95', 'shadow-xl', 'py-3');
            navbar.classList.remove('bg-transparent', 'py-5');
          } else {
            navbar.classList.remove('bg-slate-900/95', 'shadow-xl', 'py-3');
            navbar.classList.add('bg-transparent', 'py-5');
          }
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }
});
