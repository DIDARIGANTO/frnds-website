/* Корзина Frnds.
 *
 * Оплаты на сайте нет: корзина собирает выбранные блюда и превращает их
 * в готовое сообщение для WhatsApp. Названия и цены читаются из data-атрибутов
 * карточек на странице, поэтому после пересборки сайта корзина не может
 * разойтись с меню — источник правды один, data/menu.json.
 */
(function () {
  'use strict';

  var KEY = 'frnds.cart.v1';
  var TTL_DAYS = 7;
  var WHATSAPP = '77074809215';
  var MAX_URL_TEXT = 1500;

  var LANG = document.body.getAttribute('data-lang') || 'ru';

  var STR = {
    ru: {
      title: 'Ваш заказ', empty: 'Пока пусто. Выберите что-нибудь вкусное.',
      total: 'Итого', send: 'Отправить в WhatsApp', items: 'позиций',
      note: 'Это заготовка сообщения — заказ подтвердится в переписке.',
      pickup: 'Самовывоз', dinein: 'В зал', clear: 'Очистить',
      added: 'Добавлено', close: 'Закрыть', remove: 'Убрать',
      greeting: 'Здравствуйте! Заказ с сайта:', open: 'Открыть заказ',
      plural: ['позиция', 'позиции', 'позиций']
    },
    kk: {
      title: 'Сіздің тапсырысыңыз', empty: 'Әзірге бос. Дәмді бірдеңе таңдаңыз.',
      total: 'Барлығы', send: 'WhatsApp арқылы жіберу', items: 'позиция',
      note: 'Бұл — хабарлама дайындамасы, тапсырыс хат алмасуда расталады.',
      pickup: 'Өзім аламын', dinein: 'Залда', clear: 'Тазалау',
      added: 'Қосылды', close: 'Жабу', remove: 'Алып тастау',
      greeting: 'Сәлеметсіз бе! Сайттан тапсырыс:', open: 'Тапсырысты ашу',
      plural: ['позиция', 'позиция', 'позиция']
    },
    en: {
      title: 'Your order', empty: 'Empty for now. Pick something tasty.',
      total: 'Total', send: 'Send via WhatsApp', items: 'items',
      note: 'This only drafts a message — the order is confirmed in chat.',
      pickup: 'Pickup', dinein: 'Dine in', clear: 'Clear',
      added: 'Added', close: 'Close', remove: 'Remove',
      greeting: 'Hello! An order from your website:', open: 'Open order',
      plural: ['item', 'items', 'items']
    }
  }[LANG] || {};

  /* Русский требует три формы: 1 позиция, 2 позиции, 5 позиций.
     Казахский обходится одной, английский — двумя. */
  function plural(count) {
    var forms = STR.plural;
    if (LANG !== 'ru') return count === 1 ? forms[0] : forms[1];
    var mod100 = count % 100;
    var mod10 = count % 10;
    if (mod100 >= 11 && mod100 <= 14) return forms[2];
    if (mod10 === 1) return forms[0];
    if (mod10 >= 2 && mod10 <= 4) return forms[1];
    return forms[2];
  }

  /* ---------- хранилище ---------- */

  function load() {
    try {
      var raw = JSON.parse(localStorage.getItem(KEY));
      if (!raw || !Array.isArray(raw.items)) return [];
      var age = (Date.now() - (raw.updated || 0)) / 86400000;
      if (age > TTL_DAYS) { localStorage.removeItem(KEY); return []; }
      return raw.items.filter(function (i) { return i && i.id && i.qty > 0; });
    } catch (e) {
      return [];
    }
  }

  function save(items) {
    try {
      localStorage.setItem(KEY, JSON.stringify({ updated: Date.now(), items: items }));
    } catch (e) {
      /* приватный режим — корзина живёт до перезагрузки, это не повод падать */
    }
  }

  var cart = load();

  /* ---------- данные о блюдах со страницы ---------- */

  function lookup(id) {
    var node = document.querySelector('[data-item-id="' + cssEscape(id) + '"]');
    if (!node) return null;
    return {
      id: id,
      name: node.getAttribute('data-item-name') || id,
      price: parseInt(node.getAttribute('data-item-price'), 10) || 0
    };
  }

  function cssEscape(value) {
    return String(value).replace(/["\\]/g, '\\$&');
  }

  function detailed() {
    var out = [];
    for (var i = 0; i < cart.length; i++) {
      var info = lookup(cart[i].id) || cart[i].snapshot;
      if (!info || !info.price) continue;
      out.push({ id: cart[i].id, qty: cart[i].qty, name: info.name, price: info.price });
    }
    return out;
  }

  function total(list) {
    return list.reduce(function (sum, i) { return sum + i.price * i.qty; }, 0);
  }

  function money(value) {
    return String(value).replace(/\B(?=(\d{3})+(?!\d))/g, '\u202f') + '\u202f₸';
  }

  /* ---------- изменение состава ---------- */

  function add(id) {
    var info = lookup(id);
    if (!info) return;
    var found = null;
    for (var i = 0; i < cart.length; i++) if (cart[i].id === id) found = cart[i];
    if (found) {
      found.qty += 1;
    } else {
      cart.push({ id: id, qty: 1, snapshot: { name: info.name, price: info.price } });
    }
    save(cart);
    render();
  }

  function setQty(id, delta) {
    for (var i = 0; i < cart.length; i++) {
      if (cart[i].id !== id) continue;
      cart[i].qty += delta;
      if (cart[i].qty <= 0) cart.splice(i, 1);
      break;
    }
    save(cart);
    render();
  }

  function clear() {
    cart = [];
    save(cart);
    render();
  }

  /* ---------- сообщение для WhatsApp ---------- */

  function buildMessage(list, mode, compact) {
    var lines = list.map(function (i) {
      var qty = i.qty > 1 ? ' × ' + i.qty : '';
      return compact
        ? '• ' + i.name + qty
        : '• ' + i.name + qty + ' — ' + money(i.price * i.qty);
    });
    return [
      STR.greeting, '',
      lines.join('\n'), '',
      STR.total + ': ' + money(total(list)),
      mode === 'dinein' ? STR.dinein : STR.pickup
    ].join('\n');
  }

  function whatsappLink(list, mode) {
    var text = buildMessage(list, mode, false);
    // wa.me не открывается на части телефонов при слишком длинной ссылке —
    // для больших заказов убираем цены построчно, итог остаётся.
    if (encodeURIComponent(text).length > MAX_URL_TEXT) {
      text = buildMessage(list, mode, true);
    }
    return 'https://wa.me/' + WHATSAPP + '?text=' + encodeURIComponent(text);
  }

  /* ---------- разметка ---------- */

  var bar, panel, overlay, listEl, totalEl, sendEl, countEl, sumEl;

  function mount() {
    bar = document.createElement('div');
    bar.className = 'cartbar';
    bar.innerHTML =
      '<div><span class="cartbar__count"></span><span class="cartbar__sum"></span></div>' +
      '<button class="pill pill--brand" type="button">' + esc(STR.open) + '</button>';
    document.body.appendChild(bar);

    overlay = document.createElement('div');
    overlay.className = 'cart-overlay';
    document.body.appendChild(overlay);

    panel = document.createElement('aside');
    panel.className = 'cart-panel';
    panel.setAttribute('aria-label', STR.title);
    panel.setAttribute('aria-hidden', 'true');
    panel.innerHTML =
      '<div class="cart-panel__head">' +
        '<h2 style="margin:0">' + esc(STR.title) + '</h2>' +
        '<button class="cart-panel__close" type="button" aria-label="' + esc(STR.close) + '">×</button>' +
      '</div>' +
      '<ul class="cart-list"></ul>' +
      '<div class="cart-mode">' +
        '<input type="radio" name="frnds-mode" id="frnds-mode-pickup" value="pickup" checked>' +
        '<label for="frnds-mode-pickup">' + esc(STR.pickup) + '</label>' +
        '<input type="radio" name="frnds-mode" id="frnds-mode-dinein" value="dinein">' +
        '<label for="frnds-mode-dinein">' + esc(STR.dinein) + '</label>' +
      '</div>' +
      '<div class="cart-total"><span>' + esc(STR.total) + '</span><span class="cart-total__value"></span></div>' +
      '<a class="pill pill--brand cart-send" href="#" rel="noopener" target="_blank">' + esc(STR.send) + '</a>' +
      '<p class="cart-note">' + esc(STR.note) + '</p>' +
      '<p><button class="cart-clear" type="button">' + esc(STR.clear) + '</button></p>';
    document.body.appendChild(panel);

    listEl = panel.querySelector('.cart-list');
    totalEl = panel.querySelector('.cart-total__value');
    sendEl = panel.querySelector('.cart-send');
    countEl = bar.querySelector('.cartbar__count');
    sumEl = bar.querySelector('.cartbar__sum');

    bar.querySelector('button').addEventListener('click', open);
    panel.querySelector('.cart-panel__close').addEventListener('click', close);
    panel.querySelector('.cart-clear').addEventListener('click', function () { clear(); close(); });
    overlay.addEventListener('click', close);
    panel.addEventListener('change', function (e) {
      if (e.target.name === 'frnds-mode') render();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && panel.classList.contains('is-open')) close();
    });
  }

  function esc(text) {
    return String(text).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function mode() {
    var checked = panel.querySelector('input[name="frnds-mode"]:checked');
    return checked ? checked.value : 'pickup';
  }

  function render() {
    var list = detailed();
    var sum = total(list);
    var count = list.reduce(function (n, i) { return n + i.qty; }, 0);

    bar.classList.toggle('is-visible', count > 0);
    countEl.textContent = count + ' ' + plural(count);
    sumEl.textContent = money(sum);

    listEl.innerHTML = list.length
      ? list.map(function (i) {
          return '<li class="cart-item">' +
            '<span class="cart-item__name">' + esc(i.name) + '</span>' +
            '<span class="qty">' +
              '<button type="button" data-dec="' + esc(i.id) + '" aria-label="−">−</button>' +
              '<output>' + i.qty + '</output>' +
              '<button type="button" data-inc="' + esc(i.id) + '" aria-label="+">+</button>' +
            '</span>' +
            '<span class="cart-item__price">' + money(i.price * i.qty) + '</span>' +
          '</li>';
        }).join('')
      : '<li class="cart-empty">' + esc(STR.empty) + '</li>';

    totalEl.textContent = money(sum);
    sendEl.setAttribute('href', list.length ? whatsappLink(list, mode()) : '#');
    sendEl.setAttribute('aria-disabled', list.length ? 'false' : 'true');
  }

  function open() {
    panel.classList.add('is-open');
    overlay.classList.add('is-open');
    panel.setAttribute('aria-hidden', 'false');
    panel.querySelector('.cart-panel__close').focus();
  }

  function close() {
    panel.classList.remove('is-open');
    overlay.classList.remove('is-open');
    panel.setAttribute('aria-hidden', 'true');
  }

  /* ---------- события страницы ---------- */

  document.addEventListener('click', function (e) {
    var addBtn = e.target.closest ? e.target.closest('[data-add]') : null;
    if (addBtn) {
      e.preventDefault();
      add(addBtn.getAttribute('data-add'));
      var label = addBtn.querySelector('.pill__action');
      if (label) {
        var before = label.textContent;
        addBtn.classList.add('is-added');
        label.textContent = STR.added;
        setTimeout(function () {
          addBtn.classList.remove('is-added');
          label.textContent = before;
        }, 1200);
      }
      return;
    }
    var dec = e.target.closest ? e.target.closest('[data-dec]') : null;
    if (dec) { setQty(dec.getAttribute('data-dec'), -1); return; }
    var inc = e.target.closest ? e.target.closest('[data-inc]') : null;
    if (inc) { setQty(inc.getAttribute('data-inc'), +1); }
  });

  mount();
  render();
})();
