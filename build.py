import os
import random
import sys

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, 'src'))

from pages import CLOUDFLARE, HAPROXY



def render(template, values):
    out = template
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
