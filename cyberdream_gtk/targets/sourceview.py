"""GtkSourceView 5 color scheme: the editor area of Text Editor and similar
apps is painted from a style scheme, not from the GTK theme."""

from . import Target

TARGET = Target(
    name="gtksourceview-5",
    base="GtkSourceView 5",
    templates=("sourceview.xml",),
    output="cyberdream.xml",
    kind="file",
    root="data",
    dest="gtksourceview-5/styles",
)
