# Lista kontrolna po instalacji

Przed sprawdzaniem zamknij i otwórz ponownie każdą aplikację (GTK wczytuje CSS przy starcie).

Oczekiwane kolory:

| Element | Kolor |
|---|---|
| tło okna i widoków | `#16181a` |
| paski nagłówka, karty, dialogi, popovery | `#1e2124` |
| panel boczny | `#111214` |
| linie (pod nagłówkiem, obok panelu, wokół menu) | `#3c4048` |
| akcent | `#5eff6c` |
| tekst drugorzędny | `#7b8496` |
| odnośniki | `#5ef1ff`, odwiedzone `#bd5eff` |

## Wszędzie

- [ ] Brak ostrzeżeń `Theme parsing error` po uruchomieniu aplikacji z terminala.
- [ ] Zaznaczony wiersz ma zielonkawe tło i czytelny biały tekst.
- [ ] Przycisk akcji głównej (zielony) ma ciemny, czytelny napis.
- [ ] Przycisk akcji niszczącej (czerwony) ma ciemny, czytelny napis.
- [ ] Suwak przewijania: szary, jaśniejszy po najechaniu, zielony przy przeciąganiu.
- [ ] Dymek podpowiedzi: tło `#111214`, cienka ramka, biały tekst.
- [ ] Przełączniki, pola wyboru i paski postępu są zielone.
- [ ] Okno bez fokusu nie miga i nie zmienia koloru na szary Adwaita.

## GTK4 / libadwaita

- [ ] **Menedżer plików (np. Files):** panel boczny ciemniejszy od listy plików, z linią
      na krawędzi; zaznaczenie w widoku listy i siatki; pasek ścieżki; menu pod prawym
      przyciskiem z ramką; toast po skopiowaniu lub usunięciu pliku.
- [ ] **Edytor tekstu (np. Text Editor):** okno preferencji (karty `#1e2124` na tle
      `#16181a`), karty, menu. Obszar edycji ze schematem „Cyberdream": tło `#16181a`,
      zielony kursor, komentarze szare, napisy zielone, czytelne zaznaczenie i wyniki
      wyszukiwania.
- [ ] **Aplikacja z listami w ramkach i dialogami** (np. dowolne okno ustawień): wiersze,
      przełączniki, dialog potwierdzenia z przyciskiem głównym i niszczącym.
- [ ] **Aplikacja GTK4 bez libadwaita** (np. pavucontrol): suwaki i karty zielone; takie
      aplikacje biorą akcent ze zmiennej `--accent-bg-color`.

Do oceny (świadome decyzje projektu, łatwe do zmiany w `roles.toml` i szablonach):

- [ ] Paski nagłówka po stronie treści mają kolor `#1e2124` i linię pod spodem, także
      w aplikacjach z płaskim nagłówkiem libadwaita; nagłówek panelu bocznego zostaje
      w kolorze panelu (reguła `toolbarview > .top-bar` w `templates/gtk4.css`).
- [ ] Linia pod nagłówkiem (`headerbar_shade_color`) nie jest zbyt mocna.
- [ ] Tekst drugorzędny (`.dimmed`) w kolorze `#7b8496` wygląda dobrze także na
      zaznaczonych wierszach.

## GTK3 / adw-gtk3-dark

- [ ] **Aplikacja z paskiem menu** (np. Geany): menu rozwijane (ramka, podświetlenie
      pozycji), karty, drzewo (zaznaczenie jako zielonkawa płytka z białym tekstem);
      obszar edycji ze schematem „Cyberdream" ma tło `#16181a`.
- [ ] **Aplikacja z listą i paskiem nagłówka** (np. Disks): nagłówek `#1e2124`,
      zaznaczenie wiersza, menu.
- [ ] **Przeglądarka dokumentów** (np. Evince): panel miniatur, zaznaczenie tekstu.
- [ ] Aplikacje z własnym motywem (np. GIMP): sprawdź tylko okna wyboru plików.

## Inne

- [ ] **Firefox:** menu pod prawym przyciskiem ma ciemne tło i czytelny tekst.
- [ ] **Flatpak (dowolna aplikacja GTK):** kolory takie same jak w aplikacjach natywnych.
- [ ] **Aplikacje Electron/Tauri:** mają własny wygląd; sprawdź tylko systemowe okna
      wyboru plików.
- [ ] **DankMaterialShell (jeśli używany):** po zmianie motywu w DMS plik
      `~/.config/gtk-4.0/gtk.css` nadal zawiera linię `@import url("cyberdream.css");`.

## Cofnięcie

```sh
./install.sh --restore ~/.config/gtk-cyberdream-bak-RRRRMMDD-GGMMSS
```
