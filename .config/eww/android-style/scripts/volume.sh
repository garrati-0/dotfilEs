#!/bin/bash
# Usage: volume.sh get | set <0-100>

export LC_ALL=C

case "$1" in
  get)
    # Get volume, replace comma with dot for awk, multiply by 100
    wpctl get-volume @DEFAULT_AUDIO_SINK@ 2>/dev/null \
      | tr ',' '.' \
      | awk '{printf "%d\n", $2 * 100}' \
      || pactl get-sink-volume @DEFAULT_SINK@ 2>/dev/null \
         | grep -oP '\d+(?=%)' | head -1 \
      || echo "0"
    ;;
  set)
    # Ensure value is an integer
    val=$(printf "%.0f" "$2" 2>/dev/null || echo "0")
    wpctl set-volume -l 1.0 @DEFAULT_AUDIO_SINK@ "${val}%" 2>/dev/null \
      || pactl set-sink-volume @DEFAULT_SINK@ "${val}%" 2>/dev/null
    ;;
esac
