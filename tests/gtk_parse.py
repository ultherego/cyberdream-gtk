"""Parse a CSS file with the real GTK parser; exit 1 and print errors if any.

Usage: python3 gtk_parse.py {3.0|4.0} FILE
Run as a separate process per GTK version (they cannot share one).
"""

import sys

import gi

version, path = sys.argv[1], sys.argv[2]
gi.require_version("Gtk", version)
from gi.repository import GLib, Gtk  # noqa: E402

errors = []
provider = Gtk.CssProvider()


def on_error(_provider, section, error):
    if version == "4.0":
        where = section.to_string()
    else:
        where = f"line {section.get_start_line() + 1}"
    errors.append(f"{where}: {error.message}")


provider.connect("parsing-error", on_error)
try:
    provider.load_from_path(path)
except GLib.Error as exc:  # GTK3 raises on the first error as well
    if not errors:
        errors.append(exc.message)

for line in errors:
    print(line)
sys.exit(1 if errors else 0)
