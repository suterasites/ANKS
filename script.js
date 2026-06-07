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

    cards.forEach((c, i) => {
      c.addEventListener('click', () => {
        if (i !== activeIndex()) scrollToCard(i);
      });
    });

    setActive();
  }

  // Testimonials swap (click side card to activate)
  const stage = document.getElementById('testimonials-stage');
  if (stage) {
    const cards = Array.from(stage.querySelectorAll('.testimonial-card'));
    cards.forEach((card) => {
      card.addEventListener('click', (e) => {
        if (card.classList.contains('is-active')) return;
        cards.forEach((c) => {
          c.classList.toggle('is-active', c === card);
          const v = c.querySelector('video');
          if (v && c !== card) {
            v.pause();
            try { v.currentTime = 0; } catch (err) { /* ignore */ }
          }
        });
      });
    });
  }

  // Featured Projects hover-preview videos
  const isTouch = window.matchMedia('(hover: none)').matches;
  const fpCards = Array.from(document.querySelectorAll('.fp-card'));
  const fpSoundToggle = document.getElementById('fp-sound-toggle');
  const FP_MUTE_KEY = 'anks-fp-muted';

  // Default: sound on. Stored preference (if any) overrides.
  let fpMuted = false;
  try {
    const stored = sessionStorage.getItem(FP_MUTE_KEY);
    if (stored === 'true') fpMuted = true;
  } catch (e) { /* sessionStorage unavailable, ignore */ }

  function updateSoundToggleUI() {
    if (!fpSoundToggle) return;
    fpSoundToggle.setAttribute('aria-pressed', fpMuted ? 'true' : 'false');
    fpSoundToggle.setAttribute('aria-label', fpMuted ? 'Unmute project videos' : 'Mute project videos');
    const label = fpSoundToggle.querySelector('.fp-sound-label');
    if (label) label.textContent = fpMuted ? 'Sound off' : 'Sound on';
  }
  updateSoundToggleUI();

  function playFpVideo(video) {
    video.muted = fpMuted;
    const p = video.play();
    if (p && typeof p.catch === 'function') {
      p.catch(() => {
        // Browser rejected unmuted autoplay (no user gesture yet). Fall back to muted.
        video.muted = true;
        const fallback = video.play();
        if (fallback && typeof fallback.catch === 'function') fallback.catch(() => {});
      });
    }
  }

  if (fpSoundToggle) {
    fpSoundToggle.addEventListener('click', () => {
      fpMuted = !fpMuted;
      try { sessionStorage.setItem(FP_MUTE_KEY, String(fpMuted)); } catch (e) { /* ignore */ }
      updateSoundToggleUI();
      // Apply to any currently playing video so the toggle is immediate.
      fpCards.forEach((c) => {
        const v = c.querySelector('.fp-img-video');
        if (v && !v.paused) v.muted = fpMuted;
      });
    });
  }

  fpCards.forEach((card) => {
    const video = card.querySelector('.fp-img-video');
    if (!video) return;

    // Desktop: hover plays
    card.addEventListener('mouseenter', () => {
      playFpVideo(video);
    });
    card.addEventListener('mouseleave', () => {
      video.pause();
      try { video.currentTime = 0; } catch (e) { /* ignore */ }
    });

    // Touch: first tap plays the preview, taps elsewhere stop it.
    // Link navigation is suppressed on touch (use the "View all" link in
    // the section header to reach Instagram on mobile).
    if (!isTouch) return;
    card.addEventListener('click', (e) => {
      e.preventDefault();
      const wasActive = card.classList.contains('is-touch-active');
      fpCards.forEach((c) => {
        if (c === card) return;
        c.classList.remove('is-touch-active');
        const v = c.querySelector('.fp-img-video');
        if (v) {
          v.pause();
          try { v.currentTime = 0; } catch (err) { /* ignore */ }
        }
      });
      if (wasActive) {
        card.classList.remove('is-touch-active');
        video.pause();
        try { video.currentTime = 0; } catch (err) { /* ignore */ }
      } else {
        card.classList.add('is-touch-active');
        playFpVideo(video);
      }
    });
  });

  // Touch: tapping outside any FP card pauses the active preview
  if (isTouch) {
    document.addEventListener('touchstart', (e) => {
      if (e.target.closest('.fp-card')) return;
      fpCards.forEach((c) => {
        if (!c.classList.contains('is-touch-active')) return;
        c.classList.remove('is-touch-active');
        const v = c.querySelector('.fp-img-video');
        if (v) {
          v.pause();
          try { v.currentTime = 0; } catch (err) { /* ignore */ }
        }
      });
    }, { passive: true });
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
