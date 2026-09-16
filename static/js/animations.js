/**
 * Bhromonghuri GSAP & Lenis Smooth Motion Engine
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lenis Smooth Scroll if available
  if (typeof Lenis !== 'undefined') {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      wheelMultiplier: 1,
    });

    function raf(time) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);
  }

  // Initialize GSAP Animations if available
  if (typeof gsap !== 'undefined') {
    // Hero Elements Stagger Reveal
    const heroTl = gsap.timeline({ defaults: { ease: 'power3.out', duration: 1 } });

    if (document.querySelector('#hero-badge')) {
      heroTl.from('#hero-badge', { y: -20, opacity: 0, delay: 0.2 })
            .from('#hero-title', { y: 30, opacity: 0, duration: 1.2 }, '-=0.6')
            .from('#hero-subtitle', { y: 25, opacity: 0 }, '-=0.8')
            .from('#hero-cta-group', { y: 20, opacity: 0, stagger: 0.15 }, '-=0.7')
            .from('#hero-kite-mascot', { scale: 0.8, y: 40, opacity: 0, duration: 1.4, ease: 'back.out(1.7)' }, '-=1');
    }

    // ScrollTrigger Card Stagger
    if (typeof ScrollTrigger !== 'undefined') {
      gsap.registerPlugin(ScrollTrigger);

      gsap.utils.toArray('.reveal-on-scroll').forEach((elem) => {
        gsap.from(elem, {
          scrollTrigger: {
            trigger: elem,
            start: 'top 85%',
            toggleActions: 'play none none none',
          },
          y: 40,
          opacity: 0,
          duration: 0.8,
          ease: 'power2.out',
        });
      });
    }
  }
});
