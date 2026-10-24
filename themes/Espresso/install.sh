#!/bin/sh
# link the theme into the user data dir for development
set -e

here=$(cd "$(dirname "$0")" && pwd)
data=${XDG_DATA_HOME:-$HOME/.local/share}
target="$data/themes/Espresso"

mkdir -p "$data/themes"
ln -sfn "$here" "$target"
echo "linked $target"

if [ "$1" = "--user-css" ]; then
    conf=${XDG_CONFIG_HOME:-$HOME/.config}/gtk-4.0
    mkdir -p "$conf"
    cat > "$conf/gtk.css" <<EOF
/* espresso accents for libadwaita apps */
@import url("$here/gtk-4.0/_tokens-light.css");
@define-color accent_bg_color @es_accent;
@define-color accent_fg_color @es_accent_fg;
@define-color accent_color @es_accent;
EOF
    echo "wrote $conf/gtk.css"
fi
