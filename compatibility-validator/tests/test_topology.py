"""Whole-topology regressions. Any added capability/FEC/evidence is synthetic."""

import copy
import csv
import io
import unittest

from pydantic import ValidationError

from app.catalog import LiveCatalog
from app.config import DATA_PATH, PROFILE_PATH
from app.projects import (CSV_FIELDS, StaleProject, bom_csv, connection_csv,
                          import_project_csv, validate_project)
from app.topology import validate_breakout
from app.topology_models import BreakoutRequest, ProjectCSV, ProjectRequest

SNAPSHOT = LiveCatalog(DATA_PATH, PROFILE_PATH).get()
CABLE = 'Copper|MCP7Y00-Nxxx|finned head'
PN = 'MCP7Y00-N003'
EVIDENCE = dict(kind='manufacturer', source_url='https://example.com/synthetic-fixture',
                verified_on='2026-09-21', scope='Synthetic test fixture; not a catalog hardware claim.')


def cable_breakout():
    head = dict(instance_id='switch-01', port_number=1, device_id='profile:MQM9700-NS2F',
                port_group_id='ndr', mode_id='2x400', product_id=CABLE, part_number=PN)
    branches = [dict(id=f'branch-{n}', termination=n, head_links=[n], selection=dict(instance_id=f'cx8-{n}',
        port_number=1, device_id='supernic:ConnectX-8 SuperNIC', hardware_profile_id='900-9X81E-00EX-ST0',
        port_group_id='catalog-1', mode_id='1x400-ndr', product_id=CABLE, part_number=PN)) for n in (1, 2)]
    return BreakoutRequest(head=head, branches=branches, fabric='IB', length_m=3., mapping_verified=True,
                           revision=SNAPSHOT['revision'])


def cable_fixture(split_fec=False):
    snapshot, request = copy.deepcopy(SNAPSHOT), cable_breakout()
    group = next(d for d in snapshot['devices'] if d['id'] == request.head.device_id)['port_groups'][0]
    group['conditions'] = []
    next(m for m in group['modes'] if m['id'] == '2x400').update(electrical_lanes=8, lane_rate_gbps=100., fec=['F1', 'F2'])
    original = next(p for p in snapshot['hardware_profiles'] if p['id'] == request.branches[0].selection.hardware_profile_id)
    for n, branch in enumerate(request.branches):
        profile = copy.deepcopy(original); profile['id'] = f'fixture-{n}'
        for mode in profile['ports'][0]['modes']:
            if mode['id'] == '1x400-ndr': mode['fec'] = ['F2' if split_fec and n else 'F1']
        snapshot['hardware_profiles'].append(profile); branch.selection.hardware_profile_id = profile['id']
    for endpoint in next(p for p in snapshot['interconnects'] if p['id'] == CABLE)['endpoints']:
        for mode in endpoint['modes']: mode['fec'] = ['F1', 'F2']
    return snapshot, request


def optical_fixture():
    snapshot = copy.deepcopy(SNAPSHOT)
    head_pid, remote_pid = 'Transceiver|MMS1V00-WM|-', 'Transceiver|MMS1V70-CM|-'
    head_mode = dict(id='4x100-fixture', links=4, speed_gbps=100, electrical_lanes=8, lane_rate_gbps=50., fec=['F1'], fabrics=['ETH'])
    branch_mode = dict(id='1x100-fixture', links=1, speed_gbps=100, electrical_lanes=4, lane_rate_gbps=25., fec=['F1'], fabrics=['ETH'])
    for device_id, mode in [('ethernet:SN5400', head_mode), ('ethernet:SN3420', branch_mode)]:
        group = next(d for d in snapshot['devices'] if d['id'] == device_id)['port_groups'][0]
        group['modes'] = [copy.deepcopy(mode)]; group['conditions'] = []
    for pid, mode, lanes, standard in [(head_pid, head_mode, 4, 'DR4-fixture'), (remote_pid, branch_mode, 1, 'DR1-fixture')]:
        item = next(p for p in snapshot['interconnects'] if p['id'] == pid)
        item['endpoints'][0]['modes'] = [copy.deepcopy(mode)]
        item['conditions'] = []
        item['optics'].update(lanes=lanes, standard=standard, lane_rate_gbps=100., wavelengths_nm=[1310.], fec=['F1'])
    head = dict(instance_id='switch-01', port_number=1, device_id='ethernet:SN5400', port_group_id='ports-1',
                mode_id=head_mode['id'], product_id=head_pid, part_number='980-9I16Y-00W000')
    branches = [dict(id=f'branch-{n}', termination=n, head_links=[n], head_optical_port=1,
        head_optical_lanes=[n], branch_optical_lanes=[1], interop_evidence=EVIDENCE,
        selection=dict(instance_id=f'remote-{n}', port_number=1, device_id='ethernet:SN3420', port_group_id='ports-1',
        mode_id=branch_mode['id'], product_id=remote_pid, part_number='980-9I042-00C000')) for n in range(1, 5)]
    request = BreakoutRequest(topology='optical', head=head, branches=branches, fabric='ETH', length_m=3., mapping_verified=True,
        optical_fanout=dict(part_number='FIXTURE-HARNESS', branch_count=4, head_ports=1, evidence=EVIDENCE,
            fiber=dict(medium='SM', fiber_type='OS2', connector_a='MPO-12/APC', connector_b='LC duplex', pinout_verified=True)),
        revision=snapshot['revision'])
    return snapshot, request


