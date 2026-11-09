/* Zakładka Analizy: karty z filtrami po sektorze i statusie. Dane: data/analizy.json */
(function () {
  'use strict';
  var FI = window.FI, esc = FI.esc;
  var stan = { sektor: 'Wszystkie', status: 'Wszystkie' };
  var analizy = [], wPortfelu = {};

  function chip(grupa, wartosc, aktywny) {
    return '<button type="button" class="pill" data-' + grupa + '="' + esc(wartosc) + '" aria-pressed="' + aktywny + '">' + esc(wartosc) + '</button>';
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
    document.getElementById('liczba').textContent = 'Wyniki: ' + lista.length;
    var box = document.getElementById('karty');
    if (!lista.length) {
      box.innerHTML = '<p class="empty">Brak analiz dla wybranych filtrów.</p>';
      return;
    }
    box.innerHTML = lista.map(function (a) {
      return '<article class="card">' +
        '<div style="display:flex;align-items:center;gap:12px"><span class="initials" aria-hidden="true">' + esc(a.ticker) + '</span>' +
        '<div style="flex:1 1 auto;min-width:0"><h2 style="font-size:18px">' + esc(a.nazwa) + '</h2><span class="tiny muted">' + esc(a.ticker) + ' · ' + esc(a.sektor) + '</span></div>' +
        (wPortfelu[a.ticker] ? '<span class="badge">W portfelu</span>' : '') + '</div>' +
        '<div class="meta-grid"><div><span>Data</span><b>' + esc(a.data_tekst || a.data) + '</b></div><div><span>Metoda</span><b>' + esc(a.metoda) + '</b></div><div><span>Pliki</span><b>' + esc(a.pliki) + '</b></div></div>' +
        '<p class="small" style="color:var(--ink-2)">' + esc(a.teza) + '</p>' +
        '<div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:8px;margin-top:auto">' +
        '<span class="tiny" style="color:var(--ink-2)">Autorzy: ' + esc(a.autorzy) + '</span>' +
        '<span style="display:flex;flex-wrap:wrap;gap:4px 16px">' +
        (/\.pdf$/i.test(a.link) ? '' : '<a href="' + esc(FI.base + a.link) + '" style="font-weight:700;padding:10px 0">Czytaj analizę</a>') +
        (a.raport ? '<a href="' + esc(FI.base + a.raport) + '" download style="font-weight:700;padding:10px 0">Pobierz raport (PDF)</a>' : '') +
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
