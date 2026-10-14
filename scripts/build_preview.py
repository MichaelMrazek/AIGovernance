"""Build a single-file preview that works without a web server."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
html = (root / 'index.html').read_text()
css = (root / 'styles.css').read_text()
# A downloaded preview should work without network access, including fonts.
css = '\n'.join(line for line in css.splitlines() if not line.startswith('@import'))
data = json.loads((root / 'data/articles.json').read_text())
encoded = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
js = (root / 'app.js').read_text()
js = js.replace("const response=await fetch('./data/articles.json',{cache:'no-cache'});if(!response.ok)throw new Error(`HTTP ${response.status}`);const data=await response.json();", 'const data=window.PREVIEW_BRIEFING;')
html = html.replace('<link rel="stylesheet" href="styles.css">', '<style>' + css + '</style>')
html = html.replace('<script src="app.js" defer></script>', '')
html = html.replace('</body>', '<script>window.PREVIEW_BRIEFING=' + encoded + ';</script><script>' + js + '</script></body>')
(root / 'preview.html').write_text(html)
print('Built preview.html with embedded styling, scripts, and stories.')
