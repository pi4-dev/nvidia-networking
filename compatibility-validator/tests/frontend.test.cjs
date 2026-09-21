const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');
const core = require('../app/static/core.js');
const html = fs.readFileSync(path.join(__dirname, '../app/static/index.html'), 'utf8');
const script = fs.readFileSync(path.join(__dirname, '../app/static/app.js'), 'utf8');
const coreScript = fs.readFileSync(path.join(__dirname, '../app/static/core.js'), 'utf8');
const r1 = '111111111111', r2 = '222222222222';
const tick = () => new Promise(resolve => setImmediate(resolve));
async function settle() { for (let i = 0; i < 8; i++) await tick(); }
function product(id) { return { id, model: 'Product ' + id, variant: null, category: 'Copper', cable_type: 'DAC', status: 'active', part_numbers: ['PN-' + id], skus: [{part_number:'PN-'+id,length_m:3}], medium:'Copper', reach:{max_m:3}, fabric_compatibility:['IB'], endpoints:[{id:'A',role:'peer',interface_type:'OSFP-finned',count:1,modes:[{id:'2x400',links:2,speed_gbps:400}]}] }; }
function device(id) { return {id,model:id,kind:'Switch',family:'Fixture',source:'test',validation_ready:true,port_groups:[{id:'g',label:'Group '+id,connector_family:'OSFP',module_speed_gbps:800,accepted_interface_types:['OSFP-finned'],fabrics:['IB'],modes:[{id:'2x400',links:2,speed_gbps:400}]}]}; }
function evaluated(id) { return {...product(id),validation:{status:'conditional',match_type:'exact',endpoint_id:'A',endpoint_role:'peer',matched_modes:['2x400'],checks:[{code:'test',state:'unknown',message:'Test condition',required:false}],alternatives:[{endpoint_id:'A',status:'conditional'}]}}; }
function bundle(revision=r1) { return {meta:{revision,snapshot_date:'2026-09-17',device_count:2,interconnect_count:2,catalog:{state:'ready',last_successful_load:'2026-09-21T00:00:00Z'}},devices:[device('A'),device('B')],products:[product('A'),product('B')]}; }
function response(data,status=200){return {ok:status<400,status,json:async()=>data};}
function harness(handler, options={}) {
  let copied, exported;
  const dom=new JSDOM(html,{url:options.url||'http://localhost/',runScripts:'outside-only'});
  const w=dom.window;
  if(options.saved)w.localStorage.setItem('nvidia-validator-v1',JSON.stringify(options.saved));
  w.fetch=handler;
  w.Blob=Blob;
  w.URL.createObjectURL=blob=>{exported=blob;return 'blob:test';};w.URL.revokeObjectURL=()=>{};
  w.HTMLAnchorElement.prototype.click=function(){};
  Object.defineProperty(w.navigator,'clipboard',{value:{writeText:async value=>{copied=value;}}});
  w.eval(coreScript);w.eval(script);
  return {dom,w,get copied(){return copied;},get exported(){return exported;},close(){dom.window.close();}};
}
function apiHandler(revision=()=>r1) { return async(url)=>{
  if(url==='/api/catalog')return response(bundle(revision()));
  if(url==='/api/meta')return response(bundle(revision()).meta);
  const q=new URL(url,'http://localhost').searchParams;
  return response({revision:revision(),device_id:q.get('device_id'),port_group_id:q.get('port_group_id'),products:[evaluated(q.get('device_id'))]});
};}
function change(h,id,value){const e=h.w.document.getElementById(id);e.value=value;e.dispatchEvent(new h.w.Event('change'));}
function click(h,id){h.w.document.getElementById(id).click();}

test('late response for device A cannot overwrite device B, even if fetch ignores abort',async()=>{
  const pending=[];
  const h=harness(async url=>url==='/api/catalog'?response(bundle()):new Promise(resolve=>pending.push({url,resolve})));
  try{
    await settle();assert.equal(pending.length,1);
    change(h,'device','B');await settle();assert.equal(pending.length,2);
    pending[1].resolve(response({revision:r1,device_id:'B',port_group_id:'g',products:[evaluated('B')]}));await settle();
    pending[0].resolve(response({revision:r1,device_id:'A',port_group_id:'g',products:[evaluated('A')]}));await settle();
    const wrap=h.w.document.getElementById('compatibleWrap');
    assert.match(wrap.textContent,/Product B/);assert.doesNotMatch(wrap.textContent,/Product A/);
    wrap.querySelector('button').click();assert.match(h.w.document.getElementById('validationText').textContent,/Product B/);
  }finally{h.close();}
});