def project_of(*breakouts, connections=None, owned=None):
    return ProjectRequest(name='Topology fixture', breakouts=[{**b.model_dump(), 'id': f'fanout-{i + 1}'} for i, b in enumerate(breakouts)],
                          connections=connections or [], owned_parts=owned or [], revision=SNAPSHOT['revision'])


def point_connection(id_='link-1', port=1):
    pn = '980-9I601-00N003'; pid = 'Copper|MCA4J80-Nxxx-FTF|flat-to-finned'
    return dict(id=id_, fabric='IB', length_m=3.,
        a=dict(instance_id='switch-point', port_number=port, device_id='profile:MQM9700-NS2F', port_group_id='ndr', mode_id='2x400', product_id=pid, part_number=pn, endpoint_id='B'),
        b=dict(instance_id='dgx-point', port_number=port, device_id='system:DGX B200', port_group_id='cluster', mode_id='2x400', product_id=pid, part_number=pn, endpoint_id='A'))


class BreakoutTests(unittest.TestCase):
    def test_actual_cable_checks_all_branches_without_inventing_fec(self):
        result = validate_breakout(SNAPSHOT, cable_breakout())
        self.assertEqual(result['scope'], 'complete-breakout')
        self.assertEqual((result['expected_branches'], result['assigned_branches']), (2, 2))
        self.assertEqual(result['status'], 'unknown')
        self.assertFalse(any(c['state'] == 'fail' for c in result['checks']))
        self.assertTrue(any(c['code'] == 'breakout.common_fec' and c['state'] == 'unknown' for c in result['checks']))

    def test_complete_electrical_fixture_passes_technical_checks_only(self):
        snapshot, request = cable_fixture()
        result = validate_breakout(snapshot, request)
        self.assertEqual(result['technical_status'], 'compatible')
        self.assertEqual(result['status'], 'unknown')
        self.assertEqual(result['common_fec'], ['F1'])

    def test_individually_valid_fec_does_not_imply_whole_fanout_valid(self):
        snapshot, request = cable_fixture(split_fec=True)
        result = validate_breakout(snapshot, request)
        self.assertTrue(all(b['validation']['technical_status'] == 'compatible' for b in result['branches']))
        self.assertEqual(result['technical_status'], 'incompatible')
        self.assertTrue(any(c['code'] == 'breakout.common_fec' and c['state'] == 'fail' for c in result['checks']))

    def test_duplicate_and_missing_branches_and_logical_channels(self):
        for field in ('termination', 'head_links'):
            request = cable_breakout()
            setattr(request.branches[1], field, getattr(request.branches[0], field))
            with self.subTest(field=field): self.assertEqual(validate_breakout(SNAPSHOT, request)['status'], 'incompatible')
        request = cable_breakout(); request.branches.pop()
        result = validate_breakout(SNAPSHOT, request)
        self.assertEqual(result['status'], 'unknown')
        self.assertTrue(any(c['code'] == 'breakout.termination_count' and c['state'] == 'unknown' for c in result['checks']))

    def test_physical_cage_conflicts_and_ordinals_are_reported(self):
        for update in ('duplicate', 'out-of-range'):
            request = cable_breakout()
            if update == 'duplicate': request.branches[1].selection.instance_id = request.branches[0].selection.instance_id
            else: request.branches[1].selection.port_number = 2  # exact C8180 has one cage
            result = validate_breakout(SNAPSHOT, request)
            self.assertEqual(result['status'], 'incompatible')
            self.assertTrue(any(c['code'].startswith('ports.') and c['state'] == 'fail' for c in result['checks']))

    def test_oversubscription_and_wrong_branch_pn_cannot_pass(self):
        request = cable_breakout(); extra = request.branches[0].model_copy(deep=True)
        extra.id = 'extra'; extra.termination = 3; extra.head_links = [3]; extra.selection.instance_id = 'extra-host'
        request.branches.append(extra)
        result = validate_breakout(SNAPSHOT, request)
        self.assertTrue(any(c['code'] == 'breakout.bandwidth' and c['state'] == 'fail' for c in result['checks']))
        request = cable_breakout(); request.branches[0].selection.part_number = 'MCP7Y00-N001'
        self.assertEqual(validate_breakout(SNAPSHOT, request)['status'], 'incompatible')

    def test_explicit_mode_and_bounded_requests_are_required(self):
        raw = cable_breakout().model_dump(); raw['head']['mode_id'] = None
        with self.assertRaises(ValidationError): BreakoutRequest.model_validate(raw)
        raw = cable_breakout().model_dump(); raw['branches'] *= 9
        with self.assertRaises(ValidationError): BreakoutRequest.model_validate(raw)

    def test_optical_lane_map_needs_whole_coverage_and_evidence(self):
        snapshot, request = optical_fixture()
        result = validate_breakout(snapshot, request)
        self.assertEqual(result['technical_status'], 'compatible')
        self.assertEqual(result['status'], 'unknown')
        request.branches[0].interop_evidence = None
        self.assertEqual(validate_breakout(snapshot, request)['technical_status'], 'unknown')
        request.branches[0].head_optical_lanes = [2]
        self.assertEqual(validate_breakout(snapshot, request)['technical_status'], 'incompatible')

    def test_optical_rate_pinout_and_multi_connector_coverage(self):
        for case in ('lane-rate', 'pinout', 'head-ports'):
            snapshot, request = optical_fixture()
            if case == 'lane-rate': next(p for p in snapshot['interconnects'] if p['id'] == request.branches[0].selection.product_id)['optics']['lane_rate_gbps'] = 25.
            elif case == 'pinout': request.optical_fanout.fiber.pinout_verified = False
            else: request.optical_fanout.head_ports = 2
            with self.subTest(case=case): self.assertEqual(validate_breakout(snapshot, request)['technical_status'], 'unknown' if case == 'pinout' else 'incompatible')


