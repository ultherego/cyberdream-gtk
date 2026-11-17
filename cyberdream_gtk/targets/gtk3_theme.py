"""Standalone GTK3 theme "cyberdream": a complete stylesheet that does not
depend on any other theme. Installed as ~/.themes/cyberdream so it can be
selected by name (and so Flatpak apps with access to ~/.themes find it)."""

from . import Target

PARTS = ("base", "buttons", "entries", "headerbar", "menus", "views", "controls", "containers", "misc")

TARGET = Target(
    name="themes/cyberdream/gtk-3.0",
    base="a standalone GTK3 theme",
    named_sections=("common", "gtk3"),
    templates=tuple(f"gtk3-theme/{part}.css" for part in PARTS),
    output="gtk.css",
    kind="file",
    root="home",
    dest=".themes/cyberdream/gtk-3.0",
)

INDEX = Target(
    name="themes/cyberdream",
    base="theme index",
    templates=("index.theme",),
    output="index.theme",
    kind="file",
    root="home",
    dest=".themes/cyberdream",
)

# libhandy apps in dark mode only accept a theme that has a gtk-dark.css;
# without it they fall back to Adwaita. The theme is dark-only, so the dark
# variant is the same stylesheet.
DARK = Target(
    name="themes/cyberdream/gtk-3.0",
    base="dark variant",
    templates=(),
    output="gtk-dark.css",
    prelude='@import url("gtk.css");\n',
    kind="file",
    root="home",
    dest=".themes/cyberdream/gtk-3.0",
)
