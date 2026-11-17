from . import Target

TARGET = Target(
    name="gtk-3.0",
    base="an overlay on adw-gtk3-dark for gtk-3.0",
    named_sections=("common", "gtk3"),
    templates=("common.css", "gtk3.css"),
)
