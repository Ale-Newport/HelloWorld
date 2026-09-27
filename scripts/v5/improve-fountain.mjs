export const FOUNTAIN_ID='v4:v4:circular-fountain:1';

/** Replace only the old fountain's part snapshots; keep its authored placement. */
export function improveFountain(document){
 const doc=structuredClone(document),state=doc.states[FOUNTAIN_ID];
 if(!state||state.data.fountainDesign===2)return doc;
 for(const id of Object.keys(doc.states))if(id.startsWith(FOUNTAIN_ID+'/'))delete doc.states[id];
 state.data.fountainDesign=2;
 state.data.tags=['fountain','plaza','water','animated'];
 return doc;
}
