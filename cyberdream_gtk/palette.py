"""Loading and validating palette.toml + roles.toml."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .color import NAME_RE, Color, ColorError, evaluate

ROOT = Path(__file__).resolve().parent.parent
ACCENT = "accent"


class ThemeError(ValueError):
    pass


@dataclass
class Theme:
    name: str
    accent: str
    colors: dict[str, Color]
    roles: dict[str, str]
    named: dict[str, dict[str, str]]
    shape: dict[str, str] = field(default_factory=dict)
    _cache: dict[str, Color] = field(default_factory=dict, repr=False)

    @classmethod
    def load(cls, palette_path: Path | None = None, roles_path: Path | None = None) -> Theme:
        palette = _read(palette_path or ROOT / "palette.toml")
        roles = _read(roles_path or ROOT / "roles.toml")

        meta = palette.get("meta", {})
        raw_colors = palette.get("colors", {})
        if not raw_colors:
            raise ThemeError("palette: [colors] is missing or empty")
        colors = {}
        for key, value in raw_colors.items():
            _check_name(key, "palette color")
            try:
                colors[key] = Color.from_hex(value) if isinstance(value, str) else _bad(value)
            except ColorError as exc:
                raise ThemeError(f"palette color {key!r}: {exc}") from None

        accent = meta.get(ACCENT, "")
        if accent not in colors:
            raise ThemeError(
                f"palette: accent {accent!r} is not one of: {', '.join(colors)}"
            )

        role_table = roles.get("roles", {})
        for key in role_table:
            _check_name(key, "role")
            if key in colors or key == ACCENT:
                raise ThemeError(f"role {key!r} shadows a palette color")

        theme = cls(
            name=meta.get("name", "cyberdream"),
            accent=accent,
            colors=colors,
            roles=role_table,
            named=roles.get("named", {}),
            shape={k: str(v) for k, v in roles.get("shape", {}).items()},
        )
        theme.validate()
        return theme

    def resolve(self, name: str, _stack: tuple[str, ...] = ()) -> Color:
        if name in self._cache:
            return self._cache[name]
        if name in _stack:
            raise ThemeError("role cycle: " + " -> ".join((*_stack, name)))
        if name == ACCENT:
            color = self.colors[self.accent]
        elif name in self.colors:
            color = self.colors[name]
        elif name in self.roles:
            color = self.eval(self.roles[name], (*_stack, name))
        else:
            raise ThemeError(f"unknown color or role {name!r}")
        self._cache[name] = color
        return color

    def eval(self, expr: str, _stack: tuple[str, ...] = ()) -> Color:
        try:
            return evaluate(expr, lambda n: self.resolve(n, _stack))
        except ColorError as exc:
            raise ThemeError(str(exc)) from None

    def named_colors(self, *sections: str) -> dict[str, Color]:
        """Named colors for a target: later sections override earlier ones."""
        result: dict[str, Color] = {}
        for section in sections:
            for key, expr in self.named.get(section, {}).items():
                result[key] = self.eval(expr)
        return result

    def validate(self) -> None:
        for role in self.roles:
            self.resolve(role)
        for section, table in self.named.items():
            for key, expr in table.items():
                _check_name(key, f"named color in [named.{section}]")
                self.eval(expr)


def _read(path: Path) -> dict:
    try:
        with open(path, "rb") as fh:
            return tomllib.load(fh)
    except FileNotFoundError:
        raise ThemeError(f"file not found: {path}") from None
    except tomllib.TOMLDecodeError as exc:
        raise ThemeError(f"{path}: {exc}") from None


def _check_name(name: str, what: str) -> None:
    if not NAME_RE.fullmatch(name):
        raise ThemeError(f"invalid {what} name {name!r} (use a-z, 0-9, _)")


def _bad(value: object) -> Color:
    raise ColorError(f"expected a \"#rrggbb\" string, got {value!r}")
