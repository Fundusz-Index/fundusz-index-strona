/* Zakładka Analizy: karty z filtrami po sektorze i statusie. Dane: data/analizy.json */
(function () {
  'use strict';
  var FI = window.FI, esc = FI.esc;
  var stan = { sektor: 'Wszystkie', status: 'Wszystkie' };
  var analizy = [], wPortfelu = {};

  function chip(grupa, wartosc, aktywny) {
    return '<button type="button" class="pill" data-' + grupa + '="' + esc(wartosc) + '" aria-pressed="' + aktywny + '">' + esc(FI.t(wartosc)) + '</button>';
  }

  function rysuj() {
    var sektory = ['Wszystkie'].concat(analizy.map(function (a) { return a.sektor; }).filter(function (s, i, t) { return t.indexOf(s) === i; }).sort());
    document.getElementById('f-sektor').innerHTML = sektory.map(function (s) { return chip('sektor', s, s === stan.sektor); }).join('');
    document.getElementById('f-status').innerHTML = ['Wszystkie', 'W portfelu', 'Poza portfelem'].map(function (s) { return chip('status', s, s === stan.status); }).join('');
    var lista = analizy.filter(function (a) {
      var w = !!wPortfelu[a.ticker];
      return (stan.sektor === 'Wszystkie' || a.sektor === stan.sektor) &&
        (stan.status === 'Wszystkie' || (stan.status === 'W portfelu') === w);
    }).sort(function (a, b) { return String(b.data).localeCompare(String(a.data)); });
    document.getElementById('liczba').textContent = FI.t('Wyniki') + ': ' + lista.length;
    var box = document.getElementById('karty');
    if (!lista.length) {
      box.innerHTML = '<p class="empty">' + esc(FI.t('Brak analiz dla wybranych filtrów.')) + '</p>';
      return;
    }
    box.innerHTML = lista.map(function (a) {
      return '<article class="card card-hover">' +
        '<div style="display:flex;align-items:center;gap:12px"><span class="initials" aria-hidden="true">' + esc(a.ticker) + '</span>' +
        '<div style="flex:1 1 auto;min-width:0"><h2 style="font-size:18px">' + esc(a.nazwa) + '</h2><span class="tiny muted">' + esc(a.ticker) + ' · ' + esc(FI.t(a.sektor)) + '</span></div>' +
        (wPortfelu[a.ticker] ? '<span class="badge">' + esc(FI.t('W portfelu')) + '</span>' : '') + '</div>' +
        '<div class="meta-grid"><div><span>' + esc(FI.t('Data')) + '</span><b>' + esc(FI.t(a.data_tekst || a.data)) + '</b></div><div><span>' + esc(FI.t('Metoda')) + '</span><b>' + esc(FI.t(a.metoda)) + '</b></div><div><span>' + esc(FI.t('Pliki')) + '</span><b>' + esc(FI.t(a.pliki)) + '</b></div></div>' +
        '<p class="small" style="color:var(--ink-2)">' + esc(FI.t(a.teza)) + '</p>' +
        '<div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:8px;margin-top:auto">' +
        '<span class="tiny" style="color:var(--ink-2)">' + esc(FI.t('Autorzy')) + ': ' + esc(a.autorzy) + '</span>' +
        '<span style="display:flex;flex-wrap:wrap;gap:4px 16px">' +
        (/\.pdf$/i.test(a.link) ? '' : '<a class="stretch" href="' + esc(FI.base + a.link) + '" style="font-weight:700;padding:10px 0">' + esc(FI.t('Czytaj analizę')) + '</a>') +
        (a.raport ? '<a href="' + esc(FI.base + a.raport) + '" download style="font-weight:700;padding:10px 0;position:relative;z-index:1">' + esc(FI.t('Pobierz raport (PDF)')) + '</a>' : '') +
        '</span></div></article>';
    }).join('');
  }

  Promise.all([FI.json('analizy.json'), FI.portfolio.catch(function () { return { pozycje: [] }; })]).then(function (r) {
    analizy = r[0];
    r[1].pozycje.forEach(function (p) { wPortfelu[p.ticker] = true; });
    rysuj();
    document.querySelector('.filters').addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b) return;
      if (b.dataset.sektor) stan.sektor = b.dataset.sektor;
      if (b.dataset.status) stan.status = b.dataset.status;
      rysuj();
    });
  });
})();
