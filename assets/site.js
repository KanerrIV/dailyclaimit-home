/* DailyClaimIt — renders offers from /offers.json (static HTML is the fallback) + email signup. */
(function () {
  var CATS = {
    'sweepstakes': { label: 'Sweepstakes', icon: '💰' },
    'surveys-quizzes': { label: 'Surveys & Quizzes', icon: '📝' },
    'free-stuff': { label: 'Free Stuff', icon: '🎁' }
  };
  var SWEEPS_NOTE = 'No purchase necessary. See official rules on offer page.';

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  // Same rule as build.py tag_url(): rewrite s1 / subId1 to dc_<page>_<placement>_<offer>.
  function tagUrl(url, tag) {
    tag = String(tag).toLowerCase().replace(/[^a-z0-9_]/g, '').slice(0, 50);
    return url.replace(/([?&](?:s1|subId1)=)[^&]*/, '$1' + tag);
  }

  // Banner-only offers (same markup as build.py banner_card): the official image is the only offer link.
  function bannerCard(o, tag) {
    var b = o.banner;
    var t = tag ? tagUrl(o.url, tag.replace(/_[a-z]+$/, '_banner') + '_' + o.id) : o.url;
    var legal = o.category === 'sweepstakes' ? '<p class="card-legal">No purchase necessary.' +
      (o.rules_url ? ' <a href="' + esc(o.rules_url) + '" rel="nofollow noopener" target="_blank">Official rules</a>.' : ' See official rules on offer page.') + '</p>' : '';
    return '<div class="offer-card offer-card-banner" data-offer-id="' + esc(o.id) + '">' +
      '<a class="banner-link" href="' + esc(t) + '" rel="sponsored noopener" target="_blank">' +
      '<img class="offer-banner" src="' + esc(b.image) + '" width="' + esc(b.width) + '" height="' + esc(b.height) + '" alt="' + esc(b.alt) + '" loading="lazy" /></a>' +
      '<div class="card-body"><h3 class="card-title">' + esc(o.title) + '</h3><div class="card-desc">' + esc(o.description) + '</div>' + legal + '</div></div>';
  }

  function card(o, tag) {
    if (o.banner) return bannerCard(o, tag);
    var c = CATS[o.category] || { label: o.category, icon: '⭐' };
    return '<div class="offer-card" data-offer-id="' + esc(o.id) + '">' +
      '<div class="card-visual card-visual-' + esc(o.category) + '">' + c.icon +
      '<div class="card-tag tag-' + esc(o.category) + '">' + esc(c.label) + '</div></div>' +
      '<div class="card-body">' +
      '<h3 class="card-title">' + esc(o.title) + '</h3>' +
      (o.payout_note ? '<div class="card-payout">' + esc(o.payout_note) + '</div>' : '') +
      '<div class="card-desc">' + esc(o.description) + '</div>' +
      '<a href="' + esc(tag ? tagUrl(o.url, tag + '_' + o.id) : o.url) + '" class="card-cta cta-' + esc(o.category) + '" rel="sponsored noopener" target="_blank">' + esc(o.cta) + ' →</a>' +
      (o.category === 'sweepstakes' ? '<p class="card-legal">' + SWEEPS_NOTE + '</p>' : '') +
      '</div></div>';
  }

  function renderOffers() {
    var grids = document.querySelectorAll('[data-offers]');
    if (!grids.length || !window.fetch) return;
    fetch('/offers.json', { cache: 'no-cache' })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (data) {
        var list = (data.offers || []).filter(function (o) { return o.active; });
        grids.forEach(function (g) {
          var cat = g.getAttribute('data-category');
          var items = list.filter(function (o) {
            return cat ? o.category === cat && (!o.banner || g.hasAttribute('data-banners')) : o.featured && !o.banner;
          });
          var limit = parseInt(g.getAttribute('data-limit') || '0', 10);
          if (limit) items = items.slice(0, limit);
          var tag = g.getAttribute('data-tag');
          g.innerHTML = items.length ? items.map(function (o) { return card(o, tag); }).join('') :
            '<p class="empty-note">No open offers in this category right now. Check back soon.</p>';
        });
      })
      .catch(function () { /* keep the static fallback markup */ });
  }

  var APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbxmyQME2DQlSfuXG093HgPyPdqzYlvDCu2R5FxAp-NZDP-wgCC428PesYzmA6FyznOp/exec';

  function setupEmail() {
    // Every signup form (Daily Drop + Starter Kit boxes) uses the same Apps Script endpoint.
    // Each form's data-source is sent as source: 'dailyclaimit-<data-source>'.
    document.querySelectorAll('form.email-form[data-source]').forEach(setupForm);
  }

  function setupForm(form) {
    var wrap = form.closest('.email-capture-inner, .kit-inner') || form.parentNode;
    var input = form.querySelector('input[type="email"]');
    var btn = form.querySelector('button[type="submit"]');
    var error = wrap.querySelector('.email-error');
    var confirm = wrap.querySelector('.email-confirm, .kit-thanks');
    var label = btn.textContent;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var email = input.value.trim();
      error.classList.remove('show');
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        error.textContent = 'Please enter a valid email address.';
        error.classList.add('show');
        input.focus();
        return;
      }
      btn.disabled = true;
      btn.textContent = 'Sending...';
      // Apps Script does not return CORS headers, so the response is opaque:
      // we can only confirm the request was delivered, not that it was stored.
      fetch(APPS_SCRIPT_URL, {
        method: 'POST',
        mode: 'no-cors',
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify({ email: email, timestamp: new Date().toISOString(), source: 'dailyclaimit-' + (form.getAttribute('data-source') || 'site') })
      }).then(function () {
        form.style.display = 'none';
        confirm.hidden = false;
        confirm.classList.add('show');
        var dl = confirm.querySelector('.kit-download');
        if (dl) dl.focus();
      }).catch(function () {
        btn.disabled = false;
        btn.textContent = label;
        error.textContent = "We couldn't reach our signup service. Check your connection and try again.";
        error.classList.add('show');
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () { renderOffers(); setupEmail(); });
})();
