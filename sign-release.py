import base64,hashlib,json,os,re,time
from urllib.request import urlopen
from urllib.error import HTTPError
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from release_rules import check_promotion
tag=os.environ['RELEASE_TAG'];companion=os.environ['COMPANION_VERSION'];addon=os.environ['ADDON_VERSION'];channel=os.environ['CHANNEL']
target=os.environ['COMPANION_TARGET']
if target not in ('forever-atlas-windows','legacy-python'):raise SystemExit('Invalid installer target')
if not re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+(?:-[a-z0-9.]+)?',tag):raise SystemExit('Invalid version tag')
if channel not in ('preview','stable'):raise SystemExit('Invalid channel')
for version in (companion,addon):
    if not re.fullmatch(r'[0-9][a-z0-9.+-]{1,39}',version):raise SystemExit('Invalid version')
base='https://github.com/apb-hello-world/forever-atlas-releases/releases/download/'+tag+'/'
def item(name,version):
    data=Path('artifacts',name).read_bytes()
    return dict(version=version,url=base+name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
payload=dict(schema=1,channel=channel,protocol=1,issued=int(time.time()),expires=int(time.time())+90*86400,
             companion=item('ForeverAtlas-Setup.exe',companion),addon=item('ForeverMap-addon.zip',addon))
payload['companion']['target']=target
raw=json.dumps(payload,separators=(',',':'),sort_keys=True).encode()
key=Ed25519PrivateKey.from_private_bytes(base64.b64decode(os.environ['RELEASE_SIGNING_KEY'],validate=True))
previous=None
try:
    with urlopen('https://github.com/apb-hello-world/forever-atlas-releases/releases/download/'+channel+'/manifest.json',timeout=30) as response:
        current=response.read(65537)
        if len(current)>65536:raise ValueError('Oversized previous manifest')
    envelope=json.loads(current)
    old_raw=base64.b64decode(envelope['payload'],validate=True)
    key.public_key().verify(base64.b64decode(envelope['signature'],validate=True),old_raw)
    previous=json.loads(old_raw)
except HTTPError as error:
    if error.code!=404:raise
check_promotion(tag,companion,addon,channel,previous)
Path('manifest.json').write_text(json.dumps(dict(payload=base64.b64encode(raw).decode(),signature=base64.b64encode(key.sign(raw)).decode()),indent=2)+'\n')
print('Signed release metadata for '+tag)
