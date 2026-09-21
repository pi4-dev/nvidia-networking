"""Exact-board qualification and procurement regressions; fixtures are not catalog claims."""

import copy
import json
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from app.catalog import LiveCatalog
from app.config import DATA_PATH, PROFILE_PATH
from app.hardware import effective_host, inspect_hardware, validate_hardware_catalog, version_matches
from app.models import (ConnectionRequest, Evidence, HardwareInspection, HardwareProfile,
                        ProfileDocument, RecommendationRequest, VersionScope)
from app.recommendations import recommend
from app.rules import evaluate, validate_connection

SNAPSHOT = LiveCatalog(DATA_PATH, PROFILE_PATH).get()
PN = '980-9I601-00N003'
PRODUCT = 'Copper|MCA4J80-Nxxx-FTF|flat-to-finned'
EVIDENCE = dict(kind='manufacturer', source_url='https://example.com/test-fixture',
                verified_on='2026-09-21', scope='Synthetic test fixture only; not a hardware claim.')


def request(**updates):
    data = dict(a=dict(device_id='profile:MQM9700-NS2F', port_group_id='ndr'),
                b=dict(device_id='system:DGX B200', port_group_id='cluster'),
                fabric='IB', speed_gbps=400, minimum_length_m=3.)
    data.update(updates)
    return RecommendationRequest.model_validate(data)


def qualified_fixture(kind='manufacturer'):
    snapshot = copy.deepcopy(SNAPSHOT)
    connection = recommend(snapshot, request(technology='LACC'))['candidates'][0]['connection']
    for side in ('a', 'b'):
        selected = connection[side]
        group = next(g for d in snapshot['devices'] if d['id'] == selected['device_id']
                     for g in d['port_groups'] if g['id'] == selected['port_group_id'])
        for mode in group['modes']:
            if mode['id'] == '2x400':
                mode.update(electrical_lanes=8, lane_rate_gbps=100., fec=['fixture-fec'])
        profile_id = 'test-board-' + side
        profile = HardwareProfile.model_validate(dict(id=profile_id, device_id=selected['device_id'], label=profile_id,
            identity={'sku': {'value': profile_id, 'evidence': EVIDENCE}},
            ports=[dict(port_group_id=group['id'], evidence={})],
            required_context=['psid', 'firmware', 'os_name', 'os_version'],
            qualifications=[dict(id='qualified-cable', port_group_id=group['id'], product_ids=[PRODUCT],
                part_numbers=[PN], mode_ids=['2x400'], fabric='IB', psid='test-psid',
                firmware={'minimum': '2.9', 'maximum': '2.20'}, os_name='TestOS', os_version={'versions': ['1.0']},
                outcome='supported', evidence={**EVIDENCE, 'kind': kind})])).model_dump()
        snapshot['hardware_profiles'].append(profile)
        selected.update(hardware_profile_id=profile_id, runtime=dict(sku=profile_id, psid='test-psid',
                        firmware='2.10', os_name='TestOS', os_version='1.0'))
    for endpoint in next(i for i in snapshot['interconnects'] if i['id'] == PRODUCT)['endpoints']:
        for mode in endpoint['modes']:
            mode['fec'] = ['fixture-fec']
    validate_hardware_catalog(snapshot)
    return snapshot, ConnectionRequest.model_validate(connection)