class ProjectTests(unittest.TestCase):
    def test_breakout_counts_one_cable_and_global_inventory_once(self):
        first = cable_breakout(); second = first.model_copy(deep=True)
        second.head.port_number = 2
        for b in second.branches: b.selection.instance_id += '-second'
        project = project_of(first, second, owned=[dict(part_number=PN, quantity=1)])
        report = validate_project(SNAPSHOT, project)
        row = report['bom']['rows'][0]
        self.assertEqual((row['required'], row['owned'], row['reused'], row['to_buy']), (2, 1, 1, 1))
        self.assertEqual(report['summary']['physical_cages'], 6)
        self.assertTrue(report['bom']['provisional'])

    def test_shared_cage_and_inconsistent_device_identity_across_entries(self):
        first, second = point_connection(), point_connection('link-2')
        result = validate_project(SNAPSHOT, project_of(connections=[first, second]))
        self.assertEqual(result['status'], 'incompatible')
        self.assertTrue(any(c['code'] == 'ports.duplicate' and c['state'] == 'fail' for c in result['checks']))
        second['a'].update(device_id='ethernet:SN5600', port_group_id='ports-1', port_number=2)
        second['b']['port_number'] = 2
        result = validate_project(SNAPSHOT, project_of(connections=[first, second]))
        self.assertTrue(any(c['code'] == 'ports.instance_identity' and c['state'] == 'fail' for c in result['checks']))

    def test_runtime_conflict_across_different_ports_on_one_device(self):
        first, second = point_connection(), point_connection('link-2', 2)
        first['a']['runtime'] = {'firmware': '1.0'}; second['a']['runtime'] = {'firmware': '2.0'}
        result = validate_project(SNAPSHOT, project_of(connections=[first, second]))
        self.assertTrue(any(c['code'] == 'ports.instance_runtime' and c['state'] == 'fail' for c in result['checks']))

    def test_optical_bom_counts_shared_head_once_and_all_remote_modules(self):
        snapshot, request = optical_fixture()
        report = validate_project(snapshot, project_of(request, owned=[dict(part_number='980-9I042-00C000', quantity=2)]))
        rows = {r['part_number']: r for r in report['bom']['rows']}
        self.assertEqual(rows['980-9I16Y-00W000']['required'], 1)
        self.assertEqual(rows['980-9I042-00C000']['required'], 4)
        self.assertEqual(rows['980-9I042-00C000']['to_buy'], 2)
        self.assertEqual(rows['FIXTURE-HARNESS']['required'], 1)
        self.assertEqual(report['bom']['total_components'], 6)

    def test_unknown_product_does_not_hide_other_project_rows(self):
        first, second = point_connection(), point_connection('link-2', 2)
        second['a']['product_id'] = 'not-in-catalog'
        report = validate_project(SNAPSHOT, project_of(connections=[first, second]))
        self.assertEqual(len(report['results']), 2)
        self.assertEqual(report['results'][1]['status'], 'unknown')
        self.assertFalse(report['bom']['ordering_complete'])

    def test_same_external_harness_pn_cannot_have_conflicting_lengths(self):
        snapshot, first = optical_fixture()
        second = first.model_copy(deep=True); second.length_m = 5.; second.head.port_number = 2
        for branch in second.branches: branch.selection.instance_id += '-second'
        report = validate_project(snapshot, project_of(first, second))
        self.assertEqual(report['status'], 'incompatible')
        self.assertTrue(any(c['code'] == 'project.harness_identity' and c['state'] == 'fail' for c in report['checks']))

    def test_stale_nested_revision_and_duplicate_ids_are_rejected(self):
        connection = point_connection(); connection['revision'] = '000000000000'
        with self.assertRaises(StaleProject): validate_project(SNAPSHOT, project_of(connections=[connection]))
        with self.assertRaises(ValidationError): project_of(connections=[point_connection(), point_connection()])
        with self.assertRaises(ValidationError): ProjectRequest()

    def test_unused_stock_and_csv_formula_escaping(self):
        snapshot = copy.deepcopy(SNAPSHOT)
        next(p for p in snapshot['interconnects'] if p['id'] == CABLE)['model'] = '=HYPERLINK("https://example.com")'
        report = validate_project(snapshot, project_of(cable_breakout(), owned=[dict(part_number=PN, quantity=3)]))
        self.assertEqual(report['bom']['unused_inventory'], [dict(part_number=PN, quantity=2)])
        rows = list(csv.DictReader(io.StringIO(bom_csv(report))))
        self.assertTrue(rows[0]['model'].startswith("'="))
        self.assertEqual(rows[0]['required'], '1')


