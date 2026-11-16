/* Zakładka Portfel: wykres na tle benchmarku, skład, spółki z tezami, dziennik decyzji. */
(function () {
  'use strict';
  var FI = window.FI, esc = FI.esc;
  var KOLORY = ['var(--s1)', 'var(--s2)', 'var(--s3)', 'var(--s4)', 'var(--s5)'];
  var stan = { zakres: 'Od startu', hover: null, sort: 'waga', otwarta: null, sklad: 'spolki' };
  var P = null;

  function $(id) { return document.getElementById(id); }

  /* ---------- wykres ---------- */
  var WASKI = window.matchMedia('(max-width: 640px)').matches;
  var W = WASKI ? 440 : 1000, H = WASKI ? 300 : 340, L = WASKI ? 44 : 56, R = W - (WASKI ? 104 : 136), T = 20, B = H - 40;

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
    document.getElementById('wykres').setAttribute('viewBox', '0 0 ' + W + ' ' + H);
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
    (WASKI ? [0, 0.5, 1] : [0, 0.25, 0.5, 0.75, 1]).forEach(function (q, k) {
      var idx = Math.round(q * (n - 1));
      svg += '<text x="' + X(idx).toFixed(1) + '" y="' + (H - 14) + '" text-anchor="' + (k === 0 ? 'start' : q === 1 ? 'end' : 'middle') + '">' + FI.data(pkt[idx].d) + '</text>';
    });
    svg += '<line x1="' + L + '" x2="' + R + '" y1="' + B + '" y2="' + B + '" stroke="var(--line-strong)" stroke-width="1.5"/>';
    svg += '<polyline points="' + bp.join(' ') + '" fill="none" stroke="var(--bench)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>';
    svg += '<circle cx="' + X(n - 1) + '" cy="' + Y(b[n - 1]).toFixed(1) + '" r="4" fill="var(--bench)"/>';
    svg += '<polyline points="' + fp.join(' ') + '" fill="none" stroke="var(--s1)" stroke-width="3.25" stroke-linejoin="round" stroke-linecap="round"/>';
    svg += '<circle cx="' + X(n - 1) + '" cy="' + Y(f[n - 1]).toFixed(1) + '" r="5.5" fill="var(--s1)"/>';
    /* podpisy na końcach linii zamiast legendy */
    var yf = Y(f[n - 1]), yb = Y(b[n - 1]);
    if (Math.abs(yf - yb) < 34) { var sr = (yf + yb) / 2, zn = yf <= yb ? -1 : 1; yf = sr + zn * 17; yb = sr - zn * 17; }
    var podpis = function (y, nazwa, wart, kolor) {
      return '<text class="chart-end" x="' + (R + 14) + '" y="' + (y - 2).toFixed(1) + '" style="fill:' + kolor + '">' + nazwa + '</text>' +
        '<text class="chart-end chart-end-val" x="' + (R + 14) + '" y="' + (y + 14).toFixed(1) + '" style="fill:' + kolor + '">' + FI.pct(wart) + '</text>';
    };
    svg += podpis(yb, 'S&amp;P 500 (PLN)', b[n - 1], 'var(--bench-text)') + podpis(yf, esc(FI.t('Fundusz')), f[n - 1], 'var(--s1)');
    /* znaczniki decyzji: żółty romb na linii funduszu w dniu transakcji (ten sam znak co kurs na wykresie wyceny) */
    var decyzje = {};
    (P.transakcje || []).forEach(function (t) {
      var k = -1;
      for (var q = 0; q < n; q++) { if (pkt[q].d >= t.data) { k = q; break; } }
      if (k < 0 || (k === 0 && s0 > 0 && t.data < pkt[0].d)) return;
      (decyzje[k] = decyzje[k] || []).push(t);
    });
    var h = stan.hover !== null && stan.hover < n ? stan.hover : null;
    var li = h === null ? n - 1 : h;
    if (h !== null) {
      svg += '<line x1="' + X(li) + '" x2="' + X(li) + '" y1="' + T + '" y2="' + B + '" stroke="var(--ink)" stroke-width="1" stroke-dasharray="3 3"/>';
      svg += '<circle cx="' + X(li) + '" cy="' + Y(b[li]) + '" r="5" fill="var(--bench)" stroke="var(--bg)" stroke-width="2"/>';
      if (!decyzje[li]) svg += '<circle cx="' + X(li) + '" cy="' + Y(f[li]) + '" r="6.5" fill="var(--s1)" stroke="var(--bg)" stroke-width="2"/>';
    }
    Object.keys(decyzje).forEach(function (k) {
      var x = +X(+k).toFixed(1), y = +Y(f[+k]).toFixed(1);
      svg += '<rect x="' + (x - 6) + '" y="' + (y - 6) + '" width="12" height="12" transform="rotate(45 ' + x + ' ' + y + ')" fill="var(--accent)" stroke="var(--black)" stroke-width="2"/>';
    });
    var el = $('wykres');
    el.innerHTML = svg;
    el.dataset.n = n;
    $('leg-data').textContent = FI.data(pkt[li].d);
    $('leg-fundusz').textContent = FI.pct(f[li]);
    $('leg-bench').textContent = FI.pct(b[li]);
    var dymek = $('wykres-dymek');
    if (h === null && !WASKI) { dymek.hidden = true; return; }
    var roz = f[li] - b[li];
    var html = '<b>' + FI.data(pkt[li].d) + '</b>' +
      '<span><i class="k-f"></i>' + esc(FI.t('Fundusz')) + '<b>' + FI.pct(f[li]) + '</b></span>' +
      '<span><i class="k-b"></i>S&amp;P 500 (PLN)<b>' + FI.pct(b[li]) + '</b></span>' +
      '<span class="roz">' + esc(FI.t('Różnica')) + '<b>' + (roz > 0 ? '+' : roz < 0 ? '−' : '') + FI.num(Math.abs(roz), 1) + ' pp</b></span>';
    if (decyzje[li]) {
      var wg = {};
      decyzje[li].forEach(function (t) { (wg[t.typ] = wg[t.typ] || []).push(t.ticker); });
      html += Object.keys(wg).map(function (typ) {
        return '<span class="dec"><i class="k-d"></i><em>' + esc(FI.t(typ.charAt(0).toUpperCase() + typ.slice(1))) + ': ' + esc(wg[typ].join(', ')) + '</em></span>';
      }).join('');
    }
    dymek.innerHTML = html;
    dymek.hidden = false;
    if (WASKI) return;
    var lewo = X(li) / W * 100, prawa = lewo > 55;
    dymek.style.left = prawa ? 'auto' : 'calc(' + lewo.toFixed(2) + '% + 14px)';
    dymek.style.right = prawa ? 'calc(' + (100 - lewo).toFixed(2) + '% + 14px)' : 'auto';
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
    if (P.podsumowanie.gotowka_pln > 1) grupy.push([FI.t('Gotówka'), P.podsumowanie.gotowka_pln / P.podsumowanie.wartosc_pln * 100]);
    var bar = $('sklad-pasek');
    bar.innerHTML = grupy.map(function (g, i) {
      return '<span style="flex:' + g[1] + ' 1 0;background:' + KOLORY[i % 5] + '"></span>';
    }).join('');
    bar.setAttribute('aria-label', FI.t('Skład portfela') + ': ' + grupy.map(function (g) { return FI.t(g[0]) + ' ' + Math.round(g[1]) + '%'; }).join(', '));
    $('sklad-legenda').innerHTML = grupy.map(function (g, i) {
      return '<li><span class="dot" style="background:' + KOLORY[i % 5] + ';outline:1px solid var(--line)"></span>' + esc(FI.t(g[0])) + ' <b>' + Math.round(g[1]) + '%</b></li>';
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
      var link = (p.analiza ? '<a href="' + esc(FI.base + p.analiza) + '"><b>' + esc(FI.t('Czytaj analizę {t}').replace('{t}', p.ticker)) + '</b></a>' : '') +
        (p.raport ? '<a href="' + esc(FI.base + p.raport) + '" download><b>' + esc(FI.t('Pobierz raport {t} (PDF)').replace('{t}', p.ticker)) + '</b></a>' : '');
      if (!link) link = '<span class="muted">' + esc(FI.t('Analiza w przygotowaniu')) + '</span>';
      return '<li><button type="button" class="holding-btn" aria-expanded="' + open + '" data-ticker="' + esc(p.ticker) + '">' +
        '<span class="initials" aria-hidden="true">' + esc(p.ticker) + '</span>' +
        '<span class="holding-name"><strong>' + esc(p.nazwa) + '</strong><span class="tiny muted">' + esc(FI.t(p.sektor)) + ' · ' + esc(FI.t(p.opis)) + '</span></span>' +
        '<span class="holding-weight"><span class="bar-bg"><span style="width:' + (p.waga / maxW * 100).toFixed(1) + '%"></span></span><b style="width:44px;text-align:right">' + Math.round(p.waga) + '%</b></span>' +
        '<span class="holding-ret"><strong class="' + FI.lossClass(p.zwrot) + '">' + FI.pct(p.zwrot) + '</strong><span class="tiny muted">' + FI.pln(p.wartosc_pln) + ' PLN</span></span>' +
        '<span class="chev" aria-hidden="true">' + (open ? '−' : '+') + '</span></button>' +
        (open ? '<div class="holding-detail"><div style="flex:999 1 420px"><span class="label">' + esc(FI.t('Teza z raportu, zakup')) + (t.data ? ' (' + FI.data(t.data) + ')' : '') + '</span><p style="color:var(--ink-2)">' + esc(FI.t(t.tekst) || 'Brak opisu w transakcje.csv.') + '</p></div>' +
          '<div style="flex:1 1 220px"><span class="label">' + esc(FI.t('Analiza')) + '</span><span class="small" style="color:var(--ink-2)">' + esc(p.autorzy || '[autorzy analizy]') + '</span>' + link + '</div></div>' : '') +
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
      var tytul = d === P.data_startu ? FI.t('Start funduszu: kupno {n} spółek za {k} PLN').replace('{n}', lista.length).replace('{k}', FI.pln(P.kapital_startowy_pln))
        : FI.t(kupna === lista.length ? 'Kupno' : kupna === 0 ? 'Sprzedaż' : 'Zmiany w portfelu') + (lista.length > 1 ? ': ' + FI.t('{n} spółki').replace('{n}', lista.length) : ': ' + lista[0].nazwa);
      return '<li><span class="small" style="font-weight:700;padding-top:2px">' + FI.data(d) + '</span>' +
        '<span class="tl-mark" aria-hidden="true"><i></i>' + (k < daty.length - 1 ? '<b></b>' : '') + '</span>' +
        '<div class="tl-body"><strong>' + esc(tytul) + '</strong><ul>' + lista.map(function (t) {
          return '<li><b style="color:var(--ink)">' + esc(FI.t(t.typ === 'kupno' ? 'Kupno' : 'Sprzedaż')) + ' · ' + esc(t.nazwa) + ' (' + esc(t.ticker) + ')</b> · ' + FI.pln(t.kwota_pln) + ' PLN</li>';
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
      return '<dt>' + esc(FI.t(nazwy[k])) + '</dt><dd>' + FI.pct(P.okresy[k].f) + ' <span style="font-weight:400;color:var(--inv-muted)">/ ' + FI.pct(P.okresy[k].b) + '</span></dd>';
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
