"""Derived topology and physical cage inventory for one validated project."""

from collections import defaultdict

from .cabling import build_cabling
from .hardware import effective_host
from .models import HostSelection


def free_ranges(count, occupied):
    """Describe unused ordinals without allocating a catalog-sized array."""
    if count is None:
        return []
    result, start = [], 1
    for number in sorted(n for n in occupied if 1 <= n <= count):
        if start < number:
            result.append([start, number - 1])
        start = number + 1
    if start <= count:
        result.append([start, count])
    return result


def build_project_map(snapshot, project, validation):
    plan = build_cabling(snapshot, project, validation)
    results = {r['id']: r for r in validation['results']}
    locations = {p.instance_id: p for p in project.cabling.locations}
    markings = {(p.instance_id, p.port_group_id, p.port_number): p.label for p in project.cabling.port_labels}
    models = {d['id']: d for d in snapshot['devices']}
    profiles = {p['id']: p for p in snapshot.get('hardware_profiles', [])}
    selections, segments, assemblies = defaultdict(list), [], []

    def segment(entry, host, role, branch=None):
        try:
            _, group, _ = effective_host(snapshot, host)
            mode = next((m for m in group['modes'] if m['id'] == host.mode_id), None)
        except KeyError:
            mode = None
        item = dict(id=f'segment-{len(segments)}', entry_id=entry.id, instance_id=host.instance_id,
            port_group_id=host.port_group_id, port_number=host.port_number,
            port_label=markings.get((host.instance_id, host.port_group_id, host.port_number)),
            role=role, branch_id=branch.id if branch else None, termination=branch.termination if branch else None,
            head_links=branch.head_links if branch else [], selected_mode=host.mode_id,
            mode={k: mode[k] for k in ('id', 'links', 'speed_gbps')} if mode else None,
            part_number=host.part_number, status=results[entry.id]['status'])
        segments.append(item)
        selections[host.instance_id].append((host, item, entry))

    for entry in [*project.connections, *project.breakouts]:
        is_breakout = hasattr(entry, 'branches')
        rows = [r for r in plan['rows'] if r['entry_id'] == entry.id]
        result = results[entry.id]
        assemblies.append(dict(id=entry.id, type='breakout' if is_breakout else 'connection',
            topology=entry.topology if is_breakout else 'point-to-point', cable_id=rows[0]['cable_id'],
            part_number=rows[0]['part_number'], length_m=rows[0]['length_m'], fabric=entry.fabric,
            status=result['status'], checks=result['validation']['checks'], rows=rows))
        if is_breakout:
            segment(entry, entry.head, 'head')
            for branch in entry.branches:
                segment(entry, branch.selection, 'branch', branch)
        else:
            segment(entry, entry.a, 'a')
            segment(entry, entry.b, 'b')

    devices = []
    for instance, assignments in sorted(selections.items()):
        signatures = {(h.device_id, h.hardware_profile_id) for h, _, _ in assignments}
        identity_conflict = len(signatures) != 1
        first = assignments[0][0]
        device = models.get(first.device_id)
        profile = profiles.get(first.hardware_profile_id) if first.hardware_profile_id else None
        profile_valid = not first.hardware_profile_id or bool(profile and profile['device_id'] == first.device_id)
        base_groups = {g['id']: g for g in device['port_groups']} if device else {}
        allowed = {p['port_group_id'] for p in profile['ports']} if profile and profile_valid else set(base_groups)
        group_ids = allowed | {h.port_group_id for h, _, _ in assignments}
        groups = []
        for group_id in sorted(group_ids):
            base = base_groups.get(group_id, {})
            group = None
            if not identity_conflict and profile_valid:
                try:
                    _, group, _ = effective_host(snapshot, HostSelection(device_id=first.device_id,
                        hardware_profile_id=first.hardware_profile_id, port_group_id=group_id))
                except KeyError:
                    pass
            count = group.get('count') if group else None
            port_uses = defaultdict(list)
            for host, item, entry in assignments:
                if host.port_group_id == group_id:
                    port_uses[host.port_number].append((host, item, entry))
            ports = []
            for number, uses in sorted(port_uses.items()):
                ownership_conflict = identity_conflict or len(uses) > 1 or count is not None and number > count
                for _, item, _ in uses:
                    item['ownership_conflict'] = ownership_conflict
                interfaces = []
                if len(uses) == 1 and uses[0][1]['mode']:
                    _, item, entry = uses[0]
                    for logical in range(1, item['mode']['links'] + 1):
                        if item['role'] == 'head':
                            references = [b.id for b in entry.branches if logical in b.head_links]
                        elif item['mode']['links'] == 1:
                            references = [item['branch_id'] or entry.id]
                        else:
                            references = []
                        interfaces.append(dict(number=logical, speed_gbps=item['mode']['speed_gbps'],
                            references=references, state='conflict' if len(references) > 1 else 'declared' if references else 'unmapped'))
                ports.append(dict(number=number, label=markings.get((instance, group_id, number)),
                    state='conflict' if len(uses) > 1 else 'out-of-range' if count is not None and number > count else 'occupied',
                    segments=[item['id'] for _, item, _ in uses], interfaces=interfaces))
            in_range = sum(1 for n in port_uses if count is not None and n <= count)
            groups.append(dict(id=group_id, label=base.get('label', group_id),
                connector_family=base.get('connector_family'), count=count,
                occupied=len(ports), occupied_in_range=in_range if count is not None else None,
                free_count=count - in_range if count is not None else None,
                free_ranges=free_ranges(count, port_uses), ports=ports,
                capacity_known=count is not None))
        location = locations.get(instance)
        devices.append(dict(id=instance, device_id=first.device_id,
            model=device['model'] if device and not identity_conflict else 'Conflicting models/profiles' if identity_conflict else first.device_id,
            hardware_profile_id=first.hardware_profile_id, identity_conflict=identity_conflict,
            ownership_conflict=any(s.get('ownership_conflict') for _, s, _ in assignments),
            rack=location.rack if location else None, rack_u=location.rack_u if location else None,
            groups=groups, occupied=sum(g['occupied'] for g in groups),
            free_count=sum(g['free_count'] for g in groups) if groups and all(g['capacity_known'] for g in groups) else None))
    for assembly in assemblies:
        assembly['ownership_conflict'] = any(s.get('ownership_conflict') for s in segments if s['entry_id'] == assembly['id'])
    return dict(scope='project-map', name=project.name, revision=snapshot['revision'], status=validation['status'],
        devices=devices, assemblies=assemblies, segments=segments,
        checks=[c for c in validation['checks'] if c['code'].startswith(('ports.', 'project.'))],
        summary=dict(devices=len(devices), assemblies=len(assemblies), terminations=len(segments),
            occupied_cages=sum(d['occupied'] for d in devices),
            conflicting_cages=sum(p['state'] == 'conflict' for d in devices for g in d['groups'] for p in g['ports'])),
        notes=['Free means unallocated in this project; live device occupancy is not discovered.',
            'Physical cage counts come from the selected exact profile or catalog. Unknown or conflicting identities never imply free capacity.',
            'Logical interfaces belong to a selected cage mode and are not additional physical cages. Unmapped interfaces are not spare cages.',
            'Cable and breakout status comes from complete validation. A physical cage remains occupied even when compatibility fails.'])
