"""Installing the generated files.

GTK overlays go to ~/.config/gtk-{3,4}.0: cyberdream.css is copied and gtk.css
gets one @import line. Other targets are single files copied into place (the
GtkSourceView scheme goes to ~/.local/share/gtksourceview-5/styles).
Everything touched is backed up first.

How this coexists with DankMaterialShell (checked against dms 2.0.0.r45):
DMS only ever adds or removes its own `@import url("dank-colors.css");` line
in gtk.css, or a symlink gtk.css -> dank-colors.css. It leaves other lines
alone. Our import goes after DMS's, so our colors win.
"""

from __future__ import annotations

import json
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .targets import ALL as ALL_TARGETS
from .targets import Target

ALL = tuple(t for t in ALL_TARGETS if t.install)

IMPORT_LINE = '@import url("cyberdream.css");'
IMPORT_RE = re.compile(r'^\s*@import\s+(url\()?["\']cyberdream\.css["\']\)?\s*;\s*$')
ANY_IMPORT_RE = re.compile(r"^\s*@import\b")
DANK_IMPORT_LINE = '@import url("dank-colors.css");'
BACKUP_PREFIX = "gtk-cyberdream-bak-"
MANIFEST = "manifest.json"


class InstallError(RuntimeError):
    pass


@dataclass(frozen=True)
class Roots:
    """The XDG directories files are installed under."""

    config: Path
    data: Path
    home: Path

    @classmethod
    def default(cls) -> Roots:
        home = Path.home()
        return cls(
            Path(os.environ.get("XDG_CONFIG_HOME") or home / ".config"),
            Path(os.environ.get("XDG_DATA_HOME") or home / ".local" / "share"),
            home,
        )

    def path(self, key: str) -> Path:
        """Resolve a manifest key such as "data:gtksourceview-5/styles/x.xml"."""
        root, sep, rel = key.partition(":")
        if not sep:  # manifests written before the data root existed
            root, rel = "config", key
        if root not in ("config", "data", "home"):
            raise InstallError(f"unknown root in backup manifest: {key!r}")
        return getattr(self, root) / rel


def _keys(target: Target) -> list[str]:
    base = f"{target.root}:{target.install_dir}"
    keys = [f"{base}/{target.output}"]
    if target.kind == "gtk-overlay":
        keys.append(f"{base}/gtk.css")
    return keys


def _read_gtk_css(path: Path) -> str:
    """Current gtk.css content, treating a DMS symlink as its import line."""
    if path.is_symlink():
        link = os.readlink(path)
        if "dank-colors.css" in link:
            return DANK_IMPORT_LINE + "\n"
        if "themes/cyberdream/" in link:
            # Theme switchers such as nwg-look link the selected theme's GTK4
            # stylesheet here. For libadwaita that must be the overlay instead.
            return ""
        raise InstallError(
            f"{path} is a symlink to {link} that this tool did not "
            "expect; not touching it. Add this line to your stylesheet yourself:\n"
            f"  {IMPORT_LINE}"
        )
    return path.read_text(encoding="utf-8") if path.exists() else ""


def add_import(text: str) -> str:
    lines = text.splitlines()
    if any(IMPORT_RE.match(line) for line in lines):
        return text
    # @import must precede all rules, and we must come after other imports.
    last = max((i for i, line in enumerate(lines) if ANY_IMPORT_RE.match(line)), default=-1)
    lines.insert(last + 1, IMPORT_LINE)
    return "\n".join(lines) + "\n"


def remove_import(text: str) -> str:
    lines = [line for line in text.splitlines() if not IMPORT_RE.match(line)]
    return "\n".join(lines) + "\n" if lines else ""


def _write(path: Path, text: str) -> None:
    if path.is_symlink():
        path.unlink()
    path.write_text(text, encoding="utf-8")


