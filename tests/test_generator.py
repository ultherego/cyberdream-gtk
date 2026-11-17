import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cyberdream_gtk.color import Color, ColorError, contrast, evaluate
from cyberdream_gtk.palette import ROOT, Theme, ThemeError
from cyberdream_gtk.render import build, render, render_template
from cyberdream_gtk.targets import ALL, GEANY, GTK3, GTK3_THEME, GTK4, GTK4_THEME, SOURCEVIEW

OVERLAYS = (GTK3, GTK4)

GTK_PARSE = Path(__file__).with_name("gtk_parse.py")


def has_gtk(version: str) -> bool:
    code = f"import gi; gi.require_version('Gtk', '{version}'); from gi.repository import Gtk"
    return subprocess.run([sys.executable, "-c", code], capture_output=True).returncode == 0


class ColorTest(unittest.TestCase):
    def test_hex_roundtrip(self):
        self.assertEqual(Color.from_hex("#5eff6c").css(), "#5eff6c")

    def test_rejects_bad_hex(self):
        for bad in ("5eff6c", "#fff", "#gggggg", "red"):
            with self.assertRaises(ColorError):
                Color.from_hex(bad)

    def test_alpha_and_mix(self):
        look = {"a": Color(0, 0, 0), "b": Color(255, 255, 255)}.__getitem__
        self.assertEqual(evaluate("alpha(b, 0.5)", look).css(), "rgba(255, 255, 255, 0.5)")
        self.assertEqual(evaluate("mix(a, b, 0.2)", look).css(), "#333333")
        self.assertEqual(evaluate("alpha(mix(a, #ffffff, 1), 0.25)", look).a, 0.25)

    def test_bad_expressions(self):
        for bad in ("alpha(a)", "mix(a, a)", "alpha(a, 2)", "alpha(a, x)", "a b", ""):
            with self.assertRaises(ColorError, msg=bad):
                evaluate(bad, lambda n: Color(0, 0, 0))