test('catalog reload preserves device, group, mode, product, filters and PN',async()=>{
  let revision=r1;
  const h=harness(apiHandler(()=>revision),{url:'http://localhost/?device=B&group=g&mode=2x400&product=B&partNumber=PN-B&search=Product'});
  try{
    await settle();assert.equal(h.w.document.getElementById('partNumber').value,'PN-B');
    revision=r2;click(h,'retry');await settle();
    for(const [id,value] of [['device','B'],['group','g'],['mode','2x400'],['partNumber','PN-B'],['search','Product']])assert.equal(h.w.document.getElementById(id).value,value);
    assert.match(h.w.document.getElementById('validationText').textContent,/Product B/);
    click(h,'export');const report=JSON.parse(await h.exported.text());assert.equal(report.catalog.revision,r2);assert.equal(report.result.id,'B');
  }finally{h.close();}
});

test('saved configuration is not overwritten during startup',async()=>{
  const h=harness(apiHandler(),{saved:{device:'B',group:'g',mode:'2x400',product:'B',partNumber:'PN-B'}});
  try{await settle();assert.equal(h.w.document.getElementById('device').value,'B');assert.equal(h.w.document.getElementById('partNumber').value,'PN-B');}
  finally{h.close();}
});

test('share and export include the exact revision and selected ordering number',async()=>{
  const h=harness(apiHandler(),{url:'http://localhost/?device=A&group=g&product=A&partNumber=PN-A'});
  try{
    await settle();click(h,'share');await settle();const q=new URL(h.copied).searchParams;
    assert.equal(q.get('revision'),r1);assert.equal(q.get('partNumber'),'PN-A');
    click(h,'export');const report=JSON.parse(await h.exported.text());assert.equal(report.configuration.partNumber,'PN-A');assert.equal(report.result.validation.status,'conditional');
  }finally{h.close();}
});

test('startup API error is visible and Refresh recovers without reloading the page',async()=>{
  let fail=true;const real=apiHandler();
  const h=harness(async url=>{if(fail)throw new Error('Service unavailable');return real(url);});
  try{
    await settle();assert.match(h.w.document.getElementById('meta').textContent,/OFFLINE/);
    fail=false;click(h,'retry');await settle();assert.match(h.w.document.getElementById('meta').textContent,/CONNECTED/);
  }finally{h.close();}
});

test('a result from another catalog revision is never displayed',async()=>{
  const h=harness(async url=>url==='/api/catalog'?response(bundle()):response({revision:r2,device_id:'A',port_group_id:'g',products:[evaluated('A')]}));
  try{await settle();assert.doesNotMatch(h.w.document.getElementById('compatibleWrap').textContent,/Product A/);assert.equal(h.w.document.getElementById('export').disabled,true);}
  finally{h.close();}
});

test('changing a connection invalidates an in-flight POST result',async()=>{
  let resolveLink;const real=apiHandler();
  const h=harness(async url=>url==='/api/connection'?new Promise(resolve=>{resolveLink=resolve;}):real(url));
  try{
    await settle();click(h,'linkTab');click(h,'validateLink');await settle();
    assert.equal(typeof resolveLink,'function');change(h,'bDevice','B');
    resolveLink(response({revision:r1,status:'compatible',orientation:{a:'A',b:'B'},checks:[]}));await settle();
    assert.doesNotMatch(h.w.document.getElementById('linkStatus').textContent,/compatible/);
    assert.equal(h.w.document.getElementById('export').disabled,true);
  }finally{h.close();}
});

test('fiber connector changes and catalog revisions clear the pinout confirmation',async()=>{
  let revision=r1;
  const h=harness(apiHandler(()=>revision),{url:'http://localhost/?pinout=1&revision='+r1});
  try{
    await settle();const pinout=h.w.document.getElementById('pinout');assert.equal(pinout.checked,true);
    change(h,'connectorA','MPO-12/UPC');assert.equal(pinout.checked,false);
    pinout.checked=true;revision=r2;click(h,'retry');await settle();assert.equal(pinout.checked,false);
  }finally{h.close();}
});

