#!/bin/bash
# Usage: brightness.sh get | set <0-100>
# Tries brightnessctl first, falls back to xrandr
case "$1" in
  get)
    brightnessctl -m 2>/dev/null \
      | awk -F',' '{gsub(/%/,"",$4); print int($4)}' \
      || echo 80
    ;;
  set)
    val=$(printf "%.0f" "$2")
    brightnessctl set "${val}%" 2>/dev/null \
      || xrandr --output "$(xrandr | awk '/ connected/{print $1; exit}')" \
                --brightness "$(echo "$val / 100" | bc -l)"
    ;;
esac
