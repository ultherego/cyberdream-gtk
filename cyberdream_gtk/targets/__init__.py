"""Output targets.

A target is one generated file. Two kinds exist:

  gtk-overlay  CSS for ~/.config/<name>/: named colors plus a few rules on top
               of a base theme; installed next to a gtk.css that imports it.
  file         any other file rendered from templates and copied into place
               (a standalone theme stylesheet, an editor color scheme).

A target with named_sections starts with a block of @define-color lines.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Target:
    name: str                    # build subdirectory; for overlays also the config dir
    base: str                    # one-line description for the header comment
    templates: tuple[str, ...]   # files from templates/, concatenated in order
    named_sections: tuple[str, ...] = ()   # [named.*] tables from roles.toml
    output: str = "cyberdream.css"
    prelude: str = ""            # raw text placed first (e.g. an @import line)
    kind: str = "gtk-overlay"    # "gtk-overlay" or "file"
    root: str = "config"         # install under XDG "config" / "data" home, or "home"
    dest: str = ""               # directory below root; defaults to name
    install: bool = True         # False: only built, placed by hand

    @property
    def install_dir(self) -> str:
        return self.dest or self.name


from .gtk3 import TARGET as GTK3  # noqa: E402
from .gtk4 import TARGET as GTK4  # noqa: E402
from .sourceview import TARGET as SOURCEVIEW  # noqa: E402
from .firefox import TARGET as FIREFOX  # noqa: E402
from .geany import TARGET as GEANY  # noqa: E402
from .gtk3_theme import INDEX as THEME_INDEX  # noqa: E402
from .gtk3_theme import DARK as GTK3_THEME_DARK  # noqa: E402
from .gtk3_theme import TARGET as GTK3_THEME  # noqa: E402
from .gtk4_theme import DARK as GTK4_THEME_DARK  # noqa: E402
from .gtk4_theme import TARGET as GTK4_THEME  # noqa: E402

ALL: tuple[Target, ...] = (GTK3, GTK4, SOURCEVIEW, GEANY, THEME_INDEX, GTK3_THEME, GTK3_THEME_DARK, GTK4_THEME, GTK4_THEME_DARK, FIREFOX)