class CSVTests(unittest.TestCase):
    def test_connection_export_import_round_trip_preserves_context_and_ports(self):
        row = point_connection()
        row['a']['runtime'] = {'firmware': '2.10', 'os_name': 'Test OS', 'os_version': '1.0', 'psid': 'test'}
        project = project_of(connections=[row])
        imported = import_project_csv(SNAPSHOT, ProjectCSV(csv='\ufeff' + connection_csv(project), name=project.name, revision=project.revision))
        expected = project.connections[0].model_dump(); expected['revision'] = project.revision
        self.assertEqual(imported.connections[0].model_dump(), expected)

    def test_model_names_pn_resolution_and_semicolon_csv(self):
        header = ['id', 'fabric', 'a_instance', 'a_device', 'a_group', 'a_port', 'a_pn', 'b_instance', 'b_device', 'b_group', 'b_port', 'b_pn', 'length_m']
        row = ['link-1', 'IB', 'switch', 'MQM9700-NS2F', 'ndr', '1', '980-9I601-00N003', 'dgx', 'DGX B200', 'cluster', '2', '980-9I601-00N003', '3']
        text = ';'.join(header) + '\n' + ';'.join(row) + '\n'
        project = import_project_csv(SNAPSHOT, ProjectCSV(csv=text))
        self.assertEqual(project.connections[0].b.port_number, 2)
        self.assertEqual(project.connections[0].a.device_id, 'profile:MQM9700-NS2F')
        self.assertEqual(project.connections[0].a.product_id, 'Copper|MCA4J80-Nxxx-FTF|flat-to-finned')

    def test_duplicates_unknown_columns_bad_rows_and_invalid_numbers_reject_atomically(self):
        good = connection_csv(project_of(connections=[point_connection()]))
        for text in [good.replace('id,a_instance', 'id,id', 1), good.replace('id,a_instance', 'id,unexpected', 1),
                     good + 'incomplete,row\n', good.replace('switch-point,profile:', 'switch-point,profile:', 1).replace(',ndr,1,', ',ndr,-1,', 1)]:
            with self.subTest(text=text[:50]), self.assertRaises(ValueError): import_project_csv(SNAPSHOT, ProjectCSV(csv=text))

    def test_csv_cannot_silently_drop_breakout_entries(self):
        with self.assertRaisesRegex(ValueError, 'JSON'): connection_csv(project_of(cable_breakout()))

    def test_bounded_csv_count_and_unknown_part_number(self):
        good = connection_csv(project_of(connections=[point_connection()]))
        lines = good.splitlines()
        with self.assertRaises(ValueError): import_project_csv(SNAPSHOT, ProjectCSV(csv=lines[0] + '\n' + '\n'.join(lines[1] for _ in range(201))))
        bad = good.replace('Copper|MCA4J80-Nxxx-FTF|flat-to-finned', '').replace('980-9I601-00N003', 'unlisted-pn')
        with self.assertRaisesRegex(ValueError, 'row 2'): import_project_csv(SNAPSHOT, ProjectCSV(csv=bad))


if __name__ == '__main__':
    unittest.main()
