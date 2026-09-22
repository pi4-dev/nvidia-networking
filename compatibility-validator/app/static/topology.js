/* Complete fanouts and project drafts. All remote results are revision/selection bound. */
(() => {
  'use strict';
  const { RequestGate, esc, sourceLink, statusClass } = ValidatorCore;
  const $ = id => document.getElementById(id);
  const clone = value => JSON.parse(JSON.stringify(value));
  const runtimeKeys = ['sku', 'opn', 'adapter_variant', 'psid', 'firmware', 'os_name', 'os_version'];
  const gates = { breakout: new RequestGate(), project: new RequestGate(), transfer: new RequestGate() };
  let catalog = null, breakout = null, breakoutReport = null, projectReport = null, inventoryError = '';
  let pendingProjectJSON = false, pendingBreakoutJSON = false;
  let project = { format: 'nvidia-connection-project-v1', name: 'Untitled project', connections: [], breakouts: [], owned_parts: [] };
  const badge = status => `<span class="pill ${statusClass(status)}">${esc(status)}</span>`;
  const changed = () => window.dispatchEvent(new Event('topology-results-changed'));
  const product = id => catalog?.products.find(p => p.id === id);
  const emptyRuntime = () => Object.fromEntries(runtimeKeys.map(k => [k, null]));

  function restore(key) { try { return JSON.parse(localStorage.getItem(key)); } catch { return null; } }
  function persist() {
    try {
      if (breakout) localStorage.setItem('nvidia-breakout-v1', JSON.stringify(breakout));
      localStorage.setItem('nvidia-project-v1', JSON.stringify(project));
    } catch { /* Export remains available if browser storage is full or disabled. */ }
  }
  function notice(id, text) { $(id).textContent = text; $(id).classList.toggle('hidden', !text); }
  function download(value, name, type = 'application/json') {
    const blob = new Blob([type === 'application/json' ? JSON.stringify(value, null, 2) : value], { type });
    const url = URL.createObjectURL(blob), a = document.createElement('a');
    a.href = url; a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function options(rows, value, blank = null) {
    if (blank !== null) rows = [['', blank], ...rows];
    if (value && !rows.some(([id]) => id === value)) rows = [[value, 'Unavailable: ' + value], ...rows];
    return rows.map(([id, label]) => `<option value="${esc(id)}"${id === (value || '') ? ' selected' : ''}>${esc(label)}</option>`).join('');
  }
  function effectiveGroup(host) {
    const base = catalog?.devices.find(d => d.id === host.device_id)?.port_groups.find(g => g.id === host.port_group_id);
    const overlay = catalog?.hardware_profiles?.find(p => p.id === host.hardware_profile_id && p.device_id === host.device_id)?.ports.find(p => p.port_group_id === host.port_group_id);
    if (!base || !overlay) return base;
    return { ...base, ...Object.fromEntries(['module_speed_gbps', 'count', 'fabrics', 'modes'].filter(k => Array.isArray(overlay[k]) ? overlay[k].length : overlay[k]).map(k => [k, overlay[k]])) };
  }
  function hostDefault(instance, head = false) {
    const wanted = head ? 'profile:MQM9700-NS2F' : 'supernic:ConnectX-8 SuperNIC';
    const device = catalog.devices.find(d => d.id === wanted) || catalog.devices[0];
    const profile = head ? null : catalog.hardware_profiles?.find(p => p.id === '900-9X81E-00EX-ST0' && p.device_id === device?.id);
    const groupId = profile?.ports[0].port_group_id || device?.port_groups[0]?.id || '';
    const cable = catalog.products.find(p => p.id === 'Copper|MCP7Y00-Nxxx|finned head') || catalog.products.find(p => p.endpoints?.some(e => e.role === 'head'));
    const host = { instance_id: instance, port_number: 1, device_id: device?.id || '', port_group_id: groupId,
      hardware_profile_id: profile?.id || null, runtime: emptyRuntime(), product_id: cable?.id || '',
      part_number: cable?.skus.find(s => s.part_number === 'MCP7Y00-N003')?.part_number || cable?.skus[0]?.part_number || null,
      endpoint_id: head ? 'A' : 'B', mode_id: null };
    const modes = effectiveGroup(host)?.modes || [];
    host.mode_id = modes.find(m => m.id === (head ? '2x400' : '1x400-ndr'))?.id || modes[0]?.id || '';
    return host;
  }
  function example() {
    return { topology: 'cable', head: hostDefault('switch-01', true),
      branches: [1, 2].map(i => ({ id: 'branch-' + i, termination: i, head_links: [i],
        head_optical_port: 1, head_optical_lanes: [], branch_optical_lanes: [], interop_evidence: null,
        selection: hostDefault('cx8-' + i) })), fabric: 'IB', length_m: 3,
      mapping_verified: false, optical_fanout: null, revision: catalog.meta.revision };
  }
  function invalidate(kind, rewriteDocument = true) {
    gates[kind].cancel(); gates.transfer.cancel();
    if (kind === 'breakout') {
      breakoutReport = null; $('breakoutResult').replaceChildren(); $('breakoutStatus').textContent = 'Definition changed. Validate all branches.';
      $('validateBreakout').disabled = !catalog; $('addBreakoutToProject').disabled = true;
      if (breakout && rewriteDocument) { pendingBreakoutJSON = false; $('breakoutDocument').value = JSON.stringify(breakout, null, 2); }
    } else {
      projectReport = null; $('projectReport').replaceChildren(); $('projectStatus').textContent = 'Project changed. Validate again.';
      $('validateProject').disabled = !catalog; $('downloadBom').disabled = true;
      if (rewriteDocument) { pendingProjectJSON = false; $('projectDocument').value = JSON.stringify(project, null, 2); }
    }
    persist(); changed();
  }
  function control(hostKey, field, label, value, entries = null, type = 'text') {
    const id = `top-${hostKey}-${field.replaceAll('.', '-')}`;
    const attributes = `id="${id}" data-host="${hostKey}" data-field="${field}"`;
    return `<div><label for="${id}">${label}</label>${entries ? `<select ${attributes}>${options(entries, value)}</select>` : `<input ${attributes} type="${type}" value="${esc(value ?? '')}"${type === 'number' ? ' min="1" max="1024" step="1"' : ' maxlength="128"'}>`}</div>`;
  }
  function hostMarkup(key, host, heading) {
    const device = catalog.devices.find(d => d.id === host.device_id);
    const profiles = (catalog.hardware_profiles || []).filter(p => p.device_id === host.device_id);
    const profile = profiles.find(p => p.id === host.hardware_profile_id);
    const groups = (device?.port_groups || []).filter(g => !profile || profile.ports.some(p => p.port_group_id === g.id));
    const group = effectiveGroup(host);
    const cable = breakout.topology === 'cable';
    const products = catalog.products.filter(p => cable ? p.endpoints?.some(e => e.role === 'head') : p.category === 'Transceiver');
    const item = product(host.product_id);
    return `<fieldset class="topology-host"><legend>${esc(heading)}</legend><div class="grid4">${control(key, 'instance_id', 'Physical device instance', host.instance_id)}${control(key, 'port_number', 'Physical cage ordinal', host.port_number, null, 'number')}${control(key, 'device_id', 'Device model', host.device_id, catalog.devices.map(d => [d.id, d.model]))}${control(key, 'hardware_profile_id', 'Exact board / OPN', host.hardware_profile_id, [['', 'Generic board'], ...profiles.map(p => [p.id, p.label])])}${control(key, 'port_group_id', 'Physical port group', host.port_group_id, groups.map(g => [g.id, g.label]))}${control(key, 'mode_id', 'Explicit operating mode', host.mode_id, (group?.modes || []).map(m => [m.id, `${m.id} · ${m.links} × ${m.speed_gbps}G`]))}${!cable || key === 'head' ? control(key, 'product_id', cable ? 'Breakout assembly' : 'Optical module', host.product_id, products.map(p => [p.id, `${p.model} ${p.variant || ''} [${p.status}]`])) + control(key, 'part_number', 'Ordering part number', host.part_number, [['', 'PN unknown'], ...(item?.skus || []).map(s => [s.part_number, s.part_number + (s.length_m ? ` · ${s.length_m}m` : '')])]) : `<div class="small">Same assembly as head: ${esc(breakout.head.part_number || 'PN unknown')}</div>`}</div><details><summary>Observed hardware and software</summary><div class="grid4">${runtimeKeys.map(k => control(key, 'runtime.' + k, k.replaceAll('_', ' '), host.runtime?.[k])).join('')}</div></details></fieldset>`;
  }
  function listInput(index, field, label, values) {
    const id = `branch-${index}-${field}`;
    return `<div><label for="${id}">${label}</label><input id="${id}" data-branch="${index}" data-field="${field}" value="${esc(Array.isArray(values) ? values.join(',') : values ?? '')}" maxlength="128"></div>`;
  }
  function evidenceMarkup(prefix, value, scopeLabel) {
    return `<details><summary>${scopeLabel}</summary><div class="grid4"><div><label for="${prefix}-kind">Evidence type</label><select id="${prefix}-kind" data-evidence="${prefix}" data-field="kind">${options([['manufacturer', 'Manufacturer documentation'], ['lab', 'Internal lab report']], value?.kind || 'manufacturer')}</select></div>${['source_url', 'verified_on', 'scope'].map(field => `<div><label for="${prefix}-${field}">${esc(field.replaceAll('_', ' '))}</label><input id="${prefix}-${field}" data-evidence="${prefix}" data-field="${field}" type="${field === 'verified_on' ? 'date' : 'text'}" maxlength="4096" value="${esc(value?.[field] || '')}"></div>`).join('')}</div></details>`;
  }
  function renderBreakout() {
    if (!catalog || !breakout) return;
    $('breakoutType').value = breakout.topology; $('breakoutFabric').value = breakout.fabric;
    $('breakoutLength').value = breakout.length_m ?? ''; $('breakoutMapping').checked = !!breakout.mapping_verified;
    const optical = breakout.topology === 'optical';
    $('breakoutBuilder').innerHTML = hostMarkup('head', breakout.head, 'Shared head') + breakout.branches.map((b, i) => `<section class="branch-card"><div class="actionbar"><strong>${esc(b.id)}</strong><button data-remove-branch="${i}">Remove branch</button></div>${hostMarkup('b' + i, b.selection, 'Remote port')}<div class="grid4">${listInput(i, 'termination', 'Physical branch termination number', b.termination)}${listInput(i, 'head_links', 'Logical head link numbers (comma-separated)', b.head_links)}${optical ? listInput(i, 'head_optical_port', 'Head optical connector number', b.head_optical_port) + listInput(i, 'head_optical_lanes', 'Head optical Tx/Rx lane pairs', b.head_optical_lanes) + listInput(i, 'branch_optical_lanes', 'Remote optical Tx/Rx lane pairs', b.branch_optical_lanes) : ''}</div>${optical ? evidenceMarkup('interop-' + i, b.interop_evidence, 'Per-lane optical interoperability evidence') : ''}</section>`).join('');
    $('addBreakoutBranch').disabled = breakout.branches.length >= 16;
    $('opticalFanoutForm').classList.toggle('hidden', !optical);
    if (optical) {
      const f = breakout.optical_fanout;
      $('opticalFanoutForm').innerHTML = `<fieldset><legend>Complete optical fanout harness</legend><p class="small">Describe one complete harness assembly. Lane numbers identify Tx/Rx pairs, not individual MPO pin positions. Supplied evidence stays with this project.</p><div class="grid4">${[['part_number', 'Harness PN', f?.part_number], ['branch_count', 'Physical branch count', f?.branch_count], ['head_ports', 'Head optical connector count', f?.head_ports], ['connector_a', 'Head connector / polish', f?.fiber?.connector_a], ['connector_b', 'Branch connector / polish', f?.fiber?.connector_b]].map(([field, label, value]) => `<div><label for="fanout-${field}">${label}</label><input id="fanout-${field}" data-fanout="${field}" maxlength="128" value="${esc(value ?? '')}"></div>`).join('')}<div><label for="fanout-grade">Fiber grade</label><select id="fanout-grade" data-fanout="fiber_type">${options(['OS2', 'SM-unspecified', 'OM3', 'OM4', 'OM5'].map(s => [s, s]), f?.fiber?.fiber_type || 'SM-unspecified')}</select></div></div>${evidenceMarkup('harness', f?.evidence, 'Harness ordering / length / pinout evidence')}<label class="check-label"><input id="fanout-pinout" data-fanout="pinout_verified" type="checkbox"${f?.fiber?.pinout_verified ? ' checked' : ''}>I verified gender, polarity and full Tx/Rx mapping.</label></fieldset>`;
    }
    if (!pendingBreakoutJSON) $('breakoutDocument').value = JSON.stringify(breakout, null, 2);
  }
  function ensureFanout() {
    breakout.optical_fanout ||= { part_number: null, branch_count: breakout.branches.length, head_ports: 1,
      fiber: { medium: 'SM', fiber_type: 'SM-unspecified', connector_a: 'MPO-12/APC', connector_b: 'LC duplex', pinout_verified: false }, evidence: null };
    return breakout.optical_fanout;
  }
  function clearMapping() {
    breakout.mapping_verified = false; $('breakoutMapping').checked = false;
    if (breakout.optical_fanout?.fiber) breakout.optical_fanout.fiber.pinout_verified = false;
    if ($('fanout-pinout')) $('fanout-pinout').checked = false;
  }
  function syncCable() {
    if (breakout.topology !== 'cable') return;
    const item = product(breakout.head.product_id);
    breakout.head.endpoint_id = item?.endpoints.find(e => e.role === 'head')?.id || null;
    for (const branch of breakout.branches) {
      Object.assign(branch.selection, { product_id: breakout.head.product_id, part_number: breakout.head.part_number,
        endpoint_id: item?.endpoints.find(e => e.role === 'branch')?.id || null });
    }
  }
  function adjustHost(host, field) {
    if (field === 'device_id') { host.hardware_profile_id = null; host.port_group_id = null; host.runtime = emptyRuntime(); }
    if (['device_id', 'hardware_profile_id'].includes(field)) {
      const device = catalog.devices.find(d => d.id === host.device_id);
      const profile = catalog.hardware_profiles?.find(p => p.id === host.hardware_profile_id);
      host.port_group_id = profile?.ports[0]?.port_group_id || device?.port_groups[0]?.id || '';
    }
    if (['device_id', 'hardware_profile_id', 'port_group_id'].includes(field)) host.mode_id = effectiveGroup(host)?.modes[0]?.id || '';
    if (field === 'product_id') { host.part_number = product(host.product_id)?.skus[0]?.part_number || null; host.endpoint_id = product(host.product_id)?.endpoints[0]?.id || null; }
  }
  function editBuilder(event) {
    const target = event.target, d = target.dataset;
    if (target.tagName === 'SELECT' && event.type !== 'change' || target.tagName !== 'SELECT' && event.type !== 'input') return;
    if (d.host) {
      const host = d.host === 'head' ? breakout.head : breakout.branches[Number(d.host.slice(1))].selection;
      if (d.field.startsWith('runtime.')) { host.runtime ||= {}; host.runtime[d.field.slice(8)] = target.value.trim() || null; }
      else host[d.field] = d.field === 'port_number' ? Number(target.value) : target.value || null;
      if (target.tagName === 'SELECT') adjustHost(host, d.field);
      if (d.host === 'head' && d.field === 'part_number') {
        const sku = product(host.product_id)?.skus.find(s => s.part_number === host.part_number);
        if (sku?.length_m != null) breakout.length_m = sku.length_m;
      }
      syncCable();
    } else if (d.branch !== undefined) {
      const branch = breakout.branches[Number(d.branch)];
      branch[d.field] = ['termination', 'head_optical_port'].includes(d.field) ? Number(target.value) : target.value.trim() ? target.value.split(',').map(v => Number(v.trim())) : [];
    } else if (d.evidence) {
      const parent = d.evidence === 'harness' ? ensureFanout() : breakout.branches[Number(d.evidence.slice(8))];
      const field = d.evidence === 'harness' ? 'evidence' : 'interop_evidence';
      parent[field] ||= { kind: 'manufacturer', source_url: '', verified_on: '', scope: '' };
      parent[field][d.field] = target.value;
    } else if (d.fanout) {
      const fanout = ensureFanout(), value = target.type === 'checkbox' ? target.checked : target.value;
      if (['connector_a', 'connector_b', 'fiber_type', 'pinout_verified'].includes(d.fanout)) {
        fanout.fiber[d.fanout] = value;
        fanout.fiber.medium = ['OS2', 'SM-unspecified'].includes(fanout.fiber.fiber_type) ? 'SM' : 'MM';
      } else fanout[d.fanout] = ['head_ports', 'branch_count'].includes(d.fanout) ? Number(value) : value || null;
    } else return;
    if (d.fanout !== 'pinout_verified') clearMapping();
    invalidate('breakout');
    if (d.host && target.tagName === 'SELECT') renderBreakout();
  }
  async function api(path, ticket, payload, asText = false) {
    let timedOut = false;
    const timer = setTimeout(() => { timedOut = true; ticket.controller.abort(); }, 30000);
    try {
      const response = await fetch(path, { method: payload === undefined ? 'GET' : 'POST', cache: 'no-store', signal: ticket.controller.signal,
        headers: { 'Content-Type': 'application/json' }, ...(payload === undefined ? {} : { body: JSON.stringify(payload) }) });
      if (response.ok && asText) return await response.text();
      const data = await response.json();
      if (!response.ok) {
        const detail = Array.isArray(data.detail) ? data.detail.slice(0, 5).map(e => `${e.loc.join('.')}: ${e.msg}`).join('; ') : data.detail;
        const error = new Error(detail || 'Request failed'); error.status = response.status; throw error;
      }
      return data;
    } catch (error) { if (timedOut) throw new Error('Request timed out. Try a smaller project.'); throw error; }
    finally { clearTimeout(timer); }
  }
  function checksMarkup(checks) {
    return `<div class="checks"><table><thead><tr><th>Check</th><th>Evidence / requirement</th></tr></thead><tbody>${checks.map(c => `<tr><td>${badge(c.state)}<code>${esc(c.code)}</code></td><td>${esc(c.message)} ${sourceLink(c.source_url, 'Source ↗')}</td></tr>`).join('')}</tbody></table></div>`;
  }
  function gapsMarkup(gaps) { return `<details><summary>${gaps.length} missing facts / next steps</summary><ul>${gaps.map(g => `<li>${esc(g.message)}<div class="small">${esc(g.action)}</div></li>`).join('')}</ul></details>`; }
  function breakoutKey() { return JSON.stringify([catalog?.meta.revision, breakout]); }
  async function runBreakout() {
    if (!catalog || !breakout) return;
    if (pendingBreakoutJSON) { $('breakoutStatus').textContent = 'Load the edited JSON definition before validating.'; return; }
    const ticket = gates.breakout.start(breakoutKey()), request = clone(breakout);
    request.revision = catalog.meta.revision;
    breakoutReport = null; changed(); $('validateBreakout').disabled = true; $('addBreakoutToProject').disabled = true;
    $('breakoutResult').replaceChildren(); $('breakoutStatus').textContent = 'Validating every branch and the shared head…';
    try {
      const result = await api('/api/breakout', ticket, request);
      if (!gates.breakout.current(ticket, breakoutKey())) return;
      if (result.revision !== catalog.meta.revision) throw new Error('Catalog changed. Refresh before validating again.');
      breakoutReport = result;
      $('breakoutStatus').textContent = `${result.status} · ${result.assigned_branches} / ${result.expected_branches ?? '?'} branches · common FEC: ${result.common_fec.join(', ') || 'unknown'}`;
      $('breakoutResult').innerHTML = `<div class="tablewrap"><table><thead><tr><th>Branch / physical device</th><th>Head link → remote mode</th><th>Decision</th></tr></thead><tbody>${result.branches.map(b => `<tr><td>${esc(b.id)} · termination ${esc(b.termination)}<div>${esc(b.selection.instance_id)} / ${esc(b.selection.port_group_id)} / ${esc(b.selection.port_number)}</div></td><td>${esc(b.head_links.join(', '))} → ${esc(b.selection.mode_id)}</td><td>${badge(b.validation.status)}<details><summary>Branch checks</summary>${checksMarkup(b.validation.checks)}</details></td></tr>`).join('')}</tbody></table></div><details open><summary>Whole fanout checks</summary>${checksMarkup(result.checks.filter(c => /^(breakout\.|ports\.|optical\.)/.test(c.code)))}</details>${gapsMarkup(result.gaps)}`;
      $('addBreakoutToProject').disabled = false;
    } catch (error) { if (ticket.sequence === gates.breakout.sequence) $('breakoutStatus').textContent = error.message; }
    finally { if (ticket.sequence === gates.breakout.sequence) $('validateBreakout').disabled = false; changed(); }
  }
  function assertProjectShape(value) {
    if (!value || typeof value !== 'object' || Array.isArray(value) || !Array.isArray(value.connections) || !Array.isArray(value.breakouts) || !Array.isArray(value.owned_parts)) throw new Error('Project JSON requires connections, breakouts and owned_parts arrays.');
    if (value.connections.length > 200 || value.breakouts.length > 64 || value.owned_parts.length > 512) throw new Error('Project exceeds the supported entry/inventory limits.');
    if (!value.connections.every(c => c && typeof c === 'object' && c.a && c.b) || !value.owned_parts.every(p => p && typeof p === 'object')) throw new Error('Every connection needs both endpoint selections; inventory entries must be objects.');
    value.breakouts.forEach(assertBreakoutShape);
  }
  function assertBreakoutShape(value) {
    if (!value || !value.head || typeof value.head !== 'object' || !Array.isArray(value.branches) || value.branches.length > 16 ||
      !value.branches.every(b => b && b.selection && typeof b.selection === 'object') ||
      value.optical_fanout && !value.optical_fanout.fiber) throw new Error('Breakout JSON needs a head, up to 16 branch selections, and fiber properties for an optical harness.');
  }
  function staleProject(value) {
    return value.revision !== catalog.meta.revision || [...value.connections, ...value.breakouts].some(e => e.revision && e.revision !== catalog.meta.revision);
  }
  function resetVerification(value) {
    value.revision = catalog.meta.revision;
    for (const connection of value.connections || []) {
      connection.revision = catalog.meta.revision;
      if (connection.fiber) connection.fiber.pinout_verified = false;
    }
    for (const b of value.breakouts || []) {
      b.revision = catalog.meta.revision; b.mapping_verified = false;
      if (b.optical_fanout?.fiber) b.optical_fanout.fiber.pinout_verified = false;
    }
  }
  function applyProject(value, imported = false) {
    const raw = value.project || value.result?.project || value;
    assertProjectShape(raw);
    project = clone(raw); inventoryError = '';
    const stale = staleProject(project);
    if (stale) { resetVerification(project); notice('projectNotice', 'Imported catalog revision differs. Saved checks were discarded and all physical mapping confirmations were cleared. Revalidate against the current catalog.'); }
    else if (imported) notice('projectNotice', 'Project imported as a draft. Validate it against the current catalog before using its BOM.');
    invalidate('project'); renderProject();
  }
  function renderProject() {
    $('projectName').value = project.name || 'Untitled project';
    if (!inventoryError) $('projectInventory').value = project.owned_parts.map(p => `${p.part_number},${p.quantity}`).join('\n');
    const entries = [...project.connections.map(e => ({ ...e, type: 'connection' })), ...project.breakouts.map(e => ({ ...e, type: 'breakout' }))];
    $('projectRows').innerHTML = entries.length ? `<table><thead><tr><th>ID / type</th><th>Physical endpoints</th><th>Remove</th></tr></thead><tbody>${entries.map(e => `<tr><td>${esc(e.id)}<div class="small">${esc(e.type)}</div></td><td>${esc(e.type === 'connection' ? `${e.a?.instance_id} ${e.a?.port_group_id}/${e.a?.port_number} ↔ ${e.b?.instance_id} ${e.b?.port_group_id}/${e.b?.port_number}` : `${e.head?.instance_id} ${e.head?.port_group_id}/${e.head?.port_number} → ${e.branches?.length ?? '?'} branches`)}</td><td><button data-remove-entry="${esc(e.id)}" data-type="${e.type}">Remove</button></td></tr>`).join('')}</tbody></table>` : '<div class="empty">No connections yet. Add an A–B selection or a complete breakout, or import JSON/CSV.</div>';
    if (!pendingProjectJSON) $('projectDocument').value = JSON.stringify(project, null, 2);
  }
  function nextId(prefix) {
    const used = new Set([...project.connections, ...project.breakouts].map(e => e.id));
    let n = 1; while (used.has(prefix + n)) n++;
    return prefix + n;
  }
  function verifyId(id) {
    if (!/^[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}$/.test(id)) throw new Error('IDs use 1–64 letters, digits, dot, underscore, colon or hyphen.');
  }
  function addEntry(type, value, id) {
    if (pendingProjectJSON) throw new Error('Apply the pending project JSON edits before adding another connection.');
    verifyId(id);
    if ([...project.connections, ...project.breakouts].some(e => e.id === id)) throw new Error('Project entry ID already exists. Choose a unique ID.');
    if (project[type].length >= (type === 'connections' ? 200 : 64)) throw new Error('Project entry limit reached.');
    project[type].push({ ...clone(value), id, revision: catalog.meta.revision });
    project.revision = catalog.meta.revision; invalidate('project'); renderProject(); return id;
  }
  function projectKey() { return JSON.stringify([catalog?.meta.revision, project, inventoryError]); }
  function projectRequest() {
    if (pendingProjectJSON) throw new Error('Apply the pending project JSON edits before validating or exporting.');
    if (inventoryError) throw new Error(inventoryError);
    const value = clone(project); value.revision = catalog.meta.revision;
    for (const entry of [...value.connections, ...value.breakouts]) entry.revision = catalog.meta.revision;
    return value;
  }
  function renderProjectReport(result) {
    const s = result.summary, bom = result.bom;
    $('projectStatus').textContent = `${result.status} · ${s.device_instances} devices · ${s.physical_cages} cages · ${s.connections} links + ${s.breakouts} breakouts`;
    $('projectReport').innerHTML = `<p>${badge(result.status)} ${bom.provisional ? 'BOM is provisional: resolve failed checks and required unknowns.' : 'All project checks passed.'}</p><div class="tablewrap"><table><thead><tr><th>Connection</th><th>Result</th><th>Details</th></tr></thead><tbody>${result.results.map(r => `<tr><td>${esc(r.id)} · ${esc(r.type)}</td><td>${badge(r.status)}</td><td><details><summary>Checks / next steps</summary>${checksMarkup(r.validation.checks)}${gapsMarkup(r.validation.gaps || [])}</details></td></tr>`).join('')}</tbody></table></div><details open><summary>Shared ports and project consistency</summary>${checksMarkup(result.checks.filter(c => c.code.startsWith('ports.') || c.code.startsWith('project.')))}</details><h3>Bill of materials</h3><p>${esc(bom.total_components)} physical components · ${esc(bom.reused)} reused · ${esc(bom.to_buy)} to buy</p><div class="tablewrap"><table><thead><tr><th>Ordering PN / component</th><th>Required</th><th>Owned</th><th>Reuse</th><th>To buy</th><th>Used by</th></tr></thead><tbody>${bom.rows.map(row => `<tr><td><strong>${esc(row.part_number || 'PN unresolved')}</strong><div>${esc(row.model)} · ${esc(row.roles.join(', '))}</div>${row.verified_ordering ? '' : '<div class="warn">Ordering data unverified</div>'}${row.source_urls.map(url => sourceLink(url, 'Source ↗')).join(' ')}</td><td>${esc(row.required)}</td><td>${esc(row.owned)}</td><td>${esc(row.reused)}</td><td>${esc(row.to_buy)}</td><td>${esc(row.references.join(', '))}</td></tr>`).join('')}</tbody></table></div>${bom.unused_inventory.length ? `<p class="small">Unused inventory: ${esc(bom.unused_inventory.map(p => `${p.part_number} × ${p.quantity}`).join('; '))}</p>` : ''}${result.notes.map(n => `<p class="small">${esc(n)}</p>`).join('')}`;
  }
  async function runProject() {
    let request;
    try { request = projectRequest(); } catch (error) { $('projectStatus').textContent = error.message; return; }
    const ticket = gates.project.start(projectKey());
    projectReport = null; changed(); $('validateProject').disabled = true; $('downloadBom').disabled = true;
    $('projectReport').replaceChildren(); $('projectStatus').textContent = 'Checking connections, shared ports and project inventory…';
    try {
      const result = await api('/api/project', ticket, request);
      if (!gates.project.current(ticket, projectKey())) return;
      if (result.revision !== catalog.meta.revision) throw new Error('Catalog changed. Refresh and revalidate the project.');
      projectReport = result; renderProjectReport(result); $('downloadBom').disabled = false;
    } catch (error) { if (ticket.sequence === gates.project.sequence) $('projectStatus').textContent = error.message; }
    finally { if (ticket.sequence === gates.project.sequence) $('validateProject').disabled = false; changed(); }
  }
  async function exportCSV(path, filename, payload) {
    const ticket = gates.transfer.start(projectKey());
    try {
      const data = await api(path, ticket, payload, true);
      if (gates.transfer.current(ticket, projectKey())) download(data, filename, 'text/csv;charset=utf-8');
    } catch (error) { if (ticket.sequence === gates.transfer.sequence) $('projectStatus').textContent = error.message; }
  }
  function setCatalog(bundle) {
    const previous = catalog?.meta.revision;
    catalog = bundle;
    if (!breakout) {
      const saved = restore('nvidia-breakout-v1');
      try { assertBreakoutShape(saved); breakout = saved; } catch { breakout = example(); }
      const savedProject = restore('nvidia-project-v1');
      try { if (savedProject) { assertProjectShape(savedProject); project = savedProject; } } catch { /* Invalid saved draft is ignored. */ }
    }
    if (previous && previous !== bundle.meta.revision || breakout.revision && breakout.revision !== bundle.meta.revision) {
      clearMapping(); breakout.revision = bundle.meta.revision;
      notice('breakoutNotice', 'Catalog revision changed. Mapping confirmations and previous results were cleared. Review and validate again.');
    }
    if (previous && previous !== bundle.meta.revision || (project.connections.length || project.breakouts.length) && staleProject(project)) {
      resetVerification(project);
      notice('projectNotice', 'Catalog revision changed. All results and physical mapping confirmations were cleared. Review and validate the project again.');
    }
    project.revision = bundle.meta.revision;
    invalidate('breakout', !pendingBreakoutJSON); invalidate('project', !pendingProjectJSON); renderBreakout(); renderProject();
  }
  for (const container of ['breakoutBuilder', 'opticalFanoutForm']) {
    $(container).addEventListener('input', editBuilder); $(container).addEventListener('change', editBuilder);
  }
  $('breakoutBuilder').addEventListener('click', event => {
    if (event.target.dataset.removeBranch !== undefined) {
      breakout.branches.splice(Number(event.target.dataset.removeBranch), 1);
      clearMapping(); invalidate('breakout'); renderBreakout();
    }
  });
  $('addBreakoutBranch').addEventListener('click', () => {
    if (breakout.branches.length >= 16) return;
    let n = 1; while (breakout.branches.some(b => b.id === 'branch-' + n)) n++;
    breakout.branches.push({ id: 'branch-' + n, termination: n, head_links: [n], head_optical_port: 1,
      head_optical_lanes: [], branch_optical_lanes: [], interop_evidence: null, selection: hostDefault('remote-' + n) });
    syncCable(); clearMapping(); invalidate('breakout'); renderBreakout();
  });
  $('breakoutType').addEventListener('change', () => {
    breakout.topology = $('breakoutType').value;
    if (breakout.topology === 'optical') {
      ensureFanout();
      const item = catalog.products.find(p => p.category === 'Transceiver');
      for (const host of [breakout.head, ...breakout.branches.map(b => b.selection)]) { host.product_id = item?.id || ''; adjustHost(host, 'product_id'); }
    } else {
      breakout.optical_fanout = null;
      breakout.head.product_id = catalog.products.find(p => p.endpoints?.some(e => e.role === 'head'))?.id || '';
      adjustHost(breakout.head, 'product_id'); syncCable();
    }
    clearMapping(); invalidate('breakout'); renderBreakout();
  });
  $('breakoutFabric').addEventListener('change', () => { breakout.fabric = $('breakoutFabric').value; clearMapping(); invalidate('breakout'); });
  $('breakoutLength').addEventListener('input', () => { breakout.length_m = $('breakoutLength').value ? Number($('breakoutLength').value) : null; clearMapping(); invalidate('breakout'); });
  $('breakoutMapping').addEventListener('change', () => { breakout.mapping_verified = $('breakoutMapping').checked; invalidate('breakout'); });
  $('breakoutExample').addEventListener('click', () => { breakout = example(); invalidate('breakout'); renderBreakout(); });
  $('validateBreakout').addEventListener('click', runBreakout);
  $('downloadBreakout').addEventListener('click', () => {
    if (pendingBreakoutJSON) { $('breakoutStatus').textContent = 'Load the edited JSON definition before exporting.'; return; }
    if (breakout) download(breakout, 'breakout.json');
  });
  $('applyBreakoutJSON').addEventListener('click', () => {
    try {
      const value = JSON.parse($('breakoutDocument').value), raw = value.selection || value.result?.selection || value;
      assertBreakoutShape(raw);
      breakout = clone(raw);
      if (breakout.revision !== catalog.meta.revision) clearMapping();
      breakout.revision = catalog.meta.revision; invalidate('breakout'); renderBreakout();
    } catch (error) { $('breakoutStatus').textContent = error.message; }
  });
  $('addBreakoutToProject').addEventListener('click', () => {
    if (!breakoutReport) return;
    try { const id = addEntry('breakouts', breakoutReport.selection, $('breakoutEntryId').value.trim() || nextId('fanout-')); $('breakoutStatus').textContent = `Added ${id} to project.`; }
    catch (error) { $('breakoutStatus').textContent = error.message; }
  });
  $('projectName').addEventListener('input', () => { project.name = $('projectName').value; invalidate('project'); });
  $('projectInventory').addEventListener('input', () => {
    try {
      project.owned_parts = $('projectInventory').value.split(/\r?\n/).filter(v => v.trim()).map(line => {
        const parts = line.split(',').map(v => v.trim());
        if (parts.length !== 2 || !parts[0] || !/^[1-9]\d*$/.test(parts[1])) throw new Error('Inventory format: one PN,positive quantity per line.');
        return { part_number: parts[0], quantity: Number(parts[1]) };
      }); inventoryError = '';
    } catch (error) { inventoryError = error.message; }
    invalidate('project');
  });
  $('projectRows').addEventListener('click', event => {
    const d = event.target.dataset;
    if (d.removeEntry !== undefined) { const key = d.type === 'breakout' ? 'breakouts' : 'connections'; project[key] = project[key].filter(e => e.id !== d.removeEntry); invalidate('project'); renderProject(); }
  });
  $('applyProjectJSON').addEventListener('click', () => { try { applyProject(JSON.parse($('projectDocument').value), true); } catch (error) { $('projectStatus').textContent = error.message; } });
  $('projectDocument').addEventListener('input', () => { pendingProjectJSON = true; invalidate('project', false); $('projectStatus').textContent = 'JSON edits pending. Apply them before validating or exporting.'; });
  $('breakoutDocument').addEventListener('input', () => { pendingBreakoutJSON = true; invalidate('breakout', false); $('breakoutStatus').textContent = 'JSON edits pending. Load the definition before validating or exporting.'; });
  $('projectImport').addEventListener('change', async () => {
    const file = $('projectImport').files[0]; if (!file) return;
    if (file.size > 1024 * 1024) { $('projectStatus').textContent = 'Import exceeds 1 MiB.'; return; }
    const ticket = gates.transfer.start(projectKey());
    try {
      const text = await file.text();
      if (!gates.transfer.current(ticket, projectKey())) return;
      if (/\.csv$/i.test(file.name)) {
        const imported = await api('/api/project/import-csv', ticket, { name: file.name.slice(0, 128), csv: text, revision: catalog.meta.revision });
        if (!gates.transfer.current(ticket, projectKey())) return;
        if (imported.revision !== catalog.meta.revision) throw new Error('Catalog changed during import. Refresh and import again.');
        applyProject(imported.project, true);
      } else applyProject(JSON.parse(text.replace(/^\uFEFF/, '')), true);
    } catch (error) { if (ticket.sequence === gates.transfer.sequence) $('projectStatus').textContent = error.message; }
    finally { $('projectImport').value = ''; }
  });
  $('newProject').addEventListener('click', () => {
    // Keep a recoverable browser copy of the immediately preceding draft.
    try { localStorage.setItem('nvidia-project-previous-v1', JSON.stringify(project)); } catch { /* Optional storage. */ }
    project = { format: 'nvidia-connection-project-v1', name: 'Untitled project', connections: [], breakouts: [], owned_parts: [], revision: catalog?.meta.revision };
    inventoryError = ''; invalidate('project'); renderProject();
  });
  $('validateProject').addEventListener('click', runProject);
  $('downloadProjectJSON').addEventListener('click', () => { try { download(projectRequest(), 'connection-project.json'); } catch (error) { $('projectStatus').textContent = error.message; } });
  $('downloadProjectTemplate').addEventListener('click', () => exportCSV('/api/project/template.csv', 'project-template.csv'));
  $('downloadProjectCSV').addEventListener('click', () => { try { exportCSV('/api/project/connections.csv', 'project-connections.csv', projectRequest()); } catch (error) { $('projectStatus').textContent = error.message; } });
  $('downloadBom').addEventListener('click', () => { if (projectReport) exportCSV('/api/project/bom.csv', 'project-bom.csv', projectRequest()); });
  window.addEventListener('pagehide', () => Object.values(gates).forEach(g => g.cancel()));
  window.ValidatorTopology = {
    setCatalog,
    hasReport: view => !!(view === 'breakout' ? breakoutReport : projectReport),
    exportReport: view => ({ format: 'nvidia-topology-report-v1', exported_at: new Date().toISOString(), catalog: catalog.meta,
      scope: view === 'breakout' ? 'complete-breakout' : 'connection-project', result: view === 'breakout' ? breakoutReport : projectReport,
      ...(view === 'project' ? { project: clone(project) } : {}) }),
    addConnection: (request, positions) => {
      verifyId(positions.a.instance_id); verifyId(positions.b.instance_id);
      for (const p of [positions.a, positions.b]) if (!Number.isInteger(p.port_number) || p.port_number < 1 || p.port_number > 1024) throw new Error('Physical cage ordinals must be integers from 1 to 1024.');
      return addEntry('connections', { ...request, a: { ...request.a, ...positions.a }, b: { ...request.b, ...positions.b } }, positions.id || nextId('link-'));
    }
  };
})();
