(() => {
  'use strict';
  const themeButtons = document.querySelectorAll('[data-theme-choice]');
  function setTheme(theme) {
    if (theme === 'light') delete document.documentElement.dataset.theme;
    else document.documentElement.dataset.theme = theme;
    themeButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.themeChoice === theme)));
    try { localStorage.setItem('mzy-theme-v2', theme); } catch (_) { /* Themes still work without storage. */ }
  }
  themeButtons.forEach(button => button.addEventListener('click', () => setTheme(button.dataset.themeChoice)));
  setTheme(document.documentElement.dataset.theme || 'light');
  const languageToggle = document.querySelector('.language-toggle');
  function updateLanguageLink() {
    if (languageToggle) languageToggle.hash = window.location.hash;
  }
  updateLanguageLink();
  window.addEventListener('hashchange', updateLanguageLink);
  const track = document.getElementById('projects-track');
  const previous = document.getElementById('projects-prev');
  const next = document.getElementById('projects-next');
  if (track && previous && next) {
    function updateControls() {
      previous.disabled = track.scrollLeft <= 2;
      next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 2;
    }
    function scrollProjects(direction) {
      track.scrollBy({ left: direction * (track.querySelector('.project-card').offsetWidth + 18), behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
    }
    previous.addEventListener('click', () => scrollProjects(-1));
    next.addEventListener('click', () => scrollProjects(1));
    track.addEventListener('scroll', updateControls, { passive: true });
    window.addEventListener('resize', updateControls);
    updateControls();
  }
  const links = [...document.querySelectorAll('.site-nav__link')];
  function markSection() {
    let active = links[0];
    links.forEach(link => {
      if (document.querySelector(link.hash).getBoundingClientRect().top <= 160) active = link;
    });
    links.forEach(link => {
      if (link === active) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }
  window.addEventListener('scroll', markSection, { passive: true });
  markSection();
})();
