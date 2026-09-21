import copy
import json
import logging
import socket
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from pydantic import ValidationError

from app import api
from app.catalog import CatalogUnavailable, LiveCatalog, read_json_limited
from app.config import DATA_PATH, PROFILE_PATH
from app.models import CatalogDocument, ConnectionRequest, PortGroup, ProfileDocument
from app.rules import evaluate, validate_connection

RAW = json.loads(DATA_PATH.read_text())
PROFILES = json.loads(PROFILE_PATH.read_text())
SNAPSHOT = LiveCatalog(DATA_PATH, PROFILE_PATH).get()


def device(name):
    return copy.deepcopy(next(d for d in SNAPSHOT['devices'] if d['model'] == name))


def item(name):
    return copy.deepcopy(next(i for i in SNAPSHOT['interconnects'] if i['model'] == name))


def selection(model, product, end=None, pn=None):
    d, p = device(model), item(product)
    return dict(device_id=d['id'], port_group_id=d['port_groups'][0]['id'], product_id=p['id'], endpoint_id=end, part_number=pn)


def cable_request(**overrides):
    r = dict(a=selection('MQM9700-NS2F', 'MCA4J80-Nxxx-FTF', pn='980-9I601-00N003'),
             b=selection('DGX B200', 'MCA4J80-Nxxx-FTF', pn='980-9I601-00N003'),
             fabric='IB', length_m=3., revision=SNAPSHOT['revision'])
    r.update(overrides)
    return ConnectionRequest.model_validate(r)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.data, self.profiles = self.root/'catalog.json', self.root/'profiles.json'
        self.data.write_text(json.dumps(RAW)); self.profiles.write_text(json.dumps(PROFILES))
        self.catalog = LiveCatalog(self.data, self.profiles)

    def tearDown(self):
        self.temp.cleanup()

    def test_actual_json_and_nullable_pluggable(self):
        self.assertIsNone(RAW['port_interface_compatibility']['dpu']['BlueField-4 STX Storage Processor']['pluggable'])
        snapshot = self.catalog.get()
        self.assertEqual(len(snapshot['devices']), 33)
        self.assertEqual(len(snapshot['interconnects']), 76)

    def test_startup_failure_never_returns_empty_snapshot(self):
        self.data.write_text('{')
        for _ in range(3):
            with self.assertRaises(CatalogUnavailable): self.catalog.get()

    def test_reload_failure_keeps_good_revision_and_reports_degraded(self):
        before = self.catalog.get()
        self.data.write_text('{')
        after, state = self.catalog.view()
        self.assertIs(before, after)
        self.assertEqual(state['state'], 'degraded')
        self.assertEqual(state['error_code'], 'catalog_reload_rejected')
        self.assertNotIn(str(self.root), json.dumps(state))

    def test_valid_reload_recovers_and_changes_revision(self):
        old = self.catalog.get()['revision']
        self.data.write_text('{'); self.catalog.get()
        changed = copy.deepcopy(RAW); changed['notes'].append('Regression fixture')
        replacement = self.root/'new.json'; replacement.write_text(json.dumps(changed)); replacement.replace(self.data)
        snapshot, state = self.catalog.view()
        self.assertNotEqual(snapshot['revision'], old)
        self.assertEqual(state['state'], 'ready')
        self.assertIsNotNone(state['last_successful_load'])

    def test_missing_file_after_load_keeps_good_snapshot(self):
        old = self.catalog.get(); self.profiles.unlink()
        self.assertIs(self.catalog.get(), old)

    def test_limited_reader_and_duplicate_keys(self):
        self.data.write_text('x' * 12)
        with self.assertRaises(ValueError): read_json_limited(self.data, 10)
        self.data.write_text('{"x":1,"x":2}')
        with self.assertRaises(ValueError): read_json_limited(self.data, 100)

    def test_product_fields_are_typed(self):
        for field, value in [('part_numbers', {}), ('speed', 'UNKNOWN'), ('status', 'maybe'), ('interface_count', True)]:
            raw = copy.deepcopy(RAW)
            raw['linkx']['transceivers'][0][raw['linkx']['transceiver_fields'].index(field)] = value
            with self.subTest(field=field), self.assertRaises((ValidationError, ValueError)):
                CatalogDocument.model_validate(raw)

    def test_profile_semantics_and_unique_ids(self):
        profile = copy.deepcopy(PROFILES)
        profile['profiles'].append(copy.deepcopy(profile['profiles'][0]))
        with self.assertRaises(ValidationError): ProfileDocument.model_validate(profile)
        g = device('SN3420')['port_groups'][0]
        g.pop('compatibility_source')
        g['modes'].append({'id':'8x25','links':8,'speed_gbps':25})
        with self.assertRaises(ValidationError): PortGroup.model_validate(g)

    def test_unknown_schema_version_is_rejected(self):
        raw = copy.deepcopy(RAW); raw['schema_version'] = 999
        with self.assertRaises(ValidationError): CatalogDocument.model_validate(raw)

    def test_cross_file_sku_mismatch_rejects_candidate(self):
        profile = copy.deepcopy(PROFILES)
        next(iter(profile['interconnect_details'].values()))['skus'][0]['part_number'] = 'wrong-part'
        self.profiles.write_text(json.dumps(profile))
        with self.assertRaises(CatalogUnavailable): self.catalog.get()

    def test_changed_canonical_mechanics_reject_stale_endpoint_profile(self):
        raw = copy.deepcopy(RAW)
        fields = raw['linkx']['transceiver_fields']
        row = next(r for r in raw['linkx']['transceivers'] if r[fields.index('model')] == 'MMS4X00-NM')
        row[fields.index('interface_type')] = 'OSFP-flattop'
        self.data.write_text(json.dumps(raw))
        with self.assertRaises(CatalogUnavailable): self.catalog.get()

    def test_explicit_profiles_do_not_infer_adapter_cage_rate(self):
        for name in ['ConnectX-8 SuperNIC', 'ConnectX-9 SuperNIC', 'BlueField-3 DPU']:
            self.assertTrue(all(g['module_speed_gbps'] is None for g in device(name)['port_groups']))


