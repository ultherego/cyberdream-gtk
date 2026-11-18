import os
import tempfile
import unittest
from pathlib import Path

from cyberdream_gtk import install as inst
from cyberdream_gtk.palette import Theme
from cyberdream_gtk.render import build

DANK = inst.DANK_IMPORT_LINE
OURS = inst.IMPORT_LINE
quiet = lambda *_: None  # noqa: E731


class ImportLineTest(unittest.TestCase):
    def test_add_after_existing_imports(self):
        self.assertEqual(inst.add_import(""), OURS + "\n")
        self.assertEqual(inst.add_import(DANK + "\n"), f"{DANK}\n{OURS}\n")
        self.assertEqual(
            inst.add_import(f"{DANK}\nwindow {{ color: red; }}\n"),
            f"{DANK}\n{OURS}\nwindow {{ color: red; }}\n",
        )

    def test_add_is_idempotent(self):
        once = inst.add_import(DANK + "\n")
        self.assertEqual(inst.add_import(once), once)
        self.assertEqual(inst.add_import("@import 'cyberdream.css';\n"), "@import 'cyberdream.css';\n")

    def test_remove(self):
        self.assertEqual(inst.remove_import(f"{DANK}\n{OURS}\n"), DANK + "\n")
        self.assertEqual(inst.remove_import(OURS + "\n"), "")


class InstallTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.config = Path(tmp.name, "config")
        self.data = Path(tmp.name, "data")
        self.home = Path(tmp.name, "home")
        self.roots = inst.Roots(self.config, self.data, self.home)
        self.scheme = self.data / "gtksourceview-5" / "styles" / "cyberdream.xml"
        self.build = Path(tmp.name, "build")
        build(Theme.load(), self.build)
        # A layout DankMaterialShell can leave behind: GTK3 gtk.css is its
        # symlink, GTK4 gtk.css is a one-line file; both have an older overlay.
        for d in ("gtk-3.0", "gtk-4.0"):
            (self.config / d).mkdir(parents=True)
            (self.config / d / "dank-colors.css").write_text("/* dms */\n")
            (self.config / d / "cyberdream.css").write_text("/* old overlay */\n")
        os.symlink("dank-colors.css", self.config / "gtk-3.0" / "gtk.css")
        (self.config / "gtk-4.0" / "gtk.css").write_text(DANK + "\n")

    def snapshot(self):
        result = {}
        paths = [*self.config.glob("gtk-[34].0/*"), *self.config.glob("geany/*/*"), *self.data.rglob("*.xml"), *(p for p in self.home.rglob("*") if p.is_file())]
        for path in sorted(paths):
            result[str(path.relative_to(self.config.parent))] = (
                "-> " + os.readlink(path) if path.is_symlink() else path.read_text()
            )
        return result

    def test_install(self):
        inst.install(self.build, self.roots, log=quiet)
        for d in ("gtk-3.0", "gtk-4.0"):
            gtk_css = self.config / d / "gtk.css"
            self.assertFalse(gtk_css.is_symlink())
            self.assertEqual(gtk_css.read_text(), f"{DANK}\n{OURS}\n")
            self.assertEqual(
                (self.config / d / "cyberdream.css").read_text(),
                (self.build / d / "cyberdream.css").read_text(),
            )
            self.assertEqual((self.config / d / "dank-colors.css").read_text(), "/* dms */\n")
        self.assertIn('<style-scheme id="cyberdream"', self.scheme.read_text())
        self.assertIn("name=Cyberdream", (self.config / "geany/colorschemes/cyberdream.conf").read_text())

    def test_second_install_makes_no_backup(self):
        first = inst.install(self.build, self.roots, log=quiet)
        self.assertIsNotNone(first)
        self.assertIsNone(inst.install(self.build, self.roots, log=quiet))
        self.assertEqual(len(list(self.config.glob(inst.BACKUP_PREFIX + "*"))), 1)

    def test_install_twice_changes_nothing_more(self):
        inst.install(self.build, self.roots, log=quiet)
        first = self.snapshot()
        inst.install(self.build, self.roots, log=quiet)
        self.assertEqual(self.snapshot(), first)

    def test_dry_run_changes_nothing(self):
        before = self.snapshot()
        inst.install(self.build, self.roots, dry_run=True, log=quiet)
        inst.uninstall(self.roots, dry_run=True, log=quiet)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(list(self.config.glob(inst.BACKUP_PREFIX + "*")), [])

    def test_restore_brings_back_original_state(self):
        before = self.snapshot()
        backup = inst.install(self.build, self.roots, log=quiet)
        self.assertNotEqual(self.snapshot(), before)
        inst.restore(backup, self.roots, log=quiet)
        self.assertEqual(self.snapshot(), before)

    def test_restore_removes_files_that_did_not_exist(self):
        (self.config / "gtk-4.0" / "cyberdream.css").unlink()
        (self.config / "gtk-4.0" / "gtk.css").unlink()
        before = self.snapshot()
        backup = inst.install(self.build, self.roots, log=quiet)
        self.assertEqual((self.config / "gtk-4.0" / "gtk.css").read_text(), OURS + "\n")
        inst.restore(backup, self.roots, log=quiet)
        self.assertEqual(self.snapshot(), before)

    def test_uninstall(self):
        inst.install(self.build, self.roots, log=quiet)
        inst.uninstall(self.roots, log=quiet)
        for d in ("gtk-3.0", "gtk-4.0"):
            self.assertFalse((self.config / d / "cyberdream.css").exists())
            self.assertEqual((self.config / d / "gtk.css").read_text(), DANK + "\n")
        self.assertFalse(self.scheme.exists())

    def test_symlink_to_own_theme_is_replaced(self):
        """A theme switcher may link gtk-4.0/gtk.css to the selected theme."""
        gtk_css = self.config / "gtk-4.0" / "gtk.css"
        gtk_css.unlink()
        os.symlink(str(self.home / ".themes/cyberdream/gtk-4.0/gtk.css"), gtk_css)
        inst.install(self.build, self.roots, log=quiet)
        self.assertFalse(gtk_css.is_symlink())
        self.assertEqual(gtk_css.read_text(), OURS + "\n")

    def test_symlink_to_other_theme_is_replaced_and_backed_up(self):
        """nwg-look links the selected theme, e.g. adw-gtk3-dark, the same way."""
        gtk_css = self.config / "gtk-4.0" / "gtk.css"
        gtk_css.unlink()
        link = "/usr/share/themes/adw-gtk3-dark/gtk-4.0/gtk.css"
        os.symlink(link, gtk_css)
        dest = inst.install(self.build, self.roots, log=quiet)
        self.assertFalse(gtk_css.is_symlink())
        self.assertEqual(gtk_css.read_text(), OURS + "\n")
        self.assertEqual(os.readlink(dest / "config" / "gtk-4.0" / "gtk.css"), link)

    def test_foreign_symlink_is_refused_before_any_change(self):
        gtk_css = self.config / "gtk-4.0" / "gtk.css"
        gtk_css.unlink()
        os.symlink("/nix/store/something/gtk.css", gtk_css)
        before = self.snapshot()
        with self.assertRaises(inst.InstallError):
            inst.install(self.build, self.roots, log=quiet)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(list(self.config.glob(inst.BACKUP_PREFIX + "*")), [])

    def test_restore_reads_manifest_without_root_prefix(self):
        """Backups made before the data root existed use bare config paths."""
        old = self.config / "old-backup"
        (old / "gtk-4.0").mkdir(parents=True)
        (old / "gtk-4.0" / "gtk.css").write_text("/* saved */\n")
        (old / inst.MANIFEST).write_text('{"gtk-4.0/gtk.css": "file", "gtk-4.0/cyberdream.css": "absent"}')
        inst.restore(old, self.roots, log=quiet)
        self.assertEqual((self.config / "gtk-4.0" / "gtk.css").read_text(), "/* saved */\n")
        self.assertFalse((self.config / "gtk-4.0" / "cyberdream.css").exists())

    def test_restore_rejects_non_backup(self):
        with self.assertRaises(inst.InstallError):
            inst.restore(self.config, self.roots, log=quiet)


if __name__ == "__main__":
    unittest.main()
