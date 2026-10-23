#!/usr/bin/env python3
# parse the gtk3 theme files in a Gtk3 CssProvider
import pathlib
import sys

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa: E402

Gtk.init([])

theme = pathlib.Path(__file__).resolve().parent.parent
failed = False

for path in [theme / 'gtk-3.0/gtk.css', theme / 'gtk-3.0/gtk-dark.css']:
    if not path.exists():
        continue
    provider = Gtk.CssProvider()
    errors = []

    def on_error(_provider, section, error, errors=errors, path=path):
        line = section.get_start_line() + 1
        name = section.get_file().get_path() if section.get_file() else str(path)
        errors.append(f'{name}:{line}: {error.message}')

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
