const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');
const core = require('../app/static/core.js');
const html = fs.readFileSync(path.join(__dirname, '../app/static/index.html'), 'utf8');
const script = fs.readFileSync(path.join(__dirname, '../app/static/app.js'), 'utf8');
const coreScript = fs.readFileSync(path.join(__dirname, '../app/static/core.js'), 'utf8');
const topologyScript = fs.readFileSync(path.join(__dirname, '../app/static/topology.js'), 'utf8');
const mapScript = fs.readFileSync(path.join(__dirname, '../app/static/project-map.js'), 'utf8');
const cablingScript = fs.readFileSync(path.join(__dirname, '../app/static/cabling.js'), 'utf8');
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
  w.eval(coreScript);w.eval(cablingScript);w.eval(mapScript);w.eval(topologyScript);w.eval(script);
  return {dom,w,get copied(){return copied;},get exported(){return exported;},close(){dom.window.close();}};
}
function apiHandler(revision=()=>r1) { return async(url)=>{
  if(url==='/api/catalog')return response(bundle(revision()));
  if(url==='/api/meta')return response(bundle(revision()).meta);
  const q=new URL(url,'http://localhost').searchParams;
  return response({revision:revision(),device_id:q.get('device_id'),port_group_id:q.get('port_group_id'),products:[evaluated(q.get('device_id'))]});
};}
function change(h,id,value){const e=h.w.document.getElementById(id);e.value=value;e.dispatchEvent(new h.w.Event('change',{bubbles:true}));}
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

function input(h,id,value){const e=h.w.document.getElementById(id);e.value=value;e.dispatchEvent(new h.w.Event('input',{bubbles:true}));}
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

function breakoutDraft(){
  const host=(instance,device,mode)=>({instance_id:instance,device_id:device,port_group_id:'g',port_number:1,mode_id:mode,hardware_profile_id:null,runtime:{},product_id:'fan',part_number:'PN-fan',endpoint_id:device==='A'?'A':'B'});
  return {topology:'cable',head:host('head-01','A','2x400'),branches:[1,2].map(i=>({id:'branch-'+i,termination:i,head_links:[i],head_optical_port:1,head_optical_lanes:[],branch_optical_lanes:[],interop_evidence:null,selection:host('remote-'+i,'B','1x400')})),fabric:'IB',length_m:3,mapping_verified:false,optical_fanout:null,revision:r1};
}
function breakoutResponse(request=breakoutDraft(),revision=r1){return {revision,scope:'complete-breakout',status:'unknown',assigned_branches:2,expected_branches:2,common_fec:[],checks:[{code:'breakout.mapping',state:'unknown',message:'Verify the complete mapping',required:true}],gaps:[],selection:request,branches:request.branches.map(b=>({...b,validation:{status:'unknown',checks:[],gaps:[]}}))};}
function projectDraft(){return {format:'nvidia-connection-project-v1',name:'Test project',revision:r1,connections:[],breakouts:[{...breakoutDraft(),id:'fanout-1'}],owned_parts:[]};}
function projectResponse(request=projectDraft(),revision=r1){return {revision,scope:'connection-project',name:request.name,status:'unknown',summary:{connections:request.connections.length,breakouts:request.breakouts.length,device_instances:3,physical_cages:3},checks:[],gaps:[],results:[...request.connections.map(c=>({id:c.id,type:'connection',status:'unknown',validation:{checks:[],gaps:[]}})),...request.breakouts.map(b=>({id:b.id,type:'breakout',status:'unknown',validation:{checks:[],gaps:[]}}))],bom:{rows:[{part_number:'PN-fan',model:'Fanout cable',roles:['cable'],required:1,owned:1,reused:1,to_buy:0,verified_ordering:true,references:['fanout-1'],source_urls:[]}],total_components:1,reused:1,to_buy:0,ordering_complete:true,provisional:true,unused_inventory:[]},project:request,notes:['Whole project inventory.']};}
function topologyBundle(revision=r1){const b=bundle(revision);b.devices[1].port_groups[0].modes=[{id:'1x400',links:1,speed_gbps:400}];const p=product('fan');p.endpoints=[{id:'A',role:'head',count:1,interface_type:'OSFP-finned',modes:[{id:'2x400',links:2,speed_gbps:400}]},{id:'B',role:'branch',count:2,interface_type:'OSFP-flattop',modes:[{id:'1x400',links:1,speed_gbps:400}]}];b.products.push(p);return b;}
function loadBreakout(h){input(h,'breakoutDocument',JSON.stringify(breakoutDraft()));click(h,'applyBreakoutJSON');}
function loadProject(h,value=projectDraft()){input(h,'projectDocument',JSON.stringify(value));click(h,'applyProjectJSON');}

