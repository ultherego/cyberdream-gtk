#!/bin/sh
# Render the GTK3 gallery with the freshly built standalone theme, offscreen.
# Nothing is installed and no window appears: GTK runs on a private Broadway
# display, with an empty config directory and the theme taken from build/.
#
#   tools/render.sh [OUT.png]      (default: build/gallery-gtk3.png)
set -eu
cd "$(dirname "$0")/.."
out=${1:-$PWD/build/gallery-gtk3.png}
python3 -m cyberdream_gtk build >/dev/null
tmp=$(mktemp -d)
display=:97
broadwayd "$display" >/dev/null 2>&1 &
pid=$!
trap 'kill $pid 2>/dev/null; rm -rf "$tmp"' EXIT
python3 -c 'import time; time.sleep(1)'
GDK_BACKEND=broadway BROADWAY_DISPLAY="$display" \
	XDG_CONFIG_HOME="$tmp" XDG_DATA_HOME="$PWD/build" GTK_THEME=cyberdream \
	timeout 30 python3 tools/gallery_gtk3.py "$out" 2>&1 | grep -v -i -e deprecat -e pixman -e breakpoint -e '^$' || true
