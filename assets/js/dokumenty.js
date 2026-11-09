/* Dokumenty prawne: podświetla w spisie treści sekcję, którą właśnie czytasz. Bez zewnętrznych bibliotek. */
(function () {
  'use strict';
  var linki = Array.prototype.slice.call(document.querySelectorAll('.legal-toc a[href^="#"]'));
  if (!linki.length || !('IntersectionObserver' in window)) return;
  var sekcje = linki.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
  function zaznacz(id) {
    linki.forEach(function (a) {
      if (a.getAttribute('href') === '#' + id) a.setAttribute('aria-current', 'true');
      else a.removeAttribute('aria-current');
    });
  }
  var widoczne = {};
  var obs = new IntersectionObserver(function (wpisy) {
    wpisy.forEach(function (w) { widoczne[w.target.id] = w.isIntersecting; });
    for (var i = 0; i < sekcje.length; i++) {
      if (sekcje[i] && widoczne[sekcje[i].id]) { zaznacz(sekcje[i].id); return; }
    }
  }, { rootMargin: '-15% 0px -60% 0px' });
  sekcje.forEach(function (s) { if (s) obs.observe(s); });
})();