test('missing reach remains visible; known insufficient reach is excluded',()=>{
  const unknown=evaluated('A');unknown.reach=null;unknown.skus=[{part_number:'x',length_m:null}];
  const short=evaluated('B');
  const f={outcome:'all',lifecycle:'active',reach:'10'};
  assert.deepEqual(core.filteredProducts([unknown,short],f).map(p=>p.id),['A']);
});

test('unknown and retired products are available for rejection diagnostics',()=>{
  const retired=evaluated('A');retired.status='no_longer_for_sale';retired.validation.status='unknown';
  assert.equal(core.filteredProducts([retired],{outcome:'all',lifecycle:'all',search:'PN-A'}).length,1);
  assert.equal(core.filteredProducts([retired],{outcome:'all',lifecycle:'active'}).length,0);
});

test('catalog text and source URLs cannot inject script markup',()=>{
  assert.equal(core.sourceLink('javascript:alert(1)'),'—');
  assert.doesNotMatch(core.esc('<img onerror="alert(1)">'),/<img/);
  assert.equal(core.statusClass('" onclick="alert(1)'), 'warn');
});

function input(h,id,value){const e=h.w.document.getElementById(id);e.value=value;e.dispatchEvent(new h.w.Event('input'));}
function hardwareBundle(){const b=bundle();b.hardware_profiles=[{id:'board-A',device_id:'A',label:'Exact board A',identity:{},ports:[{port_group_id:'g',module_speed_gbps:800,modes:[{id:'exact-2x400',links:2,speed_gbps:400,fabrics:['IB']}]}]}];return b;}
function inspection(){return {revision:r1,profile:{label:'Exact board A',notes:[]},facts:[{field:'opn',value:'board-A',evidence:{kind:'manufacturer',verified_on:'2026-09-21',scope:'Only this board <img onerror="bad()">',source_url:'https://example.com/manual'}}],checks:[],gaps:[{code:'firmware',message:'Firmware qualification missing',action:'Read installed firmware and add a scoped report.'}]};}
function proposal(){
  const host=id=>({device_id:id,port_group_id:'g',mode_id:'2x400',hardware_profile_id:null,runtime:{},product_id:'A',endpoint_id:'A',part_number:'PN-A'});
  const validation={status:'unknown',technical_status:'conditional',orientation:{a:'A',b:'A'},checks:[],gaps:[{message:'FEC is unknown',action:'Verify FEC on both hosts.'}],qualification:{a:{status:'unknown',records:[]},b:{status:'unknown',records:[]}}};
  return {revision:r1,scope:'single-link',total_candidates:1,examined:1,truncated:false,notes:['One link only.'],candidates:[{technology:'DAC',components:[{side:'both',role:'cable',model:'Cable A',part_number:'PN-A',source_url:'https://example.com/sku'}],component_count:1,ordering_complete:true,length_m:3,reused_count:1,inventory:[{part_number:'PN-A',required:1,reused:1,to_buy:0}],evidence_summary:{passed_checks:4,unknown_checks:1},settings:{a:{id:'2x400',links:2,speed_gbps:400},b:{id:'2x400',links:2,speed_gbps:400}},connection:{a:host('A'),b:host('B'),fabric:'IB',length_m:3,fiber:null,fiber_part_number:null,revision:r1},validation}]};
}

test('exact hardware modes and runtime survive refresh, share and scoped POST',async()=>{
  const posted=[];
  const h=harness(async(url,options)=>{
    if(url==='/api/catalog')return response(hardwareBundle());
    if(url==='/api/evaluate'){
      const body=JSON.parse(options.body);posted.push(body);
      return response({revision:r1,device_id:'A',port_group_id:'g',products:[evaluated('A')],hardware:inspection()});
    }
    return apiHandler()(url);
  });
  try{
    await settle();change(h,'portProfile','board-A');await settle();
    change(h,'mode','exact-2x400');input(h,'portFirmware','2.10');await settle();
    assert.equal(posted.at(-1).runtime.firmware,'2.10');assert.equal(posted.at(-1).mode_id,'exact-2x400');
    click(h,'retry');await settle();assert.equal(h.w.document.getElementById('portProfile').value,'board-A');
    assert.equal(h.w.document.getElementById('mode').value,'exact-2x400');assert.equal(h.w.document.getElementById('portFirmware').value,'2.10');
    click(h,'share');await settle();const q=new URL(h.copied).searchParams;
    assert.equal(q.get('portProfile'),'board-A');assert.equal(q.get('portFirmware'),'2.10');
    change(h,'device','B');await settle();assert.equal(h.w.document.getElementById('portFirmware').value,'');
    assert.equal(h.w.document.getElementById('portProfile').value,'');
  }finally{h.close();}
});

