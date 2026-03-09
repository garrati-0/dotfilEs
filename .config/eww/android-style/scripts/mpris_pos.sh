#!/bin/bash
# Returns playback position as 0-100
export LC_ALL=C

pos=$(playerctl position 2>/dev/null) || { echo 0; exit; }
len=$(playerctl metadata mpris:length 2>/dev/null) || { echo 0; exit; }

# length is in microseconds
len_sec=$(echo "$len / 1000000" | bc -l 2>/dev/null)

[ -z "$len_sec" ] || [ "$len_sec" = "0" ] || [ "$len_sec" = "0.00000000000000000000" ] && { echo 0; exit; }

echo "$pos $len_sec" | awk '{printf "%d\n", ($1/$2)*100}' || echo 0