class HardwareTests(unittest.TestCase):
    def test_seed_facts_are_scoped_and_dated(self):
        self.assertEqual(len(SNAPSHOT['hardware_profiles']), 4)
        self.assertEqual(len(SNAPSHOT['fiber_assemblies']), 21)
        profile = SNAPSHOT['hardware_profiles'][0]
        self.assertFalse(profile['qualifications'])
        self.assertNotIn('psid', profile['identity'])
        self.assertTrue(all(e['verified_on'] and e['scope'] for e in profile['ports'][0]['evidence'].values()))

    def test_hardware_overrides_are_isolated_to_exact_board_and_group(self):
        host = HardwareInspection(device_id='supernic:ConnectX-8 SuperNIC', port_group_id='catalog-1',
                                  hardware_profile_id='900-9X81E-00EX-ST0')
        inspected = inspect_hardware(SNAPSHOT, host)
        self.assertEqual(inspected['effective_port']['module_speed_gbps'], 800)
        self.assertTrue(any(g['code'] == 'runtime.firmware' and g['action'] for g in inspected['gaps']))
        generic = host.model_copy(update={'hardware_profile_id': None})
        self.assertIsNone(effective_host(SNAPSHOT, generic)[1]['module_speed_gbps'])
        for update in [{'device_id': 'system:DGX B200'}, {'port_group_id': 'catalog-2'}]:
            with self.assertRaises(KeyError): effective_host(SNAPSHOT, host.model_copy(update=update))

    def test_fabric_scoped_mode_cannot_be_used_for_other_fabric(self):
        p = copy.deepcopy(next(p for p in SNAPSHOT['interconnects'] if p['id'] == PRODUCT))
        host = HardwareInspection(device_id='supernic:ConnectX-8 SuperNIC', port_group_id='catalog-1', hardware_profile_id='900-9X81E-00EX-ST0')
        group = effective_host(SNAPSHOT, host)[1]
        result = evaluate(group, p, 'ETH', '2x400-ndr', 'A')
        self.assertEqual(result['status'], 'incompatible')

    def test_missing_or_bad_provenance_is_rejected(self):
        raw = json.loads(PROFILE_PATH.read_text())
        raw['hardware_profiles'][0]['ports'][0]['evidence'].pop('module_speed_gbps')
        with self.assertRaises(ValidationError): ProfileDocument.model_validate(raw)
        for change in [{'source_url': 'javascript:alert(1)'}, {'verified_on': '2026-02-30'}, {'verified_on': '2999-01-01'}]:
            with self.assertRaises(ValidationError): Evidence.model_validate({**EVIDENCE, **change})

    def test_bad_cross_reference_rejects_new_snapshot(self):
        snapshot, _ = qualified_fixture()
        snapshot['hardware_profiles'][-1]['qualifications'][0]['part_numbers'] = ['not-in-catalog']
        with self.assertRaises(ValueError): validate_hardware_catalog(snapshot)

    def test_numeric_versions_and_explicit_version_labels(self):
        scope = VersionScope(minimum='2.9', maximum='2.10.0').model_dump()
        self.assertTrue(version_matches('2.10', scope))
        self.assertFalse(version_matches('2.8', scope))
        self.assertFalse(version_matches('2.10-beta', scope))
        self.assertTrue(version_matches('2.10-beta', VersionScope(versions=['2.10-beta']).model_dump()))
        with self.assertRaises(ValidationError): VersionScope(minimum='2.10', maximum='2.9')

    def test_manufacturer_qualification_can_complete_a_link(self):
        snapshot, connection = qualified_fixture()
        result = validate_connection(snapshot, connection)
        self.assertEqual(result['technical_status'], 'compatible')
        self.assertEqual(result['status'], 'compatible')
        self.assertTrue(all(q['manufacturer_confirmed'] for q in result['qualification'].values()))

    def test_lab_pass_is_conditional_and_never_vendor_confirmation(self):
        snapshot, connection = qualified_fixture('lab')
        result = validate_connection(snapshot, connection)
        self.assertEqual(result['status'], 'conditional')
        self.assertEqual(result['qualification']['a']['status'], 'lab-tested')
        self.assertFalse(result['qualification']['a']['manufacturer_confirmed'])

    def test_missing_untested_or_unscoped_software_remains_unknown(self):
        for change in [{'firmware': '2.21'}, {'firmware': None}, {'os_version': '2.0'}, {'psid': 'other'}]:
            snapshot, connection = qualified_fixture()
            runtime = connection.a.runtime.model_copy(update=change)
            connection = connection.model_copy(update={'a': connection.a.model_copy(update={'runtime': runtime})})
            with self.subTest(change=change): self.assertEqual(validate_connection(snapshot, connection)['status'], 'unknown')
        snapshot, connection = qualified_fixture()
        snapshot['hardware_profiles'][-2]['qualifications'][0]['firmware'] = None
        self.assertEqual(validate_connection(snapshot, connection)['status'], 'unknown')

    def test_explicit_deny_and_identity_mismatch_cannot_be_overridden(self):
        snapshot, connection = qualified_fixture()
        q = copy.deepcopy(snapshot['hardware_profiles'][-2]['qualifications'][0])
        q.update(id='denied', outcome='unsupported')
        snapshot['hardware_profiles'][-2]['qualifications'].append(q)
        result = validate_connection(snapshot, connection)
        self.assertEqual(result['status'], 'incompatible')
        self.assertTrue(any('Conflicting' in c['message'] for c in result['checks']))
        snapshot, connection = qualified_fixture()
        connection.a.runtime.sku = 'wrong-board'
        self.assertEqual(validate_connection(snapshot, connection)['status'], 'incompatible')

    def test_vendor_record_never_overrides_physical_failure(self):
        snapshot, connection = qualified_fixture()
        connection.a.endpoint_id = 'A'  # Flat-top end in a finned-only switch.
        self.assertEqual(validate_connection(snapshot, connection)['status'], 'incompatible')


