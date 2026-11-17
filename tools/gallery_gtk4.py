"""Render a GTK4/libadwaita widget gallery to a PNG without showing a window.

Usage: python3 tools/gallery_gtk4.py OUT.png

Run it under a private Broadway display (see tools/render.sh).
"""

import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gsk", "4.0")
from gi.repository import Adw, Gdk, Gio, GLib, Gsk, Gtk  # noqa: E402

out = sys.argv[1]
app = Adw.Application(application_id="dev.cyberdream.Gallery4", flags=Gio.ApplicationFlags.NON_UNIQUE)


def shot(widget, path):
    width, height = widget.get_width(), widget.get_height()
    snapshot = Gtk.Snapshot()
    Gtk.WidgetPaintable.new(widget).snapshot(snapshot, width, height)
    renderer = Gsk.CairoRenderer()
    renderer.realize_for_display(Gdk.Display.get_default())
    renderer.render_texture(snapshot.to_node(), None).save_to_png(path)
    renderer.unrealize()
    print(f"saved {path} {width}x{height}")


def row(*widgets, spacing=8):
    box = Gtk.Box(spacing=spacing)
    for w in widgets:
        box.append(w)
    return box


def activate(app):
    win = Adw.ApplicationWindow(application=app, default_width=980, default_height=700)
    view = Adw.ToolbarView()
    header = Adw.HeaderBar(title_widget=Adw.WindowTitle(title="Gallery", subtitle="GTK4 / libadwaita"))
    header.pack_start(Gtk.Button(icon_name="go-previous-symbolic"))
    header.pack_start(Gtk.Button(icon_name="go-next-symbolic"))
    header.pack_start(Gtk.Button(label="Suggested", css_classes=["suggested-action"]))
    header.pack_end(Gtk.MenuButton(icon_name="open-menu-symbolic"))
    header.pack_end(Gtk.ToggleButton(icon_name="edit-find-symbolic", active=True))
    view.add_top_bar(header)
    overlay = Adw.ToastOverlay()
    view.set_content(overlay)
    win.set_content(view)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14,
                  margin_top=18, margin_bottom=18, margin_start=18, margin_end=18)
    overlay.set_child(box)

    linked = Gtk.Box(css_classes=["linked"])
    for i, label in enumerate(("One", "Two", "Three")):
        linked.append(Gtk.ToggleButton(label=label, active=i == 1))
    box.append(row(
        Gtk.Button(label="Normal"), Gtk.Button(label="Suggested", css_classes=["suggested-action"]),
        Gtk.Button(label="Destructive", css_classes=["destructive-action"]),
        Gtk.Button(label="Flat", css_classes=["flat"]), Gtk.Button(label="Disabled", sensitive=False),
        Gtk.ToggleButton(label="Checked", active=True), linked,
        Gtk.Button(label="Pill", css_classes=["pill"]),
        Gtk.Button(icon_name="list-add-symbolic", css_classes=["circular"]),
        Gtk.LinkButton(uri="https://example.org", label="Link"),
    ))

    entry = Gtk.Entry(text="Entry", primary_icon_name="edit-find-symbolic")
    spin = Gtk.SpinButton.new_with_range(0, 100, 1)
    spin.set_value(42)
    dropdown = Gtk.DropDown.new_from_strings(["Drop-down", "Second", "Third"])
    box.append(row(entry, Gtk.Entry(placeholder_text="Placeholder"), Gtk.Entry(text="Disabled", sensitive=False),
                   Gtk.PasswordEntry(text="secret", show_peek_icon=True), spin, dropdown))

    box.append(row(Gtk.CheckButton(label="Checked", active=True), Gtk.CheckButton(label="Unchecked"),
                   Gtk.Switch(active=True, valign=Gtk.Align.CENTER), Gtk.Switch(valign=Gtk.Align.CENTER), spacing=16))

    listbox = Gtk.ListBox(css_classes=["boxed-list"], selection_mode=Gtk.SelectionMode.NONE)
    action = Adw.ActionRow(title="Action row", subtitle="With a button and a switch")
    action.add_suffix(Gtk.Button(label="Button", valign=Gtk.Align.CENTER))
    action.add_suffix(Gtk.Switch(active=True, valign=Gtk.Align.CENTER))
    listbox.append(action)
    listbox.append(Adw.EntryRow(title="Entry row", text="text"))
    listbox.append(Adw.SpinRow.new_with_range(0, 10, 1))
    combo = Adw.ComboRow(title="Combo row", model=Gtk.StringList.new(["First", "Second"]))
    listbox.append(combo)
    box.append(listbox)

    box.append(Gtk.ProgressBar(fraction=0.4))
    scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
    scale.set_value(40)
    box.append(scale)

    win.present()

    def prepare():
        overlay.add_toast(Adw.Toast(title="A toast", button_label="Undo", timeout=0))
        return False

    def capture():
        shot(win, out)
        app.quit()
        return False

    GLib.timeout_add(700, prepare)
    GLib.timeout_add(2200, capture)


app.connect("activate", activate)
app.run([])
