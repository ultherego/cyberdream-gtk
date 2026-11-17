"""Geany color scheme: Geany paints its editor from its own scheme files."""

from . import Target

TARGET = Target(
    name="geany",
    base="Geany",
    templates=("geany.conf",),
    output="cyberdream.conf",
    kind="file",
    root="config",
    dest="geany/colorschemes",
)
