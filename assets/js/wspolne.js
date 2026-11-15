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
    lossClass: function (v) { return v < 0 ? 'loss' : ''; },
    num: function (v, d) {
      var s = Math.abs(v).toFixed(d === undefined ? 2 : d).split('.');
      s[0] = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
      return (v < 0 ? '−' : '') + s.join(',');
    }
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

  /* Strona główna: najbliższe wydarzenia z data/kalendarz.json. Minione znikają same. */
  var MIESIACE = ['stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca', 'lipca', 'sierpnia',
    'września', 'października', 'listopada', 'grudnia'];
  function dzien(iso) {
    var p = String(iso).split('-');
    return { r: +p[0], m: +p[1], d: +p[2] };
  }
  function kiedy(e, rok) {
    var a = dzien(e.data), b = e.do ? dzien(e.do) : null;
    var koniec = (b || a).r !== rok ? ' ' + (b || a).r : '';
    var s;
    if (b && b.m === a.m && b.r === a.r) s = a.d + '–' + b.d + ' ' + MIESIACE[a.m - 1];
    else if (b) s = a.d + ' ' + MIESIACE[a.m - 1] + ' – ' + b.d + ' ' + MIESIACE[b.m - 1];
    else s = a.d + ' ' + MIESIACE[a.m - 1];
    return (e.szacunek ? 'ok. ' : '') + s + koniec;
  }
  function calendar() {
    var box = document.getElementById('kalendarz');
    if (!box) return;
    var list = box.querySelector('.cal');
    var limit = +box.getAttribute('data-limit') || 4;
    FI.json('kalendarz.json').then(function (k) {
      var now = new Date();
      var dzis = now.getFullYear() + '-' + ('0' + (now.getMonth() + 1)).slice(-2) + '-' + ('0' + now.getDate()).slice(-2);
      var lista = (k.wydarzenia || []).filter(function (e) { return (e.do || e.data) >= dzis; })
        .sort(function (a, b) { return a.data < b.data ? -1 : a.data > b.data ? 1 : 0; })
        .slice(0, limit);
      if (!lista.length) return;
      list.innerHTML = lista.map(function (e) {
        var tytul = esc(e.tytul);
        if (e.link && /^https:\/\//.test(e.link)) tytul = '<a href="' + esc(e.link) + '" rel="noopener">' + tytul + '</a>';
        return '<li' + (e.szacunek ? ' class="cal-est"' : '') + '>' +
          '<span class="tiny muted">' + esc(e.typ) + '</span>' +
          '<span class="cal-date">' + esc(kiedy(e, now.getFullYear())) + '</span>' +
          '<span class="cal-title">' + tytul + '</span>' +
          (e.opis ? '<span class="cal-meta">' + esc(e.opis) + '</span>' : '') +
          (e.szacunek ? '<span class="tiny muted">Termin szacunkowy, spółka go jeszcze nie ogłosiła</span>' : '') +
          '</li>';
      }).join('');
      box.hidden = false;
    }).catch(function () {});
  }

  /* Strona analizy: kurs z ostatniej sesji i zmiana od dnia wyceny. */
  function analysisQuote(p) {
    var box = document.querySelector('[data-kurs]');
    if (!box) return;
    var t = box.getAttribute('data-kurs');
    var x = p.pozycje.filter(function (y) { return y.ticker === t; })[0];
    if (!x || !x.kurs_usd) return;
    var w = parseFloat(box.getAttribute('data-wycena'));
    var wData = box.getAttribute('data-wycena-data');
    var od = w ? (x.kurs_usd / w - 1) * 100 : null;
    var data = FI.data(p.stan_na);
    box.innerHTML = '<span class="small muted">Kurs zamknięcia z ' + esc(data) + '</span>' +
      '<div class="quote-row"><b class="quote-price">' + FI.num(x.kurs_usd) + ' USD</b>' +
      '<span class="chg ' + FI.lossClass(x.zmiana_dzienna) + '">' + (x.zmiana_dzienna < 0 ? '▼ ' : '▲ ') + FI.pct(x.zmiana_dzienna, 2) + '</span>' +
      '<span class="small muted">ostatnia sesja</span></div>' +
      (od === null ? '' : '<span class="small" style="color:var(--ink-2)">Od dnia wyceny (' + esc(wData) + ', ' + FI.num(w) + ' USD): <b class="' +
        FI.lossClass(od) + '">' + FI.pct(od, 1) + '</b></span>') +
      (p.demo ? '<span class="tiny muted">Dane przykładowe</span>' : '');
    box.hidden = false;
  }

  FI.portfolio = FI.json('portfolio.json');
  FI.portfolio.then(function (p) {
    demoNotes(p);
    ticker(p);
    homeSnapshot(p);
    analysisQuote(p);
  }).catch(function (e) { console.error(e); });
  announcement();
  calendar();
})();
