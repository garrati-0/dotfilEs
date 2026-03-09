#!/bin/bash
# Returns formatted playback time e.g. "01:23 / 03:45"
export LC_ALL=C

status=$(playerctl status 2>/dev/null)
if [ "$status" = "Stopped" ] || [ -z "$status" ]; then
    echo ""
    exit 0
fi

pos=$(playerctl position 2>/dev/null) || { echo ""; exit; }
len=$(playerctl metadata mpris:length 2>/dev/null) || { echo ""; exit; }

# Length is in microseconds
len_sec=$(echo "$len / 1000000" | bc -l 2>/dev/null)

[ -z "$len_sec" ] || [ "$len_sec" = "0" ] || [ "$len_sec" = "0.00000000000000000000" ] && { echo ""; exit; }

pos_int=$(printf "%.0f" "$pos" 2>/dev/null || echo 0)
len_int=$(printf "%.0f" "$len_sec" 2>/dev/null || echo 0)

# Format to MM:SS
pos_min=$((pos_int / 60))
pos_sec=$((pos_int % 60))
len_min=$((len_int / 60))
len_sec=$((len_int % 60))

printf "%02d:%02d / %02d:%02d\n" $pos_min $pos_sec $len_min $len_sec