test('complete breakout submits explicit modes and every physical branch, then adds one project entry',async()=>{
  let posted;
  const h=harness(async(url,opts)=>{
    if(url==='/api/catalog')return response(topologyBundle());
    if(url==='/api/breakout'){posted=JSON.parse(opts.body);return response(breakoutResponse(posted));}
    return apiHandler()(url);
  });
  try{
    await settle();click(h,'breakoutTab');loadBreakout(h);h.w.document.getElementById('breakoutMapping').click();
    click(h,'validateBreakout');await settle();
    assert.equal(posted.head.mode_id,'2x400');assert.equal(posted.branches.length,2);assert.equal(posted.mapping_verified,true);
    assert.equal(posted.branches[1].selection.instance_id,'remote-2');assert.deepEqual(posted.branches[1].head_links,[2]);
    assert.match(h.w.document.getElementById('breakoutStatus').textContent,/2 \/ 2/);
    click(h,'addBreakoutToProject');click(h,'projectTab');click(h,'downloadProjectJSON');
    const exported=JSON.parse(await h.exported.text());assert.equal(exported.breakouts.length,1);assert.equal(exported.connections.length,0);
    assert.equal(exported.breakouts[0].branches.length,2);
  }finally{h.close();}
});

test('editing a branch clears mapping confirmation and rejects an old breakout response',async()=>{
  let resolve;
  const h=harness(async url=>url==='/api/catalog'?response(topologyBundle()):url==='/api/breakout'?new Promise(done=>{resolve=done;}):apiHandler()(url));
  try{
    await settle();click(h,'breakoutTab');loadBreakout(h);h.w.document.getElementById('breakoutMapping').click();click(h,'validateBreakout');await settle();
    input(h,'top-b0-port_number','2');assert.equal(h.w.document.getElementById('breakoutMapping').checked,false);
    resolve(response(breakoutResponse()));await settle();assert.equal(h.w.document.getElementById('breakoutResult').textContent,'');
    assert.equal(h.w.document.getElementById('addBreakoutToProject').disabled,true);assert.equal(h.w.document.getElementById('export').disabled,true);
  }finally{h.close();}
});

test('project input, aggregate BOM display and full report export preserve the document',async()=>{
  let posted;
  const h=harness(async(url,opts)=>{
    if(url==='/api/project'){posted=JSON.parse(opts.body);return response(projectResponse(posted));}
    return apiHandler()(url);
  });
  try{
    await settle();click(h,'projectTab');loadProject(h);input(h,'projectInventory','PN-fan,1');click(h,'validateProject');await settle();
    assert.deepEqual(posted.owned_parts,[{part_number:'PN-fan',quantity:1}]);assert.equal(posted.breakouts[0].branches.length,2);
    assert.match(h.w.document.getElementById('projectReport').textContent,/1 physical components · 1 reused · 0 to buy/);
    click(h,'export');const report=JSON.parse(await h.exported.text());assert.equal(report.scope,'connection-project');assert.equal(report.project.breakouts.length,1);
    assert.equal(report.result.revision,r1);assert.equal(h.w.document.getElementById('share').disabled,true);
  }finally{h.close();}
});

