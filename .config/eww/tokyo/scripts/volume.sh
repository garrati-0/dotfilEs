#!/bin/bash
# Usage: volume.sh get | set <0-100>
case "$1" in
  get)
    wpctl get-volume @DEFAULT_AUDIO_SINK@ 2>/dev/null \
      | awk '{printf "%d", $2 * 100}' \
      || pactl get-sink-volume @DEFAULT_SINK@ \
         | grep -oP '\d+(?=%)' | head -1
    ;;
  set)
    val=$(printf "%.0f" "$2")
    wpctl set-volume @DEFAULT_AUDIO_SINK@ "${val}%" 2>/dev/null \
      || pactl set-sink-volume @DEFAULT_SINK@ "${val}%"
    ;;
esac
