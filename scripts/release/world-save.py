"""Pack an edited local JSON for Git, or restore the working copy on a fresh clone."""
import argparse, gzip, json, os
from pathlib import Path
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('action',choices=['pack','restore']);a=p.parse_args()
raw=root/'exports/worlds/archipelago/editor-world.json';packed=raw.with_suffix('.json.gz')
if a.action=='pack':
    content=raw.read_bytes();doc=json.loads(content)
    assert doc['schema']==2 and doc['states']['v4:world']['data']['worldVariant']['id']=='archipelago'
    temp=packed.with_suffix('.tmp');temp.write_bytes(gzip.compress(content,compresslevel=6,mtime=0));os.replace(temp,packed)
    print(f'Archipelago: {len(content):,} bytes → {packed.stat().st_size:,} bytes (lossless)')
elif not raw.exists():
    raw.write_bytes(gzip.decompress(packed.read_bytes()));print('Restored local editable JSON')
