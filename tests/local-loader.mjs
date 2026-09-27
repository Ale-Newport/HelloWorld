const root=new URL('../',import.meta.url);
export async function resolve(specifier,context,nextResolve){
 const local={'three':'preview/vendor/three/build/three.module.js','@dimforge/rapier3d-compat':'preview/vendor/@dimforge/rapier3d-compat/rapier.es.js'};
 if(specifier.startsWith('three/addons/'))return {url:new URL('preview/vendor/three/examples/jsm/'+specifier.slice(13),root).href,shortCircuit:true};
 if(local[specifier])return {url:new URL(local[specifier],root).href,shortCircuit:true};
 return nextResolve(specifier,context);
}
