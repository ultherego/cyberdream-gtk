from . import Target

TARGET = Target(
    name="gtk-4.0",
    base="an overlay on libadwaita for gtk-4.0",
    named_sections=("common", "gtk4"),
    templates=("common.css", "gtk4.css"),
)
