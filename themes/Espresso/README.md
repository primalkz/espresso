# espresso

A GTK theme built from the Frappe Espresso design tokens.

GTK4 is the target. GTK3 is a port of the same selectors. GTK2 gets the
palette only. The full rules are in `PLAN.md`.

## install

For development, link it:

```sh
./install.sh
```

That puts a symlink at `~/.local/share/themes/espresso`. For a real install,
`meson install` copies `data/themes` into the data dir.

## fonts

espresso is designed around Inter. The theme does not force a font family,
so the system font picker keeps working. For the intended look set Inter as
the system font. `tests/shot.sh` uses a throwaway config with Inter 10.

## use

```sh
gsettings set org.gnome.desktop.interface gtk-theme espresso
```

or set `gtk-theme-name=espresso` in `~/.config/gtk-4.0/settings.ini`.
Dark mode uses the same theme. Set `color-scheme` to `prefer-dark` and GTK
loads `gtk-dark.css`.

Test a single app without changing the session:

```sh
GTK_THEME=Espresso app
GTK_THEME=Espresso:dark app
```

## libadwaita

libadwaita apps ignore GTK themes. They only read the system accent and the
user CSS file. `install.sh --user-css` writes an optional
`~/.config/gtk-4.0/gtk.css` that maps the Espresso colors for those apps. It is
off by default because it overrides every GTK4 app the user runs.

## tokens

`tokens/tokens.json` is a pinned copy of `frappe/frappe-ui` `tailwind/tokens`.
Regenerate the color maps after a token sync:

```sh
node tokens/gen-css.mjs
node tokens/gen-gtk2.mjs
```

The generated files are committed, so building the theme needs no node.

## checks

```sh
python3 tokens/check-css.py
GTK_THEME=Espresso python3 tests/gallery.py Buttons --shot /tmp/espresso.png
```

The gallery renders itself, so it works without a compositor screenshot tool.

## credit

Design tokens and component metrics: Frappe Espresso, `frappe/frappe-ui`,
MIT. The theme code is GPL-3.0-or-later.
