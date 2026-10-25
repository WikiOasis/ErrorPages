import os
import random
import sys

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, 'src'))

from pages import CLOUDFLARE, HAPROXY


CELL = 110
COLS = 7
GRADIENTS = [('gA', '#6fc5f1', '#2f8fd6'), ('gB', '#4aa8e8', '#2470bd'), ('gC', '#2c6fb0', '#184f86'), ('gD', '#8fd8f7', '#4aa8e8')]
WEIGHTS = [4, 4, 3, 1]


def decor_svg():
    rng = random.Random(11)
    size = CELL * COLS
    half = CELL / 2
    defs = ''.join(
        '<linearGradient id="%s" x1="0.15" y1="0" x2="0.85" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % g
        for g in GRADIENTS
    )
    keep = {0: 1, 1: 1, 2: 1, 3: 1, 4: 0.85, 5: 0.6, 6: 0.3, 7: 0.12}
    tiles = []
    for row in range(COLS):
        for col in range(COLS):
            distance = (COLS - 1 - row) + (COLS - 1 - col)
            if rng.random() > keep.get(distance, 0):
                continue
            gradient = rng.choices(GRADIENTS, WEIGHTS)[0][0]
            turn = rng.randrange(4) * 90
            tiles.append(
                '<g transform="translate(%d,%d)"><path class="tile" data-r="%d" style="transform-origin:%spx %spx;transform:rotate(%ddeg)" d="M0,0 L%d,0 A%d,%d 0 0 1 0,%d Z" fill="url(#%s)"/></g>'
                % (col * CELL, row * CELL, turn, half, half, turn, CELL, CELL, CELL, CELL, gradient)
            )
    return '<svg class="decor" viewBox="0 0 %d %d" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"><defs>%s</defs>%s</svg>' % (size, size, defs, ''.join(tiles))


def render(template, values):
    out = template.replace('@@decor@@', decor_svg())
    for key, value in values.items():
        out = out.replace('@@%s@@' % key, value)
    return out


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)


def haproxy_html(base, page):
    values = {k: v for k, v in page.items() if k != 'headers'}
    values['code'] = str(page['code'])
    return render(base, values)


def build_html():
    with open(os.path.join(ROOT, 'src', 'base.html'), encoding='utf-8') as f:
        base = f.read()
    for page in HAPROXY:
        write(os.path.join(ROOT, 'haproxy', '%d.html' % page['code']), haproxy_html(base, page))
    for page in CLOUDFLARE:
        values = {k: v for k, v in page.items() if k != 'path'}
        write(os.path.join(ROOT, page['path']), render(base, values))


def build_http(outdir):
    with open(os.path.join(ROOT, 'src', 'base.html'), encoding='utf-8') as f:
        base = f.read()
    os.makedirs(outdir, exist_ok=True)
    for page in HAPROXY:
        body = haproxy_html(base, page).encode('utf-8')
        headers = [
            'HTTP/1.1 %d %s' % (page['code'], page['reason']),
            'Content-Type: text/html; charset=utf-8',
            'Content-Length: %d' % len(body),
            'Cache-Control: no-store',
            'Connection: close',
        ] + ['%s: %s' % kv for kv in page['headers'].items()]
        target = os.path.join(outdir, '%d.http' % page['code'])
        with open(target + '.new', 'wb') as f:
            f.write(('\r\n'.join(headers) + '\r\n\r\n').encode('ascii') + body)
        os.replace(target + '.new', target)


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'http':
        build_http(sys.argv[2])
    elif len(sys.argv) == 1:
        build_html()
    else:
        sys.exit('usage: build.py [http OUTDIR]')
