/* Zakładka Portfel: wykres na tle benchmarku, skład, spółki z tezami, dziennik decyzji. */
(function () {
  'use strict';
  var FI = window.FI, esc = FI.esc;
  var KOLORY = ['var(--s1)', 'var(--s2)', 'var(--s3)', 'var(--s4)', 'var(--s5)'];
  var stan = { zakres: '1R', hover: null, sort: 'waga', otwarta: null, sklad: 'spolki' };
  var P = null;

  function $(id) { return document.getElementById(id); }

  /* ---------- wykres ---------- */
  var W = 1000, H = 340, L = 56, R = 984, T = 20, B = 300;

  function poczatekZakresu(seria, zakres) {
    var ost = new Date(seria[seria.length - 1].d + 'T00:00:00Z');
    if (zakres === 'Od startu') return 0;
    if (zakres === 'YTD') {
      var rok = ost.getUTCFullYear() + '-01-01';
      var i = -1;
      seria.forEach(function (p, k) { if (p.d < rok) i = k; });
      return Math.max(0, i);
    }
    var dni = { '1M': 30, '3M': 91, '6M': 182, '1R': 365 }[zakres];
    var granica = new Date(ost.getTime() - dni * 864e5).toISOString().slice(0, 10);
    var j = 0;
    seria.forEach(function (p, k) { if (p.d <= granica) j = k; });
    return j;
  }

  function rysujWykres() {
    var seria = P.seria, s0 = poczatekZakresu(seria, stan.zakres);
    var pkt = seria.slice(s0);
    if (pkt.length < 2) pkt = seria.slice(Math.max(0, seria.length - 2));
    var f = pkt.map(function (p) { return (p.f / pkt[0].f - 1) * 100; });
    var b = pkt.map(function (p) { return (p.b / pkt[0].b - 1) * 100; });
    var n = pkt.length;
    var mn = Math.min(0, Math.min.apply(null, f), Math.min.apply(null, b));
    var mx = Math.max(0, Math.max.apply(null, f), Math.max.apply(null, b));
    var kroki = [0.25, 0.5, 1, 2, 2.5, 5, 10, 20, 25, 50], krok = 50;
    for (var i = 0; i < kroki.length; i++) { if ((mx - mn || 1) / kroki[i] <= 6) { krok = kroki[i]; break; } }
    var lo = Math.floor(mn / krok) * krok, hi = Math.ceil(mx / krok) * krok;
    if (hi === lo) hi = lo + krok;
    var X = function (k) { return L + (n > 1 ? k / (n - 1) : 0) * (R - L); };
    var Y = function (v) { return B - (v - lo) / (hi - lo) * (B - T); };
    var fp = f.map(function (v, k) { return X(k).toFixed(1) + ',' + Y(v).toFixed(1); });
    var bp = b.map(function (v, k) { return X(k).toFixed(1) + ',' + Y(v).toFixed(1); });
    var svg = '';
    for (var v = lo; v <= hi + 1e-9; v += krok) {
      var zero = Math.abs(v) < 1e-9;
      svg += '<line x1="' + L + '" x2="' + R + '" y1="' + Y(v).toFixed(1) + '" y2="' + Y(v).toFixed(1) +
        '" stroke="' + (zero ? 'var(--line-strong)' : 'var(--line)') + '" stroke-width="1"/>';
      svg += '<text x="' + (L - 8) + '" y="' + (Y(v) + 4).toFixed(1) + '" text-anchor="end">' +
        (zero ? '0' : FI.pct(v, krok < 1 ? 1 : 0)) + '</text>';
    }
    [0, 0.25, 0.5, 0.75, 1].forEach(function (q, k) {
      var idx = Math.round(q * (n - 1));
      svg += '<text x="' + X(idx).toFixed(1) + '" y="' + (H - 14) + '" text-anchor="' + (k === 0 ? 'start' : k === 4 ? 'end' : 'middle') + '">' + FI.data(pkt[idx].d) + '</text>';
    });
    svg += '<polygon points="' + fp.concat(bp.slice().reverse()).join(' ') + '" fill="var(--area)" stroke="none"/>';
    svg += '<polyline points="' + bp.join(' ') + '" fill="none" stroke="var(--bench)" stroke-width="2" stroke-dasharray="6 4" stroke-linejoin="round"/>';
    svg += '<polyline points="' + fp.join(' ') + '" fill="none" stroke="var(--s1)" stroke-width="2.75" stroke-linejoin="round"/>';
    var h = stan.hover !== null && stan.hover < n ? stan.hover : null;
    var li = h === null ? n - 1 : h;
    if (h !== null) {
      svg += '<line x1="' + X(li) + '" x2="' + X(li) + '" y1="' + T + '" y2="' + B + '" stroke="var(--ink)" stroke-width="1" stroke-dasharray="3 3"/>';
      svg += '<circle cx="' + X(li) + '" cy="' + Y(b[li]) + '" r="5" fill="var(--bg)" stroke="var(--bench)" stroke-width="2"/>';
      svg += '<circle cx="' + X(li) + '" cy="' + Y(f[li]) + '" r="7" fill="#FFD60A" stroke="#0D0D0D" stroke-width="2"/>';
    }
    var el = $('wykres');
    el.innerHTML = svg;
    el.dataset.n = n;
    $('leg-data').textContent = FI.data(pkt[li].d);
    $('leg-fundusz').textContent = FI.pct(f[li]);
    $('leg-bench').textContent = FI.pct(b[li]);
  }

  function hover(e) {
    var el = $('wykres'), r = el.getBoundingClientRect(), n = +el.dataset.n;
    var x = (e.clientX - r.left) / r.width * W;
    var i = Math.max(0, Math.min(n - 1, Math.round((x - L) / (R - L) * (n - 1))));
    if (i !== stan.hover) { stan.hover = i; rysujWykres(); }
  }

  /* ---------- skład ---------- */
  function rysujSklad() {
    var grupy;
    if (stan.sklad === 'spolki') {
      grupy = P.pozycje.map(function (p) { return [p.nazwa, p.waga]; });
    } else {
      var m = {};
      P.pozycje.forEach(function (p) { m[p.sektor] = (m[p.sektor] || 0) + p.waga; });
      grupy = Object.keys(m).map(function (k) { return [k, m[k]]; }).sort(function (a, b) { return b[1] - a[1]; });
    }
    if (P.podsumowanie.gotowka_pln > 1) grupy.push(['Gotówka', P.podsumowanie.gotowka_pln / P.podsumowanie.wartosc_pln * 100]);
    var bar = $('sklad-pasek');
    bar.innerHTML = grupy.map(function (g, i) {
      return '<span style="flex:' + g[1] + ' 1 0;background:' + KOLORY[i % 5] + '"></span>';
    }).join('');
    bar.setAttribute('aria-label', 'Skład portfela: ' + grupy.map(function (g) { return g[0] + ' ' + Math.round(g[1]) + '%'; }).join(', '));
    $('sklad-legenda').innerHTML = grupy.map(function (g, i) {
      return '<li><span class="dot" style="background:' + KOLORY[i % 5] + ';outline:1px solid var(--line)"></span>' + esc(g[0]) + ' <b>' + Math.round(g[1]) + '%</b></li>';
    }).join('');
    document.querySelectorAll('[data-sklad]').forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.sklad === stan.sklad); });
  }

  /* ---------- spółki ---------- */
  function teza(ticker) {
    var t = P.transakcje.filter(function (x) { return x.ticker === ticker && x.typ === 'kupno'; })[0];
    return t ? { tekst: t.uzasadnienie, data: t.data } : { tekst: '', data: '' };
  }

  function rysujSpolki() {
    var lista = P.pozycje.slice().sort(function (a, b) {
      if (stan.sort === 'nazwa') return a.nazwa.localeCompare(b.nazwa, 'pl');
      return b[stan.sort] - a[stan.sort];
    });
    var maxW = Math.max.apply(null, lista.map(function (p) { return p.waga; }));
    $('spolki').innerHTML = lista.map(function (p) {
      var open = stan.otwarta === p.ticker, t = teza(p.ticker);
      var link = p.analiza
        ? '<a href="' + esc(FI.base + p.analiza) + '"><b>Czytaj analizę ' + esc(p.ticker) + '</b></a>'
        : '<span class="muted">Analiza w przygotowaniu</span>';
      return '<li><button type="button" class="holding-btn" aria-expanded="' + open + '" data-ticker="' + esc(p.ticker) + '">' +
        '<span class="initials" aria-hidden="true">' + esc(p.ticker) + '</span>' +
        '<span class="holding-name"><strong>' + esc(p.nazwa) + '</strong><span class="tiny muted">' + esc(p.sektor) + ' · ' + esc(p.opis) + '</span></span>' +
        '<span class="holding-weight"><span class="bar-bg"><span style="width:' + (p.waga / maxW * 100).toFixed(1) + '%"></span></span><b style="width:44px;text-align:right">' + Math.round(p.waga) + '%</b></span>' +
        '<span class="holding-ret"><strong class="' + FI.lossClass(p.zwrot) + '">' + FI.pct(p.zwrot) + '</strong><span class="tiny muted">' + FI.pln(p.wartosc_pln) + ' PLN</span></span>' +
        '<span class="chev" aria-hidden="true">' + (open ? '−' : '+') + '</span></button>' +
        (open ? '<div class="holding-detail"><div style="flex:999 1 420px"><span class="label">Teza przy zakupie' + (t.data ? ' (' + FI.data(t.data) + ')' : '') + '</span><p style="color:var(--ink-2)">' + esc(t.tekst || 'Brak opisu w transakcje.csv.') + '</p></div>' +
          '<div style="flex:1 1 220px"><span class="label">Analiza</span><span class="small" style="color:var(--ink-2)">' + esc(p.autorzy || '[autorzy analizy]') + '</span>' + link + '</div></div>' : '') +
        '</li>';
    }).join('');
    document.querySelectorAll('[data-sort]').forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.sort === stan.sort); });
  }

  /* ---------- dziennik decyzji ---------- */
  function rysujDziennik() {
    var dni = {};
    P.transakcje.forEach(function (t) { (dni[t.data] = dni[t.data] || []).push(t); });
    var daty = Object.keys(dni).sort().reverse();
    $('dziennik').innerHTML = daty.map(function (d, k) {
      var lista = dni[d], kupna = lista.filter(function (t) { return t.typ === 'kupno'; }).length;
      var tytul = d === P.data_startu ? 'Start funduszu: kupno ' + lista.length + ' spółek za ' + FI.pln(P.kapital_startowy_pln) + ' PLN'
        : (kupna === lista.length ? 'Kupno' : kupna === 0 ? 'Sprzedaż' : 'Zmiany w portfelu') + (lista.length > 1 ? ': ' + lista.length + ' spółki' : ': ' + lista[0].nazwa);
      return '<li><span class="small" style="font-weight:700;padding-top:2px">' + FI.data(d) + '</span>' +
        '<span class="tl-mark" aria-hidden="true"><i></i>' + (k < daty.length - 1 ? '<b></b>' : '') + '</span>' +
        '<div class="tl-body"><strong>' + esc(tytul) + '</strong><ul>' + lista.map(function (t) {
          return '<li><b style="color:var(--ink)">' + (t.typ === 'kupno' ? 'Kupno' : 'Sprzedaż') + ' · ' + esc(t.nazwa) + ' (' + esc(t.ticker) + ')</b> · ' + FI.pln(t.kwota_pln) + ' PLN</li>';
        }).join('') + '</ul></div></li>';
    }).join('');
  }

  /* ---------- liczby ---------- */
  function rysujLiczby() {
    var s = P.podsumowanie;
    $('teza-zwrot').textContent = FI.pct(s.zwrot_od_startu);
    $('teza-bench').textContent = FI.pct(s.benchmark_od_startu);
    $('meta-start').textContent = FI.data(P.data_startu);
    $('meta-kapital').textContent = FI.pln(P.kapital_startowy_pln);
    $('meta-stan').textContent = FI.data(P.stan_na);
    $('k-wartosc').textContent = FI.pln(s.wartosc_pln) + ' PLN';
    $('k-zwrot').textContent = FI.pct(s.zwrot_od_startu);
    $('k-bench').textContent = FI.pct(s.benchmark_od_startu);
    $('k-roznica').textContent = FI.pp(s.zwrot_od_startu - s.benchmark_od_startu);
    $('k-gotowka').textContent = FI.pln(s.gotowka_pln) + ' PLN';
    $('k-pozycje').textContent = s.liczba_pozycji;
    var nazwy = { '1M': '1 miesiąc', '3M': '3 miesiące', '6M': '6 miesięcy', 'YTD': 'Od początku roku', '1R': '1 rok' };
    $('okresy').innerHTML = Object.keys(nazwy).filter(function (k) { return P.okresy[k]; }).map(function (k) {
      return '<dt>' + nazwy[k] + '</dt><dd>' + FI.pct(P.okresy[k].f) + ' <span style="font-weight:400;color:var(--inv-muted)">/ ' + FI.pct(P.okresy[k].b) + '</span></dd>';
    }).join('');
  }

  function zakresy() {
    document.querySelectorAll('[data-zakres]').forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.zakres === stan.zakres); });
  }

  FI.portfolio.then(function (p) {
    P = p;
    rysujLiczby(); rysujSklad(); rysujSpolki(); rysujDziennik(); zakresy(); rysujWykres();
    document.querySelectorAll('[data-zakres]').forEach(function (b) {
      b.addEventListener('click', function () { stan.zakres = b.dataset.zakres; stan.hover = null; zakresy(); rysujWykres(); });
    });
    document.querySelectorAll('[data-sklad]').forEach(function (b) {
      b.addEventListener('click', function () { stan.sklad = b.dataset.sklad; rysujSklad(); });
    });
    document.querySelectorAll('[data-sort]').forEach(function (b) {
      b.addEventListener('click', function () { stan.sort = b.dataset.sort; rysujSpolki(); });
    });
    $('spolki').addEventListener('click', function (e) {
      var btn = e.target.closest('.holding-btn');
      if (!btn) return;
      stan.otwarta = stan.otwarta === btn.dataset.ticker ? null : btn.dataset.ticker;
      rysujSpolki();
      var again = document.querySelector('.holding-btn[data-ticker="' + btn.dataset.ticker + '"]');
      if (again) again.focus();
    });
    var w = $('wykres');
    w.addEventListener('pointermove', hover);
    w.addEventListener('pointerleave', function () { stan.hover = null; rysujWykres(); });
  }).catch(function (e) {
    $('blad').hidden = false;
    console.error(e);
  });
})();
