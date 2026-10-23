#!/usr/bin/env python3
# parse every espresso css file in a GtkCssProvider
# usage: python3 tokens/check-css.py
import pathlib
import re
import sys

import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk  # noqa: E402

theme = pathlib.Path(__file__).resolve().parent.parent
entries = [theme / 'gtk-4.0/gtk.css', theme / 'gtk-4.0/gtk-dark.css']

defined = set()
for path in (theme / 'gtk-4.0').glob('_tokens-*.css'):
    defined |= set(re.findall(r'@define-color\s+(\w+)', path.read_text()))

failed = False
for path in entries:
    if not path.exists():
        continue
    provider = Gtk.CssProvider()
    errors = []

    def on_error(_provider, section, error, errors=errors):
        loc = section.get_start_location()
        name = section.get_file().get_path() if section.get_file() else str(path)
        errors.append(f'{name}:{loc.lines}:{loc.line_chars}: {error.message}')

    text = path.read_text()
    used = set(re.findall(r'@(es_\w+)', text))
    missing = sorted(used - defined)
    if missing:
        failed = True
        print(f'FAIL {path.relative_to(theme)} unknown tokens')
        for token in missing:
            print(f'  @{token}')

    provider.connect('parsing-error', on_error)
    provider.load_from_path(str(path))
    if errors:
        failed = True
        print(f'FAIL {path.relative_to(theme)}')
        for line in errors:
            print(f'  {line}')
    else:
        print(f'ok   {path.relative_to(theme)}')

sys.exit(1 if failed else 0)
