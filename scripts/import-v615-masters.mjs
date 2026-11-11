#!/usr/bin/env node
/**
 * ScanBack Kids — V6.15 source-master import.
 * Usage: node scripts/import-v615-masters.mjs /path/to/ScanBack_96_V615_Development_Upload_Package.zip
 * Run in repository root. Does NOT promote candidates to commercial print masters.
 */
import {execFileSync} from 'node:child_process';
import {mkdtempSync, readFileSync, existsSync, mkdirSync, copyFileSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join, resolve, dirname} from 'node:path';
import {createHash} from 'node:crypto';
const zip=resolve(process.argv[2]||'');
if (!process.argv[2]||!existsSync(zip)) throw Error('Supply the actual 96-artwork ZIP file path');
const root=process.cwd();
const tmp=mkdtempSync(join(tmpdir(),'scanback-v615-'));
try {
  execFileSync('unzip',['-q',zip,'-d',tmp]);
  const manifest=JSON.parse(readFileSync(join(tmp,'manifest.json'),'utf8'));
  const rows=Array.isArray(manifest)?manifest:(manifest.items||manifest.entries||manifest.catalog||manifest.designs);
  if(!Array.isArray(rows)||rows.length!==96) throw Error('Manifest must contain exactly 96 artwork entries');
  const ids=new Set();
  const planned=[];
  for(const row of rows) {
    const id=row.id;
    const path=row.candidate_path;
    if(!/^(SPACE|DINO|RAINBOW|SPORTS)-(0[1-9]|1[0-9]|2[0-4])$/.test(id)||ids.has(id)) throw Error('Invalid or duplicate ID: '+id);
    ids.add(id);
    if(!/^assets\/print-master-candidates\/(space|dino|rainbow|sports)\/(0[1-9]|1[0-9]|2[0-4])\.webp$/.test(path)) throw Error('Unsafe candidate path: '+path);
    const source=join(tmp,path);
    if(!existsSync(source)) throw Error('Missing image: '+path);
    const sha=createHash('sha256').update(readFileSync(source)).digest('hex');
    if(sha!==row.candidate_sha256) throw Error('Checksum mismatch: '+id);
    planned.push({source,dest:join(root,path)});
  }
  for(const {source,dest} of planned){mkdirSync(dirname(dest),{recursive:true});copyFileSync(source,dest);}
  mkdirSync(join(root,'docs','development-artwork-audit'),{recursive:true});
  copyFileSync(join(tmp,'manifest.json'),join(root,'docs','development-artwork-audit','v615-candidate-manifest.json'));
  console.log('Imported 96 verified candidate files. V6.15 production approval remains blocked pending print/identity validation.');
} finally {rmSync(tmp,{recursive:true,force:true});}
