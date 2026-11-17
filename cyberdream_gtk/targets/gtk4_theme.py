"""GTK4 part of the "cyberdream" theme, for GTK4 apps without libadwaita.

Interim: it imports adw-gtk3-dark's GTK4 stylesheet from the sibling theme
directory and recolors it. libadwaita apps ignore GTK themes and are covered
by the gtk-4.0 overlay instead."""

from . import Target

TARGET = Target(
    name="themes/cyberdream/gtk-4.0",
    base="GTK4 theme for non-libadwaita apps (interim, on adw-gtk3-dark)",
    named_sections=("common", "gtk4"),
    templates=("gtk4-theme/interim.css",),
    output="gtk.css",
    prelude='@import url("../../adw-gtk3-dark/gtk-4.0/gtk-dark.css");\n',
    kind="file",
    root="home",
    dest=".themes/cyberdream/gtk-4.0",
)