class ThemeTest(unittest.TestCase):
    def load(self, palette: str, roles: str = "[roles]\n") -> Theme:
        with tempfile.TemporaryDirectory() as tmp:
            p, r = Path(tmp, "p.toml"), Path(tmp, "r.toml")
            p.write_text(palette)
            r.write_text(roles)
            return Theme.load(p, r)

    PALETTE = '[meta]\naccent = "green"\n[colors]\ngreen = "#5eff6c"\nblue = "#5ea1ff"\n'

    def test_project_files_load(self):
        theme = Theme.load()
        self.assertEqual(theme.accent, "green")
        self.assertEqual(theme.resolve("accent").css(), "#5eff6c")

    def test_accent_switch(self):
        theme = self.load(self.PALETTE.replace('"green"', '"blue"', 1))
        self.assertEqual(theme.resolve("accent").css(), "#5ea1ff")

    def test_unknown_accent(self):
        with self.assertRaisesRegex(ThemeError, "accent"):
            self.load(self.PALETTE.replace('accent = "green"', 'accent = "teal"'))

    def test_unknown_role_reference(self):
        with self.assertRaisesRegex(ThemeError, "unknown color or role 'nope'"):
            self.load(self.PALETTE, '[roles]\nx = "nope"\n')

    def test_role_cycle(self):
        with self.assertRaisesRegex(ThemeError, "cycle"):
            self.load(self.PALETTE, '[roles]\nx = "y"\ny = "x"\n')

    def test_role_cannot_shadow_palette(self):
        with self.assertRaisesRegex(ThemeError, "shadows"):
            self.load(self.PALETTE, '[roles]\ngreen = "blue"\n')

    def test_contrast(self):
        theme = Theme.load()
        pairs = [
            ("text", "window_bg", 7), ("text", "raised_bg", 7), ("text", "sidebar_bg", 7),
            ("on_accent", "accent", 4.5), ("on_accent", "destructive", 4.5),
            ("on_accent", "warning", 4.5), ("muted", "window_bg", 4.5),
            ("link", "window_bg", 4.5), ("link_visited", "window_bg", 4.5),
        ]
        for fg, bg, minimum in pairs:
            ratio = contrast(theme.resolve(fg), theme.resolve(bg))
            self.assertGreaterEqual(ratio, minimum, f"{fg} on {bg}: {ratio:.2f}")

    def test_contrast_with_blue_accent(self):
        theme = Theme.load()
        theme.accent = "blue"
        self.assertGreaterEqual(contrast(theme.resolve("on_accent"), theme.resolve("accent")), 4.5)


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.theme = Theme.load()

    def test_placeholder_error_has_location(self):
        with self.assertRaisesRegex(ThemeError, r"t\.css:2: unknown color or role 'nope'"):
            render_template("a {\n  color: {{nope}};\n}\n", self.theme, "t.css")

    def test_output_is_complete_and_deterministic(self):
        for target in ALL:
            out = render(self.theme, target)
            self.assertEqual(out, render(Theme.load(), target))
            self.assertNotIn("{{", out)
            self.assertNotIn("}}", out)
        for target in OVERLAYS:
            css = render(self.theme, target)
            self.assertEqual(css.count("{"), css.count("}"))
            self.assertTrue(css.endswith("}\n"))

    def test_named_colors(self):
        for target in OVERLAYS:
            css = render(self.theme, target)
            defined = re.findall(r"^@define-color (\w+) +(.+);$", css, re.M)
            names = [name for name, _ in defined]
            self.assertEqual(len(names), len(set(names)))
            for required in ("accent_bg_color", "window_bg_color", "headerbar_bg_color",
                             "sidebar_bg_color", "card_bg_color", "popover_bg_color"):
                self.assertIn(required, names)
            self.assertIn(("accent_bg_color", "#5eff6c"), defined)
            self.assertIn(("sidebar_bg_color", "#111214"), defined)
            self.assertIn(("headerbar_bg_color", "#16181a"), defined)
            self.assertIn(("card_bg_color", "#1e2124"), defined)
        self.assertIn("theme_selected_bg_color", render(self.theme, GTK3))
        self.assertNotIn("theme_selected_bg_color", render(self.theme, GTK4))

    def test_gtk4_sets_accent_variable(self):
        """adw-gtk3's GTK4 theme ignores @accent_bg_color; the variable is needed."""
        self.assertIn("--accent-bg-color: #5eff6c;", render(self.theme, GTK4))
        self.assertNotIn("--accent-bg-color", render(self.theme, GTK3))

    def test_only_palette_colors_are_opaque_hex(self):
        """No stray hex: every opaque color comes from the palette or a mix()."""
        allowed = {c.css() for c in self.theme.colors.values()}
        allowed |= {self.theme.eval(e).css() for t in self.theme.named.values() for e in t.values()}
        allowed |= {self.theme.eval("mix(link, fg, 0.25)").css()}
        for target in OVERLAYS:
            found = set(re.findall(r"#[0-9a-f]{6}\b", render(self.theme, target)))
            self.assertLessEqual(found, allowed)

    def test_gtk_parsers_accept_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            build(self.theme, Path(tmp))
            for target, version in ((GTK3, "3.0"), (GTK4, "4.0"), (GTK3_THEME, "3.0")):
                with self.subTest(gtk=version):
                    if not has_gtk(version):
                        self.skipTest(f"PyGObject / GTK {version} not available")
                    result = subprocess.run(
                        [sys.executable, str(GTK_PARSE), version,
                         str(Path(tmp, target.name, target.output))],
                        capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class StandaloneThemeTest(unittest.TestCase):
    def setUp(self):
        self.theme = Theme.load()

    def test_shape_tokens(self):
        self.assertEqual(render_template("a { r: {{@radius}}; }", self.theme), "a { r: 6px; }")
        with self.assertRaisesRegex(ThemeError, "unknown shape token"):
            render_template("a { r: {{@nope}}; }", self.theme)

    def test_gtk3_theme_covers_the_widget_set(self):
        css = render(self.theme, GTK3_THEME)
        self.assertNotIn("adw-gtk3", css)  # standalone: no dependency on another theme
        self.assertNotIn("@import", css)
        self.assertEqual(css.count("{"), css.count("}"))
        for selector in ("button", "entry", "headerbar", "menu", "popover.background", "notebook > header",
                         "treeview.view", "scrollbar slider", "switch", "check", "radio", "scale slider",
                         "progressbar progress", "levelbar block", "tooltip.background", "decoration",
                         "calendar", "infobar", "spinbutton", "combobox arrow", "placessidebar row",
                         "paned > separator", "expander arrow", "list row", ".sidebar"):
            self.assertRegex(css, r"(?m)^" + re.escape(selector) + r"\b", selector)

    def test_dark_variant_exists(self):
        """libhandy falls back to Adwaita for themes without gtk-dark.css."""
        from cyberdream_gtk.targets import GTK3_THEME_DARK, GTK4_THEME_DARK

        for target in (GTK3_THEME_DARK, GTK4_THEME_DARK):
            self.assertEqual(target.output, "gtk-dark.css")
            self.assertEqual(render(self.theme, target), '@import url("gtk.css");\n')

    def test_gtk4_theme_imports_first(self):
        css = render(self.theme, GTK4_THEME)
        self.assertTrue(css.startswith("@import "))
        self.assertIn("--accent-bg-color: #5eff6c;", css)


class SourceViewTest(unittest.TestCase):
    def setUp(self):
        self.xml = render(Theme.load(), SOURCEVIEW)

    def test_well_formed_and_opaque(self):
        import xml.etree.ElementTree as ET

        root = ET.fromstring(self.xml.encode())
        self.assertEqual(root.tag, "style-scheme")
        self.assertEqual(root.get("id"), "cyberdream")
        self.assertNotIn("rgba(", self.xml)  # style schemes need #rrggbb
        styles = {s.get("name"): s for s in root.iter("style")}
        self.assertEqual(styles["text"].get("background"), "#16181a")
        self.assertEqual(styles["text"].get("foreground"), "#ffffff")
        self.assertEqual(styles["cursor"].get("foreground"), "#5eff6c")
        for style in styles.values():
            for attr in ("foreground", "background"):
                value = style.get(attr)
                if value is not None:
                    self.assertRegex(value, r"^#[0-9a-f]{6}$")

    def test_gtksourceview_loads_it(self):
        code = (
            "import sys, gi\n"
            "gi.require_version('GtkSource', '5')\n"
            "from gi.repository import GtkSource\n"
            "m = GtkSource.StyleSchemeManager()\n"
            "m.set_search_path([sys.argv[1]])\n"
            "s = m.get_scheme('cyberdream')\n"
            "assert s is not None, 'scheme not found'\n"
            "for n in ('text', 'cursor', 'selection', 'def:comment', 'def:string'):\n"
            "    assert s.get_style(n) is not None, n\n"
            "assert s.get_style('text').props.background == '#16181a'\n"
        )
        probe = "import gi; gi.require_version('GtkSource', '5'); from gi.repository import GtkSource"
        if subprocess.run([sys.executable, "-c", probe], capture_output=True).returncode:
            self.skipTest("GtkSourceView 5 not available")
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "cyberdream.xml").write_text(self.xml)
            result = subprocess.run([sys.executable, "-c", code, tmp], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


class GeanyTest(unittest.TestCase):
    def test_scheme_is_valid_keyfile_with_opaque_colors(self):
        import configparser

        text = render(Theme.load(), GEANY)
        self.assertNotIn("rgba(", text.split("[theme_info]")[1])
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.optionxform = str
        cfg.read_string(text)
        self.assertEqual(cfg["theme_info"]["name"], "Cyberdream")
        styles = cfg["named_styles"]
        self.assertEqual(styles["default"], "#ffffff;#16181a;false;false")
        self.assertEqual(styles["caret"], "#5eff6c")
        names = set(styles) | {"default"}
        for key, value in styles.items():
            for field in value.split(";")[:2]:
                field = field.split(",")[0]
                if field:
                    self.assertTrue(
                        re.fullmatch(r"#[0-9a-f]{6}", field) or field in names,
                        f"{key}: bad color or unknown style {field!r}",
                    )


if __name__ == "__main__":
    unittest.main()
