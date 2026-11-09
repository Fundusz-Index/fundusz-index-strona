/* Zakładka Artykuły: działy jak w BSIC. Dane: data/artykuly.json */
(function () {
  'use strict';
  var FI = window.FI, esc = FI.esc;
  var DZIALY = ['Wszystkie', 'Przegląd tygodnia', 'Profit Journal', 'Edukacja', 'Z życia funduszu'];
  var stan = 'Wszystkie', wszystkie = [];

  function rysuj() {
    document.getElementById('dzialy').innerHTML = DZIALY.map(function (d) {
      return '<button type="button" class="tab" role="tab" aria-selected="' + (d === stan) + '" data-dzial="' + esc(d) + '">' + esc(d) + '</button>';
    }).join('');
    var lista = wszystkie.filter(function (a) { return stan === 'Wszystkie' || a.dzial === stan; })
      .sort(function (a, b) { return String(b.data).localeCompare(String(a.data)); });
    var wyr = document.getElementById('wyrozniony'), box = document.getElementById('lista');
    if (!lista.length) {
      wyr.hidden = true;
      box.innerHTML = '<li class="empty" style="display:block">W tym dziale nie ma jeszcze artykułów.</li>';
      return;
    }
    var a = lista[0];
    wyr.hidden = false;
    wyr.innerHTML = '<span class="label" style="color:var(--inv-muted)">' + esc(a.dzial) + ' · ' + FI.data(a.data) + '</span>' +
      '<h2 style="font-size:30px;line-height:1.2"><a href="' + esc(a.link || '#') + '" style="text-decoration:none">' + esc(a.tytul) + '</a></h2>' +
      '<p style="color:var(--inv-muted)">' + esc(a.wstep || '') + '</p><span class="small muted">' + esc(a.autor || '') + '</span>';
    box.innerHTML = lista.slice(1).map(function (x) {
      return '<li><div><span class="label">' + esc(x.dzial) + '</span><br><span class="tiny muted">' + FI.data(x.data) + '</span></div>' +
        '<div style="display:flex;flex-direction:column;gap:6px;min-width:0"><a href="' + esc(x.link || '#') + '">' + esc(x.tytul) + '</a>' +
        '<span class="small" style="color:var(--ink-2)">' + esc(x.wstep || '') + '</span><span class="tiny muted">' + esc(x.autor || '') + '</span></div></li>';
    }).join('');
  }

  FI.json('artykuly.json').then(function (lista) {
    wszystkie = lista;
    rysuj();
    document.getElementById('dzialy').addEventListener('click', function (e) {
      var b = e.target.closest('[data-dzial]');
      if (!b) return;
      stan = b.dataset.dzial;
      rysuj();
    });
  });
})();