class RulesTests(unittest.TestCase):
    def test_reversed_flat_to_finned_cable(self):
        cable = item('MCA4J80-Nxxx-FTF')
        for name, end in [('MQM9700-NS2F', 'B'), ('DGX B200', 'A')]:
            result = evaluate(device(name)['port_groups'][0], cable)
            self.assertEqual(result['endpoint_id'], end)
            self.assertEqual(result['status'], 'conditional')
            self.assertFalse(any(c['state']=='fail' for c in result['checks']))

    def test_breakout_branch_uses_400g_not_800g_assembly_rate(self):
        result = evaluate(device('DGX GB200 Compute Tray')['port_groups'][0], item('MCP7Y00-Nxxx'))
        self.assertEqual(result['endpoint_id'], 'B')
        self.assertEqual(result['endpoint_role'], 'branch')
        self.assertEqual(result['matched_modes'], ['1x400'])
        self.assertNotEqual(result['status'], 'incompatible')

    def test_single_800_is_not_twin_400(self):
        g = device('DGX B200')['port_groups'][0]
        g['modes'] = [{'id':'1x800','links':1,'speed_gbps':800}]
        result = evaluate(g, item('MMS4X00-NM-FLT'))
        self.assertEqual(result['status'], 'incompatible')
        self.assertIn('port.mode', [c['code'] for c in result['checks'] if c['state']=='fail'])

    def test_missing_fabric_and_speed_cannot_pass(self):
        p = item('MMS1V00-WM'); p['fabric_compatibility']=[]; p['speed_gbps']=None
        result = evaluate(device('SN5400')['port_groups'][0], p)
        self.assertEqual(result['status'], 'unknown')
        self.assertEqual(result['match_type'], 'exact')

    def test_mechanical_match_does_not_imply_complete_compatibility(self):
        result = evaluate(device('SN6600-LD')['port_groups'][0], item('MMS4C11'))
        self.assertEqual(result['status'], 'unknown')
        self.assertEqual(result['match_type'], 'unknown')

    def test_qm9700_profiles_agree_on_twin_capacity(self):
        for model in ['QM9700 family','MQM9700-NS2F']:
            result = evaluate(device(model)['port_groups'][0],item('MMS4X00-NM'))
            self.assertNotEqual(result['status'],'incompatible')
            self.assertIn('2x400',result['matched_modes'])

    def test_sn3420_never_fabricates_eight_lane_breakout(self):
        g=device('SN3420')['port_groups'][0]
        self.assertNotIn('8x25',[m['id'] for m in g['modes']])
        self.assertTrue(all(m['links']*m['speed_gbps']<=g['module_speed_gbps'] for m in g['modes']))

    def test_fixed_port_rejects_pluggables(self):
        result=evaluate(device('SN2201')['port_groups'][0],item('MMS1V70-CM'))
        self.assertEqual(result['status'],'incompatible')

    def test_unknown_endpoint_is_explicit_failure(self):
        result=evaluate(device('SN5400')['port_groups'][0],item('MMS1V00-WM'),endpoint_id='B')
        self.assertEqual(result['status'],'incompatible')

    def test_connection_orientation_and_missing_fec(self):
        result=validate_connection(SNAPSHOT,cable_request())
        self.assertEqual(result['orientation'],{'a':'B','b':'A'})
        self.assertEqual(result['status'],'unknown')
        self.assertTrue(any(c['code']=='A.port.fec' and c['required'] and c['state']=='unknown' for c in result['checks']))

    def test_connection_same_end_cannot_pass(self):
        r=cable_request().model_dump();r['a']['endpoint_id']='A';r['b']['endpoint_id']='A'
        result=validate_connection(SNAPSHOT,ConnectionRequest.model_validate(r))
        self.assertEqual(result['status'],'incompatible')

    def test_connection_wrong_sku_and_length_fail(self):
        for pn,length in [('not-a-real-part',3.),('980-9I601-00N003',5.)]:
            r=cable_request().model_dump();r['a']['part_number']=pn;r['length_m']=length
            with self.subTest(pn=pn,length=length):
                self.assertEqual(validate_connection(SNAPSHOT,ConnectionRequest.model_validate(r))['status'],'incompatible')

    def test_complete_electrical_fixture_can_pass(self):
        snapshot=copy.deepcopy(SNAPSHOT)
        for model in ['MQM9700-NS2F','DGX B200']:
            g=next(d for d in snapshot['devices'] if d['model']==model)['port_groups'][0]
            for m in g['modes']:
                if m['id']=='2x400':m.update(electrical_lanes=8,lane_rate_gbps=100.,fec=['fixture-fec'])
        p=next(i for i in snapshot['interconnects'] if i['model']=='MCA4J80-Nxxx-FTF')
        for e in p['endpoints']:
            for m in e['modes']:m['fec']=['fixture-fec']
        self.assertEqual(validate_connection(snapshot,cable_request())['status'],'compatible')

    def test_locally_matching_fec_must_also_agree_across_the_cable(self):
        snapshot = copy.deepcopy(SNAPSHOT)
        cable = next(p for p in snapshot['interconnects'] if p['model'] == 'MCA4J80-Nxxx-FTF')
        for model, end, fec in [('MQM9700-NS2F', 'B', 'fixture-fec-a'), ('DGX B200', 'A', 'fixture-fec-b')]:
            group = next(d for d in snapshot['devices'] if d['model'] == model)['port_groups'][0]
            for mode in group['modes']:
                if mode['id'] == '2x400': mode.update(electrical_lanes=8, lane_rate_gbps=100., fec=[fec])
            for mode in next(e for e in cable['endpoints'] if e['id'] == end)['modes']:
                mode['fec'] = [fec]
        result = validate_connection(snapshot, cable_request())
        self.assertEqual(result['status'], 'incompatible')
        self.assertIn('link.cable_fec', [c['code'] for c in result['checks'] if c['state'] == 'fail'])

    def test_best_host_modes_cannot_be_combined_into_an_impossible_link(self):
        snapshot = copy.deepcopy(SNAPSHOT)
        cable = next(p for p in snapshot['interconnects'] if p['model'] == 'MCA4J80-Nxxx-FTF')
        for end in cable['endpoints']:
            end['modes'] = [dict(id=id_, links=links, speed_gbps=rate, electrical_lanes=8,
                                 lane_rate_gbps=100., fec=['fixture-fec'])
                            for id_, links, rate in [('2x400', 2, 400), ('1x800', 1, 800)]]
        for model, supported in [('MQM9700-NS2F', '2x400'), ('DGX B200', '1x800')]:
            group = next(d for d in snapshot['devices'] if d['model'] == model)['port_groups'][0]
            group['modes'] = copy.deepcopy(cable['endpoints'][0]['modes'])
            for mode in group['modes']:
                if mode['id'] != supported: mode.update(electrical_lanes=4, lane_rate_gbps=200.)
        result = validate_connection(snapshot, cable_request())
        self.assertEqual(result['status'], 'incompatible')

    def test_optical_wrong_polish_and_shorter_fiber_reach(self):
        r=dict(a=selection('SN5400','MMS1V00-WM',pn='980-9I16Y-00W000'),
               b=selection('SN5400','MMS1V00-WM',pn='980-9I16Y-00W000'),fabric='ETH',length_m=501.,
               fiber=dict(medium='SM',fiber_type='OS2',connector_a='MPO-12/UPC',connector_b='MPO-12/APC',pinout_verified=True))
        result=validate_connection(SNAPSHOT,ConnectionRequest.model_validate(r))
        fails={c['code'] for c in result['checks'] if c['state']=='fail'}
        self.assertIn('A.optical_connector',fails);self.assertIn('A.reach',fails)