test('project edits and unapplied JSON invalidate pending validations and cannot export stale BOM',async()=>{
  let resolve;
  const h=harness(async url=>url==='/api/project'?new Promise(done=>{resolve=done;}):apiHandler()(url));
  try{
    await settle();click(h,'projectTab');loadProject(h);click(h,'validateProject');await settle();
    input(h,'projectDocument','{ invalid edits');resolve(response(projectResponse()));await settle();
    assert.equal(h.w.document.getElementById('projectReport').textContent,'');assert.equal(h.w.document.getElementById('downloadBom').disabled,true);
    click(h,'downloadProjectJSON');assert.match(h.w.document.getElementById('projectStatus').textContent,/pending project JSON/);
    assert.equal(h.exported,undefined);
  }finally{h.close();}
});

test('old project revisions clear nested mapping and pinout confirmations before revalidation',async()=>{
  const h=harness(apiHandler());
  try{
    await settle();const p=projectDraft();p.revision=r2;p.breakouts[0].mapping_verified=true;
    loadProject(h,p);click(h,'downloadProjectJSON');const exported=JSON.parse(await h.exported.text());
    assert.equal(exported.revision,r1);assert.equal(exported.breakouts[0].mapping_verified,false);
    assert.match(h.w.document.getElementById('projectNotice').textContent,/confirmations were cleared/);
  }finally{h.close();}
});

test('malformed JSON imports preserve the preceding valid project',async()=>{
  const h=harness(apiHandler());
  try{
    await settle();loadProject(h);input(h,'projectDocument',JSON.stringify({...projectDraft(),connections:[null]}));click(h,'applyProjectJSON');
    assert.match(h.w.document.getElementById('projectStatus').textContent,/endpoint selections/);
    const saved=JSON.parse(h.w.localStorage.getItem('nvidia-project-v1'));assert.equal(saved.breakouts.length,1);assert.equal(saved.connections.length,0);
  }finally{h.close();}
});

test('catalog refresh preserves unapplied topology JSON edits and invalid inventory text',async()=>{
  const h=harness(apiHandler());
  try{
    await settle();loadProject(h);loadBreakout(h);
    input(h,'projectInventory','PN-fan,invalid');
    input(h,'projectDocument','{ project work in progress');input(h,'breakoutDocument','{ breakout work in progress');
    h.w.ValidatorTopology.setCatalog(topologyBundle(r2));
    assert.equal(h.w.document.getElementById('projectDocument').value,'{ project work in progress');
    assert.equal(h.w.document.getElementById('breakoutDocument').value,'{ breakout work in progress');
    assert.equal(h.w.document.getElementById('projectInventory').value,'PN-fan,invalid');
    click(h,'downloadProjectJSON');assert.match(h.w.document.getElementById('projectStatus').textContent,/pending project JSON/);
    click(h,'downloadBreakout');assert.match(h.w.document.getElementById('breakoutStatus').textContent,/edited JSON/);
    assert.equal(h.exported,undefined);
  }finally{h.close();}
});

test('breakout import without a catalog revision requires fresh mapping confirmation',async()=>{
  const h=harness(apiHandler());
  try{
    await settle();const b=breakoutDraft();delete b.revision;b.mapping_verified=true;
    input(h,'breakoutDocument',JSON.stringify(b));click(h,'applyBreakoutJSON');click(h,'downloadBreakout');
    const exported=JSON.parse(await h.exported.text());assert.equal(exported.mapping_verified,false);assert.equal(exported.revision,r1);
  }finally{h.close();}
});

