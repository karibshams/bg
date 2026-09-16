/**
 * Bhromonghuri Magnetic Button Effect
 * Pulls buttons gently toward cursor on hover for a tactile, playful feel.
 */

document.addEventListener('DOMContentLoaded', () => {
  const magnets = document.querySelectorAll('.magnetic-btn');

  magnets.forEach((btn) => {
    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;

      btn.style.transform = `translate(${x * 0.25}px, ${y * 0.25}px)`;
    });

    btn.addEventListener('mouseleave', () => {
      btn.style.transform = 'translate(0px, 0px)';
      btn.style.transition = 'transform 0.4s cubic-bezier(0.25, 1, 0.5, 1)';
    });

    btn.addEventListener('mouseenter', () => {
      btn.style.transition = 'none';
    });
  });
});
