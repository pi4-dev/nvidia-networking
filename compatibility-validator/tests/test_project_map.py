"""Physical inventory and graph regressions; modified catalog facts are synthetic."""

import copy
import unittest

from app.project_map import build_project_map, free_ranges
from app.projects import validate_project
from test_cabling import installed_project
from test_topology import SNAPSHOT, cable_breakout, optical_fixture, point_connection, project_of


def graph(project, snapshot=SNAPSHOT):
    return build_project_map(snapshot, project, validate_project(snapshot, project))


def group(data, instance, group_id):
    return next(g for d in data['devices'] if d['id'] == instance for g in d['groups'] if g['id'] == group_id)


class ProjectMapTests(unittest.TestCase):
    def test_complete_breakout_has_one_physical_head_and_separate_logical_links(self):
        data = graph(installed_project())
        self.assertEqual(data['summary'], dict(devices=3, assemblies=1, terminations=3, occupied_cages=3, conflicting_cages=0))
        self.assertEqual(sum(s['role'] == 'head' for s in data['segments']), 1)
        head = group(data, 'switch-01', 'ndr')
        self.assertEqual((head['count'], head['occupied'], head['free_count']), (32, 1, 31))
        self.assertEqual(head['free_ranges'], [[2, 32]])
        self.assertEqual(head['ports'][0]['label'], '1/1')
        self.assertEqual([i['references'] for i in head['ports'][0]['interfaces']], [['branch-1'], ['branch-2']])
        self.assertEqual(data['assemblies'][0]['cable_id'], 'IB-A001')
        self.assertEqual(data['status'], 'unknown')
        self.assertFalse(data['assemblies'][0]['ownership_conflict'])

    def test_exact_board_limits_capacity_to_the_selected_physical_profile(self):
        data = graph(project_of(cable_breakout()))
        remote = group(data, 'cx8-1', 'catalog-1')
        self.assertEqual((remote['count'], remote['occupied'], remote['free_count']), (1, 1, 0))
        self.assertEqual(len(remote['ports'][0]['interfaces']), 1)

    def test_unknown_count_keeps_occupied_cages_without_inventing_free_capacity(self):
        snapshot = copy.deepcopy(SNAPSHOT)
        next(d for d in snapshot['devices'] if d['id'] == 'profile:MQM9700-NS2F')['port_groups'][0]['count'] = None
        data = graph(project_of(cable_breakout()), snapshot)
        head = group(data, 'switch-01', 'ndr')
        self.assertEqual(head['occupied'], 1)
        self.assertIsNone(head['free_count'])
        self.assertEqual(head['free_ranges'], [])

    def test_duplicate_assignments_reserve_one_cage_and_flag_every_affected_assembly(self):
        data = graph(project_of(connections=[point_connection(), point_connection('link-2')]))
        self.assertEqual(data['summary']['occupied_cages'], 2)
        self.assertEqual(data['summary']['conflicting_cages'], 2)
        head = group(data, 'switch-point', 'ndr')
        self.assertEqual(head['free_count'], 31)
        self.assertEqual(head['ports'][0]['state'], 'conflict')
        self.assertEqual(head['ports'][0]['interfaces'], [])
        self.assertTrue(all(a['ownership_conflict'] for a in data['assemblies']))
        self.assertEqual(data['status'], 'incompatible')

    def test_out_of_range_cage_is_visible_but_does_not_consume_a_valid_free_cage(self):
        p = project_of(cable_breakout()); p.breakouts[0].head.port_number = 33
        data = graph(p); head = group(data, 'switch-01', 'ndr')
        self.assertEqual(head['free_count'], 32)
        self.assertEqual(head['ports'][0]['state'], 'out-of-range')
        self.assertTrue(data['assemblies'][0]['ownership_conflict'])

    def test_conflicting_device_identity_disables_capacity_for_that_instance(self):
        a, b = point_connection(), point_connection('link-2', 2)
        b['a']['device_id'] = b['b']['device_id']; b['a']['port_group_id'] = 'cluster'
        data = graph(project_of(connections=[a, b]))
        device = next(d for d in data['devices'] if d['id'] == 'switch-point')
        self.assertTrue(device['identity_conflict'])
        self.assertIsNone(device['free_count'])
        self.assertTrue(all(g['count'] is None for g in device['groups']))
        self.assertTrue(all(a['ownership_conflict'] for a in data['assemblies']))

    def test_missing_catalog_selection_is_still_visible_with_unknown_capacity(self):
        p = project_of(connections=[point_connection()]); p.connections[0].a.device_id = 'missing-device'
        data = graph(p)
        self.assertEqual(len(data['segments']), 2)
        self.assertIsNone(group(data, 'switch-point', 'ndr')['count'])
        self.assertEqual(data['assemblies'][0]['status'], 'unknown')

    def test_unmapped_and_duplicate_head_links_are_distinct_from_free_cages(self):
        p = project_of(cable_breakout()); p.breakouts[0].branches[1].head_links = [1]
        head = group(graph(p), 'switch-01', 'ndr')
        self.assertEqual(head['free_count'], 31)
        self.assertEqual([v['state'] for v in head['ports'][0]['interfaces']], ['conflict', 'unmapped'])

    def test_point_link_does_not_invent_logical_split_mapping(self):
        p = project_of(connections=[point_connection()]); data = graph(p)
        head = group(data, 'switch-point', 'ndr')['ports'][0]
        self.assertEqual([i['state'] for i in head['interfaces']], ['unmapped', 'unmapped'])
        p.connections[0].a.mode_id = None
        self.assertEqual(group(graph(p), 'switch-point', 'ndr')['ports'][0]['interfaces'], [])

    def test_optical_harness_retains_branch_mapping_and_separate_module_pns(self):
        snapshot, request = optical_fixture()
        data = graph(project_of(request), snapshot)
        self.assertEqual((len(data['assemblies']), len(data['segments'])), (1, 5))
        self.assertEqual(data['assemblies'][0]['part_number'], 'FIXTURE-HARNESS')
        self.assertEqual(data['segments'][0]['part_number'], '980-9I16Y-00W000')
        self.assertTrue(data['assemblies'][0]['rows'][0]['head_optical_lanes'])

    def test_large_or_zero_capacity_is_compact_and_never_expanded_in_the_api(self):
        self.assertEqual(free_ranges(10**9, [1, 3, 10**9]), [[2, 2], [4, 10**9 - 1]])
        self.assertEqual(free_ranges(0, [1]), [])
        self.assertEqual(free_ranges(None, [1]), [])

    def test_map_generation_does_not_mutate_catalog_or_project(self):
        p = installed_project(); before = p.model_dump(); snapshot = copy.deepcopy(SNAPSHOT)
        data = graph(p, snapshot)
        self.assertEqual(data['assemblies'][0]['rows'][0]['checked'], True)
        self.assertEqual(snapshot, SNAPSHOT)
        self.assertEqual(p.model_dump(), before)


if __name__ == '__main__':
    unittest.main()
