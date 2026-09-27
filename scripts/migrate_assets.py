"""Read-only source migration. All destinations are beneath this project."""
from pathlib import Path
import shutil, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
SOURCE=next(p for p in (ROOT.parent/'Portfolio',ROOT.parent/'Portafolio') if p.is_dir())
entries=[]
def copy(src,dst):
 dst=ROOT/dst;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 entries.append({'file':str(dst.relative_to(ROOT)),'source':str(src.relative_to(SOURCE)),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
for p in (SOURCE/'assets/world2-source').rglob('*'):
 if p.is_file():copy(p,Path('textures/source')/p.relative_to(SOURCE/'assets/world2-source'))
for p in (SOURCE/'public/world2').rglob('*'):
 if p.is_file():copy(p,Path('assets/environment/portfolio')/p.relative_to(SOURCE/'public/world2'))
for rel in ['THIRD_PARTY_NOTICES.md','WORLD2_ASSET_NOTICES.md']:
 copy(SOURCE/rel,Path('docs/source')/rel)
fonts=list((SOURCE/'node_modules/geist').rglob('Geist-Bold.ttf'))
if fonts:copy(fonts[0],Path('assets/fonts/Geist-Bold.ttf'))
copy(SOURCE/'node_modules/geist/LICENSE.txt',Path('assets/fonts/LICENSE.txt'))
for rel in ['three/build/three.module.js','three/build/three.core.js','three/examples/jsm/loaders/GLTFLoader.js','three/examples/jsm/utils/BufferGeometryUtils.js','three/examples/jsm/utils/SkeletonUtils.js','three/examples/jsm/controls/OrbitControls.js','three/LICENSE','@dimforge/rapier3d-compat/rapier.es.js']:
 copy(SOURCE/'node_modules'/rel,Path('preview/vendor')/rel)
(ROOT/'reports/asset-migration.json').write_text(json.dumps(entries,indent=2))
(ROOT/'ASSET_SOURCES.md').write_text('# Asset sources\n\nPortfolio was read only. Every runtime resource is a local copy.\n\nOriginal diorama: Bruno Simon, MIT (see textures/source/LICENSE.md). Ferris wheel: user-supplied ferris-wheel.zip; retain its distribution rights separately. New zones and editor authored for this project.\n\n| Local file | Source in ../Portfolio | SHA-256 |\n|---|---|---|\n'+''.join(f"| `{e['file']}` | `{e['source']}` | `{e['sha256']}` |\n" for e in entries))
print('Copied',len(entries),'assets')
