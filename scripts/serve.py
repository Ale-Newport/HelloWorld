"""Local static preview. Binds only to localhost; no external account or build needed."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import argparse,webbrowser,threading,errno,urllib.request,json,os,shutil
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8844);p.add_argument('--open',action='store_true');a=p.parse_args()
root=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
 def do_POST(self):
  if self.path not in ['/api/world','/api/export']:self.send_error(404);return
  origin=self.headers.get('Origin','');host=self.headers.get('Host','')
  if origin and origin not in [f'http://{host}']:self.send_error(403);return
  if host not in [f'127.0.0.1:{a.port}',f'localhost:{a.port}']:self.send_error(403);return
  try:
   length=int(self.headers.get('Content-Length','0'))
   if not 0<length<100_000_000:raise ValueError('World exceeds 100 MB')
   raw=self.rfile.read(length)
   if self.path=='/api/export':
    if raw[:4]!=b'glTF':raise ValueError('Expected a binary glTF world')
    target=root/'exports/EditedWorld.glb';temp=target.with_suffix('.tmp')
    if target.exists():shutil.copyfile(target,root/'backups/EditedWorld.previous.glb')
    temp.write_bytes(raw);os.replace(temp,target);self.send_response(200);self.end_headers();self.wfile.write(b'{"exported":true}');return
   data=json.loads(raw)
   if data.get('schema')!=2 or not isinstance(data.get('states'),dict) or not isinstance(data.get('added'),list):raise ValueError('Invalid world document')
   target=root/'exports/editor-world.json';temp=target.with_suffix('.tmp')
   if target.exists():shutil.copyfile(target,root/'backups/editor-world.previous.json')
   temp.write_text(json.dumps(data,separators=(',',':')));os.replace(temp,target)
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
