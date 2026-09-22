/* Installation metadata and revision-bound cabling documents for the project. */
(() => {
  'use strict';
  const { esc, RequestGate, statusClass } = ValidatorCore;
  const $ = id => document.getElementById(id);
  const gate = new RequestGate();
  let context, report = null;
  const empty = () => ({ locations: [], port_labels: [], cables: [] });
  const entries = project => [...project.connections, ...project.breakouts];
  const selections = project => [...project.connections.flatMap(c => [c.a, c.b]), ...project.breakouts.flatMap(b => [b.head, ...b.branches.map(v => v.selection)])];
  const portKey = p => JSON.stringify([p.instance_id, p.port_group_id, p.port_number]);
  const endpointText = p => `${p.rack || 'Rack unknown'}${p.rack_u ? ' / U' + p.rack_u : ''}\n${p.instance_id}\n${p.port_label || 'Label unconfirmed'} (${p.port_group_id}/${p.port_number})${p.optical_port ? ' / optical ' + p.optical_port : ''}`;
  const field = (attributes, value, label, type = 'text') => `<input ${attributes} type="${type}" aria-label="${esc(label)}" value="${esc(value ?? '')}" maxlength="64"${type === 'number' ? ' min="1" max="1000" step="1"' : ''}>`;

  function options(project) { project.cabling ||= empty(); return project.cabling; }
  function cable(project, id) {
    const values = options(project).cables;
    let value = values.find(c => c.entry_id === id);
    if (!value) { value = { entry_id: id, cable_id: null, progress: [] }; values.push(value); }
    return value;
  }
  function invalidate() {
    gate.cancel(); report = null; $('cablingReport').replaceChildren();
    $('cablingStatus').textContent = 'Build the plan to review connections and export current documents.';
    for (const id of ['downloadCablingPDF', 'downloadLabelsPDF', 'downloadCablingXLSX']) $(id).disabled = true;
    $('buildCabling').disabled = false;
  }
  function render(project) {
    const data = project.cabling || empty(), all = selections(project);
    const instances = [...new Set(all.map(p => p.instance_id))].sort();
    const ports = [...new Map(all.map(p => [portKey(p), p])).values()];
    $('cablingLocations').innerHTML = instances.length ? `<table><thead><tr><th>Physical device</th><th>Rack</th><th>Rack unit (optional)</th></tr></thead><tbody>${instances.map(id => {
      const value = data.locations.find(p => p.instance_id === id) || {};
      return `<tr><td>${esc(id)}</td><td>${field(`data-location="${esc(id)}" data-field="rack"`, value.rack, id + ' rack')}</td><td>${field(`data-location="${esc(id)}" data-field="rack_u"`, value.rack_u, id + ' rack unit', 'number')}</td></tr>`;
    }).join('')}</tbody></table>` : '<p>Add a connection or breakout to prepare its installation plan.</p>';
    $('cablingPorts').innerHTML = `<table><thead><tr><th>Device / physical cage</th><th>Label printed on device</th></tr></thead><tbody>${ports.map((p, index) => {
      const value = data.port_labels.find(v => portKey(v) === portKey(p));
      return `<tr><td>${esc(p.instance_id)} / ${esc(p.port_group_id)} / ${esc(p.port_number)}</td><td>${field(`data-port-index="${index}"`, value?.label, p.instance_id + ' physical port ' + p.port_number)}</td></tr>`;
    }).join('')}</tbody></table>`;
    $('cablingIds').innerHTML = `<table><thead><tr><th>Project entry</th><th>Unique cable ID (blank uses C-entry)</th></tr></thead><tbody>${entries(project).map(e => `<tr><td>${esc(e.id)}</td><td>${field(`data-cable="${esc(e.id)}" placeholder="${esc('C-' + e.id)}"`, data.cables.find(c => c.entry_id === e.id)?.cable_id, e.id + ' cable ID')}</td></tr>`).join('')}</tbody></table>`;
    $('buildCabling').disabled = !instances.length;
    $('cablingPorts').dataset.keys = JSON.stringify(ports.map(p => ({ instance_id: p.instance_id, port_group_id: p.port_group_id, port_number: p.port_number })));
  }
  function prune(project) {
    if (!project.cabling) return;
    const all = selections(project), ports = new Set(all.map(portKey)), instances = new Set(all.map(p => p.instance_id));
    project.cabling.locations = project.cabling.locations.filter(p => instances.has(p.instance_id));
    project.cabling.port_labels = project.cabling.port_labels.filter(p => ports.has(portKey(p)));
    project.cabling.cables = project.cabling.cables.filter(c => entries(project).some(e => e.id === c.entry_id));
  }
  function shape(project) {
    if (project.cabling === undefined) return;
    const c = project.cabling;
    if (!c || typeof c !== 'object' || !['locations', 'port_labels', 'cables'].every(k => Array.isArray(c[k]) && c[k].length <= 512 && c[k].every(v => v && typeof v === 'object'))) throw new Error('Cabling metadata needs locations, port_labels and cables arrays.');
    if (!c.cables.every(v => Array.isArray(v.progress) && v.progress.every(p => p && typeof p === 'object'))) throw new Error('Cable installation entries need progress arrays.');
  }
  function download(blob, filename) {
    const url = URL.createObjectURL(blob), a = document.createElement('a');
    a.href = url; a.download = filename; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  async function request(path, binary = false) {
    let payload;
    try { payload = context.getProject(); } catch (error) { $('cablingStatus').textContent = error.message; return; }
    const ticket = gate.start(context.key());
    const timer = setTimeout(() => ticket.controller.abort(), 30000);
    $('cablingStatus').textContent = binary ? 'Preparing document…' : 'Building the complete installation plan…';
    try {
      const response = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, cache: 'no-store', signal: ticket.controller.signal, body: JSON.stringify(payload) });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(Array.isArray(data.detail) ? data.detail.slice(0, 5).map(v => `${v.loc.join('.')}: ${v.msg}`).join('; ') : data.detail || 'Cabling request failed');
      }
      const value = binary ? await response.blob() : await response.json();
      if (!gate.current(ticket, context.key())) return;
      const revision = binary ? response.headers.get('X-Catalog-Revision') : value.revision;
      if (revision !== payload.revision) throw new Error('Catalog changed. Refresh and build the plan again.');
      if (binary) {
        download(value, path.endsWith('labels.pdf') ? 'cable-labels.pdf' : 'cabling-plan.' + (path.endsWith('xlsx') ? 'xlsx' : 'pdf'));
        $('cablingStatus').textContent = 'Document exported from the current project.';
      } else { report = value; renderReport(); }
    } catch (error) {
      if (ticket.sequence === gate.sequence) $('cablingStatus').textContent = error.name === 'AbortError' ? 'Request timed out. Try again.' : error.message;
    } finally { clearTimeout(timer); }
  }
  function renderReport() {
    const s = report.summary;
    $('cablingStatus').textContent = `${s.cables} cables · ${s.legs} legs · ${s.labels} end labels · installed ${s.installed}/${s.legs} · checked ${s.checked}/${s.legs}`;
    $('cablingReport').innerHTML = `<p><span class="pill ${statusClass(report.status)}">${esc(report.status)}</span> ${report.provisional ? 'Provisional plan: review compatibility and missing installation details.' : 'All required plan checks passed.'}</p><div class="tablewrap"><table><thead><tr><th>Cable / branch</th><th>Source</th><th>Destination</th><th>Cable PN / length</th><th>Installed</th><th>Checked</th></tr></thead><tbody>${report.rows.map((r, i) => `<tr><td><strong>${esc(r.cable_id)}</strong><div>${esc(r.entry_id)}${r.branch_id ? ' / ' + esc(r.branch_id) + ' (termination ' + esc(r.termination) + ')' : ''}</div>${r.progress_stale ? '<div class="warn">Previous confirmation is stale</div>' : ''}${r.notes ? `<div>${esc(r.notes)}</div>` : ''}</td><td class="endpoint-text">${esc(endpointText(r.source))}</td><td class="endpoint-text">${esc(endpointText(r.destination))}</td><td>${esc(r.part_number || 'PN unknown')}<div>${r.length_m == null ? 'Length unknown' : esc(r.length_m) + ' m'} · ${esc(r.fabric)}</div></td><td><input type="checkbox" data-progress="${i}" data-field="installed" aria-label="${esc(r.cable_id + ' ' + (r.branch_id || '') + ' installed')}"${r.installed ? ' checked' : ''}></td><td><input type="checkbox" data-progress="${i}" data-field="checked" aria-label="${esc(r.cable_id + ' ' + (r.branch_id || '') + ' checked')}"${r.checked ? ' checked' : ''}></td></tr>`).join('')}</tbody></table></div><details><summary>${report.issues.length} installation details to complete</summary><ul>${report.issues.map(v => `<li>${esc(v)}</li>`).join('')}</ul></details><details><summary>Preview end labels</summary><div class="label-preview">${report.labels.map(l => `<article><strong>${esc(l.label_id)}</strong><div class="endpoint-text">${esc(endpointText(l.local))}</div><p>Remote: ${l.peers.length === 1 ? esc(l.peers[0].instance_id + ' / ' + (l.peers[0].port_label || l.peers[0].port_group_id + '/' + l.peers[0].port_number)) : esc(l.peers.length + ' branches; see plan')}</p><span class="small">${esc(l.part_number || 'PN unknown')}</span></article>`).join('')}</div></details>`;
    for (const id of ['downloadCablingPDF', 'downloadLabelsPDF', 'downloadCablingXLSX']) $(id).disabled = false;
  }
  for (const id of ['cablingLocations', 'cablingPorts', 'cablingIds']) $(id).addEventListener('input', event => {
    const input = event.target, d = input.dataset;
    try {
      context.change(project => {
        const data = options(project);
        if (d.location !== undefined) {
          let value = data.locations.find(p => p.instance_id === d.location);
          if (!value) { value = { instance_id: d.location, rack: null, rack_u: null }; data.locations.push(value); }
          value[d.field] = d.field === 'rack_u' ? (input.value ? Number(input.value) : null) : input.value.trim() || null;
        } else if (d.portIndex !== undefined) {
          const port = JSON.parse($('cablingPorts').dataset.keys)[Number(d.portIndex)];
          data.port_labels = data.port_labels.filter(p => portKey(p) !== portKey(port));
          if (input.value.trim()) data.port_labels.push({ ...port, label: input.value.trim() });
        } else if (d.cable !== undefined) cable(project, d.cable).cable_id = input.value.trim() || null;
      });
    } catch (error) { $('cablingStatus').textContent = error.message; }
  });
  $('cablingReport').addEventListener('change', event => {
    const d = event.target.dataset;
    if (d.progress === undefined || !report) return;
    const row = report.rows[Number(d.progress)], checked = event.target.checked;
    try {
      context.change(project => {
        const record = cable(project, row.entry_id);
        let progress = record.progress.find(p => (p.branch_id || null) === row.branch_id);
        if (!progress) { progress = { branch_id: row.branch_id, notes: '' }; record.progress.push(progress); }
        Object.assign(progress, { installed: row.installed, checked: row.checked, definition: row.definition });
        progress[d.field] = checked;
        if (d.field === 'checked' && checked) progress.installed = true;
        if (d.field === 'installed' && !checked) progress.checked = false;
      });
      request('/api/project/cabling');
    } catch (error) { $('cablingStatus').textContent = error.message; }
  });
  $('buildCabling').addEventListener('click', () => request('/api/project/cabling'));
  for (const [id, path] of [['downloadCablingPDF', 'cabling.pdf'], ['downloadLabelsPDF', 'labels.pdf'], ['downloadCablingXLSX', 'cabling.xlsx']]) $(id).addEventListener('click', () => { if (report) request('/api/project/' + path, true); });
  window.addEventListener('pagehide', () => gate.cancel());
  window.ValidatorCabling = { init: value => { context = value; }, render, invalidate, prune, shape };
})();
