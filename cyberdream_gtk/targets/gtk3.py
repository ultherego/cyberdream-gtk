from . import Target

TARGET = Target(
    name="gtk-3.0",
    base="adw-gtk3-dark",
    named_sections=("common", "gtk3"),
    templates=("common.css", "gtk3.css"),
)
