/* Навигация и карта.
 *
 * Три независимых блока: бургер, скролл-шпион якорной навигации меню
 * и карта. Каждый проверяет наличие своих элементов и молча выходит,
 * если их нет на этой странице.
 */
(function () {
  'use strict';

  /* ---------- мобильное меню ---------- */

  var burger = document.querySelector('.burger');
  var mobileNav = document.getElementById('mobile-nav');

  if (burger && mobileNav) {
    burger.addEventListener('click', function () {
      var open = burger.getAttribute('aria-expanded') === 'true';
      burger.setAttribute('aria-expanded', open ? 'false' : 'true');
      mobileNav.hidden = open;
    });
    mobileNav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        burger.setAttribute('aria-expanded', 'false');
        mobileNav.hidden = true;
      }
    });
  }

  /* ---------- скролл-шпион якорной навигации ---------- */

  var chips = document.querySelectorAll('.chip');
  var sections = document.querySelectorAll('.menu-section');

  if (chips.length && sections.length && 'IntersectionObserver' in window) {
    var byId = {};
    chips.forEach(function (chip) {
      byId[chip.getAttribute('href').slice(1)] = chip;
    });

    var current = null;
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var chip = byId[entry.target.id];
        if (!chip || chip === current) return;
        if (current) current.classList.remove('is-active');
        chip.classList.add('is-active');
        current = chip;
        // Держим активный чип в поле зрения на мобильном
        var strip = chip.parentElement;
        if (strip && strip.scrollWidth > strip.clientWidth) {
          var left = chip.offsetLeft - strip.clientWidth / 2 + chip.clientWidth / 2;
          strip.parentElement.scrollTo({ left: Math.max(0, left), behavior: 'smooth' });
        }
      });
    }, { rootMargin: '-30% 0px -60% 0px', threshold: 0 });

    sections.forEach(function (section) { observer.observe(section); });
  }

  /* ---------- уведомление о персональных данных ---------- */

  var consent = document.getElementById('consent');
  if (consent) {
    var KEY = 'frnds.consent.v1';
    var seen = false;
    try { seen = !!localStorage.getItem(KEY); } catch (e) { /* приватный режим */ }
    if (!seen) consent.hidden = false;
    var ok = document.getElementById('consent-ok');
    if (ok) {
      ok.addEventListener('click', function () {
        consent.hidden = true;
        try { localStorage.setItem(KEY, String(Date.now())); } catch (e) { /* ок */ }
      });
    }
  }

  /* ---------- карта ---------- */

  var mapEl = document.getElementById('map');
  if (mapEl && window.L) {
    var lat = parseFloat(mapEl.getAttribute('data-lat'));
    var lon = parseFloat(mapEl.getAttribute('data-lon'));
    var label = mapEl.getAttribute('data-label') || 'Frnds';

    var map = L.map(mapEl, { scrollWheelZoom: false }).setView([lat, lon], 17);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap'
    }).addTo(map);

    var icon = L.divIcon({
      className: 'map-pin',
      html: '<span style="display:block;width:22px;height:22px;border-radius:50%;' +
            'background:#FF7F17;border:4px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,.35)"></span>',
      iconSize: [22, 22],
      iconAnchor: [11, 11]
    });
    L.marker([lat, lon], { icon: icon, title: label }).addTo(map).bindPopup(label);
  }
})();