test('a late CSV import cannot overwrite a project edited while importing',async()=>{
  let resolveImport;
  const h=harness(async url=>url==='/api/project/import-csv'?new Promise(done=>{resolveImport=done;}):apiHandler()(url));
  try{
    await settle();loadProject(h);
    const element=h.w.document.getElementById('projectImport');
    Object.defineProperty(element,'files',{value:[{name:'links.csv',size:100,text:async()=> 'id,fabric\nlink-1,IB'}],configurable:true});
    element.dispatchEvent(new h.w.Event('change'));await settle();
    input(h,'projectName','Edited while importing');resolveImport(response({revision:r1,project:{...projectDraft(),name:'Stale CSV'}}));await settle();
    assert.equal(h.w.document.getElementById('projectName').value,'Edited while importing');
  }finally{h.close();}
});

test('physical identifiers and port ordinals are included when adding an A-to-B result to the project',async()=>{
  const h=harness(async(url,options)=>url==='/api/connection'?response({...proposal().candidates[0].validation,revision:r1}):apiHandler()(url));
  try{
    await settle();click(h,'linkTab');click(h,'validateLink');await settle();
    input(h,'projectAInstance','leaf-01');input(h,'projectAPort','4');input(h,'projectBInstance','dgx-02');input(h,'projectBPort','2');
    click(h,'addConnectionToProject');click(h,'downloadProjectJSON');const p=JSON.parse(await h.exported.text());
    assert.equal(p.connections[0].a.instance_id,'leaf-01');assert.equal(p.connections[0].a.port_number,4);
    assert.equal(p.connections[0].b.instance_id,'dgx-02');assert.equal(p.connections[0].b.port_number,2);
  }finally{h.close();}
});

function cablingResponse(project){
  const value=project.breakouts[0], meta=project.cabling||{locations:[],port_labels:[],cables:[]};
  const settings=meta.cables.find(c=>c.entry_id===value.id), id=settings?.cable_id||'C-'+value.id;
  const end=s=>({...s,model:s.device_id,rack:meta.locations.find(l=>l.instance_id===s.instance_id)?.rack||null,rack_u:null,port_label:meta.port_labels.find(p=>p.instance_id===s.instance_id)?.label||null,optical_port:null});
  const a=end(value.head), bs=value.branches.map(b=>end(b.selection));
  const rows=value.branches.map((b,i)=>{const p=settings?.progress.find(v=>v.branch_id===b.id)||{};return {entry_id:value.id,branch_id:b.id,termination:b.termination,cable_id:id,part_number:'PN-fan',length_m:3,fabric:'IB',source:a,destination:bs[i],definition:'a'.repeat(64),installed:!!p.installed,checked:!!p.checked,notes:p.notes||'',progress_stale:false};});
  const labels=[{label_id:id+'/H',cable_id:id,end:'H',local:a,peers:bs,part_number:'PN-fan'},...bs.map((b,i)=>({label_id:id+'/BR-'+value.branches[i].id,cable_id:id,end:'BR-'+value.branches[i].id,local:b,peers:[a],part_number:'PN-fan'}))];
  return {revision:r1,status:'unknown',provisional:true,summary:{cables:1,legs:2,labels:3,installed:rows.filter(r=>r.installed).length,checked:rows.filter(r=>r.checked).length},rows,labels,issues:[]};
}
function enter(h,selector,value){const element=h.w.document.querySelector(selector);element.value=value;element.dispatchEvent(new h.w.Event('input',{bubbles:true}));}

test('cabling editor persists rack, native port and unique cable ID in requests and project JSON',async()=>{
  let posted;
  const h=harness(async(url,opts)=>{if(url==='/api/project/cabling'){posted=JSON.parse(opts.body);return response(cablingResponse(posted));}return apiHandler()(url);});
  try{
    await settle();loadProject(h);
    enter(h,'[data-location="head-01"][data-field="rack"]','Poznań A');
    enter(h,'[data-location="head-01"][data-field="rack_u"]','12');
    enter(h,'[data-port-index="0"]','1/1');enter(h,'[data-cable="fanout-1"]','IB-A001');
    click(h,'buildCabling');await settle();
    assert.equal(posted.cabling.locations[0].rack,'Poznań A');assert.equal(posted.cabling.locations[0].rack_u,12);
    assert.equal(posted.cabling.port_labels[0].label,'1/1');assert.equal(posted.cabling.cables[0].cable_id,'IB-A001');
    assert.equal(h.w.document.querySelectorAll('.label-preview article').length,3);
    assert.match(h.w.document.getElementById('cablingStatus').textContent,/1 cables · 2 legs · 3 end labels/);
    click(h,'downloadProjectJSON');const exported=JSON.parse(await h.exported.text());assert.equal(exported.cabling.locations[0].rack,'Poznań A');
  }finally{h.close();}
});

