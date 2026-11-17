"""Firefox tab colors, as a stylesheet for the profile's chrome/ directory.

Firefox computes its tab colors itself, so a GTK theme cannot set them. The
profile directory differs per installation, so this target is built but not
installed; the header of the generated file says where to put it."""

from . import Target

TARGET = Target(
    name="firefox",
    base="Firefox tab colors",
    templates=("firefox.css",),
    output="cyberdream.css",
    kind="file",
    install=False,
)
