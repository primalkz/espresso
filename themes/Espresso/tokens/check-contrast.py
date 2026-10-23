#!/usr/bin/env python3
# wcag contrast for the token pairs the theme actually composes
import json
import math
import pathlib

TOKENS = pathlib.Path(__file__).resolve().parent / 'tokens.json'


def parse(value):
    v = value.strip()
    if v.startswith('oklch('):
        body = v[6:-1].replace('/', ' ').split()
        L, C, H = (float(x) for x in body[:3])
        alpha = float(body[3]) if len(body) > 3 else 1.0
        h = math.radians(H)
        a, b = C * math.cos(h), C * math.sin(h)
        l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
        m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
        s = (L - 0.0894841775 * a - 1.291485548 * b) ** 3
        rgb = (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
               -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
               -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s)
        lin = tuple(max(0.0, min(1.0, x)) for x in rgb)
        enc = tuple(12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055 for x in lin)
        return enc + (alpha,)
    if v.startswith('#') and len(v) in (7, 9):
        rgb = tuple(int(v[i:i + 2], 16) / 255 for i in (1, 3, 5))
        alpha = int(v[7:9], 16) / 255 if len(v) == 9 else 1.0
        return rgb + (alpha,)
    return (0, 0, 0, 1)


def over(fg, bg):
    a = fg[3]
    return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3)) + (1,)


def lum(c):
    r, g, b = (x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    fg = over(fg, bg)
    a, b = sorted((lum(fg), lum(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


data = json.loads(TOKENS.read_text())
colors = data['colors']
themed = colors['themedVariables']


def resolve(ref):
    parts = ref.split('/')
    if parts[0] == 'neutral':
        return parse(colors['neutral'][parts[1]])
    mode, family, step = parts
    return parse(colors[mode][family][step])


def get(mode, group, key):
    return resolve(themed[mode][group][key])


PAIRS = [
    ('body on surface', 'ink', 'gray-8', 'surface', 'base'),
    ('secondary on surface', 'ink', 'gray-6', 'surface', 'base'),
    ('muted on surface', 'ink', 'gray-5', 'surface', 'base'),
    ('disabled on surface', 'ink', 'gray-3', 'surface', 'base'),
    ('link on surface', 'ink', 'blue-link', 'surface', 'base'),
    ('text on accent', 'ink', 'base', 'surface', 'blue-6'),
    ('text on destructive', 'ink', 'base', 'surface', 'red-7'),
    ('text on success', 'ink', 'base', 'surface', 'green-7'),
    ('tooltip text', 'surface', 'base', 'ink', 'gray-9'),
]

fail = 0
for mode in ('light', 'dark'):
    print(mode)
    for label, fg_group, fg_key, bg_group, bg_key in PAIRS:
        r = ratio(get(mode, fg_group, fg_key), get(mode, bg_group, bg_key))
        need = 3.0 if 'disabled' in label else 4.5
        mark = 'ok' if r >= need else 'LOW'
        if r < need and 'disabled' not in label:
            fail += 1
        print(f'  {label:24} {r:5.2f}  {mark}')
    print()

raise SystemExit(1 if fail else 0)
