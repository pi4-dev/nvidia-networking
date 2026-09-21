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
