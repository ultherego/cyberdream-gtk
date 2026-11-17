# Post-install checklist

Close and reopen each app before checking it (GTK loads CSS at startup).

Expected colors:

| Element | Color |
|---|---|
| window, view, header bar, menu, popover and dialog background | `#16181a` |
| cards | `#1e2124` |
| buttons and entries | filled with 10% of the text color, no border |
| sidebar | `#111214` |
| lines (under the header, beside the sidebar, around menus) | `#3c4048` |
| accent | `#5eff6c` |
| secondary text | `#7b8496` |
| links | `#5ef1ff`, visited `#bd5eff` |

## Everywhere

- [ ] No `Theme parsing error` warnings when an app is started from a terminal.
- [ ] A selected row has a greenish background and readable white text.
- [ ] The suggested-action button (green) has dark, readable text.
- [ ] The destructive-action button (red) has dark, readable text.
- [ ] Scrollbar slider: grey, lighter on hover, green while dragging.
- [ ] Tooltip: `#111214` background, thin border, white text.
- [ ] Switches, check boxes and progress bars are green.
- [ ] An unfocused window does not flash or turn Adwaita grey.

## GTK4 / libadwaita

- [ ] **File manager (e.g. Files):** sidebar darker than the file list, with a line on
      its edge; selection in list and grid view; path bar; context menu with a border;
      toast after copying or deleting a file.
- [ ] **Text editor (e.g. Text Editor):** preferences window (`#1e2124` cards on a
      `#16181a` background), tabs, menu. Editing area with the "Cyberdream" scheme:
      `#16181a` background, green cursor, grey comments, green strings, readable
      selection and search matches.
- [ ] **An app with boxed lists and dialogs** (e.g. any settings window): rows, switches,
      a confirmation dialog with a suggested and a destructive button.
- [ ] **A GTK4 app without libadwaita** (e.g. pavucontrol): green sliders and tabs; such
      apps take the accent from the `--accent-bg-color` variable.

To judge (deliberate design choices, easy to change in `roles.toml` and the templates):

- [ ] Header bars are in the window color (`header_bg` in `roles.toml`), separated
      from the content by a line where the toolkit draws one.
- [ ] The line under the header (`headerbar_shade_color`) is not too strong.
- [ ] Secondary text (`.dimmed`) in `#7b8496` also looks right on selected rows.

## GTK3 (the standalone `cyberdream` theme)

- [ ] **An app with a menu bar** (e.g. Geany): drop-down menu (border, item highlight),
      tabs, tree (selection as a greenish plate with white text); the editing area with
      the "Cyberdream" scheme has a `#16181a` background.
- [ ] **An app with a list and a header bar** (e.g. Disks): header in the window color with a line under it, row
      selection, menu.
- [ ] **A document viewer** (e.g. Evince): thumbnail panel, text selection.
- [ ] Apps with their own theme (e.g. GIMP): check only the file chooser dialogs.

## Other

- [ ] **Firefox:** the toolbar and the context menu have a `#16181a` background, readable text and the
      theme's accent. If it is grey (`#36363a`), the GTK theme name still starts with
      `adw`; see the Firefox section of the README.
- [ ] **Flatpak (any GTK app):** same colors as in native apps.
- [ ] **Electron/Tauri apps:** they have their own look; check only the system file
      chooser dialogs.
- [ ] **DankMaterialShell (if used):** after changing the theme in DMS,
      `~/.config/gtk-4.0/gtk.css` still contains the line `@import url("cyberdream.css");`.

## Undo

```sh
./install.sh --restore ~/.config/gtk-cyberdream-bak-YYYYMMDD-HHMMSS
```
