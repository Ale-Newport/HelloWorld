"""Read-only source copy and deterministic evaluation of terrain/Mix.005.
No image synthesis: the original grayscale mask and audited linear colour
mix are converted to a standard sRGB albedo so glTF preserves the shader.
"""
from pathlib import Path
import hashlib,json,struct,zlib,shutil,binascii
ROOT=Path('/Users/alejandro/Projects/HelloWorld');SRC=Path('/Users/alejandro/Projects/Portfolio/assets/world2-source/textures/slabs.png');OUT=ROOT/'assets/surfaces/world2';OUT.mkdir(parents=True,exist_ok=True)
data=SRC.read_bytes();offset=8;chunks={}
while offset<len(data):
 n=struct.unpack_from('>I',data,offset)[0];kind=data[offset+4:offset+8];chunks.setdefault(kind,[]).append(data[offset+8:offset+8+n]);offset+=n+12
w,h,depth,kind,*_=struct.unpack('>IIBBBBB',chunks[b'IHDR'][0]);assert(depth,kind)==(8,6)
raw=zlib.decompress(b''.join(chunks[b'IDAT']));stride=w*4;rows=[];previous=bytearray(stride)
def paeth(a,b,c):
 p=a+b-c;d=[abs(p-a),abs(p-b),abs(p-c)];return [a,b,c][d.index(min(d))]
for y in range(h):
 method=raw[y*(stride+1)];row=bytearray(raw[y*(stride+1)+1:(y+1)*(stride+1)])
 for x in range(stride):
  a=row[x-4] if x>=4 else 0;b=previous[x];c=previous[x-4] if x>=4 else 0
  row[x]=(row[x]+[0,a,b,(a+b)//2,paeth(a,b,c)][method])&255
 rows.append(row);previous=row
A=[.39157015085220337,.18447518348693848,.1221388429403305];B=[1,.6239606738090515,.25818297266960144]
def linear(c):
 c=c/255;return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
def srgb(c):return round(255*(12.92*c if c<=.0031308 else 1.055*c**(1/2.4)-.055))
encoded=[]
for row in rows:
 out=bytearray()
 for i in range(0,len(row),4):
  assert row[i]==row[i+1]==row[i+2], 'Source must be grayscale to retain exact Blender colour→factor conversion'
  t=linear(row[i]);out.extend([srgb(a+(b-a)*t) for a,b in zip(A,B)]+[255])
 encoded.append(b'\0'+out)
def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',binascii.crc32(kind+data)&0xffffffff)
result=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'sRGB',b'\0')+chunk(b'IDAT',zlib.compress(b''.join(encoded),9))+chunk(b'IEND',b'')
shutil.copyfile(SRC,OUT/'slabs.png');(OUT/'slabs-albedo.png').write_bytes(result)
manifest=dict(source='Portfolio/assets/world2-source/textures/slabs.png',sourceSHA256=hashlib.sha256(data).hexdigest(),albedoSHA256=hashlib.sha256(result).hexdigest(),width=w,height=h,material='terrain',node='Mix.005',maskColorSpace='sRGB',linearColors=[A,B],positionMultiply=.20000000298023224,tileMetres=1/.20000000298023224,uv='[worldX * positionMultiply, -worldZ * positionMultiply]',roughness=.5,metalness=0,normalMap=None,bump=None,interpolation='Linear',extension='REPEAT',projection='FLAT')
(OUT/'slabs-source.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
