#!/bin/sh
# Remove the cyberdream-gtk overlay (cyberdream.css and its @import line).
# A backup is made first. Use --dry-run to preview.
set -eu
cd "$(dirname "$0")"
exec python3 -m cyberdream_gtk uninstall "$@"
