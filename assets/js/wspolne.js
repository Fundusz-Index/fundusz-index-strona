/* Wspólne funkcje strony Funduszu Index. Bez zewnętrznych bibliotek. */
(function () {
  'use strict';
  var baseEl = document.querySelector('[data-base]');
  var base = baseEl ? baseEl.getAttribute('data-base') : '';

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  var FI = window.FI = {
    base: base,
    esc: esc,
    json: function (nazwa) {
      return fetch(base + 'data/' + nazwa, { cache: 'no-cache' }).then(function (r) {
        if (!r.ok) throw new Error('Nie udało się wczytać ' + nazwa);
        return r.json();
      });
    },
    pct: function (v, d) {
      if (v === null || v === undefined || isNaN(v)) return '–';
      d = d === undefined ? 1 : d;
      return (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(d).replace('.', ',') + '%';
    },
    pp: function (v) {
      if (v === null || v === undefined || isNaN(v)) return '–';
      return (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(1).replace('.', ',') + ' pp';
    },
    pln: function (v) {
      var s = Math.round(v).toString();
      return s.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    },
    data: function (iso) {
      var p = String(iso).split('-');
      return p.length === 3 ? p[2] + '.' + p[1] + '.' + p[0] : iso;
    },
    lossClass: function (v) { return v < 0 ? 'loss' : ''; }
  };

  /* Notka o danych przykładowych: pokazuje się tylko, gdy portfolio.json ma "demo": true. */
  function demoNotes(p) {
    document.querySelectorAll('[data-demo-note]').forEach(function (el) { el.hidden = !p.demo; });
  }

  /* Strona główna: pasek kursów, ogłoszenie, portfel w skrócie. */
  function ticker(p) {
    var box = document.getElementById('ticker');
    if (!box) return;
    var items = [{ sym: 'Portfel', name: 'Fundusz Index', chg: p.podsumowanie.zmiana_dzienna, href: 'portfel.html' }];
    p.pozycje.forEach(function (x) {
      items.push({ sym: x.ticker, name: x.nazwa, chg: x.zmiana_dzienna, href: x.analiza || 'portfel.html' });
    });
    items.push({ sym: p.benchmark, name: 'w PLN', chg: p.podsumowanie.benchmark_zmiana_dzienna, href: 'portfel.html' });
    function li(i, dup) {
      var arrow = i.chg < 0 ? '▼' : '▲';
      var link = dup ? '<span style="font-weight:700">' + esc(i.sym) + '</span>' : '<a href="' + esc(base + i.href) + '">' + esc(i.sym) + '</a>';
      return '<li' + (dup ? ' aria-hidden="true"' : '') + '>' + link + '<span class="tiny muted">' + esc(i.name) +
        '</span><span class="chg ' + FI.lossClass(i.chg) + '">' + arrow + ' ' + FI.pct(i.chg) + '</span></li>';
    }
    box.querySelector('.ticker-track').innerHTML = items.map(function (i) { return li(i, false); }).join('') +
      items.map(function (i) { return li(i, true); }).join('');
    var d = box.querySelector('[data-ticker-date]');
    if (d) d.textContent = 'zmiana dzienna · ' + FI.data(p.stan_na) + (p.demo ? ' · przykład' : '');
    box.hidden = false;
  }

  function homeSnapshot(p) {
    var el = document.getElementById('start-portfel');
    if (!el) return;
    el.querySelector('[data-zwrot]').textContent = FI.pct(p.podsumowanie.zwrot_od_startu);
    el.querySelector('[data-bench]').textContent = FI.pct(p.podsumowanie.benchmark_od_startu);
    var kolory = ['var(--s1)', 'var(--s2)', 'var(--s3)', 'var(--s4)', 'var(--s5)'];
    el.querySelector('.alloc-bar').innerHTML = p.pozycje.map(function (x, i) {
      return '<span style="flex:' + x.waga + ' 1 0;background:' + kolory[i % 5] + '"></span>';
    }).join('');
    el.querySelector('.alloc-bar').setAttribute('aria-label', 'Skład portfela: ' + p.pozycje.map(function (x) {
      return x.nazwa + ' ' + Math.round(x.waga) + '%';
    }).join(', '));
    el.querySelector('[data-sklad]').textContent = p.pozycje.map(function (x) {
      return x.nazwa + ' ' + Math.round(x.waga) + '%';
    }).join(' · ');
    var last = p.transakcje[0];
    var dec = document.getElementById('ostatnia-decyzja');
    if (dec && last) {
      var tegoDnia = p.transakcje.filter(function (t) { return t.data === last.data; });
      dec.querySelector('[data-data]').textContent = FI.data(last.data);
      dec.querySelector('[data-opis]').textContent = tegoDnia.length > 1
        ? (last.typ === 'kupno' ? 'Kupno ' : 'Sprzedaż ') + tegoDnia.length + ' spółek'
        : (last.typ === 'kupno' ? 'Kupno: ' : 'Sprzedaż: ') + last.nazwa + ' (' + last.ticker + ')';
    }
  }

  function announcement() {
    var box = document.getElementById('ogloszenie');
    if (!box) return;
    FI.json('ogloszenie.json').then(function (o) {
      if (!o.pokaz) return;
      box.querySelector('[data-etykieta]').textContent = o.etykieta || 'Ogłoszenie';
      box.querySelector('[data-tytul]').textContent = o.tytul || '';
      box.querySelector('[data-tekst]').textContent = o.tekst || '';
      var a = box.querySelector('[data-link]');
      if (o.link) { a.href = o.link; a.textContent = o.link_tekst || 'Szczegóły'; } else { a.hidden = true; }
      box.hidden = false;
    }).catch(function () {});
  }

  FI.portfolio = FI.json('portfolio.json');
  FI.portfolio.then(function (p) {
    demoNotes(p);
    ticker(p);
    homeSnapshot(p);
  }).catch(function (e) { console.error(e); });
  announcement();
})();
