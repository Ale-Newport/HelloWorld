"""Exercise the real save endpoint in an isolated temporary repository."""
import gzip,json,shutil,socket,subprocess,tempfile,time,urllib.request,urllib.error
from pathlib import Path
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='archipelago-save-') as directory:
    dest=Path(directory);(dest/'scripts').mkdir();shutil.copy(root/'scripts/serve.py',dest/'scripts/serve.py')
    with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    server=subprocess.Popen(['python3',str(dest/'scripts/serve.py'),'--port',str(port)],stdout=subprocess.DEVNULL)
    base=f'http://127.0.0.1:{port}'
    try:
        for _ in range(50):
            try:urllib.request.urlopen(base,timeout=1).close();break
            except (OSError,urllib.error.URLError):time.sleep(.1)
        payload=gzip.decompress((root/'exports/worlds/archipelago/editor-world.json.gz').read_bytes())
        request=urllib.request.Request(base+'/api/world',data=payload,headers={'Content-Type':'application/json','Origin':base})
        with urllib.request.urlopen(request,timeout=60) as response:assert json.load(response)['saved']
        folder=dest/'exports/worlds/archipelago'
        saved=(folder/'editor-world.json').read_bytes()
        assert json.loads(saved)==json.loads(payload)
        assert gzip.decompress((folder/'editor-world.json.gz').read_bytes())==saved
        for retired in ['original','lagoon','coast','../../other']:
            try:urllib.request.urlopen(urllib.request.Request(base+'/api/world?world='+retired,data=b'{}'))
            except urllib.error.HTTPError as error:assert error.code==400
            else:raise AssertionError('Retired world accepted')
        print(f'PASS saved {len(payload):,} bytes through real API, verified compressed mirror and rejected retired worlds')
    finally:server.terminate();server.wait()
