/** Build the self-contained, read-only /world player from the editor's exact runtime. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
const root=fileURLToPath(new URL('../../',import.meta.url));
const target=path.resolve(process.argv[2]??path.join(root,'dist/archipelago'));
if(target===root||target===path.dirname(root))throw Error('Invalid output directory');
if(fs.existsSync(target)&&!fs.existsSync(path.join(target,'release.json'))&&fs.readdirSync(target).length)throw Error('Output must be empty or a previous Archipelago release');
if(fs.existsSync(path.join(root,'exports/worlds/archipelago/editor-world.json')))execFileSync('python3',[path.join(root,'scripts/release/world-save.py'),'pack']);
fs.mkdirSync(target,{recursive:true});
const copy=(relative)=>fs.cpSync(path.join(root,relative),path.join(target,relative),{recursive:true,filter:p=>!/(\.DS_Store|__pycache__|\.pyc$)/.test(p)});
copy('preview');
for(const entry of ['environment','fonts','surfaces','vehicles'])copy('assets/'+entry);
for(const entry of ['AlejandroWorld.glb','navigation.json','worlds/archipelago/editor-world.json.gz','worlds/archipelago/asset-definitions.json'])copy('exports/'+entry);
for(const entry of ['ASSET_SOURCES.md','docs/source/THIRD_PARTY_NOTICES.md','docs/source/WORLD2_ASSET_NOTICES.md'])copy(entry);
let html=fs.readFileSync(path.join(root,'preview/index.html'),'utf8');
html=html.replace('<body>','<body data-player="true" class="player">').replace('</head>','<link rel="stylesheet" href="player.css"></head>')
 .replace('Alejandro World — World Studio','Archipiélago — Alejandro Newport').replace('Vista 3D editable de Alejandro World','Conduce y explora Archipiélago')
 .replace('ESC <span>editar</span>','ESC <span>cerrar actividad</span>')
 .replace(/<dialog id="help-dialog">[\s\S]*?<\/dialog>/,`<dialog id="help-dialog"><button id="close-help">Cerrar ×</button><h2>Explora Archipiélago</h2><p>WASD / flechas: conducir · Shift: boost · SPACE: frenar · doble SPACE: coche / avión · R: volver al camino.</p><p>E / Enter: interactuar · M / Tab: mapa · K: logros · C: cámara · Esc: cerrar actividad.</p><p>Avión: W/S velocidad · A/D giro · Q/E cabeceo.</p></dialog>`);
html=html.replace(/<img src="\.\.\/docs\/alejandro-world-map-reference.png"[^>]*>/,'');
// The editor DOM stays as an internal loader dependency; visitors get only the driving interface.
html=html.replace('<script type="module" src="main.js">','<nav id="player-nav" aria-label="Explorar"><a href="/" target="_top">← Portfolio</a><button id="player-map">Mapa</button><button id="player-help">Controles</button><button id="player-awards">Logros</button></nav><script type="module" src="player.js"></script><script type="module" src="main.js">');
fs.writeFileSync(path.join(target,'preview/index.html'),html);
const files={};
function inventory(dir){for(const name of fs.readdirSync(dir).sort()){const full=path.join(dir,name);if(fs.statSync(full).isDirectory())inventory(full);else if(name!=='release.json'){const rel=path.relative(target,full);files[rel]=createHash('sha256').update(fs.readFileSync(full)).digest('hex');}}}
inventory(target);
const manifest={world:'archipelago',source:'https://github.com/Ale-Newport/HelloWorld',sourceRevision:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),worldSHA256:files['exports/worlds/archipelago/editor-world.json.gz'],files};
fs.writeFileSync(path.join(target,'release.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(`Published ${Object.keys(files).length} files to ${target}`);
