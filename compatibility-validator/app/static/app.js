/* Vanilla browser UI. Every async result is bound to selection + catalog revision. */
(() => {
  'use strict';
  const { RequestGate, esc, sourceLink, statusClass, filteredProducts, configurationURL, revisionMatches } = ValidatorCore;
  const $ = id => document.getElementById(id);
  const state = { meta: null, devices: [], products: [], hardware: [], fibers: [], rows: [], selected: null, linkResult: null, wizardResult: null, view: 'port', online: false };
  const portGate = new RequestGate(), catalogGate = new RequestGate(), linkGate = new RequestGate(), hardwareGate = new RequestGate(), wizardGate = new RequestGate();
  const plainFields = ['search', 'outcomeFilter', 'lifecycleFilter', 'fabricFilter', 'categoryFilter', 'typeFilter', 'mediumFilter', 'speedFilter', 'reachFilter', 'linkFabric', 'linkLength', 'fiberType', 'connectorA', 'connectorB'];
  const hosts = ['port', 'a', 'b', 'wa', 'wb'];
  const runtimeFields = { Sku: 'sku', Opn: 'opn', Variant: 'adapter_variant', Psid: 'psid', Firmware: 'firmware', Os: 'os_name', OsVersion: 'os_version' };
  const wizardFields = ['wizardFabric', 'wizardSpeed', 'wizardLength', 'wizardTechnology', 'wizardFiber', 'reusePn', 'reuseSide', 'wizardSort', 'ownedParts'];
  plainFields.push(...wizardFields, ...hosts.flatMap(h => Object.keys(runtimeFields).map(f => h + f)));
  for (const host of hosts) {
    $(host + 'Hardware').innerHTML = `<label for="${host}Profile">Exact hardware / OPN</label><select id="${host}Profile"></select><details><summary>Observed hardware and software (optional)</summary><div class="grid3">${Object.entries(runtimeFields).map(([suffix, field]) => `<div><label for="${host + suffix}">${esc(field.replaceAll('_', ' '))}</label><input id="${host + suffix}" maxlength="128" autocomplete="off"></div>`).join('')}</div></details>`;
  }
  const storageKey = 'nvidia-validator-v1';
  let pollTimer, sharedRevision = null;

  function choices(id, entries, preferred, placeholder = null) {
    const select = $(id);
    select.replaceChildren();
    if (placeholder != null) entries = [['', placeholder], ...entries];
    entries.forEach(([value, label]) => {
      const option = document.createElement('option');
      option.value = value;
      option.textContent = label;
      select.appendChild(option);
    });
    if (entries.some(([value]) => value === preferred)) select.value = preferred;
    select.disabled = !entries.length;
  }
  function assign(id, value) {
    if (value == null) return;
    const element = $(id);
    if (element.tagName !== 'SELECT' || Array.from(element.options).some(o => o.value === String(value))) element.value = String(value);
  }
  function readConfig() {
    const config = { revision: state.meta?.revision, view: state.view, kind: $('kind').value, device: $('device').value, group: $('group').value, mode: $('mode').value, product: state.selected || '', partNumber: $('partNumber').value, pinout: $('pinout').checked ? '1' : '0' };
    plainFields.forEach(id => { config[id] = $(id).value; });
    for (const side of ['a', 'b']) for (const field of ['Device', 'Group', 'Mode', 'Product', 'End', 'Pn']) config[side + field] = $(side + field).value;
    for (const side of ['wa', 'wb']) for (const field of ['Device', 'Group', 'Mode']) config[side + field] = $(side + field).value;
    hosts.forEach(h => { config[h + 'Profile'] = $(h + 'Profile').value; });
    config.fiberPn = $('fiberPn').value; config.includeUnknown = $('includeUnknown').checked ? '1' : '0';
    return config;
  }
  function restoreConfig() {
    const url = new URL(location.href);
    sharedRevision = url.searchParams.get('revision');
    if (url.searchParams.size) return Object.fromEntries(url.searchParams);
    try { return JSON.parse(localStorage.getItem(storageKey) || '{}') || {}; } catch { return {}; }
  }
  function save() { if (!state.meta) return; try { localStorage.setItem(storageKey, JSON.stringify(readConfig())); } catch { /* Storage may be disabled. */ } }
  function kv(key, value) { return `<div class="kv"><div class="k">${esc(key)}</div><div class="v">${esc(value ?? '—')}</div></div>`; }
  function badge(status) { return `<span class="pill ${statusClass(status)}">${esc(status)}</span>`; }
  function groupFor(deviceId, groupId, profileId = '') {
    const group = state.devices.find(d => d.id === deviceId)?.port_groups.find(g => g.id === groupId);
    const port = state.hardware.find(p => p.id === profileId && p.device_id === deviceId)?.ports.find(p => p.port_group_id === groupId);
    if (!group || !port) return group;
    const overlay = Object.fromEntries(['module_speed_gbps', 'count', 'fabrics', 'modes'].filter(k => Array.isArray(port[k]) ? port[k].length : port[k]).map(k => [k, port[k]]));
    return { ...group, ...overlay };
  }
  function hostId(host, field) { return host === 'port' ? field.toLowerCase() : host + field; }
  function hostGroup(host) { return groupFor($(hostId(host, 'Device')).value, $(hostId(host, 'Group')).value, $(host + 'Profile').value); }
  function hostSelection(host) {
    return { device_id: $(hostId(host, 'Device')).value, port_group_id: $(hostId(host, 'Group')).value,
      mode_id: $(hostId(host, 'Mode')).value || null, hardware_profile_id: $(host + 'Profile').value || null,
      runtime: Object.fromEntries(Object.entries(runtimeFields).map(([suffix, field]) => [field, $(host + suffix).value.trim() || null])) };
  }
  function fillHardware(host, wanted = {}) {
    const device = state.devices.find(d => d.id === $(hostId(host, 'Device')).value);
    choices(host + 'Profile', state.hardware.filter(p => p.device_id === device?.id).map(p => [p.id, p.label]), wanted[host + 'Profile'], 'Generic device — exact board not selected');
    const profile = state.hardware.find(p => p.id === $(host + 'Profile').value);
    const groups = (device?.port_groups || []).filter(g => !profile || profile.ports.some(p => p.port_group_id === g.id));
    choices(hostId(host, 'Group'), groups.map(g => [g.id, g.label]), wanted[hostId(host, 'Group')]);
    fillModes(hostId(host, 'Mode'), hostGroup(host), wanted[hostId(host, 'Mode')]);
  }
  function clearRuntime(host) { Object.keys(runtimeFields).forEach(f => { $(host + f).value = ''; }); }
  function productFor(id) { return state.products.find(p => p.id === id); }
  function portKey() { return JSON.stringify([state.meta?.revision, hostSelection('port'), $('fabricFilter').value]); }
  function updateExport() {
    $('export').disabled = ['breakout', 'project'].includes(state.view) ? !window.ValidatorTopology?.hasReport(state.view) : state.view === 'wizard' ? !state.wizardResult : state.view === 'link' ? !state.linkResult : !state.hardwareReport && !state.rows.some(i => i.id === state.selected);
    $('addConnectionToProject').disabled = !state.linkResult;
  }
  function showChecks(id, checks) {
    $(id).innerHTML = `<table><thead><tr><th>Check</th><th>Evidence and remaining requirements</th><th>Source</th></tr></thead><tbody>${checks.map(c => `<tr><td>${badge(c.state)}<code>${esc(c.code)}</code></td><td>${esc(c.message)}${c.state === 'unknown' ? `<div class="small">${c.required ? 'Required information missing' : 'Condition to verify'}</div>` : ''}</td><td>${c.source_url ? sourceLink(c.source_url, 'Source ↗') : '—'}</td></tr>`).join('')}</tbody></table>`;
  }
  function serviceMessage(message) {
    $('serviceMessage').textContent = message;
    $('serviceMessage').classList.toggle('hidden', !message);
  }
  function renderMeta() {
    if (!state.meta) return;
    const meta = state.meta, degraded = meta.catalog.state === 'degraded';
    $('meta').innerHTML = `<span class="${degraded ? 'warn' : 'ok'}"><b>${degraded ? 'DEGRADED · last good catalog' : 'CONNECTED'}</b></span><span>snapshot <b>${esc(meta.snapshot_date)}</b></span><span>revision <code>${esc(meta.revision)}</code></span><span>${esc(meta.device_count)} devices · ${esc(meta.interconnect_count)} products</span>`;
    if (degraded) serviceMessage(`A catalog update was rejected. Results use the last valid revision ${meta.revision}, loaded ${meta.catalog.last_successful_load}.`);
    else if (sharedRevision && sharedRevision !== meta.revision) serviceMessage(`This link was created for revision ${sharedRevision}. The available catalog is ${meta.revision}; all results have been recalculated.`);
    else serviceMessage('');
  }
  function offline(error) {
    state.online = false;
    $('meta').innerHTML = '<span class="bad"><b>OFFLINE / API unavailable</b></span>';
    serviceMessage(`${error.message}. ${state.meta ? `Displayed catalog revision ${state.meta.revision} was fetched earlier.` : 'Waiting for a valid catalog.'} Use Refresh catalog to retry.`);
  }
  async function jsonRequest(url, ticket, options = {}) {
    let timeout = false;
    const timer = setTimeout(() => { timeout = true; ticket.controller.abort(); }, 12000);
    try {
      const response = await fetch(url, { ...options, signal: ticket.controller.signal, cache: 'no-store' });
      const data = await response.json();
      if (!response.ok) {
        const error = new Error(typeof data.detail === 'string' ? data.detail : 'Invalid request; check the selected parameters.');
        error.status = response.status;
        throw error;
      }
      return data;
    } catch (error) {
      if (timeout) throw new Error('Request timed out');
      throw error;
    } finally { clearTimeout(timer); }
  }
  function fillPortDevices(wanted = {}) {
    const preferred = state.devices.find(d => d.id === wanted.device) || state.devices.find(d => d.id === 'ethernet:SN5600') || state.devices[0];
    const kinds = [...new Set(state.devices.map(d => d.kind))].sort();
    choices('kind', kinds.map(k => [k, k]), preferred?.kind);
    fillDeviceOptions(preferred?.id);
    fillGroups(wanted.group, wanted.mode, wanted);
  }
  function fillDeviceOptions(preferred) {
    choices('device', state.devices.filter(d => d.kind === $('kind').value).map(d => [d.id, `${d.model}${d.validation_ready ? '' : ' [no port profile]'}`]), preferred);
  }
  function fillGroups(preferred, mode, wanted = {}) {
    const device = state.devices.find(d => d.id === $('device').value);
    choices('group', (device?.port_groups || []).map(g => [g.id, g.label]), preferred);
    fillHardware('port', { ...wanted, group: preferred, mode });
    $('deviceSummary').innerHTML = ['Model', 'Family', 'Profile', 'Source'].map((label, i) => `<div class="summary-box"><div class="k">${label}</div><div class="v">${esc([device?.model, device?.family, device?.source, device?.sku || 'See documentation'][i] || '—')}</div></div>`).join('');
    $('deviceMessage').textContent = device?.warning || device?.notes || '';
    $('deviceMessage').classList.toggle('hidden', !$('deviceMessage').textContent);
  }
  function fillModes(id, group, preferred) {
    choices(id, (group?.modes || []).map(m => [m.id, `${m.id} · ${m.links} × ${m.speed_gbps}G${m.fabrics?.length ? ' · ' + m.fabrics.join('/') : ''}`]), preferred, group?.modes.length ? 'Any documented mode' : 'Mode unknown');
  }
  function resetDecision() {
    $('selectedOutcome').textContent = 'No selection';
    $('selectedOutcome').className = 'pill';
    $('validationText').textContent = 'Select a product to inspect every check.';
    $('sideProduct').replaceChildren(); $('checks').replaceChildren(); $('skuDetails').replaceChildren();
    choices('partNumber', [], null); $('export').disabled = true;
  }
  function renderGroup() {
    const g = hostGroup('port');
    $('sideGroup').innerHTML = g ? kv('Group', g.label) + kv('Cage', g.connector_family) + kv('Capacity', g.module_speed_gbps ? `${g.module_speed_gbps}G` : 'Unknown') + kv('Modes', g.modes.map(m => `${m.links} × ${m.speed_gbps}G`).join(', ') || 'Unknown') + kv('Fabric', g.fabrics.join(', ') || 'Unknown') + kv('Mechanics', g.accepted_interface_types.join(', ') || 'Not specified') + kv('Scope', g.scope_note || 'See source') + sourceLink(g.source_url, 'Port profile source ↗') : 'No port profile.';
  }
  function refreshFilters(wanted = {}) {
    for (const [id, key, label] of [['categoryFilter', 'category', 'All categories'], ['typeFilter', 'cable_type', 'All types']]) {
      const previous = wanted[id] ?? $(id).value;
      choices(id, [...new Set(state.products.map(p => p[key]).filter(Boolean))].sort().map(v => [v, v]), previous, label);
    }
    const previous = wanted.speedFilter ?? $('speedFilter').value;
    const speeds = [...new Set(state.products.flatMap(p => (p.endpoints || []).flatMap(e => e.modes.map(m => m.links * m.speed_gbps))))].sort((a, b) => a - b);
    choices('speedFilter', speeds.map(s => [String(s), `${s}G`]), previous, 'Any rate');
  }
  function filters() {
    return { search: $('search').value, outcome: $('outcomeFilter').value, lifecycle: $('lifecycleFilter').value,
      category: $('categoryFilter').value, type: $('typeFilter').value, medium: $('mediumFilter').value,
      speed: $('speedFilter').value, reach: $('reachFilter').value };
  }
  function renderProducts() {
    const rows = filteredProducts(state.rows, filters());
    $('compatibleCount').textContent = `${rows.length} / ${state.rows.length} products`;
    if (!rows.length) {
      $('compatibleWrap').innerHTML = '<div class="empty">No matching products. Try All results / All lifecycle states to inspect rejected or retired products.</div>';
      return;
    }
    $('compatibleWrap').innerHTML = `<table><thead><tr><th>Model / variant</th><th>Result</th><th>Connect this end</th><th>Mode per termination</th><th>Type / medium</th><th>Reach</th><th>Part numbers</th></tr></thead><tbody>${rows.map(item => {
      const v = item.validation, end = item.endpoints.find(e => e.id === v.endpoint_id);
      return `<tr class="${item.id === state.selected ? 'selected' : ''}" data-id="${esc(item.id)}"><td><button class="model-button" data-product="${esc(item.id)}" aria-pressed="${item.id === state.selected}">${esc(item.model)}</button><div class="small">${esc(item.variant || '')}</div><div class="small">${esc(item.status)}</div></td><td>${badge(v.status)}</td><td>${esc(end ? `${end.id} · ${end.interface_type}` : 'Unknown')}<div class="small">${esc(end?.role || '')}${end?.count > 1 ? ` · ${end.count} terminations` : ''}</div></td><td>${esc((end?.modes || []).map(m => `${m.links} × ${m.speed_gbps}G`).join(', ') || 'Unknown')}</td><td>${esc(item.cable_type)}<div class="small">${esc(item.medium || 'Unknown')}</div></td><td>${esc(item.reach?.max_m != null ? `${item.reach.max_m}m` : 'Unknown')}</td><td class="pn-cell small">${esc(item.part_numbers.join(', ') || 'Not documented')}</td></tr>`;
    }).join('')}</tbody></table>`;
    $('compatibleWrap').querySelectorAll('[data-product]').forEach(button => button.addEventListener('click', () => selectProduct(button.dataset.product)));
  }
  function renderSKU() {
    const item = state.rows.find(i => i.id === state.selected);
    const sku = item?.skus.find(s => s.part_number === $('partNumber').value);
    $('skuDetails').innerHTML = sku ? kv('Length', sku.length_m != null ? `${sku.length_m}m` : item.category === 'Transceiver' ? 'Fiber selected separately' : 'Not documented for this PN') + sourceLink(sku.source_url, 'SKU source ↗') : 'Choose a part number; family reach does not specify a cable SKU length.';
  }
  function selectProduct(id, pn = null) {
    const item = state.rows.find(i => i.id === id);
    state.selected = item ? id : null;
    if (!item) { resetDecision(); updateExport(); return; }
    const v = item.validation, end = item.endpoints.find(e => e.id === v.endpoint_id);
    $('selectedOutcome').textContent = v.status.toUpperCase();
    $('selectedOutcome').className = `pill ${statusClass(v.status)}`;
    $('validationText').textContent = `${item.model}: ${v.status}. ${end ? `Use termination ${end.id} (${end.interface_type}, ${end.role}).` : 'Endpoint details are missing.'} Scope: selected host port.${v.qualification ? ' Hardware/software qualification: ' + v.qualification.status + '.' : ''}`;
    $('sideProduct').innerHTML = kv('Model', item.model) + kv('Variant', item.variant) + kv('Mechanical match', v.match_type) + kv('Fabric', item.fabric_compatibility.join(', ') || 'Unknown') + kv('Other ends', v.alternatives.map(a => `${a.endpoint_id || '?'}: ${a.status}`).join('; ')) + sourceLink(item.source_url);
    choices('partNumber', item.skus.map(s => [s.part_number, `${s.part_number}${s.length_m != null ? ` · ${s.length_m}m` : ''}`]), pn, 'Choose PN');
    showChecks('checks', v.checks); renderSKU(); renderProducts(); updateExport(); save();
  }
  async function refreshPort(preferred = state.selected, pn = $('partNumber').value) {
    const context = { revision: state.meta?.revision, device: $('device').value, group: $('group').value };
    const ticket = portGate.start(portKey());
    state.rows = []; state.selected = null; resetDecision(); renderGroup(); invalidateHardware();
    $('compatibleCount').textContent = '0 products';
    if (!context.group || !context.device) {
      $('compatibleWrap').innerHTML = '<div class="empty">No explicit port profile is available for this device.</div>';
      return;
    }
    $('compatibleWrap').innerHTML = '<div class="empty">Evaluating products…</div>';
    const query = new URLSearchParams({ device_id: context.device, port_group_id: context.group, revision: context.revision });
    if ($('mode').value) query.set('mode_id', $('mode').value);
    if ($('fabricFilter').value) query.set('fabric', $('fabricFilter').value);
    try {
      const hardware = hostSelection('port');
      const scoped = hardware.hardware_profile_id || Object.values(hardware.runtime).some(Boolean);
      const result = await jsonRequest(scoped ? '/api/evaluate' : `/api/evaluate?${query}`, ticket, scoped ? {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...hardware, fabric: $('fabricFilter').value || null, revision: state.meta.revision }) } : {});
      if (!portGate.current(ticket, portKey())) return;
      if (!revisionMatches(result, context)) throw new Error('Catalog revision changed during validation; refresh the catalog.');
      state.rows = result.products;
      if (result.hardware) renderHardware(result.hardware);
      renderProducts();
      if (preferred) selectProduct(preferred, pn);
    } catch (error) {
      if (ticket.sequence !== portGate.sequence) return;
      if (error.status === 409) { await loadCatalog(); return; }
      $('compatibleWrap').innerHTML = `<div class="empty bad">${esc(error.message)}</div>`;
      if (!error.status || error.status >= 500) offline(error);
    }
    updateExport(); save();
  }
  function fillLinkGroups(side, wanted = {}) {
    fillHardware(side, wanted);
  }
  function fillLinkProduct(side, wanted = {}) {
    const item = productFor($(side + 'Product').value);
    choices(side + 'End', (item?.endpoints || []).map(e => [e.id, `${e.id}: ${e.interface_type} (${e.role}${e.count > 1 ? `, ${e.count} ends` : ''})`]), wanted[side + 'End'], 'Choose best documented end');
    choices(side + 'Pn', (item?.skus || []).map(s => [s.part_number, `${s.part_number}${s.length_m != null ? ` · ${s.length_m}m` : ' · length unspecified'}`]), wanted[side + 'Pn'], 'Choose PN');
    updateFiberVisibility();
  }
  function fillLink(wanted) {
    for (const side of ['a', 'b']) {
      choices(side + 'Device', state.devices.map(d => [d.id, d.model]), wanted[side + 'Device'] || (side === 'a' ? 'profile:MQM9700-NS2F' : 'system:DGX B200'));
      fillLinkGroups(side, wanted);
      const defaultCable = state.products.find(p => p.model === 'MCA4J80-Nxxx-FTF');
      choices(side + 'Product', state.products.map(p => [p.id, `${p.model}${p.variant ? ` · ${p.variant}` : ''} [${p.status}]`]), wanted[side + 'Product'] || defaultCable?.id);
      fillLinkProduct(side, wanted);
    }
  }
  function updateFiberVisibility() {
    const optical = productFor($('aProduct').value)?.category === 'Transceiver' && productFor($('bProduct').value)?.category === 'Transceiver';
    $('fiberOptions').classList.toggle('hidden', !optical);
  }
  function invalidateLink() {
    linkGate.cancel(); state.linkResult = null;
    $('linkChecks').replaceChildren(); $('linkStatus').textContent = 'Selection changed. Run validation.';
    $('linkQualification').replaceChildren(); $('linkGaps').replaceChildren();
    $('validateLink').disabled = !state.meta; updateExport(); save();
  }
  function connectionRequest() {
    const selection = side => ({ ...hostSelection(side),
      product_id: $(side + 'Product').value, endpoint_id: $(side + 'End').value || null,
      mode_id: $(side + 'Mode').value || null, part_number: $(side + 'Pn').value || null });
    const optical = productFor($('aProduct').value)?.category === 'Transceiver' && productFor($('bProduct').value)?.category === 'Transceiver';
    return { a: selection('a'), b: selection('b'), fabric: $('linkFabric').value,
      length_m: $('linkLength').value ? Number($('linkLength').value) : null,
      fiber_part_number: optical ? $('fiberPn').value || null : null,
      fiber: optical ? { medium: ['OS2', 'SM-unspecified'].includes($('fiberType').value) ? 'SM' : 'MM', fiber_type: $('fiberType').value,
        connector_a: $('connectorA').value, connector_b: $('connectorB').value, pinout_verified: $('pinout').checked } : null,
      revision: state.meta?.revision };
  }
  async function runLink() {
    const request = connectionRequest(), key = JSON.stringify(request), ticket = linkGate.start(key);
    state.linkResult = null; updateExport(); $('linkChecks').replaceChildren();
    $('validateLink').disabled = true; $('linkStatus').textContent = 'Validating both endpoints…';
    try {
      const result = await jsonRequest('/api/connection', ticket, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: key });
      if (!linkGate.current(ticket, JSON.stringify(connectionRequest()))) return;
      if (result.revision !== state.meta.revision) throw new Error('Catalog changed during validation. Refresh and try again.');
      state.linkResult = result;
      $('linkStatus').innerHTML = `${badge(result.status)} End ${esc(result.orientation.a || '?')} at A → end ${esc(result.orientation.b || '?')} at B · one link`;
      showChecks('linkChecks', result.checks);
      $('linkQualification').textContent = qualificationText(result);
      $('linkGaps').innerHTML = gapsMarkup(result.gaps || []);
    } catch (error) {
      if (ticket.sequence !== linkGate.sequence) return;
      if (error.status === 409) { await loadCatalog(); return; }
      $('linkStatus').textContent = error.message;
      if (!error.status || error.status >= 500) offline(error);
    } finally {
      if (ticket.sequence === linkGate.sequence) $('validateLink').disabled = false;
      updateExport(); save();
    }
  }
  function setView(view) {
    state.view = ['link', 'wizard', 'breakout', 'project'].includes(view) ? view : 'port';
    for (const name of ['port', 'link', 'wizard', 'breakout', 'project']) {
      $(name + 'View').classList.toggle('hidden', state.view !== name);
      $(name + 'Tab').setAttribute('aria-selected', String(state.view === name));
    }
    $('share').disabled = ['breakout', 'project'].includes(state.view);
    $('share').title = $('share').disabled ? 'Export the complete definition/project JSON to share these configurations.' : '';
    updateExport();
  }
  async function loadCatalog(initial = false) {
    const ticket = catalogGate.start('catalog');
    portGate.cancel(); invalidateLink(); invalidateWizard(); invalidateHardware();
    try {
      const bundle = await jsonRequest('/api/catalog', ticket);
      if (!catalogGate.current(ticket, 'catalog')) return;
      const wanted = initial || !state.meta ? restoreConfig() : readConfig();
      state.meta = bundle.meta; state.devices = bundle.devices; state.products = bundle.products; state.online = true; $('validateLink').disabled = false;
      state.hardware = bundle.hardware_profiles || []; state.fibers = bundle.fiber_assemblies || [];
      window.ValidatorTopology?.setCatalog(bundle);
      refreshFilters(wanted); fillPortDevices(wanted); fillLink(wanted); fillWizard(wanted);
      choices('fiberPn', state.fibers.map(f => [f.part_number, `${f.part_number} · ${f.length_m}m · ${f.fiber_type}`]), wanted.fiberPn, 'Custom fiber — ordering PN unspecified');
      for (const side of ['A', 'B']) {
        const id = 'connector' + side;
        const connectors = [...new Set([...Array.from($(id).options).map(o => o.value), ...state.products.map(p => p.optics?.connector).filter(Boolean), ...state.fibers.map(f => f['connector_' + side.toLowerCase()]), 'Unspecified'])];
        choices(id, connectors.map(c => [c, c]), wanted[id] || $(id).value);
      }
      plainFields.forEach(id => assign(id, wanted[id]));
      $('includeUnknown').checked = wanted.includeUnknown !== '0';
      $('pinout').checked = wanted.pinout === '1' && (!wanted.revision || wanted.revision === bundle.meta.revision);
      setView(wanted.view); renderMeta(); updateFiberVisibility();
      if (wanted.product && !state.products.some(p => p.id === wanted.product)) $('actionMessage').textContent = 'The previously selected product is no longer present in this revision.';
      await refreshPort(wanted.product, wanted.partNumber);
    } catch (error) { if (ticket.sequence === catalogGate.sequence) offline(error); }
  }
  async function pollMeta() {
    const controller = new AbortController(), ticket = { controller };
    try {
      const meta = await jsonRequest('/api/meta', ticket);
      if (!state.meta || state.meta.revision !== meta.revision) await loadCatalog();
      else { state.meta = meta; state.online = true; renderMeta(); }
    } catch (error) { offline(error); }
    finally { pollTimer = setTimeout(pollMeta, 5000); }
  }
  function exportedReport() {
    if (['breakout', 'project'].includes(state.view)) return window.ValidatorTopology.exportReport(state.view);
    const item = state.rows.find(p => p.id === state.selected);
    return { format: 'nvidia-compatibility-report-v1', exported_at: new Date().toISOString(),
      catalog: state.meta, api_online: state.online, configuration: readConfig(),
      configuration_url: configurationURL(readConfig(), state.meta?.revision, location.href),
      scope: state.view === 'wizard' ? 'connection-recommendations' : state.view === 'link' ? 'single-link' : 'host-port',
      result: state.view === 'wizard' ? state.wizardResult : state.view === 'link' ? state.linkResult : item || state.hardwareReport,
      hardware_report: state.view === 'port' ? state.hardwareReport : undefined,
      port_profile: state.view === 'port' ? hostGroup('port') : undefined };
  }
  function gapsMarkup(gaps) {
    return gaps.length ? `<details class="evidence-details"><summary>${gaps.length} missing facts / next steps</summary><ul>${gaps.map(g => `<li><strong>${esc(g.message)}</strong><div>${esc(g.action)}</div></li>`).join('')}</ul></details>` : '<p class="small">No missing facts in this scope.</p>';
  }
  function qualificationText(result) {
    return result.qualification ? `Technical checks: ${result.technical_status}. Qualification: A ${result.qualification.a.status}; B ${result.qualification.b.status}.` : '';
  }
  function evidenceMarkup(evidence, fallback) {
    return evidence ? `${esc(evidence.kind === 'lab' ? 'Internal lab' : 'Manufacturer source')} · ${esc(evidence.verified_on)}<div>${esc(evidence.scope)}</div>${sourceLink(evidence.source_url, 'Evidence ↗')}${evidence.note ? `<div class="small">${esc(evidence.note)}</div>` : ''}` : `${sourceLink(fallback, 'Catalog source ↗')}<div class="small">Verification date / exact scope not recorded</div>`;
  }
  function invalidateHardware() {
    hardwareGate.cancel(); state.hardwareReport = null;
    $('hardwareReport').textContent = 'Inspect the current board and runtime to see evidence and missing facts.';
    $('inspectHardware').disabled = !state.meta;
    updateExport();
  }
  function renderHardware(result) {
    state.hardwareReport = result;
    $('hardwareReport').innerHTML = `<p>${esc(result.profile?.label || 'Generic device profile')} · ${esc(result.revision)}</p>${(result.checks || []).map(c => `<p>${badge(c.state)} ${esc(c.message)}</p>`).join('')}<div class="tablewrap"><table><thead><tr><th>Parameter</th><th>Value</th><th>Source, verification date and scope</th></tr></thead><tbody>${result.facts.map(f => `<tr><td>${esc(f.field)}</td><td>${esc(f.value == null ? 'Unknown' : typeof f.value === 'object' ? JSON.stringify(f.value) : f.value)}</td><td>${evidenceMarkup(f.evidence, f.source_url)}</td></tr>`).join('')}</tbody></table></div>${gapsMarkup(result.gaps)}${(result.profile?.notes || []).map(n => `<p class="small">${esc(n)}</p>`).join('')}`;
    updateExport();
  }
  async function inspectHardware() {
    state.hardwareReport = null; updateExport();
    const ticket = hardwareGate.start(portKey());
    $('inspectHardware').disabled = true; $('hardwareReport').textContent = 'Inspecting hardware evidence…';
    try {
      const result = await jsonRequest('/api/hardware/inspect', ticket, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...hostSelection('port'), revision: state.meta.revision }) });
      if (!hardwareGate.current(ticket, portKey())) return;
      if (result.revision !== state.meta.revision) throw new Error('Catalog changed. Refresh and inspect again.');
      renderHardware(result);
    } catch (error) {
      if (ticket.sequence !== hardwareGate.sequence) return;
      if (error.status === 409) { await loadCatalog(); return; }
      $('hardwareReport').textContent = error.message;
    } finally { if (ticket.sequence === hardwareGate.sequence) $('inspectHardware').disabled = false; }
  }
  function fillWizard(wanted) {
    for (const side of ['wa', 'wb']) {
      choices(side + 'Device', state.devices.map(d => [d.id, d.model]), wanted[side + 'Device'] || (side === 'wa' ? 'profile:MQM9700-NS2F' : 'system:DGX B200'));
      fillHardware(side, wanted);
    }
    $('knownParts').replaceChildren(...[...new Set([...state.products.flatMap(p => p.part_numbers), ...state.fibers.map(f => f.part_number)])].sort().map(pn => { const option = document.createElement('option'); option.value = pn; return option; }));
    $('recommend').disabled = false;
  }
  function wizardKey() { return JSON.stringify([state.meta?.revision, hostSelection('wa'), hostSelection('wb'), ...wizardFields.map(id => $(id).value), $('includeUnknown').checked]); }
  function invalidateWizard() {
    wizardGate.cancel(); state.wizardResult = null;
    $('wizardResults').replaceChildren(); $('wizardStatus').textContent = 'Requirements changed. Search again.';
    $('recommend').disabled = !state.meta; updateExport(); save();
  }
  function recommendationRequest() {
    const owned = $('ownedParts').value.split(/\r?\n/).filter(line => line.trim()).map(line => {
      const fields = line.split(',').map(v => v.trim());
      if (fields.length > 2 || !fields[0] || (fields.length === 2 && !/^[1-9]\d*$/.test(fields[1]))) throw new Error('Inventory format: one PN,positive quantity per line.');
      return { part_number: fields[0], quantity: fields.length === 1 ? 1 : Number(fields[1]) };
    });
    return { a: hostSelection('wa'), b: hostSelection('wb'), fabric: $('wizardFabric').value,
      speed_gbps: Number($('wizardSpeed').value), minimum_length_m: Number($('wizardLength').value),
      technology: $('wizardTechnology').value, fiber_type: $('wizardFiber').value,
      reuse_part_number: $('reusePn').value.trim() || null, reuse_side: $('reuseSide').value,
      owned_parts: owned, sort_by: $('wizardSort').value, include_unknown: $('includeUnknown').checked,
      revision: state.meta.revision };
  }
  function renderRecommendations(result) {
    $('wizardStatus').textContent = `${result.candidates.length} shown / ${result.total_candidates} proposals · ${result.examined} combinations checked${result.truncated ? ' · SEARCH LIMITED — narrow requirements' : ''}`;
    const notes = result.notes.map(n => `<p class="small">${esc(n)}</p>`).join('');
    $('wizardResults').innerHTML = notes + (result.candidates.length ? `<div class="tablewrap"><table class="recommendation-table"><thead><tr><th>Option / decision</th><th>Components and ordering numbers</th><th>Length / settings</th><th>Evidence / inventory</th><th>Review</th></tr></thead><tbody>${result.candidates.map((c, index) => {
      const v = c.validation;
      return `<tr><td><strong>${esc(c.technology)}</strong><div>${badge(v.status)}</div><div class="small">${esc(qualificationText(v))}</div>${c.ordering_complete ? '' : '<div class="warn">Ordering number unresolved</div>'}</td><td>${c.components.map(p => `<div class="component"><strong>${esc(p.side.toUpperCase())}: ${esc(p.part_number || 'PN unknown')}</strong><div>${esc(p.model)} · ${esc(p.role)}</div>${sourceLink(p.source_url, 'Ordering source ↗')}</div>`).join('')}</td><td>${esc(c.length_m == null ? 'Length unknown' : c.length_m + ' m')}<div>${Object.entries(c.settings).map(([side, m]) => `${esc(side.toUpperCase())}: ${esc(m ? m.id + ' (' + m.links + ' × ' + m.speed_gbps + 'G); FEC ' + (m.fec?.join('/') || 'unknown') : 'mode unknown')}`).join('<br>')}</div><div class="small">Cable ends: ${esc(v.orientation.a || '?')} at A / ${esc(v.orientation.b || '?')} at B</div></td><td>${esc(c.evidence_summary.passed_checks)} checks passed · ${esc(c.evidence_summary.unknown_checks)} unknown<div>${esc(c.component_count)} components · ${esc(c.reused_count)} reused</div>${c.inventory.map(p => `<div class="small">${esc(p.part_number)}: need ${esc(p.required)}, reuse ${esc(p.reused)}, buy ${esc(p.to_buy)}</div>`).join('')}</td><td><button data-proposal="${index}">Open connection</button>${gapsMarkup(v.gaps || [])}<details><summary>All checks and qualification evidence</summary>${v.checks.map(check => `<p>${badge(check.state)} ${esc(check.message)} ${sourceLink(check.source_url, 'Source ↗')}</p>`).join('')}${Object.entries(v.qualification).map(([side, q]) => q.records.map(record => `<p>${esc(side.toUpperCase())}: ${esc(record.outcome)} · ${evidenceMarkup(record.evidence)}</p>`).join('')).join('')}</details></td></tr>`;
    }).join('')}</tbody></table></div>` : '<div class="empty">No matching proposal. Adjust requirements or inspect the hardware evidence.</div>');
    $('wizardResults').querySelectorAll('[data-proposal]').forEach(button => button.addEventListener('click', () => openProposal(Number(button.dataset.proposal))));
  }
  async function runWizard() {
    let request;
    try { request = recommendationRequest(); } catch (error) { invalidateWizard(); $('wizardStatus').textContent = error.message; return; }
    const ticket = wizardGate.start(wizardKey());
    state.wizardResult = null; updateExport(); $('recommend').disabled = true;
    $('wizardResults').replaceChildren(); $('wizardStatus').textContent = 'Checking cable and optical combinations…';
    try {
      const result = await jsonRequest('/api/recommendations', ticket, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(request) });
      if (!wizardGate.current(ticket, wizardKey())) return;
      if (result.revision !== state.meta.revision) throw new Error('Catalog changed. Refresh and search again.');
      state.wizardResult = result; renderRecommendations(result);
    } catch (error) {
      if (ticket.sequence !== wizardGate.sequence) return;
      if (error.status === 409) { await loadCatalog(); return; }
      $('wizardStatus').textContent = error.message;
      if (!error.status || error.status >= 500) offline(error);
    } finally { if (ticket.sequence === wizardGate.sequence) $('recommend').disabled = false; updateExport(); save(); }
  }
  function openProposal(index) {
    const request = state.wizardResult?.candidates[index]?.connection;
    if (!request) return;
    const wanted = readConfig();
    for (const side of ['a', 'b']) {
      for (const [field, key] of Object.entries({ Device: 'device_id', Group: 'port_group_id', Mode: 'mode_id', Profile: 'hardware_profile_id', Product: 'product_id', End: 'endpoint_id', Pn: 'part_number' })) wanted[side + field] = request[side][key] || '';
      for (const [suffix, field] of Object.entries(runtimeFields)) wanted[side + suffix] = request[side].runtime[field] || '';
    }
    fillLink(wanted); plainFields.forEach(id => assign(id, wanted[id]));
    assign('linkFabric', request.fabric); assign('linkLength', request.length_m == null ? '' : request.length_m);
    assign('fiberPn', request.fiber_part_number || '');
    if (request.fiber) { assign('fiberType', request.fiber.fiber_type); assign('connectorA', request.fiber.connector_a); assign('connectorB', request.fiber.connector_b); }
    $('pinout').checked = false;
    setView('link'); invalidateLink(); runLink();
  }
  $('inspectHardware').addEventListener('click', inspectHardware);
  $('recommend').addEventListener('click', runWizard);
  $('wizardTab').addEventListener('click', () => { setView('wizard'); save(); });
  for (const name of ['breakout', 'project']) $(name + 'Tab').addEventListener('click', () => { setView(name); save(); });
  window.addEventListener('topology-results-changed', updateExport);
  $('addConnectionToProject').addEventListener('click', () => {
    if (!state.linkResult) return;
    try {
      const request = state.linkResult.selection || connectionRequest();
      const id = window.ValidatorTopology.addConnection(request, { id: $('projectConnectionId').value.trim(),
        a: { instance_id: $('projectAInstance').value.trim(), port_number: Number($('projectAPort').value) },
        b: { instance_id: $('projectBInstance').value.trim(), port_number: Number($('projectBPort').value) } });
      $('addProjectMessage').textContent = `Added ${id}. Open Project / BOM to check shared ports and inventory.`;
      $('projectConnectionId').value = '';
    } catch (error) { $('addProjectMessage').textContent = error.message; }
  });
  for (const host of hosts) {
    const invalidate = host === 'port' ? () => refreshPort() : host.startsWith('w') ? invalidateWizard : () => { $('pinout').checked = false; invalidateLink(); };
    $(host + 'Profile').addEventListener('change', () => { const wanted = readConfig(); clearRuntime(host); fillHardware(host, wanted); invalidate(); });
    Object.keys(runtimeFields).forEach(field => $(host + field).addEventListener('input', invalidate));
  }
  for (const side of ['wa', 'wb']) {
    $(side + 'Device').addEventListener('change', () => { clearRuntime(side); fillHardware(side); invalidateWizard(); });
    $(side + 'Group').addEventListener('change', () => { fillModes(side + 'Mode', hostGroup(side)); invalidateWizard(); });
    $(side + 'Mode').addEventListener('change', invalidateWizard);
  }
  for (const id of [...wizardFields, 'includeUnknown']) $(id).addEventListener($(id).tagName === 'SELECT' || id === 'includeUnknown' ? 'change' : 'input', invalidateWizard);
  $('fiberPn').addEventListener('change', () => {
    const fiber = state.fibers.find(f => f.part_number === $('fiberPn').value);
    if (fiber) { assign('fiberType', fiber.fiber_type); assign('connectorA', fiber.connector_a); assign('connectorB', fiber.connector_b); assign('linkLength', fiber.length_m); }
    $('pinout').checked = false; invalidateLink();
  });
  $('kind').addEventListener('change', () => { clearRuntime('port'); fillDeviceOptions(); fillGroups(); refreshPort(null); });
  $('device').addEventListener('change', () => { clearRuntime('port'); fillGroups(); refreshPort(null); });
  $('group').addEventListener('change', () => { fillModes('mode', hostGroup('port')); refreshPort(null); });
  for (const id of ['mode', 'fabricFilter']) $(id).addEventListener('change', () => refreshPort());
  for (const id of ['search', 'outcomeFilter', 'lifecycleFilter', 'categoryFilter', 'typeFilter', 'mediumFilter', 'speedFilter', 'reachFilter']) $(id).addEventListener(id === 'search' || id === 'reachFilter' ? 'input' : 'change', () => { renderProducts(); save(); });
  $('partNumber').addEventListener('change', () => { renderSKU(); save(); });
  $('whyRejected').addEventListener('click', () => { $('outcomeFilter').value = 'all'; $('lifecycleFilter').value = 'all'; renderProducts(); $('search').focus(); save(); });
  for (const side of ['a', 'b']) {
    $(side + 'Device').addEventListener('change', () => { clearRuntime(side); $('pinout').checked = false; fillLinkGroups(side); invalidateLink(); });
    $(side + 'Group').addEventListener('change', () => { $('pinout').checked = false; fillModes(side + 'Mode', hostGroup(side)); invalidateLink(); });
    $(side + 'Product').addEventListener('change', () => {
      $('pinout').checked = false;
      fillLinkProduct(side);
      if (side === 'a' && productFor($('aProduct').value)?.category !== 'Transceiver') { $('bProduct').value = $('aProduct').value; fillLinkProduct('b'); }
      invalidateLink();
    });
    for (const field of ['Mode', 'End']) $(side + field).addEventListener('change', () => { $('pinout').checked = false; invalidateLink(); });
    $(side + 'Pn').addEventListener('change', () => {
      $('pinout').checked = false;
      if (side === 'a' && $('aProduct').value === $('bProduct').value) assign('bPn', $('aPn').value);
      const sku = productFor($(side + 'Product').value)?.skus.find(s => s.part_number === $(side + 'Pn').value);
      if (sku?.length_m != null) $('linkLength').value = String(sku.length_m);
      invalidateLink();
    });
  }
  for (const id of ['linkFabric', 'linkLength', 'fiberType', 'connectorA', 'connectorB', 'pinout']) $(id).addEventListener(id === 'linkLength' ? 'input' : 'change', () => {
    if (['fiberType', 'connectorA', 'connectorB'].includes(id)) { $('pinout').checked = false; $('fiberPn').value = ''; }
    invalidateLink();
  });
  $('portTab').addEventListener('click', () => { setView('port'); save(); });
  $('linkTab').addEventListener('click', () => { setView('link'); save(); });
  $('validateLink').addEventListener('click', runLink);
  $('retry').addEventListener('click', () => loadCatalog());
  $('share').addEventListener('click', async () => {
    const url = configurationURL(readConfig(), state.meta?.revision, location.href);
    history.replaceState(null, '', url);
    try { await navigator.clipboard.writeText(url); $('actionMessage').textContent = 'Configuration link copied. It includes the catalog revision.'; }
    catch { $('actionMessage').textContent = 'Configuration saved in the address bar. Copy the page URL to share it.'; }
  });
  $('export').addEventListener('click', () => {
    if ($('export').disabled) return;
    const blob = new Blob([JSON.stringify(exportedReport(), null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob), anchor = document.createElement('a');
    anchor.href = url; anchor.download = `compatibility-${state.meta.revision}.json`;
    anchor.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  window.addEventListener('pagehide', () => { clearTimeout(pollTimer); portGate.cancel(); catalogGate.cancel(); linkGate.cancel(); hardwareGate.cancel(); wizardGate.cancel(); });
  loadCatalog(true).finally(() => { pollTimer = setTimeout(pollMeta, 5000); });
})();