class RecommendationTests(unittest.TestCase):
    def test_actual_catalog_returns_cable_and_complete_optical_alternatives(self):
        result = recommend(SNAPSHOT, request())
        self.assertFalse(result['truncated'])
        self.assertEqual(result['candidates'][0]['components'][0]['part_number'], PN)
        self.assertEqual(result['candidates'][0]['validation']['orientation'], {'a': 'B', 'b': 'A'})
        optical = next(c for c in result['candidates'] if c['technology'] == 'optical')
        self.assertEqual([c['role'] for c in optical['components']], ['module', 'fiber', 'module'])
        self.assertTrue(optical['ordering_complete'])
        self.assertEqual(optical['components'][1]['part_number'], 'MFP7E30-N003')
        self.assertFalse(optical['connection']['fiber']['pinout_verified'])
        self.assertTrue(all(c['validation']['status'] == 'unknown' for c in result['candidates']))

    def test_length_constraint_selects_actual_longer_assembly(self):
        result = recommend(SNAPSHOT, request(technology='optical', minimum_length_m=4.))
        self.assertTrue(result['candidates'])
        self.assertEqual(result['candidates'][0]['length_m'], 5.)
        self.assertTrue(all(c['length_m'] >= 4 for c in result['candidates']))
        self.assertFalse(recommend(SNAPSHOT, request(technology='LACC', minimum_length_m=4.))['candidates'])

    def test_per_link_rate_is_never_replaced_by_aggregate(self):
        self.assertFalse(recommend(SNAPSHOT, request(speed_gbps=800))['candidates'])

    def test_reuse_filter_orientation_and_inventory_counts(self):
        result = recommend(SNAPSHOT, request(reuse_part_number=PN, reuse_side='a', owned_parts=[dict(part_number=PN, quantity=1)]))
        self.assertEqual(len(result['candidates']), 1)
        candidate = result['candidates'][0]
        self.assertEqual(candidate['inventory'], [dict(part_number=PN, required=1, owned=1, reused=1, to_buy=0)])
        self.assertFalse(recommend(SNAPSHOT, request(reuse_part_number='does-not-exist'))['candidates'])
        optical = recommend(SNAPSHOT, request(technology='optical'))['candidates'][0]
        pn = optical['components'][0]['part_number']
        self.assertTrue(recommend(SNAPSHOT, request(reuse_part_number=pn, reuse_side='a'))['candidates'])
        self.assertFalse(recommend(SNAPSHOT, request(reuse_part_number=pn, reuse_side='b'))['candidates'])

    def test_two_equal_module_pns_consume_two_inventory_units(self):
        from app.recommendations import _inventory
        rows, reused = _inventory([{'part_number': 'module'}, {'part_number': 'module'}, {'part_number': 'fiber'}],
            request(owned_parts=[dict(part_number='module', quantity=1)]))
        module = next(r for r in rows if r['part_number'] == 'module')
        self.assertEqual((module['required'], module['reused'], module['to_buy'], reused), (2, 1, 1, 1))

    def test_reuse_priority_can_prefer_owned_optical_parts(self):
        owned = 'MFP7E30-N005'
        result = recommend(SNAPSHOT, request(sort_by='reuse', owned_parts=[dict(part_number=owned, quantity=1)]))
        first = result['candidates'][0]
        self.assertEqual(first['technology'], 'optical')
        self.assertIn(owned, [p['part_number'] for p in first['components']])
        self.assertEqual(first['reused_count'], 1)

    def test_unknown_filter_and_search_bound_are_explicit(self):
        self.assertFalse(recommend(SNAPSHOT, request(include_unknown=False))['candidates'])
        with patch('app.recommendations.MAX_EVALUATIONS', 1):
            result = recommend(SNAPSHOT, request())
        self.assertTrue(result['truncated'])
        self.assertEqual(result['examined'], 1)
        self.assertTrue(any('limit reached' in n for n in result['notes']))

    def test_unavailable_fiber_pn_remains_unresolved(self):
        snapshot = copy.deepcopy(SNAPSHOT); snapshot['fiber_assemblies'] = []
        result = recommend(snapshot, request(technology='optical'))
        self.assertTrue(result['candidates'])
        self.assertTrue(all(not c['ordering_complete'] and c['components'][1]['part_number'] is None for c in result['candidates']))
        self.assertTrue(all(any(g['code'] == 'link.fiber_sku' for g in c['validation']['gaps']) for c in result['candidates']))

    def test_fiber_pn_cannot_certify_wrong_length_or_properties(self):
        data = recommend(SNAPSHOT, request(technology='optical'))['candidates'][0]['connection']
        for update in ['length', 'grade']:
            bad = copy.deepcopy(data)
            if update == 'length': bad['length_m'] = 4.
            else: bad['fiber'].update(medium='MM', fiber_type='OM3')
            self.assertEqual(validate_connection(SNAPSHOT, ConnectionRequest.model_validate(bad))['status'], 'incompatible')

    def test_deterministic_ranking_and_unknown_pn_length(self):
        first = recommend(SNAPSHOT, request(sort_by='fewest_components'))
        self.assertEqual(first, recommend(SNAPSHOT, request(sort_by='fewest_components')))
        self.assertEqual(first['candidates'][0]['component_count'], 1)
        snapshot = copy.deepcopy(SNAPSHOT)
        cable = next(p for p in snapshot['interconnects'] if p['id'] == PRODUCT)
        cable['skus'][0]['length_m'] = None
        candidate = recommend(snapshot, request(reuse_part_number=PN))['candidates'][0]
        self.assertIsNone(candidate['length_m'])
        self.assertEqual(candidate['validation']['status'], 'unknown')

    def test_invalid_inventory_and_constraints_are_rejected(self):
        for update in [{'speed_gbps': 0}, {'minimum_length_m': -1.}, {'owned_parts': [dict(part_number=PN, quantity=0)]},
                       {'owned_parts': [dict(part_number=PN), dict(part_number=PN)]}]:
            with self.subTest(update=update), self.assertRaises(ValidationError): request(**update)


if __name__ == '__main__':
    unittest.main()
