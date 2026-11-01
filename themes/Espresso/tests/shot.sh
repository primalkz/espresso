#!/bin/sh
# usage: tests/shot.sh <page> <out.png> [dark]
set -e
page=${1:-Buttons}
out=${2:-/tmp/espresso.png}
theme=espresso
[ "$3" = "dark" ] && theme=espresso:dark
GTK_THEME=$theme GDK_BACKEND=wayland python3 "$(dirname "$0")/gallery.py" "$page" --shot "$out"
echo "$out"
