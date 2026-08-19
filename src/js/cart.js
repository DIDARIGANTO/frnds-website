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

  // Тот же значок WhatsApp, что и в кнопках на страницах (build/components.py)
  var ICON_WA = '<svg class="icon-wa" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
    '<path fill="currentColor" d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15' +
    '-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48' +
    '-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099' +
    '-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57' +
    '-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 ' +
    '2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006' +
    '-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031' +
    '-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888' +
    '-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413' +
    '-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305' +
    '-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>';

  var LANG = document.body.getAttribute('data-lang') || 'ru';

  var STR = {
    ru: {
      title: 'Твой заказ', empty: 'Пока пусто. Выбери что-нибудь вкусное.',
      total: 'Итого', send: 'Отправить в WhatsApp', items: 'позиций',
      note: 'Это заготовка сообщения — заказ подтвердится в переписке.',
      pickup: 'Самовывоз', dinein: 'В зал', delivery: 'Доставка',
      deliveryMsg: 'Доставка — адрес напишу в чате', clear: 'Очистить',
      added: 'Добавлено', close: 'Закрыть', remove: 'Убрать',
      greeting: 'Здравствуйте! Заказ с сайта:', open: 'Открыть заказ',
      plural: ['позиция', 'позиции', 'позиций']
    },
    kk: {
      title: 'Сіздің тапсырысыңыз', empty: 'Әзірге бос. Дәмді бірдеңе таңдаңыз.',
      total: 'Барлығы', send: 'WhatsApp арқылы жіберу', items: 'позиция',
      note: 'Бұл — хабарлама дайындамасы, тапсырыс хат алмасуда расталады.',
      pickup: 'Өзім аламын', dinein: 'Залда', delivery: 'Жеткізу',
      deliveryMsg: 'Жеткізу — мекенжайын чатта жазамын', clear: 'Тазалау',
      added: 'Қосылды', close: 'Жабу', remove: 'Алып тастау',
      greeting: 'Сәлеметсіз бе! Сайттан тапсырыс:', open: 'Тапсырысты ашу',
      plural: ['позиция', 'позиция', 'позиция']
    },
    en: {
      title: 'Your order', empty: 'Empty for now. Pick something tasty.',
      total: 'Total', send: 'Send via WhatsApp', items: 'items',
      note: 'This only drafts a message — the order is confirmed in chat.',
      pickup: 'Pickup', dinein: 'Dine in', delivery: 'Delivery',
      deliveryMsg: "Delivery — I'll send the address in chat", clear: 'Clear',
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
    var modeLine = mode === 'dinein' ? STR.dinein
      : mode === 'delivery' ? STR.deliveryMsg
      : STR.pickup;
    return [
      STR.greeting, '',
      lines.join('\n'), '',
      STR.total + ': ' + money(total(list)),
      modeLine
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
        '<input type="radio" name="frnds-mode" id="frnds-mode-delivery" value="delivery" checked>' +
        '<label for="frnds-mode-delivery">' + esc(STR.delivery) + '</label>' +
        '<input type="radio" name="frnds-mode" id="frnds-mode-pickup" value="pickup">' +
        '<label for="frnds-mode-pickup">' + esc(STR.pickup) + '</label>' +
        '<input type="radio" name="frnds-mode" id="frnds-mode-dinein" value="dinein">' +
        '<label for="frnds-mode-dinein">' + esc(STR.dinein) + '</label>' +
      '</div>' +
      '<div class="cart-total"><span>' + esc(STR.total) + '</span><span class="cart-total__value"></span></div>' +
      '<a class="pill pill--brand pill--wa cart-send" href="#" rel="noopener" target="_blank">' + ICON_WA + '<span>' + esc(STR.send) + '</span></a>' +
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
