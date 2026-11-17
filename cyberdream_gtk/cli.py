"""Command line: python3 -m cyberdream_gtk <command>."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__, install as inst
from .palette import ROOT, Theme, ThemeError
from .render import build


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cyberdream_gtk", description=__doc__)
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--palette", type=Path, help="palette file (default: palette.toml)")
    parser.add_argument("--roles", type=Path, help="roles file (default: roles.toml)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("build", help="generate files into build/")
    p.add_argument("--out", type=Path, default=ROOT / "build")

    p = sub.add_parser("install", help="build, back up, install")
    p.add_argument("--dry-run", action="store_true", help="show what would change")

    p = sub.add_parser("uninstall", help="back up, then remove the overlay")
    p.add_argument("--dry-run", action="store_true")

    p = sub.add_parser("restore", help="put back the files saved in a backup")
    p.add_argument("backup", type=Path)
    p.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.command in ("build", "install"):
            theme = Theme.load(args.palette, args.roles)
            out = args.out if args.command == "build" else ROOT / "build"
            for path in build(theme, out):
                print(f"built  {path}")
        if args.command == "install":
            dest = inst.install(ROOT / "build", dry_run=args.dry_run)
            _epilogue(dest, args.dry_run)
        elif args.command == "uninstall":
            dest = inst.uninstall(dry_run=args.dry_run)
            _epilogue(dest, args.dry_run)
        elif args.command == "restore":
            inst.restore(args.backup, dry_run=args.dry_run)
    except (ThemeError, inst.InstallError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def _epilogue(backup_dir: Path, dry_run: bool) -> None:
    if dry_run:
        print("dry run: nothing was changed")
        return
    print("done. Restart GTK apps to see the change. To undo:")
    print(f"  {ROOT / 'install.sh'} --restore {backup_dir}")
