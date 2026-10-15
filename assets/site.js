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

  function card(o) {
    var c = CATS[o.category] || { label: o.category, icon: '⭐' };
    return '<div class="offer-card" data-offer-id="' + esc(o.id) + '">' +
      '<div class="card-visual card-visual-' + esc(o.category) + '">' + c.icon +
      '<div class="card-tag tag-' + esc(o.category) + '">' + esc(c.label) + '</div></div>' +
      '<div class="card-body">' +
      '<h3 class="card-title">' + esc(o.title) + '</h3>' +
      (o.payout_note ? '<div class="card-payout">' + esc(o.payout_note) + '</div>' : '') +
      '<div class="card-desc">' + esc(o.description) + '</div>' +
      '<a href="' + esc(o.url) + '" class="card-cta cta-' + esc(o.category) + '" rel="sponsored noopener" target="_blank">' + esc(o.cta) + ' →</a>' +
      (o.category === 'sweepstakes' ? '<p class="card-legal">' + SWEEPS_NOTE + '</p>' : '') +
      '</div><div class="card-foot">Sponsored offer · See provider terms</div></div>';
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
            return cat ? o.category === cat : o.featured;
          });
          var limit = parseInt(g.getAttribute('data-limit') || '0', 10);
          if (limit) items = items.slice(0, limit);
          g.innerHTML = items.length ? items.map(card).join('') :
            '<p class="empty-note">No open offers in this category right now. Check back soon.</p>';
        });
      })
      .catch(function () { /* keep the static fallback markup */ });
  }

  var APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbxmyQME2DQlSfuXG093HgPyPdqzYlvDCu2R5FxAp-NZDP-wgCC428PesYzmA6FyznOp/exec';

  function setupEmail() {
    var form = document.getElementById('email-form');
    if (!form) return;
    var input = document.getElementById('email-input');
    var btn = document.getElementById('email-submit-btn');
    var error = document.getElementById('email-error');
    var confirm = document.getElementById('email-confirm');
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
        confirm.classList.add('show');
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
