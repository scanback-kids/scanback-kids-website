// Run locally with: node --test printing/a4-six-pack-layout.test.cjs
const test=require('node:test');
const assert=require('node:assert/strict');
const A4=require('./a4-six-pack-layout.js');
for(const [shape,expected] of [
 ['rounded',{w:60,h:31,left:32.5,top:82.5,bleed:2.5}],
 ['diecut',{w:55,h:58,left:39,top:44,bleed:2.5}]
]){
 test('A4 six-up '+shape+' full-backing layout',()=>{
   const g=A4.geometry(shape);
   assert.equal(g.PERPAGE,6);assert.equal(g.COLS,2);
   assert.equal(g.W,expected.w);assert.equal(g.H,expected.h);
   assert.equal(g.LEFT,expected.left);assert.equal(g.TOP,expected.top);
   assert.equal(g.BLEED,expected.bleed);
   const rects=[];
   for(let i=0;i<6;i++){
     const p=A4.gridOrigin(i,shape),w=g.W+2*g.BLEED,h=g.H+2*g.BLEED;
     assert.ok(p.x>=5&&p.y>=12,'press safe margins');
     assert.ok(p.x+w<=210-5&&p.y+h<=297-12,'within full A4');
     for(const other of rects)assert.ok(p.x>=other.x+other.w || other.x>=p.x+w || p.y>=other.y+other.h || other.y>=p.y+h,'bleed boxes must not overlap');
     rects.push({x:p.x,y:p.y,w,h});
   }
   assert.ok(g.LEFT>0&&g.TOP>0);
 });
}
test('invalid shapes and sheet positions fail closed',()=>{
 assert.throws(()=>A4.geometry('unknown'));
 assert.throws(()=>A4.gridOrigin(6,'rounded'));
 assert.throws(()=>A4.gridOrigin(-1,'diecut'));
 assert.throws(()=>A4.gridOrigin(1.2,'rounded'));
});
