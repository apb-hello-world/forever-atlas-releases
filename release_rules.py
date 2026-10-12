"""Channel promotion rules shared by signing and tests."""
import re

def version_key(value):
    match=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)(?:-?(a|alpha\.?|b|beta\.?|rc\.?)(\d+))?',value)
    if not match:raise ValueError('Invalid release version')
    stage=match[4] or ''
    rank=0 if stage.startswith('a') else 1 if stage.startswith('b') else 2 if stage.startswith('rc') else 3
    return tuple(map(int,match.group(1,2,3)))+(rank,int(match[5] or 0))

def check_promotion(tag,companion,addon,channel,previous=None):
    if version_key(tag.removeprefix('v'))!=version_key(companion):raise ValueError('Tag does not match companion version')
    if channel=='stable' and version_key(companion)[3]!=3:raise ValueError('Prerelease cannot be promoted to Stable')
    if previous:
        if previous['channel']!=channel:raise ValueError('Wrong previous channel')
        for name,current in (('companion',companion),('addon',addon)):
            if version_key(previous[name]['version'])>version_key(current):raise ValueError('Refusing to roll back channel '+name)
