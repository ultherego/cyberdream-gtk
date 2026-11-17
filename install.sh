#!/bin/sh
# Build and install cyberdream-gtk into ~/.config/gtk-3.0 and ~/.config/gtk-4.0.
# Everything touched is backed up first; the undo command is printed at the end.
#
#   ./install.sh              build + install
#   ./install.sh --dry-run    show what would change
#   ./install.sh --restore ~/.config/gtk-cyberdream-bak-YYYYMMDD-HHMMSS
set -eu
cd "$(dirname "$0")"

if [ "${1:-}" = "--restore" ]; then
	[ $# -ge 2 ] || { echo "usage: $0 --restore BACKUP_DIR" >&2; exit 2; }
	shift
	exec python3 -m cyberdream_gtk restore "$@"
fi
exec python3 -m cyberdream_gtk install "$@"
