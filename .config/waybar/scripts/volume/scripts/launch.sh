#!/bin/bash
WIDGET_WIDTH=280
# Prende la posizione X del mouse
MOUSE_X=$(hyprctl cursorpos | cut -d',' -f1)
# Calcola la posizione per centrare il widget
TARGET_X=$((MOUSE_X - WIDGET_WIDTH / 2))

# Usiamo il flag -c per essere sicuri di parlare col demone giusto
eww -c ~/.config/waybar/scripts/volume update vol_x="${TARGET_X}px"
eww -c ~/.config/waybar/scripts/volume open --toggle audiomenu
