/* ANKS Construction and Landscaping - homepage draft script */

(function () {
  'use strict';

  // Preloader - show for a fixed 1.5s, then fade out
  const preloader = document.getElementById('preloader');
  if (preloader) {
    setTimeout(() => {
      preloader.classList.add('is-hidden');
      setTimeout(() => { preloader.style.display = 'none'; }, 650);
    }, 1500);
  }

  // Mobile nav toggle
  const toggle = document.getElementById('nav-toggle');
  const mobileNav = document.getElementById('mobile-nav');

  // Header solid-on-scroll + hide on scroll down, show on scroll up
  const header = document.getElementById('site-header');
  let lastScroll = 0;
  function onScroll() {
    const y = window.scrollY;
    if (y > 80) header.classList.add('is-scrolled');
    else header.classList.remove('is-scrolled');

    const menuOpen = mobileNav && mobileNav.classList.contains('is-open');
    if (Math.abs(y - lastScroll) > 5 && !menuOpen) {
      if (y > lastScroll && y > 200) header.classList.add('is-hidden');
      else header.classList.remove('is-hidden');
    }
    lastScroll = y;
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if (toggle && mobileNav) {
    toggle.addEventListener('click', () => {
      const open = mobileNav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });
    // Close on link click
    mobileNav.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        mobileNav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // Footer year
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  // FAQ accordion - one open at a time
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach((item) => {
    item.addEventListener('toggle', () => {
      if (item.open) {
        faqItems.forEach((other) => {
          if (other !== item) other.open = false;
        });
      }
    });
  });

  // Services carousel
  const track = document.getElementById('services-track');
  if (track) {
    const cards = Array.from(track.children);
    const prev = document.getElementById('services-prev');
    const next = document.getElementById('services-next');

    function activeIndex() {
      const center = track.scrollLeft + track.clientWidth / 2;
      let best = 0, bestDist = Infinity;
      cards.forEach((c, i) => {
        const cc = c.offsetLeft + c.offsetWidth / 2;
        const d = Math.abs(cc - center);
        if (d < bestDist) { bestDist = d; best = i; }
      });
      return best;
    }
    function setActive() {
      const idx = activeIndex();
      cards.forEach((c, i) => c.classList.toggle('is-active', i === idx));
    }
    function scrollToCard(i) {
      const c = cards[Math.max(0, Math.min(cards.length - 1, i))];
      if (c) track.scrollTo({ left: c.offsetLeft - (track.clientWidth - c.offsetWidth) / 2, behavior: 'smooth' });
    }

    let raf = null;
    track.addEventListener('scroll', () => {
      if (raf) cancelAnimationFrame(raf);
      raf = requestAnimationFrame(setActive);
    }, { passive: true });
    if (prev) prev.addEventListener('click', () => scrollToCard(activeIndex() - 1));
    if (next) next.addEventListener('click', () => scrollToCard(activeIndex() + 1));
    setActive();
  }

  // Hero video reduced-motion fallback
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const video = document.getElementById('hero-video');
    if (video) {
      video.pause();
      video.removeAttribute('autoplay');
    }
  }
})();
