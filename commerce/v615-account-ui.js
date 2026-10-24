(function(root){'use strict';const $=id=>document.getElementById(id);
function mount(read,restore){const section=$('v615Account');if(!section)return;const config=root.SCANBACK_V615_DEV_CONFIG;
if(!config?.ENABLED)return;
// A deliberate allowlist is required in addition to the server-side CORS allowlist.
const approvedSandbox='https://khaxvskqypmabqozpkel.supabase.co';
let valid=false;
try{
  const url=new URL(config.SUPABASE_URL);
  const site=new URL(root.location.href);
  const banned=site.hostname==='scanback.in'||site.hostname.endsWith('.scanback.in')||
    site.hostname==='scanback-kids-website.vercel.app';
  valid=url.origin===approvedSandbox&&url.pathname==='/'&&!url.username&&!url.password&&
    !banned&&Array.isArray(config.ALLOWED_SITE_ORIGINS)&&
    config.ALLOWED_SITE_ORIGINS.includes(site.origin)&&
    /^sb_publishable_[a-zA-Z0-9_-]+$/.test(config.SUPABASE_ANON_KEY||'')&&
    config.EDGE_FUNCTION==='v615-design-drafts';
}catch{}
if(!valid||!root.supabase?.createClient)return;
const sb=root.supabase.createClient(config.SUPABASE_URL,config.SUPABASE_ANON_KEY);
section.hidden=false;let draftId=null;let generation=0;
const status=t=>$('v615AccountStatus').textContent=t;
function clearVisibleAccountDetails(){
  generation++;draftId=null;
  $('v615DraftList').replaceChildren();
  $('v615Email').value='';$('v615Password').value='';
  $('v615Login').hidden=false;$('v615SignOut').hidden=true;$('v615Refresh').hidden=true;
  if($('v615Save'))$('v615Save').hidden=true;
  // The studio Reset button already restores the 6 default stickers and default nickname.
  $('reset')?.click();
  // Don't leave the previous owner's saved draft ID in the address bar.
  try{
    const url=new URL(root.location.href);
    if(url.searchParams.has('draft_id')){
      url.searchParams.delete('draft_id');
      root.history?.replaceState(null,'',url.pathname+url.search+url.hash);
    }
  }catch{}
}
async function call(action,params={}){const {data:user,error:uerr}=await sb.auth.getUser();if(uerr||!user.user||user.user.is_anonymous)throw Error('Sign in to your test account');const {data,error}=await sb.functions.invoke(config.EDGE_FUNCTION,{body:{action,...params}});if(error)throw error;if(!data?.ok)throw Error(data?.error||'Action not confirmed');return data;}
async function listing(){const ticket=generation;const result=await call('list');if(ticket!==generation)return;const list=$('v615DraftList');list.replaceChildren();for(const x of result.drafts){const p=document.createElement('p'),link=document.createElement('a');link.href='customize-ready.html?draft_id='+encodeURIComponent(x.id);link.textContent=x.child_display_name+' — '+x.pack_size+' stickers (edit)';p.append(link);list.append(p);}if(!result.drafts.length)list.textContent='No saved drafts yet.';}
async function refresh(){const ticket=generation;const {data}=await sb.auth.getUser();if(ticket!==generation)return;const active=!!data?.user&&!data.user.is_anonymous;$('v615Login').hidden=active;$('v615SignOut').hidden=!active;$('v615Refresh').hidden=!active;if($('v615Save'))$('v615Save').hidden=!active;if(active)await listing();}
async function restoreFromUrl(){const id=new URL(root.location.href).searchParams.get('draft_id');if(id&&restore){
  const ticket=generation;const d=await call('get',{id});
  if(ticket!==generation)return;
  const {data,error}=await sb.auth.getUser();
  if(ticket!==generation||error||!data?.user||data.user.is_anonymous)return;
  restore(d.draft);draftId=id;status('Draft reloaded from your development account.');
}}
$('v615Login').onsubmit=async e=>{e.preventDefault();try{const {error}=await sb.auth.signInWithPassword({email:$('v615Email').value.trim(),password:$('v615Password').value});if(error)throw error;$('v615Password').value='';await refresh();await restoreFromUrl();status('Signed in to development account.');}catch(e){status(e.message)}};
$('v615SignOut').onclick=async()=>{
  // Remove personalized information instantly, before the sign-out request completes.
  clearVisibleAccountDetails();
  try{
    const {error}=await sb.auth.signOut();if(error)throw error;
    await refresh();status('Signed out.');
  }catch(e){status('Sign out failed; please retry: '+e.message);await refresh().catch(()=>{});}
};
sb.auth.onAuthStateChange?.(event=>{
  if(event==='SIGNED_OUT'){clearVisibleAccountDetails();status('Signed out.');}
});
$('v615Refresh').onclick=()=>listing().catch(e=>status(e.message));
if($('v615Save'))$('v615Save').onclick=async()=>{try{const d=read();const data=await call('save',{...(draftId?{id:draftId}:{}),child_display_name:d.child_display_name,pack_size:d.pack_size,stickers:d.stickers.map(s=>({artwork_id:s.artwork_id,item_name:s.item_name}))});draftId=data.draft.id;await listing();status('Saved. This is not a paid order and has no live QR.');}catch(e){status(e.message)}};
refresh().then(restoreFromUrl).catch(e=>status(e.message));
}root.ScanBackV615AccountUI={mount};})(window);