def backup(roots: Roots, log=print, dry_run: bool = False) -> Path:
    stem = BACKUP_PREFIX + datetime.now().strftime("%Y%m%d-%H%M%S")
    dest, n = roots.config / stem, 1
    while dest.exists():  # never reuse an existing backup directory
        n += 1
        dest = roots.config / f"{stem}-{n}"
    manifest = {}
    for key in (k for t in ALL for k in _keys(t)):
        path = roots.path(key)
        manifest[key] = "symlink" if path.is_symlink() else "file" if path.exists() else "absent"
    log(f"backup -> {dest}")
    if dry_run:
        return dest
    dest.mkdir(parents=True)
    for key, kind in manifest.items():
        if kind != "absent":
            saved = dest / key.replace(":", "/", 1)
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(roots.path(key), saved, follow_symlinks=False)
    (dest / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return dest


def _same(a: Path, b: Path) -> bool:
    return b.is_file() and not b.is_symlink() and a.read_bytes() == b.read_bytes()


def install(
    build_dir: Path, roots: Roots | None = None, dry_run: bool = False, log=print
) -> Path | None:
    """Install every target. Returns the backup directory, or None when
    everything was already up to date (then nothing is touched or backed up)."""
    roots = roots or Roots.default()
    plan = []
    for target in ALL:
        source = build_dir / target.name / target.output
        if not source.is_file():
            raise InstallError(f"missing build output: {source}")
        directory = getattr(roots, target.root) / target.install_dir
        gtk_css = new_text = None
        if target.kind == "gtk-overlay":
            gtk_css = directory / "gtk.css"
            new_text = add_import(_read_gtk_css(gtk_css))
        plan.append((source, directory / target.output, gtk_css, new_text))

    def current(item) -> bool:
        source, out, gtk_css, new_text = item
        return _same(source, out) and (
            gtk_css is None
            or (gtk_css.is_file() and not gtk_css.is_symlink()
                and gtk_css.read_text(encoding="utf-8") == new_text)
        )

    plan = [item for item in plan if not current(item)]
    if not plan:
        log("already up to date")
        return None

    dest = backup(roots, log, dry_run)
    for source, out, gtk_css, new_text in plan:
        log(f"write  {out}")
        if gtk_css:
            log(f"ensure {gtk_css} imports cyberdream.css")
        if dry_run:
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, out)
        if gtk_css and (
            gtk_css.is_symlink()
            or not gtk_css.exists()
            or gtk_css.read_text(encoding="utf-8") != new_text
        ):
            _write(gtk_css, new_text)
    return dest


def uninstall(roots: Roots | None = None, dry_run: bool = False, log=print) -> Path:
    roots = roots or Roots.default()
    dest = backup(roots, log, dry_run)
    for target in ALL:
        directory = getattr(roots, target.root) / target.install_dir
        out = directory / target.output
        if out.exists():
            log(f"remove {out}")
            if not dry_run:
                out.unlink()
        gtk_css = directory / "gtk.css"
        if target.kind != "gtk-overlay" or gtk_css.is_symlink() or not gtk_css.exists():
            continue
        old = gtk_css.read_text(encoding="utf-8")
        new = remove_import(old)
        if new != old:
            log(f"remove cyberdream import from {gtk_css}")
            if not dry_run:
                gtk_css.write_text(new, encoding="utf-8") if new else gtk_css.unlink()
    return dest


def restore(backup_dir: Path, roots: Roots | None = None, dry_run: bool = False, log=print) -> None:
    roots = roots or Roots.default()
    manifest_path = backup_dir / MANIFEST
    if not manifest_path.is_file():
        raise InstallError(f"not a cyberdream-gtk backup (no {MANIFEST}): {backup_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key, kind in manifest.items():
        path = roots.path(key)
        log(f"{'remove ' if kind == 'absent' else 'restore'} {path}")
        if dry_run:
            continue
        if path.is_symlink() or path.exists():
            path.unlink()
        if kind != "absent":
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_dir / key.replace(":", "/", 1), path, follow_symlinks=False)