test('checking a cabling leg also marks installed and binds progress to the current definition',async()=>{
  let posted;
  const h=harness(async(url,opts)=>{if(url==='/api/project/cabling'){posted=JSON.parse(opts.body);return response(cablingResponse(posted));}return apiHandler()(url);});
  try{
    await settle();loadProject(h);click(h,'buildCabling');await settle();
    const checkbox=h.w.document.querySelector('[data-progress="0"][data-field="checked"]');checkbox.click();await settle();
    const progress=posted.cabling.cables[0].progress[0];assert.equal(progress.branch_id,'branch-1');
    assert.equal(progress.installed,true);assert.equal(progress.checked,true);assert.equal(progress.definition,'a'.repeat(64));
    assert.match(h.w.document.getElementById('cablingReport').textContent,/unknown/);
    h.w.document.querySelector('[data-progress="0"][data-field="installed"]').click();await settle();
    assert.equal(posted.cabling.cables[0].progress[0].checked,false);
  }finally{h.close();}
});

test('installation edits cancel an obsolete PDF download even when fetch ignores abort',async()=>{
  let finish;
  const h=harness(async(url,opts)=>{
    if(url==='/api/project/cabling')return response(cablingResponse(JSON.parse(opts.body)));
    if(url==='/api/project/cabling.pdf')return new Promise(done=>{finish=done;});
    return apiHandler()(url);
  });
  try{
    await settle();loadProject(h);click(h,'buildCabling');await settle();click(h,'downloadCablingPDF');await settle();
    enter(h,'[data-location="head-01"][data-field="rack"]','Moved rack');
    finish({ok:true,headers:{get:()=>r1},blob:async()=>new Blob(['%PDF-stale'],{type:'application/pdf'})});await settle();
    assert.equal(h.exported,undefined);assert.equal(h.w.document.getElementById('downloadCablingPDF').disabled,true);
    assert.equal(h.w.document.getElementById('cablingReport').textContent,'');
  }finally{h.close();}
});

test('PDF, end-label and XLSX downloads preserve binary bodies and require the current revision',async()=>{
  let revision=r1;
  const h=harness(async(url,opts)=>{
    if(url==='/api/project/cabling')return response(cablingResponse(JSON.parse(opts.body)));
    if(/\.(pdf|xlsx)$/.test(url))return {ok:true,headers:{get:()=>revision},blob:async()=>new Blob([url.endsWith('xlsx')?'PK-Excel':'%PDF-test'],{type:url.endsWith('xlsx')?'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':'application/pdf'})};
    return apiHandler()(url);
  });
  try{
    await settle();loadProject(h);click(h,'buildCabling');await settle();
    for(const button of ['downloadCablingPDF','downloadLabelsPDF','downloadCablingXLSX']){click(h,button);await settle();assert.equal((await h.exported.text()).startsWith(button.endsWith('XLSX')?'PK':'%PDF'),true);}
    const previous=h.exported;revision=r2;click(h,'downloadCablingPDF');await settle();assert.equal(h.exported,previous);
    assert.match(h.w.document.getElementById('cablingStatus').textContent,/Catalog changed/);
  }finally{h.close();}
});

