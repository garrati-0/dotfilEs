# EWW Control Center — Tokyo Night

Minimal EWW control center in Tokyo Night palette.

## Dipendenze

| Tool          | Uso                        |
|---------------|----------------------------|
| `eww`         | widget daemon              |
| `playerctl`   | controllo media MPRIS      |
| `wpctl`       | volume (pipewire)          |
| `brightnessctl` | luminosità               |
| `nmcli`       | Wi-Fi                      |
| `rfkill`      | Bluetooth                  |
| `dunstctl`    | DND                        |
| `hyprsunset`  | night mode (opzionale)     |
| `wofi`/`rofi` | power menu                 |
| JetBrainsMono Nerd Font | font con icone  |

Installa su Arch:
```bash
paru -S eww-wayland playerctl wireplumber brightnessctl \
        networkmanager dunst hyprsunset wofi \
        ttf-jetbrains-mono-nerd
```

## Struttura

```
eww-tokyonight/
├── eww.yuck        # widget definitions
├── eww.scss        # stili Tokyo Night
└── scripts/
    ├── cpu.sh
    ├── ram.sh
    ├── volume.sh
    ├── brightness.sh
    ├── mpris_pos.sh
    ├── mpris_seek.sh
    ├── wifi.sh
    ├── bt.sh
    ├── nightmode.sh
    ├── dnd.sh
    └── powermenu.sh
```

## Installazione

```bash
# 1. Copia nella config dir di eww
cp -r eww-tokyonight ~/.config/eww

# 2. Rendi eseguibili gli script
chmod +x ~/.config/eww/scripts/*.sh

# 3. Avvia il daemon
eww daemon

# 4. Apri il control center
eww open control-center
```

## Keybind Hyprland

Aggiungi a `hyprland.conf`:
```ini
bind = SUPER, C, exec, eww open --toggle control-center
```

## Palette Tokyo Night

| Nome    | Hex       |
|---------|-----------|
| bg      | `#1a1b2e` |
| surface | `#1f2040` |
| border  | `#292b4a` |
| text    | `#c0caf5` |
| blue    | `#7aa2f7` |
| purple  | `#bb9af7` |
| cyan    | `#7dcfff` |
| green   | `#9ece6a` |
| orange  | `#e0af68` |
| red     | `#f7768e` |
