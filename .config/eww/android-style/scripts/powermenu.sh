#!/bin/bash
# Simple power menu with wofi / rofi fallback
OPTIONS="  Shutdown\n  Reboot\n  Suspend\n  Lock\n󰍃  Logout"

if command -v wofi &>/dev/null; then
  CHOICE=$(echo -e "$OPTIONS" | wofi --dmenu --prompt "Power" --width 180 --height 220)
elif command -v rofi &>/dev/null; then
  CHOICE=$(echo -e "$OPTIONS" | rofi -dmenu -p "Power")
else
  exit 1
fi

case "$CHOICE" in
  *Shutdown) systemctl poweroff ;;
  *Reboot)   systemctl reboot   ;;
  *Suspend)  systemctl suspend  ;;
  *Lock)     loginctl lock-session ;;
  *Logout)   hyprctl dispatch exit ;;
esac
