(function(root){'use strict';const $=id=>document.getElementById(id);
function mount(read,restore){const section=$('v615Account');if(!section)return;const config=root.SCANBACK_V615_DEV_CONFIG;
if(!config?.ENABLED)return;let host;
try{host=new URL(config.SUPABASE_URL).hostname;if(host==='oliujepmidoensqhvanf.supabase.co'||['www.scanback.in','scanback.in'].includes(location.hostname)||!host.endsWith('.supabase.co')||!config.SUPABASE_ANON_KEY)throw Error('Isolated development project required');}catch{return;}
if(!root.supabase?.createClient)return;
const sb=root.supabase.createClient(config.SUPABASE_URL,config.SUPABASE_ANON_KEY);
section.hidden=false;let draftId=null;
const status=t=>$('v615AccountStatus').textContent=t;
async function call(action,params={}){const {data:user,error:uerr}=await sb.auth.getUser();if(uerr||!user.user||user.user.is_anonymous)throw Error('Sign in to your test account');const {data,error}=await sb.functions.invoke(config.EDGE_FUNCTION,{body:{action,...params}});if(error)throw error;if(!data?.ok)throw Error(data?.error||'Action not confirmed');return data;}
async function listing(){const list=$('v615DraftList');list.replaceChildren();const result=await call('list');for(const x of result.drafts){const p=document.createElement('p'),link=document.createElement('a');link.href='customize-ready.html?draft_id='+encodeURIComponent(x.id);link.textContent=x.child_display_name+' — '+x.pack_size+' stickers (edit)';p.append(link);list.append(p);}if(!result.drafts.length)list.textContent='No saved drafts yet.';}
async function refresh(){const {data}=await sb.auth.getUser(),active=!!data?.user;$('v615Login').hidden=active;$('v615SignOut').hidden=!active;$('v615Refresh').hidden=!active;if($('v615Save'))$('v615Save').hidden=!active;if(active)await listing();}
async function restoreFromUrl(){const id=new URLSearchParams(location.search).get('draft_id');if(id&&restore){const d=await call('get',{id});restore(d.draft);draftId=id;status('Draft reloaded from your development account.');}}
$('v615Login').onsubmit=async e=>{e.preventDefault();try{const {error}=await sb.auth.signInWithPassword({email:$('v615Email').value.trim(),password:$('v615Password').value});if(error)throw error;$('v615Password').value='';await refresh();await restoreFromUrl();status('Signed in to development account.');}catch(e){status(e.message)}};
$('v615SignOut').onclick=async()=>{const {error}=await sb.auth.signOut();if(error)return status(error.message);draftId=null;$('v615DraftList').replaceChildren();await refresh();status('Signed out.');};
$('v615Refresh').onclick=()=>listing().catch(e=>status(e.message));
if($('v615Save'))$('v615Save').onclick=async()=>{try{const d=read();const data=await call('save',{...(draftId?{id:draftId}:{}),child_display_name:d.child_display_name,pack_size:d.pack_size,stickers:d.stickers.map(s=>({artwork_id:s.artwork_id,item_name:s.item_name}))});draftId=data.draft.id;await listing();status('Saved. This is not a paid order and has no live QR.');}catch(e){status(e.message)}};
refresh().then(restoreFromUrl).catch(e=>status(e.message));
}root.ScanBackV615AccountUI={mount};})(window);
