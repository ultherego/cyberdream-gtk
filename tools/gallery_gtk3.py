"""Render a GTK3 widget gallery to a PNG without showing a window.

Usage: python3 tools/gallery_gtk3.py OUT.png

Run it under a private Broadway display so nothing appears on the desktop;
tools/render.sh sets that up and points GTK at the freshly built theme.
"""

import sys

import cairo
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk  # noqa: E402

out = sys.argv[1]


def cls(widget, *names):
    for name in names:
        widget.get_style_context().add_class(name)
    return widget


def row(*widgets, spacing=8):
    box = Gtk.Box(spacing=spacing)
    for w in widgets:
        box.pack_start(w, False, False, 0)
    return box


win = Gtk.Window(default_width=1100, default_height=820)
hb = Gtk.HeaderBar(title="Gallery", subtitle="GTK3", show_close_button=True)
hb.pack_start(cls(Gtk.Button(label="Suggested"), "suggested-action"))
hb.pack_start(Gtk.Button.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON))
hb.pack_end(Gtk.ToggleButton(label="Toggle", active=True))
win.set_titlebar(hb)

root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
win.add(root)

menubar = Gtk.MenuBar()
for label in ("File", "Edit", "View", "Help"):
    menubar.append(Gtk.MenuItem(label=label))
root.pack_start(menubar, False, False, 0)

toolbar = Gtk.Toolbar()
for icon in ("document-new-symbolic", "document-open-symbolic", "document-save-symbolic"):
    toolbar.insert(Gtk.ToolButton(icon_name=icon), -1)
toolbar.insert(Gtk.SeparatorToolItem(), -1)
toolbar.insert(Gtk.ToggleToolButton(icon_name="format-text-bold-symbolic", active=True), -1)
root.pack_start(toolbar, False, False, 0)

info = Gtk.InfoBar(message_type=Gtk.MessageType.WARNING, show_close_button=True)
info.get_content_area().add(Gtk.Label(label="An info bar with a warning"))
root.pack_start(info, False, False, 0)

paned = Gtk.Paned()
root.pack_start(paned, True, True, 0)

side = cls(Gtk.ListBox(), "sidebar")
side_wrap = cls(Gtk.ScrolledWindow(min_content_width=190), "sidebar")
for text in ("Home", "Documents", "Downloads", "Music", "Pictures"):
    side.add(Gtk.Label(label=text, xalign=0, margin=9))
side_wrap.add(side)
paned.pack1(side_wrap, False, False)

notebook = Gtk.Notebook()
paned.pack2(notebook, True, False)

page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin=16)
notebook.append_page(page, Gtk.Label(label="Controls"))
notebook.append_page(Gtk.Label(label="second page"), Gtk.Label(label="Second"))
notebook.append_page(Gtk.Label(label="third page"), Gtk.Label(label="Third"))

disabled = Gtk.Button(label="Disabled", sensitive=False)
linked = cls(Gtk.Box(), "linked")
for i, label in enumerate(("One", "Two", "Three")):
    linked.pack_start(Gtk.ToggleButton(label=label, active=i == 1), False, False, 0)
page.pack_start(row(
    Gtk.Button(label="Normal"), cls(Gtk.Button(label="Suggested"), "suggested-action"),
    cls(Gtk.Button(label="Destructive"), "destructive-action"), cls(Gtk.Button(label="Flat"), "flat"),
    disabled, linked, Gtk.LinkButton(uri="https://example.org", label="Link"),
), False, False, 0)

entry = Gtk.Entry(text="Entry with a selection")
entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, "edit-find-symbolic")
spin = Gtk.SpinButton.new_with_range(0, 100, 1)
spin.set_value(42)
combo = Gtk.ComboBoxText()
for text in ("Combo box", "Second", "Third"):
    combo.append_text(text)
