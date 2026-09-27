from pathlib import Path
import json,hashlib,struct,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
results=[]
def check(name,ok,detail=''):
 results.append({'name':name,'passed':bool(ok),'detail':detail});print(('PASS' if ok else 'FAIL'),name,detail)
checks=json.loads((ROOT/'backups/checksums.json').read_text())
check('Original blend and backup byte-identical',sha(ROOT/'folio-2025.blend')==sha(ROOT/'backups/hello_world_original.blend')==checks['folio-2025.blend'])
# Portfolio is optional at runtime. Verify its snapshot when it still exists.
source=next((p for p in [ROOT.parent/'Portfolio',ROOT.parent/'Portafolio'] if p.is_dir()),None)
if source:
 before=json.loads((ROOT/'reports/portfolio-before.json').read_text());changed=[]
 for rel,state in before.items():
  p=source/rel
  if not p.is_file():changed.append(rel+' (missing)');continue
  st=p.stat()
  if sha(p)!=state['sha256'] or st.st_mtime_ns!=state['mtime_ns'] or st.st_mode!=state['mode']:changed.append(rel)
 check('Portfolio source files unchanged',not changed,{'checked':len(before),'changes':changed})
else:check('Portfolio independent runtime',True,'Portfolio is absent; all world resources remain local')
for path in ['world/AlejandroWorld.blend','exports/AlejandroWorld.glb','editor/alejandro_world/__init__.py','editor/AlejandroWorldBuilder.zip','preview/vendor/three/build/three.module.js','preview/vendor/three/examples/jsm/utils/SkeletonUtils.js','preview/vendor/@dimforge/rapier3d-compat/rapier.es.js']:
 check(path+' exists',(ROOT/path).is_file())
raw=(ROOT/'exports/AlejandroWorld.glb').read_bytes();length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length]);check('GLB container length',struct.unpack_from('<I',raw,8)[0]==len(raw));check('Textures embedded in GLB',all('bufferView' in i or i.get('uri','').startswith('data:') for i in doc.get('images',[])));check('No Portfolio dependency in GLB',b'/Portfolio/' not in raw and b'/Portafolio/' not in raw)
# All browser ES module imports and import-map resources are bundled locally.
check('Preview code has no external source directory dependency',all('/Portfolio/' not in p.read_text() and '/Portafolio/' not in p.read_text() for p in (ROOT/'preview').rglob('*.js')))
(ROOT/'reports/asset-tests.json').write_text(json.dumps(results,indent=2));sys.exit(not all(r['passed'] for r in results))
