/* Dokumenty prawne: podświetla w spisie treści sekcję, którą właśnie czytasz. Bez zewnętrznych bibliotek.
   Kliknięta pozycja zostaje podświetlona także wtedy, gdy krótkie sekcje na końcu strony
   nie mogą dojechać do góry ekranu. */
(function () {
  'use strict';
  var linki = Array.prototype.slice.call(document.querySelectorAll('.legal-toc a[href^="#"]'));
  if (!linki.length) return;
  var sekcje = linki.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
  var wybrana = null;   // sekcja kliknięta w spisie; trzyma podświetlenie do następnego ręcznego przewinięcia
  var czekaj = false;

  function zaznacz(id) {
    linki.forEach(function (a) {
      if (a.getAttribute('href') === '#' + id) a.setAttribute('aria-current', 'true');
      else a.removeAttribute('aria-current');
    });
  }

  function aktywna() {
    var prog = window.innerHeight * 0.3;
    var naDole = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4;
    var id = null;
    for (var i = 0; i < sekcje.length; i++) {
      if (!sekcje[i]) continue;
      var gora = sekcje[i].getBoundingClientRect().top;
      if (gora <= prog || (naDole && gora < window.innerHeight)) id = sekcje[i].id;
    }
    return id || (sekcje[0] && sekcje[0].id);
  }

  function odswiez() {
    czekaj = false;
    if (wybrana) return;
    var id = aktywna();
    if (id) zaznacz(id);
  }

  linki.forEach(function (a) {
    a.addEventListener('click', function () {
      wybrana = a.getAttribute('href').slice(1);
      zaznacz(wybrana);
    });
  });

  // Ręczne przewinięcie (kółko, dotyk, klawisze) zwalnia podświetlenie z kliknięcia.
  ['wheel', 'touchstart', 'keydown'].forEach(function (typ) {
    window.addEventListener(typ, function () { wybrana = null; }, { passive: true });
  });

  window.addEventListener('scroll', function () {
    if (!czekaj) { czekaj = true; window.requestAnimationFrame(odswiez); }
  }, { passive: true });

  if (location.hash && document.getElementById(location.hash.slice(1))) {
    wybrana = location.hash.slice(1);
    zaznacz(wybrana);
  } else {
    odswiez();
  }
})();