test('unapplied project JSON blocks cabling generation and removing an entry prunes its installation metadata',async()=>{
  let calls=0;
  const h=harness(async url=>{if(url==='/api/project/cabling')calls++;return apiHandler()(url);});
  try{
    await settle();loadProject(h);enter(h,'[data-location="head-01"][data-field="rack"]','Rack A');enter(h,'[data-cable="fanout-1"]','IB-001');
    input(h,'projectDocument','{ pending edit');click(h,'buildCabling');await settle();assert.equal(calls,0);
    assert.match(h.w.document.getElementById('cablingStatus').textContent,/pending project JSON/);
    const saved=JSON.parse(h.w.localStorage.getItem('nvidia-project-v1'));loadProject(h,saved);
    h.w.document.querySelector('[data-remove-entry="fanout-1"]').click();click(h,'downloadProjectJSON');
    const exported=JSON.parse(await h.exported.text());assert.deepEqual(exported.cabling,{locations:[],port_labels:[],cables:[]});
  }finally{h.close();}
});

function mapResponse(project=projectDraft()) {
  const c=cablingResponse(project), entry=project.breakouts[0];
  const hosts=[entry.head,...entry.branches.map(b=>b.selection)];
  const segments=hosts.map((h,i)=>({id:'segment-'+i,entry_id:entry.id,instance_id:h.instance_id,port_group_id:h.port_group_id,port_number:h.port_number,port_label:i?'NIC '+i:'1/1',role:i?'branch':'head',branch_id:i?'branch-'+i:null,termination:i||null,head_links:i?[i]:[],selected_mode:h.mode_id,mode:{id:h.mode_id,links:i?1:2,speed_gbps:400},part_number:'PN-fan',status:'unknown',ownership_conflict:false}));
  const devices=hosts.map((h,i)=>({id:h.instance_id,device_id:h.device_id,model:i?'Adapter':'Switch',hardware_profile_id:null,rack:'Rack A',rack_u:12,identity_conflict:false,occupied:1,free_count:i?0:31,groups:[{id:h.port_group_id,label:'Physical cages',connector_family:'OSFP',count:i?1:32,occupied:1,free_count:i?0:31,free_ranges:i?[]:[[2,32]],ports:[{number:1,label:i?'NIC '+i:'1/1',state:'occupied',segments:['segment-'+i],interfaces:Array.from({length:i?1:2},(_,n)=>({number:n+1,speed_gbps:400,state:'declared',references:['branch-'+(i||n+1)]}))}]}]}));
  return {revision:r1,status:'unknown',summary:{devices:3,assemblies:1,occupied_cages:3,terminations:3,conflicting_cages:0},devices,segments,assemblies:[{id:entry.id,type:'breakout',cable_id:'C-'+entry.id,part_number:'PN-fan',length_m:3,fabric:'IB',status:'unknown',checks:[{state:'unknown',code:'breakout.common_fec',message:'FEC evidence missing'}],rows:c.rows.map(r=>({...r,source_label:'H',destination_label:r.branch_id,head_optical_lanes:[],branch_optical_lanes:[]})),ownership_conflict:false}],checks:[]};
}
function mapHandler(transform=value=>value){return async(url,opts)=>url==='/api/project/map'?response(transform(mapResponse(JSON.parse(opts.body)))):apiHandler()(url);}
function selectMap(h,selector){const element=h.w.document.querySelector(selector);assert.ok(element,selector);element.dispatchEvent(new h.w.MouseEvent('click',{bubbles:true}));}

test('map draws one breakout hub and three physical terminations with clickable PN, modes and validation',async()=>{
  const h=harness(mapHandler());
  try{
    await settle();loadProject(h);click(h,'buildProjectMap');await settle();
    assert.equal(h.w.document.querySelectorAll('.map-device').length,3);
    assert.equal(h.w.document.querySelectorAll('.map-assembly').length,1);
    assert.equal(h.w.document.querySelectorAll('.map-segment').length,3);
    assert.equal(h.w.document.querySelectorAll('.map-head').length,1);
    selectMap(h,'.map-assembly');const detail=h.w.document.getElementById('mapDetails').textContent;
    assert.match(detail,/PN-fan/);assert.match(detail,/2 × 400G/);assert.match(detail,/FEC evidence missing/);
    assert.match(detail,/One shared head cage/);assert.match(detail,/unknown/);
    const paths=[...h.w.document.querySelectorAll('.map-line')].map(p=>p.getAttribute('d'));assert.equal(new Set(paths).size,3);
  }finally{h.close();}
});

