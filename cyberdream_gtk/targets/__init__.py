"""Output targets.

A target is one generated file. Two kinds exist:

  gtk-overlay  CSS for ~/.config/<name>/: named colors plus a few rules on top
               of a base theme; installed next to a gtk.css that imports it.
  file         any other file rendered from templates and copied into place
               (an editor color scheme, later perhaps a Kvantum theme).

A full standalone stylesheet (Phase 2) is added as another module here and
listed in ALL; nothing else in the generator needs to change.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Target:
    name: str                    # build subdirectory; for overlays also the config dir
    base: str                    # what this sits on (for the header comment)
    templates: tuple[str, ...]   # files from templates/, concatenated in order
    named_sections: tuple[str, ...] = ()   # [named.*] tables from roles.toml
    output: str = "cyberdream.css"
    kind: str = "gtk-overlay"    # "gtk-overlay" or "file"
    root: str = "config"         # install under XDG "config" or "data" home
    dest: str = ""               # directory below root; defaults to name

    @property
    def install_dir(self) -> str:
        return self.dest or self.name


from .gtk3 import TARGET as GTK3  # noqa: E402
from .gtk4 import TARGET as GTK4  # noqa: E402
from .sourceview import TARGET as SOURCEVIEW  # noqa: E402

ALL: tuple[Target, ...] = (GTK3, GTK4, SOURCEVIEW)
