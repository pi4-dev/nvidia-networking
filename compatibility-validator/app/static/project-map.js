/* Project topology: server-derived ownership, keyboard-accessible SVG and port inventory. */
(() => {
  'use strict';
  const { esc, RequestGate, statusClass } = ValidatorCore;
  const $ = id => document.getElementById(id), gate = new RequestGate();
  const pageSize = 40, portPageSize = 64;
  let context, report = null, page = 0, selected = null, portPage = {}, drawingWidth = 1160;
  const badge = status => `<span class="pill ${statusClass(status)}">${esc(status)}</span>`;
  const short = (value, limit = 32) => String(value ?? '').length > limit ? String(value).slice(0, limit - 1) + '…' : String(value ?? '');
  const modeText = segment => segment.mode ? `${segment.mode.id}: ${segment.mode.links} × ${segment.mode.speed_gbps}G` : `${segment.selected_mode || 'Auto'} — mode unresolved`;
  const checks = rows => `<ul class="map-checks">${rows.map(c => `<li><strong>${esc(c.state)}</strong> ${esc(c.message)}<span class="small"> ${esc(c.code)}</span></li>`).join('')}</ul>`;

  function invalidate() {
    gate.cancel(); report = null; selected = null; page = 0; portPage = {};
    $('mapCanvas').replaceChildren(); $('mapDetails').replaceChildren(); $('mapConnections').replaceChildren(); $('mapChecks').replaceChildren();
    $('mapStatus').textContent = 'Build the map from the current project to inspect connections and physical ports.';
    $('mapPageStatus').textContent = ''; $('buildProjectMap').disabled = false;
    $('mapPrevious').disabled = $('mapNext').disabled = true;
  }
  async function build() {
    let payload;
    try { payload = context.getProject(); } catch (error) { $('mapStatus').textContent = error.message; return; }
    invalidate();
    const ticket = gate.start(context.key());
    const timer = setTimeout(() => ticket.controller.abort(), 30000);
    $('buildProjectMap').disabled = true; $('mapStatus').textContent = 'Validating connections and resolving physical cage capacity…';
    try {
      const response = await fetch('/api/project/map', { method: 'POST', headers: { 'Content-Type': 'application/json' }, cache: 'no-store', signal: ticket.controller.signal, body: JSON.stringify(payload) });
      const value = await response.json();
      if (!gate.current(ticket, context.key())) return;
      if (!response.ok) throw new Error(Array.isArray(value.detail) ? value.detail.slice(0, 5).map(v => `${v.loc.join('.')}: ${v.msg}`).join('; ') : value.detail || 'Map request failed');
      if (value.revision !== payload.revision) throw new Error('Catalog changed. Refresh and build the map again.');
      report = value;
      const current = $('mapDeviceFilter').value;
      $('mapDeviceFilter').innerHTML = '<option value="">All devices</option>' + report.devices.map(d => `<option value="${esc(d.id)}">${esc(d.id)}${d.rack ? ' · ' + esc(d.rack) : ''}</option>`).join('');
      if (report.devices.some(d => d.id === current)) $('mapDeviceFilter').value = current;
      const s = report.summary;
      $('mapStatus').textContent = `${report.status} · ${s.devices} devices · ${s.assemblies} assemblies · ${s.occupied_cages} occupied cages · ${s.conflicting_cages} cage conflicts · catalog ${report.revision}`;
      $('mapChecks').innerHTML = `<details><summary>Project ownership checks</summary>${checks(report.checks)}</details>`;
      render();
    } catch (error) {
      if (ticket.sequence === gate.sequence) $('mapStatus').textContent = error.name === 'AbortError' ? 'Map request timed out. Try again.' : error.message;
    } finally { clearTimeout(timer); if (ticket.sequence === gate.sequence) $('buildProjectMap').disabled = false; }
  }
  function filteredAssemblies() {
    const device = $('mapDeviceFilter').value, fabric = $('mapFabric').value, status = $('mapOutcome').value, query = $('mapSearch').value.trim().toLowerCase();
    return report.assemblies.filter(a => {
      const attached = report.segments.filter(s => s.entry_id === a.id), ids = new Set(attached.map(s => s.instance_id));
      const devices = report.devices.filter(d => ids.has(d.id));
      return (!device || ids.has(device)) && (!fabric || a.fabric === fabric) && (!status || a.status === status) &&
        (!query || [a.id, a.cable_id, a.part_number, ...devices.flatMap(d => [d.id, d.model, d.rack]), ...attached.flatMap(s => [s.part_number, s.port_label])].join(' ').toLowerCase().includes(query));
    });
  }
  function render() {
    if (!report) return;
    const filtered = filteredAssemblies(), pages = Math.max(1, Math.ceil(filtered.length / pageSize));
    page = Math.min(page, pages - 1);
    const assemblies = filtered.slice(page * pageSize, (page + 1) * pageSize), ids = new Set(assemblies.map(a => a.id));
    const segments = report.segments.filter(s => ids.has(s.entry_id)), instances = new Set(segments.map(s => s.instance_id));
    const devices = report.devices.filter(d => instances.has(d.id));
    const leftIds = new Set(segments.filter(s => ['a', 'head'].includes(s.role)).map(s => s.instance_id));
    const left = devices.filter(d => leftIds.has(d.id)), right = devices.filter(d => !leftIds.has(d.id));
    const height = Math.max(340, (Math.max(left.length, right.length, assemblies.length) + 1) * 120);
    const positions = new Map(), assemblyPositions = new Map();
    const distribute = (items, x, width, target) => items.forEach((item, i) => target.set(item.id, { x, y: 30 + i * (height - 100) / Math.max(1, items.length), width }));
    distribute(left, 20, 250, positions); distribute(right, 890, 250, positions); distribute(assemblies, 450, 260, assemblyPositions);
    const isSelected = (kind, id) => selected?.kind === kind && selected.id === id;
    const linked = s => !selected || selected.kind === 'assembly' && selected.id === s.entry_id || selected.kind === 'device' && selected.id === s.instance_id;
    const paths = segments.map(s => {
      const d = positions.get(s.instance_id), a = assemblyPositions.get(s.entry_id), isLeft = d.x < a.x;
      const deviceEnds = segments.filter(v => v.instance_id === s.instance_id), assemblyEnds = segments.filter(v => v.entry_id === s.entry_id);
      const x1 = isLeft ? d.x + d.width : d.x, x2 = isLeft ? a.x : a.x + a.width;
      const y1 = d.y + 12 + 56 * (deviceEnds.indexOf(s) + 1) / (deviceEnds.length + 1), y2 = a.y + 10 + 64 * (assemblyEnds.indexOf(s) + 1) / (assemblyEnds.length + 1);
      const index = report.assemblies.findIndex(v => v.id === s.entry_id);
      const label = `${s.instance_id} / ${s.port_label || s.port_group_id + '/' + s.port_number} → ${s.entry_id} ${s.branch_id || s.role}; ${modeText(s)}; ${s.status}`;
      const middle = (x1 + x2) / 2;
      const branchLabel = s.role === 'branch';
      const labelX = branchLabel ? x1 + (isLeft ? 7 : -7) : x2 + (isLeft ? -7 : 7), labelY = branchLabel ? y1 - 9 : y2 - 7;
      const labelAnchor = branchLabel ? (isLeft ? 'start' : 'end') : (isLeft ? 'end' : 'start');
      return `<g class="map-segment ${linked(s) ? '' : 'map-dim'}" data-assembly="${index}" role="button" tabindex="0" aria-label="${esc(label)}"><title>${esc(label)}</title><path class="map-hit" d="M ${x1} ${y1} C ${middle} ${y1}, ${middle} ${y2}, ${x2} ${y2}"/><path class="map-line state-${s.ownership_conflict ? 'incompatible' : s.status}${s.role === 'head' ? ' map-head' : ''}" d="M ${x1} ${y1} C ${middle} ${y1}, ${middle} ${y2}, ${x2} ${y2}"/><text x="${labelX}" y="${labelY}" text-anchor="${labelAnchor}">${esc(branchLabel && deviceEnds.length > 2 ? '' : s.role === 'branch' ? 'BR ' + s.termination : s.role.toUpperCase())}</text></g>`;
    }).join('');
    const nodes = devices.map(d => {
      const p = positions.get(d.id), index = report.devices.indexOf(d);
      return `<g class="map-device${d.ownership_conflict ? ' map-conflict' : ''}${isSelected('device', d.id) ? ' map-selected' : ''}" data-device="${index}" role="button" tabindex="0" aria-label="${esc('Device ' + d.id + '; ' + d.occupied + ' occupied cages; ' + (d.free_count ?? 'unknown') + ' free')}"><title>${esc(d.id + ' · ' + d.model + (d.rack ? ' · ' + d.rack : ''))}</title><rect x="${p.x}" y="${p.y}" width="${p.width}" height="80" rx="9"/><text x="${p.x + 12}" y="${p.y + 23}" class="map-node-title">${esc(short(d.id))}</text><text x="${p.x + 12}" y="${p.y + 44}">${esc(short(d.model))}</text><text x="${p.x + 12}" y="${p.y + 65}">${esc(d.identity_conflict ? 'Conflicting identity' : `${d.occupied} occupied · ${d.free_count ?? '?'} free cages`)}</text></g>`;
    }).join('');
    const cables = assemblies.map(a => {
      const p = assemblyPositions.get(a.id), index = report.assemblies.indexOf(a);
      return `<g class="map-assembly state-${a.ownership_conflict ? 'incompatible' : a.status}${isSelected('assembly', a.id) ? ' map-selected' : ''}" data-assembly="${index}" role="button" tabindex="0" aria-label="${esc(a.cable_id + '; ' + a.type + '; ' + a.status)}"><title>${esc(a.id + ' · ' + (a.part_number || 'PN unknown'))}</title><rect x="${p.x}" y="${p.y}" width="${p.width}" height="86" rx="18"/><text x="${p.x + 12}" y="${p.y + 23}" class="map-node-title">${esc(short(a.cable_id))}</text><text x="${p.x + 12}" y="${p.y + 43}">${esc(short(a.part_number || 'PN unknown'))}</text><text x="${p.x + 12}" y="${p.y + 64}">${esc(a.ownership_conflict ? 'Port conflict · ' + a.fabric : a.type + ' · ' + a.fabric + ' · ' + a.status)}</text></g>`;
    }).join('');
    $('mapCanvas').innerHTML = assemblies.length ? `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${drawingWidth} ${height}" width="${drawingWidth}" height="${height}" role="group" aria-label="Interactive project connections">${paths}${nodes}${cables}</svg>` : '<p class="empty">No connections match these filters.</p>';
    zoom();
    $('mapPageStatus').textContent = `${filtered.length ? page * pageSize + 1 : 0}–${Math.min((page + 1) * pageSize, filtered.length)} of ${filtered.length} matching assemblies · page ${page + 1}/${pages} · device counts cover the entire project`;
    $('mapPrevious').disabled = page === 0; $('mapNext').disabled = page + 1 >= pages;
    $('mapConnections').innerHTML = assemblies.map(a => `<button type="button" data-assembly="${report.assemblies.indexOf(a)}">${esc(a.cable_id)} · ${esc(a.status)}</button>`).join('');
    renderDetails();
  }
  function zoom() {
    const svg = $('mapCanvas').querySelector('svg');
    if (svg) { const scale = Number($('mapZoom').value) / 100; svg.setAttribute('width', drawingWidth * scale); svg.setAttribute('height', svg.viewBox?.baseVal?.height ? svg.viewBox.baseVal.height * scale : Number(svg.getAttribute('viewBox').split(' ')[3]) * scale); }
    $('mapZoomValue').textContent = $('mapZoom').value + '%';
  }
  function renderDetails() {
    if (!selected) { $('mapDetails').innerHTML = '<p class="small">Select a device to inspect physical cages, or a cable/line to inspect the whole connection and its validation.</p>'; return; }
    if (selected.kind === 'assembly') {
      const a = report.assemblies.find(a => a.id === selected.id);
      if (!a) { selected = null; renderDetails(); return; }
      const segs = report.segments.filter(s => s.entry_id === a.id);
      $('mapDetails').innerHTML = `<h4>${esc(a.cable_id)}</h4><p>${badge(a.status)} ${esc(a.id)} · ${esc(a.type)} · ${esc(a.fabric)}</p>${a.ownership_conflict ? '<p class="bad">Port allocation conflict: review device cages and project ownership checks.</p>' : ''}<p>Cable/harness PN: <strong>${esc(a.part_number || 'unknown')}</strong> · ${a.length_m == null ? 'Length unknown' : esc(a.length_m) + ' m'}</p><p class="small">${a.type === 'breakout' ? 'One shared head cage; each branch is shown separately. Status applies to the complete assembly.' : 'Both physical ends are shown.'}</p><ul>${segs.map(s => `<li><button type="button" data-device="${report.devices.findIndex(d => d.id === s.instance_id)}">${esc(s.instance_id)}</button> ${esc(s.port_group_id)}/${esc(s.port_number)}${s.port_label ? ' · ' + esc(s.port_label) : ''}<div>${esc(s.branch_id || s.role)} · ${esc(modeText(s))}</div><div>Endpoint PN: ${esc(s.part_number || 'unknown')}${s.head_links.length ? ' · head links ' + esc(s.head_links.join(', ')) : ''}</div></li>`).join('')}</ul><details><summary>Branch paths and installation</summary>${a.rows.map(r => `<p>${esc(r.branch_id || 'A ↔ B')} · ${esc(r.source_label)} ↔ ${esc(r.destination_label)}<br>${esc(r.source.instance_id)} → ${esc(r.destination.instance_id)} · installed ${r.installed ? 'yes' : 'no'} · checked ${r.checked ? 'yes' : 'no'}${r.head_optical_lanes.length ? '<br>Optical pairs: ' + esc(r.head_optical_lanes.join(',')) + ' → ' + esc(r.branch_optical_lanes.join(',')) : ''}</p>`).join('')}</details><details open><summary>Validation checks</summary>${checks(a.checks)}</details>`;
      return;
    }
    const d = report.devices.find(d => d.id === selected.id);
    if (!d) { selected = null; renderDetails(); return; }
    $('mapDetails').innerHTML = `<h4>${esc(d.id)}</h4><p>${esc(d.model)}${d.hardware_profile_id ? ' · ' + esc(d.hardware_profile_id) : ''}</p><p>${esc(d.rack || 'Rack unspecified')}${d.rack_u ? ' / U' + esc(d.rack_u) : ''} · ${d.occupied} occupied · ${d.free_count ?? 'unknown'} free physical cages</p>${d.identity_conflict ? '<p class="bad">Conflicting device/profile declarations. Capacity cannot be resolved.</p>' : ''}<p class="small">Free cages are unallocated in this project. Logical interfaces inside an occupied cage do not add free physical ports.</p>${d.groups.map((g, gi) => {
      const pageKey = d.id + '/' + g.id, offset = Math.min(portPage[pageKey] || 0, Math.max(0, Math.ceil((g.count || 1) / portPageSize) - 1));
      const numbers = g.count === null ? g.ports.map(p => p.number) : Array.from({length:Math.min(portPageSize, Math.max(0, g.count - offset * portPageSize))}, (_, i) => i + 1 + offset * portPageSize);
      const extra = g.count === null ? [] : g.ports.filter(p => p.number > g.count).map(p => p.number);
      const ranges = g.free_ranges.map(([a,b]) => a === b ? a : `${a}–${b}`).join(', ');
      return `<section class="map-port-group"><h5>${esc(g.label)} · ${esc(g.connector_family || 'connector unknown')}</h5><p>${g.count ?? 'Unknown'} cages · ${g.occupied} occupied · ${g.free_count ?? 'unknown'} free</p>${g.count === null ? '<p class="warn">Capacity unknown: only declared cages are displayed.</p>' : `<p class="small">Free cage ordinals: ${esc(ranges || 'none')}</p>`}<div class="map-cages">${[...numbers, ...extra].map(n => { const p = g.ports.find(v => v.number === n); return `<button type="button" class="map-cage cage-${p?.state || 'free'}" data-port-group="${gi}" data-port="${n}" aria-label="${esc(g.id + ' cage ' + n + ', ' + (p?.state || 'free'))}">${n}<span>${esc(short(p?.label || p?.state || 'free', 16))}</span></button>`; }).join('')}</div>${g.count > portPageSize ? `<div class="actionbar"><button data-port-page="${gi}" data-offset="${offset - 1}"${offset === 0 ? ' disabled' : ''}>Previous cages</button><span>${offset * portPageSize + 1}–${Math.min(g.count, (offset + 1) * portPageSize)}</span><button data-port-page="${gi}" data-offset="${offset + 1}"${(offset + 1) * portPageSize >= g.count ? ' disabled' : ''}>Next cages</button></div>` : ''}</section>`;
    }).join('')}<div id="mapPortDetail" aria-live="polite"><p>Select a cage to inspect its allocation and logical interfaces.</p></div>`;
  }
  function selectPort(groupIndex, number) {
    const d = report.devices.find(d => d.id === selected.id), g = d.groups[groupIndex], port = g.ports.find(p => p.number === number);
    const segs = port ? report.segments.filter(s => port.segments.includes(s.id)) : [];
    $('mapPortDetail').innerHTML = `<h5>${esc(g.id)} / cage ${number}${port?.label ? ' · ' + esc(port.label) : ''}</h5><p>${esc(port?.state || 'free in this project')}</p>${port ? `<ul>${segs.map(s => `<li><button type="button" data-assembly="${report.assemblies.findIndex(a => a.id === s.entry_id)}">${esc(s.entry_id)} · ${esc(s.branch_id || s.role)}</button><div>${esc(modeText(s))}</div></li>`).join('')}</ul><h5>Logical interfaces within this physical cage</h5>${port.interfaces.length ? `<ul>${port.interfaces.map(i => `<li>Interface ${i.number} · ${i.speed_gbps}G · ${esc(i.state)}${i.references.length ? ' → ' + esc(i.references.join(', ')) : ''}</li>`).join('')}</ul>` : '<p class="warn">Logical interfaces unresolved: choose an explicit supported mode and resolve cage conflicts.</p>'}` : '<p>No cable is allocated here in this project; the physical port is not a live discovery result.</p>'}`;
  }
  function activate(event) {
    if (!report) return;
    const target = event.target.closest('[data-device],[data-assembly],[data-port],[data-port-page]');
    if (!target) return;
    if (event.type === 'keydown') { if (!['Enter', ' '].includes(event.key) || target.tagName.toLowerCase() === 'button') return; event.preventDefault(); }
    if (target.dataset.port !== undefined) { selectPort(Number(target.dataset.portGroup), Number(target.dataset.port)); return; }
    if (target.dataset.portPage !== undefined) {
      const d = report.devices.find(d => d.id === selected.id), g = d.groups[Number(target.dataset.portPage)];
      portPage[d.id + '/' + g.id] = Number(target.dataset.offset); renderDetails(); return;
    }
    const kind = target.dataset.device !== undefined ? 'device' : 'assembly';
    const item = kind === 'device' ? report.devices[Number(target.dataset.device)] : report.assemblies[Number(target.dataset.assembly)];
    selected = { kind, id: item.id }; render();
    if (event.type === 'keydown') $('mapDetails').focus();
  }
  $('buildProjectMap').addEventListener('click', build);
  for (const id of ['mapDeviceFilter', 'mapFabric', 'mapOutcome', 'mapSearch']) $(id).addEventListener(id === 'mapSearch' ? 'input' : 'change', () => { page = 0; selected = null; render(); });
  $('mapPrevious').addEventListener('click', () => { page--; render(); });
  $('mapNext').addEventListener('click', () => { page++; render(); });
  $('mapZoom').addEventListener('input', zoom);
  $('mapReset').addEventListener('click', () => { for (const id of ['mapDeviceFilter', 'mapFabric', 'mapOutcome', 'mapSearch']) $(id).value = ''; $('mapZoom').value = '100'; page = 0; selected = null; render(); $('mapCanvas').scrollTop = $('mapCanvas').scrollLeft = 0; });
  for (const id of ['mapCanvas', 'mapDetails', 'mapConnections']) { $(id).addEventListener('click', activate); $(id).addEventListener('keydown', activate); }
  window.addEventListener('pagehide', () => gate.cancel());
  window.ValidatorProjectMap = { init: value => { context = value; }, invalidate, renderDraft: project => { $('buildProjectMap').disabled = !project.connections.length && !project.breakouts.length; } };
})();
