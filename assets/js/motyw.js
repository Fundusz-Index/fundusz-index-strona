/* Motyw jasny i ciemny: przycisk w prawym górnym rogu nagłówka, przed przełącznikiem języka. Domyślnie strona idzie za ustawieniem
   systemu. Wybór działa tylko na bieżącej stronie: niczego nie zapisujemy w przeglądarce
   (polityka prywatności, pkt 7), więc po przejściu na inną stronę wraca motyw systemu. */
(function () {
  'use strict';
  var root = document.documentElement;
  var systemCiemny = window.matchMedia('(prefers-color-scheme: dark)');
  var SLONCE = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.5"/><path d="M12 1.5v3M12 19.5v3M1.5 12h3M19.5 12h3M4.6 4.6l2.1 2.1M17.3 17.3l2.1 2.1M4.6 19.4l2.1-2.1M17.3 6.7l2.1-2.1"/></svg>';
  var KSIEZYC = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 14.2A8.5 8.5 0 1 1 9.8 3.5a7 7 0 0 0 10.7 10.7z"/></svg>';

  function ciemny() {
    var m = root.getAttribute('data-theme');
    return m ? m === 'dark' : systemCiemny.matches;
  }
  function t(s) { return window.FI ? window.FI.t(s) : s; }

  document.addEventListener('DOMContentLoaded', function () {
    var miejsce = document.querySelector('.header-tools');
    if (!miejsce) return;
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'theme-switch';
    function odswiez() {
      var napis = ciemny() ? t('Włącz jasny motyw') : t('Włącz ciemny motyw');
      b.setAttribute('aria-label', napis);
      b.title = napis;
      b.innerHTML = ciemny() ? SLONCE : KSIEZYC;
    }
    b.addEventListener('click', function () {
      root.setAttribute('data-theme', ciemny() ? 'light' : 'dark');
      odswiez();
    });
    if (systemCiemny.addEventListener) systemCiemny.addEventListener('change', odswiez);
    odswiez();
    miejsce.insertBefore(b, miejsce.querySelector('.lang-switch') || miejsce.firstChild);
  });
})();
