from . import Target

TARGET = Target(
    name="gtk-4.0",
    base="libadwaita",
    named_sections=("common", "gtk4"),
    templates=("common.css", "gtk4.css"),
)
