# cyberdream-gtk

Motyw GTK3 i GTK4/libadwaita w kolorach [cyberdream](https://github.com/scottmckendry/cyberdream.nvim),
generowany z jednej palety. Napisany od zera, bez kodu i zależności innych motywów.

Stan: **Faza 1, nakładka**. Motyw ustawia nazwane kolory i kilkanaście reguł CSS
na bazie libadwaita (GTK4) oraz `adw-gtk3-dark` (GTK3). Kształty, odstępy i wygląd
widżetów pochodzą z motywu bazowego, dlatego motywem GTK w ustawieniach systemu
musi pozostać `adw-gtk3-dark`; „cyberdream" nie pojawia się na liście motywów.

Do tego schematy kolorów dla edytorów, które nie biorą kolorów obszaru edycji z motywu
GTK: GtkSourceView 5 (Text Editor i podobne) oraz Geany.

## Wymagania

- Python 3.11 lub nowszy (tylko biblioteka standardowa)
- GTK3: motyw `adw-gtk3-dark` ustawiony jako motyw GTK
- GTK4: libadwaita
- opcjonalnie PyGObject, wtedy testy sprawdzają CSS prawdziwym parserem GTK

## Użycie

```sh
./install.sh --dry-run    # pokaż, co się zmieni
./install.sh              # zbuduj i zainstaluj
./uninstall.sh            # usuń nakładkę
python3 -m unittest discover -s tests
```

Po instalacji uruchom ponownie aplikacje GTK. Co sprawdzić: [tests/CHECKLIST.md](tests/CHECKLIST.md).

### Co robi instalator

1. Kopiuje wszystkie dotykane pliki do `~/.config/gtk-cyberdream-bak-RRRRMMDD-GGMMSS/`.
2. W `~/.config/gtk-3.0` i `~/.config/gtk-4.0` zapisuje wygenerowany `cyberdream.css`
   i dopisuje do `gtk.css` linię `@import url("cyberdream.css");` po pozostałych importach.
3. Zapisuje schematy edytorów: `~/.local/share/gtksourceview-5/styles/cyberdream.xml`
   i `~/.config/geany/colorschemes/cyberdream.conf`.

Schemat edytora trzeba raz wybrać w aplikacji:

- Text Editor: menu → Preferencje, albo
  `gsettings set org.gnome.TextEditor style-scheme cyberdream` (powrót: `Adwaita`)
- Geany: Widok → Zmień schemat kolorów → Cyberdream

Na końcu wypisuje komendę cofającą zmiany:

```sh
./install.sh --restore ~/.config/gtk-cyberdream-bak-RRRRMMDD-GGMMSS
```

Pliki są kopiowane, nie dowiązywane, żeby widziały je też Flatpaki z dostępem do
`xdg-config/gtk-3.0` i `xdg-config/gtk-4.0`.

### DankMaterialShell

Instalator współpracuje z kolorami GTK generowanymi przez DMS (sprawdzone na 2.0.0.r45).
DMS dodaje lub usuwa w `gtk.css` wyłącznie własną linię `@import url("dank-colors.css");`
(albo dowiązanie `gtk.css -> dank-colors.css`), a pozostałych linii nie rusza.
Import cyberdream stoi po imporcie DMS, więc to jego kolory wygrywają.

## Zmiana kolorów

| Plik | Zawartość |
|---|---|
| `palette.toml` | 15 kolorów cyberdream i wybór akcentu |
| `roles.toml` | role (np. `raised_bg = "bg_alt"`) i mapowanie ról na nazwane kolory GTK |
| `cyberdream_gtk/templates/*.css` | reguły CSS z odwołaniami `{{rola}}` |

Akcent zmienia jedna linia w `palette.toml`, po czym trzeba ponownie uruchomić `./install.sh`:

```toml
accent = "blue"   # domyślnie "green"; dowolna nazwa koloru z palety
```

Wyrażenia dostępne w `roles.toml` i w szablonach: nazwa koloru lub roli, `#rrggbb`,
`alpha(kolor, 0.3)`, `mix(a, b, 0.25)`. Generator wylicza je do gotowych wartości,
więc wynikowy CSS nie zależy od funkcji kolorów konkretnej wersji GTK.

## Budowa

```
palette.toml, roles.toml      źródło prawdy
cyberdream_gtk/
  color.py                    kolory i wyrażenia
  palette.py                  wczytanie i walidacja
  render.py                   szablony -> CSS
  targets/                    cele wyjściowe (gtk3, gtk4, sourceview, geany)
  templates/                  common.css, gtk3.css, gtk4.css, sourceview.xml, geany.conf
  install.py, cli.py          instalator i wiersz poleceń
tests/                        testy i lista kontrolna
build/                        wynik (poza repozytorium)
```

Każdy cel to wpis `Target` w `cyberdream_gtk/targets/`: rodzaj (nakładka GTK albo
zwykły plik), miejsce instalacji, sekcje nazwanych kolorów i lista szablonów. Faza 2 (pełny, samodzielny arkusz) albo cele
dla Flatpaka czy Kvantum dochodzą jako kolejne moduły w tym katalogu.

## Licencja

MIT, patrz [LICENSE](LICENSE). Paleta pochodzi z cyberdream.nvim (MIT).
