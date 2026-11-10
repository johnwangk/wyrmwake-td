#!/usr/bin/env python3
"""Refresh the file:// fallback copy of assets/manifest.json inside index.html.
Only needed for opening index.html straight from disk (browsers block fetch on file://).
Over http (GitHub Pages, python3 -m http.server) the game always reads assets/manifest.json."""
import json, re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
m = json.loads((root/'assets/manifest.json').read_text())
keep = ('id','path','category','frame_w','frame_h','frames','fps','loop','anchor','hit_frame','dragon','level','anim','enemy','state','facing','rotatable','states','text_area','slice','layout','enhancement','title','effect','safe_areas')
compact = {'sheets': [{k: s[k] for k in keep if k in s} for s in m.get('sheets', [])]}
html = (root/'index.html').read_text()
new = '/*FILE_FALLBACK_BEGIN*/const FILE_FALLBACK_MANIFEST = ' + json.dumps(compact, separators=(',',':')) + ';/*FILE_FALLBACK_END*/'
html, n = re.subn(r'/\*FILE_FALLBACK_BEGIN\*/.*?/\*FILE_FALLBACK_END\*/', lambda _: new, html, flags=re.S)
assert n == 1, 'marker not found'
(root/'index.html').write_text(html); print('embedded', len(compact['sheets']), 'sheets')
