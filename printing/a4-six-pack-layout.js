// ScanBack Kids six-pack A4 sheet planner (geometry only). Test Mode, NOT printer-approved.
// Keep the entire A4 liner intact; ask vendor for KISS-CUT, never cut through the liner.
(function(root){
  'use strict';
  const PAGE=Object.freeze({W:210,H:297});
  const SPECS=Object.freeze({
    rounded:Object.freeze({W:60,H:31,BLEED:2.5,GAP:15,ROW_GAP:12}),
    diecut:Object.freeze({W:55,H:58,BLEED:2.5,GAP:12,ROW_GAP:10})
  });
  function geometry(shape){
    if(shape!=='rounded'&&shape!=='diecut')throw Error('Unknown ScanBack sticker shape');
    const s=SPECS[shape],cols=2,rows=3,cellW=s.W+2*s.BLEED,cellH=s.H+2*s.BLEED;
    const layoutWidth=cols*cellW+(cols-1)*s.GAP;
    const layoutHeight=rows*cellH+(rows-1)*s.ROW_GAP;
    const LEFT=(PAGE.W-layoutWidth)/2,TOP=(PAGE.H-layoutHeight)/2;
    if(LEFT<5||TOP<12||TOP+layoutHeight>PAGE.H-12)throw Error('Unsafe A4 margins');
    return {...s,COLS:cols,ROWS:rows,PERPAGE:6,LEFT,TOP,PAGE_W:PAGE.W,PAGE_H:PAGE.H};
  }
  function gridOrigin(index,shape){
    if(!Number.isInteger(index)||index<0||index>5)throw Error('A six-pack sheet needs positions 0 to 5');
    const g=geometry(shape),cellW=g.W+2*g.BLEED,cellH=g.H+2*g.BLEED;
    return {x:g.LEFT+(index%g.COLS)*(cellW+g.GAP),
      y:g.TOP+Math.floor(index/g.COLS)*(cellH+g.ROW_GAP)};
  }
  const api=Object.freeze({geometry,gridOrigin,page:Object.freeze({...PAGE})});
  if(root)root.ScanBackA4SixPack=api;
  if(typeof module==='object'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
