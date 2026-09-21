/* Shared pure helpers used by the UI and regression tests. */
(function (root) {
  'use strict';
  class RequestGate {
    constructor() { this.sequence = 0; this.controller = null; }
    cancel() { this.sequence += 1; this.controller?.abort(); }
    start(key) {
      this.cancel();
      this.controller = new AbortController();
      return { sequence: this.sequence, key, controller: this.controller };
    }
    current(ticket, key) {
      return ticket.sequence === this.sequence && ticket.key === key && !ticket.controller.signal.aborted;
    }
  }
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[char]));
  const statusClass = status => ({ compatible: 'ok', conditional: 'warn', unknown: 'warn', incompatible: 'bad', pass: 'ok', fail: 'bad' }[status] || 'warn');
  function sourceLink(url, label = 'NVIDIA documentation ↗') {
    try {
      const parsed = new URL(url);
      if (!['https:', 'http:'].includes(parsed.protocol)) return '—';
      return `<a class="source-link" href="${esc(parsed.href)}" target="_blank" rel="noopener noreferrer">${esc(label)}</a>`;
    } catch { return '—'; }
  }
  function filteredProducts(rows, filters) {
    return rows.filter(item => {
      const validation = item.validation || {};
      const endpoint = (item.endpoints || []).find(e => e.id === validation.endpoint_id);
      const haystack = [item.model, item.variant, item.category, item.cable_type, item.medium,
        ...(item.fabric_compatibility || []), ...(item.part_numbers || []),
        ...(item.endpoints || []).map(e => e.interface_type)].join(' ').toLowerCase();
      if (filters.search && !haystack.includes(filters.search.trim().toLowerCase())) return false;
      if (filters.lifecycle === 'active' && item.status !== 'active') return false;
      if (filters.outcome === 'candidates' && validation.status === 'incompatible') return false;
      if (!['all', 'candidates'].includes(filters.outcome) && filters.outcome !== validation.status) return false;
      if (filters.category && item.category !== filters.category) return false;
      if (filters.type && item.cable_type !== filters.type) return false;
      if (filters.medium && item.medium !== filters.medium) return false;
      if (filters.speed && !(endpoint?.modes || []).some(m => m.links * m.speed_gbps === Number(filters.speed))) return false;
      if (filters.reach) {
        const required = Number(filters.reach);
        if (item.reach?.max_m != null && item.reach.max_m < required) return false;
        if (item.category !== 'Transceiver' && item.skus?.length && item.skus.every(s => s.length_m != null && s.length_m < required)) return false;
      }
      return true;
    });
  }
  function configurationURL(config, revision, href) {
    const url = new URL(href);
    url.search = '';
    Object.entries(config).forEach(([key, value]) => {
      if (value !== '' && value != null) url.searchParams.set(key, String(value));
    });
    if (revision) url.searchParams.set('revision', revision);
    url.hash = '';
    return url.href;
  }
  function revisionMatches(result, context) {
    return result.revision === context.revision && result.device_id === context.device && result.port_group_id === context.group;
  }
  const api = { RequestGate, esc, sourceLink, statusClass, filteredProducts, configurationURL, revisionMatches };
  root.ValidatorCore = api;
  if (typeof module !== 'undefined') module.exports = api;
})(globalThis);