test('hardware inspection exposes dated sources, actionable gaps and exports safely',async()=>{
  const h=harness(async(url,options)=>url==='/api/hardware/inspect'?response(inspection()):apiHandler()(url));
  try{
    await settle();click(h,'inspectHardware');await settle();
    const report=h.w.document.getElementById('hardwareReport');
    assert.match(report.textContent,/2026-09-21/);assert.match(report.textContent,/Read installed firmware/);
    assert.equal(report.querySelector('img'),null);
    click(h,'export');const json=JSON.parse(await h.exported.text());assert.equal(json.hardware_report.profile.label,'Exact board A');
  }finally{h.close();}
});

test('assistant compares parts and opens the exact proposed connection',async()=>{
  let requested,connection;
  const h=harness(async(url,options)=>{
    if(url==='/api/recommendations'){requested=JSON.parse(options.body);return response(proposal());}
    if(url==='/api/connection'){connection=JSON.parse(options.body);return response({...proposal().candidates[0].validation,revision:r1});}
    return apiHandler()(url);
  });
  try{
    await settle();click(h,'wizardTab');input(h,'ownedParts','PN-A,1');input(h,'reusePn','PN-A');click(h,'recommend');await settle();
    assert.deepEqual(requested.owned_parts,[{part_number:'PN-A',quantity:1}]);assert.equal(requested.speed_gbps,400);
    assert.match(h.w.document.getElementById('wizardResults').textContent,/need 1, reuse 1, buy 0/);
    click(h,'export');const report=JSON.parse(await h.exported.text());assert.equal(report.scope,'connection-recommendations');
    h.w.document.querySelector('[data-proposal]').click();await settle();
    assert.equal(connection.a.part_number,'PN-A');assert.equal(connection.b.device_id,'B');assert.equal(connection.length_m,3);
    assert.equal(h.w.document.getElementById('linkView').classList.contains('hidden'),false);
  }finally{h.close();}
});

test('changing assistant requirements invalidates an in-flight result',async()=>{
  let resolve;
  const h=harness(async url=>url==='/api/recommendations'?new Promise(done=>{resolve=done;}):apiHandler()(url));
  try{
    await settle();click(h,'wizardTab');click(h,'recommend');await settle();
    input(h,'wizardLength','10');resolve(response(proposal()));await settle();
    assert.equal(h.w.document.getElementById('wizardResults').textContent,'');
    assert.equal(h.w.document.getElementById('export').disabled,true);
  }finally{h.close();}
});

test('assistant rejects another revision and malformed inventory, with a visible error',async()=>{
  let calls=0;
  const h=harness(async url=>{if(url==='/api/recommendations'){calls++;return response({...proposal(),revision:r2});}return apiHandler()(url);});
  try{
    await settle();click(h,'wizardTab');click(h,'recommend');await settle();
    assert.match(h.w.document.getElementById('wizardStatus').textContent,/Catalog changed/);
    assert.equal(h.w.document.getElementById('wizardResults').textContent,'');
    input(h,'ownedParts','PN-A,-2');click(h,'recommend');await settle();
    assert.match(h.w.document.getElementById('wizardStatus').textContent,/Inventory format/);assert.equal(calls,1);
  }finally{h.close();}
});

test('assistant constraints and inventory restore from a shared URL',async()=>{
  const h=harness(apiHandler(),{url:'http://localhost/?view=wizard&waDevice=B&waGroup=g&waMode=2x400&wizardLength=10&wizardSpeed=200&ownedParts=PN-A%2C2&includeUnknown=0'});
  try{
    await settle();assert.equal(h.w.document.getElementById('wizardView').classList.contains('hidden'),false);
    assert.equal(h.w.document.getElementById('waDevice').value,'B');assert.equal(h.w.document.getElementById('wizardLength').value,'10');
    assert.equal(h.w.document.getElementById('includeUnknown').checked,false);
    click(h,'share');await settle();const q=new URL(h.copied).searchParams;
    assert.equal(q.get('ownedParts'),'PN-A,2');assert.equal(q.get('wizardSpeed'),'200');
  }finally{h.close();}
});