test('device inventory separates free physical cages from the two logical interfaces in its occupied head',async()=>{
  const h=harness(mapHandler());
  try{
    await settle();loadProject(h);click(h,'buildProjectMap');await settle();selectMap(h,'.map-device[data-device="0"]');
    assert.equal(h.w.document.querySelectorAll('.cage-occupied').length,1);assert.equal(h.w.document.querySelectorAll('.cage-free').length,31);
    selectMap(h,'[data-port="1"]');let detail=h.w.document.getElementById('mapPortDetail').textContent;
    assert.match(detail,/Interface 1 · 400G/);assert.match(detail,/Interface 2 · 400G/);assert.match(detail,/branch-2/);
    selectMap(h,'[data-port="2"]');detail=h.w.document.getElementById('mapPortDetail').textContent;
    assert.match(detail,/free in this project/);assert.doesNotMatch(detail,/Interface 1/);
  }finally{h.close();}
});

test('unknown capacity shows only occupied ports and unresolved logical interfaces',async()=>{
  const h=harness(mapHandler(v=>{const d=v.devices[0],g=d.groups[0];d.free_count=null;g.count=null;g.free_count=null;g.free_ranges=[];g.ports[0].interfaces=[];return v;}));
  try{
    await settle();loadProject(h);click(h,'buildProjectMap');await settle();selectMap(h,'.map-device[data-device="0"]');
    assert.equal(h.w.document.querySelectorAll('.map-cage').length,1);assert.equal(h.w.document.querySelectorAll('.cage-free').length,0);
    assert.match(h.w.document.getElementById('mapDetails').textContent,/Capacity unknown/);
    selectMap(h,'[data-port="1"]');assert.match(h.w.document.getElementById('mapPortDetail').textContent,/Logical interfaces unresolved/);
  }finally{h.close();}
});

test('project ownership conflicts remain visible even when an individual assembly validates',async()=>{
  const h=harness(mapHandler(v=>{v.status='incompatible';v.assemblies[0].status='compatible';v.assemblies[0].ownership_conflict=true;v.devices[0].ownership_conflict=true;v.devices[0].groups[0].ports[0].state='conflict';v.segments[0].ownership_conflict=true;return v;}));
  try{
    await settle();loadProject(h);click(h,'buildProjectMap');await settle();
    assert.ok(h.w.document.querySelector('.map-assembly.state-incompatible'));
    assert.ok(h.w.document.querySelector('.map-head.state-incompatible'));
    selectMap(h,'.map-assembly');assert.match(h.w.document.getElementById('mapDetails').textContent,/Port allocation conflict/);
    selectMap(h,'.map-device[data-device="0"]');assert.equal(h.w.document.querySelectorAll('.cage-conflict').length,1);
  }finally{h.close();}
});