class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import uvicorn
        cls.temp=tempfile.TemporaryDirectory();root=Path(cls.temp.name)
        cls.data=root/'catalog.json';cls.profile=root/'profiles.json'
        cls.data.write_text(json.dumps(RAW));cls.profile.write_text(json.dumps(PROFILES))
        cls.original=api.catalog;api.catalog=LiveCatalog(cls.data,cls.profile)
        cls.sock=socket.socket();cls.sock.bind(('127.0.0.1',0));cls.port=cls.sock.getsockname()[1]
        cls.server=uvicorn.Server(uvicorn.Config(api.app,log_level='critical',lifespan='off'))
        cls.thread=threading.Thread(target=cls.server.run,kwargs={'sockets':[cls.sock]},daemon=True);cls.thread.start()
        deadline=time.monotonic()+5
        while not cls.server.started and time.monotonic()<deadline:time.sleep(.01)
        if not cls.server.started:raise RuntimeError('HTTP test server failed to start')

    @classmethod
    def tearDownClass(cls):
        cls.server.should_exit=True;cls.thread.join(5);api.catalog=cls.original;cls.temp.cleanup()

    def request(self,path,body=None):
        req=urllib.request.Request(f'http://127.0.0.1:{self.port}'+path,data=body,headers={'Content-Type':'application/json'})
        try:resp=urllib.request.urlopen(req,timeout=5)
        except urllib.error.HTTPError as exc:resp=exc
        with resp:return resp.status,dict(resp.headers),resp.read()

    def test_real_http_health_devices_and_bundle(self):
        code,_,body=self.request('/healthz');self.assertEqual(code,200);self.assertEqual(json.loads(body),{'status':'ok'})
        code,headers,body=self.request('/api/devices');self.assertEqual(code,200);self.assertEqual(len(json.loads(body)),33)
        self.assertIn('x-catalog-revision', {k.lower():v for k,v in headers.items()})
        code,_,body=self.request('/api/catalog');bundle=json.loads(body)
        self.assertEqual(code,200);self.assertEqual(bundle['meta']['catalog']['state'],'ready')
        self.assertNotIn('data_path',body.decode())

    def test_evaluation_has_rejected_products_and_revision(self):
        query=urllib.parse.urlencode({'device_id':'profile:MQM9700-NS2F','port_group_id':'ndr'})
        code,_,body=self.request('/api/evaluate?'+query);result=json.loads(body)
        self.assertEqual(code,200);self.assertTrue(result['revision'])
        self.assertTrue(any(p['validation']['status']=='incompatible' for p in result['products']))

    def test_invalid_id_fabric_and_revision(self):
        cases=[({'device_id':'missing','port_group_id':'x'},404),({'device_id':'x'*129,'port_group_id':'x'},422),
               ({'device_id':'profile:MQM9700-NS2F','port_group_id':'ndr','fabric':'BAD'},422),
               ({'device_id':'profile:MQM9700-NS2F','port_group_id':'ndr','revision':'000000000000'},409)]
        for query,expected in cases:
            with self.subTest(query=query):self.assertEqual(self.request('/api/evaluate?'+urllib.parse.urlencode(query))[0],expected)

    def test_connection_and_request_size_limit(self):
        r=cable_request().model_dump();r['revision']=api.catalog.get()['revision']
        code,_,body=self.request('/api/connection',json.dumps(r).encode());result=json.loads(body)
        self.assertEqual(code,200);self.assertEqual(result['orientation'],{'a':'B','b':'A'})
        self.assertEqual(self.request('/api/connection',b'x'*17000)[0],413)
        self.assertEqual(self.request('/api/connection',b'{}')[0],422)

    def test_missing_catalog_returns_503_on_every_route(self):
        previous=api.catalog;api.catalog=LiveCatalog(Path(self.temp.name)/'absent',self.profile)
        try:
            for path in ['/api/meta','/healthz','/api/devices','/api/meta']:
                code,_,body=self.request(path);self.assertEqual(code,503);self.assertEqual(json.loads(body),{'detail':'Service unavailable'})
        finally:api.catalog=previous

    def test_static_scripts_and_csp(self):
        code,headers,body=self.request('/');self.assertEqual(code,200)
        normalized={k.lower():v for k,v in headers.items()}
        self.assertNotIn('unsafe-inline',normalized['content-security-policy'])
        self.assertNotIn(b'<style>',body)
        for path in ['/static/app.js','/static/core.js','/static/styles.css']:
            self.assertEqual(self.request(path)[0],200)


if __name__=='__main__':
    logging.disable(logging.CRITICAL)
    unittest.main()