combo.set_active(0)
page.pack_start(row(entry, Gtk.Entry(placeholder_text="Placeholder"),
                    Gtk.Entry(text="Disabled", sensitive=False), spin, combo), False, False, 0)

r1 = Gtk.RadioButton(label="Radio on")
r2 = Gtk.RadioButton(label="Radio off", group=r1)
mixed = Gtk.CheckButton(label="Mixed", inconsistent=True)
page.pack_start(row(
    Gtk.CheckButton(label="Checked", active=True), Gtk.CheckButton(label="Unchecked"), mixed,
    Gtk.CheckButton(label="Disabled", active=True, sensitive=False), r1, r2,
    Gtk.Switch(active=True), Gtk.Switch(), Gtk.Switch(active=True, sensitive=False), spacing=14,
), False, False, 0)

scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
scale.set_value(40)
scale.set_draw_value(False)
scale.add_mark(50, Gtk.PositionType.BOTTOM, "50")
scale.set_size_request(300, -1)
level = Gtk.LevelBar(value=0.6)
level.set_size_request(200, -1)
level.set_valign(Gtk.Align.CENTER)
progress = Gtk.ProgressBar(fraction=0.4, show_text=True)
progress.set_size_request(220, -1)
progress.set_valign(Gtk.Align.CENTER)
page.pack_start(row(scale, progress, level, Gtk.Spinner(active=True), spacing=20), False, False, 0)

lower = Gtk.Box(spacing=14)
page.pack_start(lower, True, True, 0)

store = Gtk.ListStore(str, str, bool, int)
for i in range(6):
    store.append([f"Item {i}", "description", i % 2 == 0, i * 18])
tree = Gtk.TreeView(model=store)
tree.append_column(Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=0))
tree.append_column(Gtk.TreeViewColumn("Description", Gtk.CellRendererText(), text=1))
tree.append_column(Gtk.TreeViewColumn("On", Gtk.CellRendererToggle(), active=2))
tree.append_column(Gtk.TreeViewColumn("Progress", Gtk.CellRendererProgress(), value=3))
tree.get_selection().select_path(1)
tree_sw = Gtk.ScrolledWindow(shadow_type=Gtk.ShadowType.IN, min_content_width=380)
tree_sw.add(tree)
lower.pack_start(tree_sw, True, True, 0)

listbox = Gtk.ListBox()
for text in ("List row", "Selected list row", "Another row"):
    listbox.add(Gtk.Label(label=text, xalign=0, margin=8))
frame = Gtk.Frame(label="Frame")
frame.add(listbox)
mid = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
mid.pack_start(frame, False, False, 0)
expander = Gtk.Expander(label="Expander", expanded=True)
expander.add(cls(Gtk.Label(label="Dim label inside", xalign=0, margin=6), "dim-label"))
mid.pack_start(expander, False, False, 0)
text = Gtk.TextView()
text.get_buffer().set_text("Text view\nwith several\nlines of text")
text_sw = Gtk.ScrolledWindow(shadow_type=Gtk.ShadowType.IN, min_content_height=70)
text_sw.add(text)
mid.pack_start(text_sw, True, True, 0)
lower.pack_start(mid, True, True, 0)

lower.pack_start(Gtk.Calendar(), False, False, 0)

status = Gtk.Statusbar()
status.push(0, "Status bar text")
root.pack_start(status, False, False, 0)

win.show_all()
listbox.select_row(listbox.get_row_at_index(1))
side.select_row(side.get_row_at_index(1))


def prepare():
    entry.grab_focus()
    entry.select_region(0, 5)
    return False


def capture():
    alloc = win.get_allocation()
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, alloc.width, alloc.height)
    win.draw(cairo.Context(surface))
    surface.write_to_png(out)
    print(f"saved {out} {alloc.width}x{alloc.height}")
    Gtk.main_quit()
    return False


GLib.timeout_add(600, prepare)
GLib.timeout_add(1500, capture)
Gtk.main()