test('map filters and zoom preserve whole-project capacity and support keyboard activation',async()=>{
  const h=harness(mapHandler());
  try{
    await settle();loadProject(h);click(h,'buildProjectMap');await settle();
    change(h,'mapDeviceFilter','head-01');assert.equal(h.w.document.querySelectorAll('.map-assembly').length,1);
    assert.match(h.w.document.getElementById('mapPageStatus').textContent,/counts cover the entire project/);
    input(h,'mapSearch','absent-pn');assert.match(h.w.document.getElementById('mapCanvas').textContent,/No connections/);
    click(h,'mapReset');change(h,'mapFabric','ETH');assert.equal(h.w.document.querySelectorAll('.map-assembly').length,0);
    click(h,'mapReset');input(h,'mapZoom','150');assert.equal(h.w.document.querySelector('#mapCanvas svg').getAttribute('width'),'1740');
    h.w.document.querySelector('.map-assembly').dispatchEvent(new h.w.KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
    assert.equal(h.w.document.activeElement.id,'mapDetails');assert.match(h.w.document.getElementById('mapDetails').textContent,/PN-fan/);
  }finally{h.close();}
});

test('edited drafts and catalog refresh discard obsolete map responses and rendered details',async()=>{
  let finish;
  const h=harness(async(url,opts)=>url==='/api/project/map'?new Promise(done=>{finish=()=>done(response(mapResponse(JSON.parse(opts.body))));}):apiHandler()(url));
  try{
    await settle();loadProject(h);click(h,'buildProjectMap');await settle();input(h,'projectDocument','{ pending');finish();await settle();
    assert.equal(h.w.document.querySelector('#mapCanvas svg'),null);click(h,'buildProjectMap');assert.match(h.w.document.getElementById('mapStatus').textContent,/pending project JSON/);
    loadProject(h);click(h,'buildProjectMap');await settle();finish();await settle();assert.ok(h.w.document.querySelector('#mapCanvas svg'));
    h.w.ValidatorTopology.setCatalog(topologyBundle(r2));assert.equal(h.w.document.querySelector('#mapCanvas svg'),null);
    assert.equal(h.w.document.getElementById('mapDetails').textContent,'');
  }finally{h.close();}
});

test('map rejects another catalog revision and escapes labels in both SVG and details',async()=>{
  let old=true;
  const h=harness(mapHandler(v=>{v.revision=old?r2:r1;v.assemblies[0].part_number='<img src=x onerror="alert(1)">';v.devices[0].model='<script>alert(1)</script>';return v;}));
  try{
    await settle();loadProject(h);click(h,'buildProjectMap');await settle();assert.equal(h.w.document.querySelector('#mapCanvas svg'),null);
    assert.match(h.w.document.getElementById('mapStatus').textContent,/Catalog changed/);
    old=false;click(h,'buildProjectMap');await settle();selectMap(h,'.map-assembly');
    assert.equal(h.w.document.querySelector('#mapCanvas script, #mapCanvas img, #mapDetails img'),null);
    assert.match(h.w.document.getElementById('mapDetails').textContent,/<img src=x/);
  }finally{h.close();}
});

test('large maps page connections explicitly and large device inventories page cage buttons',async()=>{
  const h=harness(mapHandler(v=>{
    const a=v.assemblies[0],segments=v.segments;
    v.assemblies=Array.from({length:41},(_,i)=>({...a,id:'link-'+i,cable_id:'Cable-'+i}));
    v.segments=v.assemblies.flatMap(a=>segments.map((s,i)=>({...s,id:a.id+'-'+i,entry_id:a.id})));
    v.summary.assemblies=41;const g=v.devices[0].groups[0];g.count=200;g.free_count=199;g.free_ranges=[[2,200]];v.devices[0].free_count=199;return v;
  }));
  try{
    await settle();loadProject(h);click(h,'buildProjectMap');await settle();assert.equal(h.w.document.querySelectorAll('.map-assembly').length,40);
    assert.match(h.w.document.getElementById('mapPageStatus').textContent,/1–40 of 41/);click(h,'mapNext');assert.equal(h.w.document.querySelectorAll('.map-assembly').length,1);
    assert.match(h.w.document.getElementById('mapPageStatus').textContent,/41–41 of 41/);
    selectMap(h,'.map-device[data-device="0"]');assert.equal(h.w.document.querySelectorAll('.map-cage').length,64);
    selectMap(h,'[data-port-page="0"][data-offset="1"]');assert.equal(h.w.document.querySelector('.map-cage').dataset.port,'65');
  }finally{h.close();}
});
