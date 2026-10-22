// Guard and configuration regression checks for development browser config.
// Run locally with: node --test commerce/v615-sandbox-browser.test.cjs
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const configSource=fs.readFileSync(__dirname+'/v615-dev-config.js','utf8');
const uiSource=fs.readFileSync(__dirname+'/v615-account-ui.js','utf8');
function runtime(overrides={},href='https://dev-preview.example.test/customize-ready.html'){
  const confContext={window:{}};vm.runInNewContext(configSource,confContext);
  const cfg={...confContext.window.SCANBACK_V615_DEV_CONFIG,...overrides};
  let connects=0;
  const root={location:{href},SCANBACK_V615_DEV_CONFIG:cfg,
    supabase:{createClient(){connects++;return {auth:{async getUser(){return {data:{user:null}}}}};}}};
  const fakeElement={hidden:true};const document={getElementById(){return fakeElement;}};
  const context={window:root,document,URL};
  vm.runInNewContext(uiSource,context);
  root.ScanBackV615AccountUI.mount(null,null);
  return {connects,shown:!fakeElement.hidden,cfg};
}
test('default configuration is disabled with empty origin allowlist',()=>{
 const r=runtime();assert.equal(r.cfg.ENABLED,false);assert.equal(r.connects,0);
 assert.equal(r.shown,false);assert.equal(r.cfg.ALLOWED_SITE_ORIGINS.length,0);
 assert.match(r.cfg.SUPABASE_URL,/^https:\/\/khaxvskqypmabqozpkel\.supabase\.co$/);
 assert.match(r.cfg.SUPABASE_ANON_KEY,/^sb_publishable_/);
 assert.doesNotMatch(r.cfg.SUPABASE_ANON_KEY,/^sb_secret_/);
});
test('turning on client flag alone cannot authorize a preview origin',()=>{
 assert.equal(runtime({ENABLED:true}).connects,0);
});
test('wrong project, missing key, and production domain fail closed',()=>{
 const opts={ENABLED:true,ALLOWED_SITE_ORIGINS:['https://dev-preview.example.test']};
 assert.equal(runtime({...opts,SUPABASE_URL:'https://oliujepmidoensqhvanf.supabase.co'}).connects,0);
 assert.equal(runtime({...opts,SUPABASE_URL:'https://another-project.supabase.co'}).connects,0);
 assert.equal(runtime({...opts,SUPABASE_ANON_KEY:'sb_secret_do-not-use'}).connects,0);
 assert.equal(runtime({...opts,ALLOWED_SITE_ORIGINS:['https://scanback.in']},'https://scanback.in/customize-ready.html').connects,0);
 assert.equal(runtime({...opts,ALLOWED_SITE_ORIGINS:['https://shop.scanback.in']},'https://shop.scanback.in/customize-ready.html').connects,0);
});
test('non-allowlisted dev preview cannot initiate client',()=>{
 const opts={ENABLED:true,ALLOWED_SITE_ORIGINS:['https://other-preview.example.test']};
 assert.equal(runtime(opts).connects,0);
});
test('approved sandbox plus explicit dev preview gate prepares client connection',()=>{
 const opts={ENABLED:true,ALLOWED_SITE_ORIGINS:['https://dev-preview.example.test']};
 const r=runtime(opts);assert.equal(r.connects,1);
});
