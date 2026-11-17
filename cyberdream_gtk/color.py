"""Colors and the small expression language used in roles.toml and templates."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

HEX_RE = re.compile(r"#[0-9a-fA-F]{6}")
NAME_RE = re.compile(r"[a-z][a-z0-9_]*")
CALL_RE = re.compile(r"(alpha|mix)\((.*)\)", re.S)


class ColorError(ValueError):
    pass


@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int
    a: float = 1.0

    @classmethod
    def from_hex(cls, text: str) -> Color:
        if not HEX_RE.fullmatch(text):
            raise ColorError(f"not a #rrggbb color: {text!r}")
        return cls(int(text[1:3], 16), int(text[3:5], 16), int(text[5:7], 16))

    def alpha(self, factor: float) -> Color:
        return Color(self.r, self.g, self.b, self.a * factor)

    def mix(self, other: Color, t: float) -> Color:
        def lerp(x: float, y: float) -> float:
            return x + (y - x) * t

        return Color(
            round(lerp(self.r, other.r)),
            round(lerp(self.g, other.g)),
            round(lerp(self.b, other.b)),
            lerp(self.a, other.a),
        )

    def css(self) -> str:
        if self.a >= 1:
            return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
        return f"rgba({self.r}, {self.g}, {self.b}, {round(self.a, 3):g})"

    def luminance(self) -> float:
        """WCAG relative luminance (alpha ignored)."""

        def channel(v: int) -> float:
            c = v / 255
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        return 0.2126 * channel(self.r) + 0.7152 * channel(self.g) + 0.0722 * channel(self.b)


def contrast(a: Color, b: Color) -> float:
    """WCAG contrast ratio between two opaque colors."""
    hi, lo = sorted((a.luminance(), b.luminance()), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _split_args(text: str) -> list[str]:
    args, depth, start = [], 0, 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 0:
            args.append(text[start:i])
            start = i + 1
    args.append(text[start:])
    return [a.strip() for a in args]


def _fraction(text: str, expr: str) -> float:
    try:
        value = float(text)
    except ValueError:
        raise ColorError(f"expected a number, got {text!r} in {expr!r}") from None
    if not 0 <= value <= 1:
        raise ColorError(f"number out of range 0..1: {text} in {expr!r}")
    return value


def evaluate(expr: str, lookup: Callable[[str], Color]) -> Color:
    """Evaluate an expression; `lookup` resolves bare names."""
    expr = expr.strip()
    if HEX_RE.fullmatch(expr):
        return Color.from_hex(expr)
    if NAME_RE.fullmatch(expr):
        return lookup(expr)
    call = CALL_RE.fullmatch(expr)
    if call:
        func, args = call[1], _split_args(call[2])
        if func == "alpha" and len(args) == 2:
            return evaluate(args[0], lookup).alpha(_fraction(args[1], expr))
        if func == "mix" and len(args) == 3:
            return evaluate(args[0], lookup).mix(
                evaluate(args[1], lookup), _fraction(args[2], expr)
            )
        raise ColorError(f"wrong number of arguments in {expr!r}")
    raise ColorError(f"cannot parse color expression {expr!r}")
