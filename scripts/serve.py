"""Local static preview. Binds only to localhost; no external account or build needed."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import argparse,webbrowser,threading,errno,urllib.request,json,os,shutil,gzip
from urllib.parse import urlparse,parse_qs
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8844);p.add_argument('--open',action='store_true');a=p.parse_args()
root=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
 def do_POST(self):
  parsed=urlparse(self.path);endpoint=parsed.path;slot=parse_qs(parsed.query).get('world',['archipelago'])[0]
  if endpoint not in ['/api/world','/api/export','/api/assets']:self.send_error(404);return
  if slot!='archipelago':self.send_error(400,'Unknown world');return
  folder=root/'exports/worlds/archipelago'
  previous_dir=root/'backups/worlds/archipelago'
  folder.mkdir(parents=True,exist_ok=True);previous_dir.mkdir(parents=True,exist_ok=True)
  origin=self.headers.get('Origin','');host=self.headers.get('Host','')
  if origin and origin not in [f'http://{host}']:self.send_error(403);return
  if host not in [f'127.0.0.1:{a.port}',f'localhost:{a.port}']:self.send_error(403);return
  try:
   length=int(self.headers.get('Content-Length','0'))
   if not 0<length<256_000_000:raise ValueError('World exceeds 256 MB')
   raw=self.rfile.read(length)
   if endpoint=='/api/export':
    if raw[:4]!=b'glTF':raise ValueError('Expected a binary glTF world')
    target=folder/'EditedWorld.glb';temp=target.with_suffix('.tmp')
    if target.exists():shutil.copyfile(target,previous_dir/'EditedWorld.previous.glb')
    temp.write_bytes(raw);os.replace(temp,target);self.send_response(200);self.end_headers();self.wfile.write(b'{"exported":true}');return
   data=json.loads(raw)
   if endpoint=='/api/assets':
    if data.get('schema')!=1 or not isinstance(data.get('definitions'),list):raise ValueError('Invalid asset definitions')
    ids=set()
    for item in data['definitions']:
     if not isinstance(item,dict) or not isinstance(item.get('id'),str) or item['id'] in ids or not isinstance(item.get('object',{}).get('object'),dict):raise ValueError('Invalid or duplicate asset definition')
     ids.add(item['id'])
    target=folder/'asset-definitions.json';previous=previous_dir/'asset-definitions.previous.json'
   else:
    if data.get('schema')!=2 or not isinstance(data.get('states'),dict) or not isinstance(data.get('added'),list):raise ValueError('Invalid world document')
    target=folder/'editor-world.json';previous=previous_dir/'editor-world.previous.json'
   temp=target.with_suffix('.tmp')
   if target.exists():shutil.copyfile(target,previous)
   payload=json.dumps(data,separators=(',',':')).encode()
   temp.write_bytes(payload);os.replace(temp,target)
   if endpoint=='/api/world':
    packed=target.with_suffix('.json.gz');packed_temp=packed.with_suffix('.tmp')
    packed_temp.write_bytes(gzip.compress(payload,compresslevel=6,mtime=0));os.replace(packed_temp,packed)
   self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b'{"saved":true}')
  except Exception as error:self.send_error(400,str(error))
 def end_headers(self):
  self.send_header('Cache-Control','no-cache');super().end_headers()
 def log_message(self,*args):pass
try:
 server=ThreadingHTTPServer(('127.0.0.1',a.port),partial(Handler,directory=str(root)))
except OSError as error:
 if error.errno!=errno.EADDRINUSE:raise
 url=f'http://127.0.0.1:{a.port}/preview/'
 try:
  with urllib.request.urlopen(url,timeout=2) as response:existing=response.read(8192).decode(errors='replace')
 except Exception:existing=''
 if 'Alejandro World' in existing:
  print(f'Alejandro World is already running: {url}',flush=True)
  if a.open:webbrowser.open(url)
  raise SystemExit(0)
 p.error(f'Port {a.port} is occupied. Choose another with --port 8850.')
print(f'Alejandro World: http://127.0.0.1:{a.port}/preview/',flush=True)
if a.open:threading.Timer(.5,lambda:webbrowser.open(f'http://127.0.0.1:{a.port}/preview/')).start()
try:server.serve_forever()
except KeyboardInterrupt:server.server_close()
