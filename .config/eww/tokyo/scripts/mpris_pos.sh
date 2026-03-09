#!/bin/bash
# Returns playback position as 0-100
pos=$(playerctl position 2>/dev/null) || { echo 0; exit; }
len=$(playerctl metadata mpris:length 2>/dev/null) || { echo 0; exit; }
# length is in microseconds
len_sec=$(echo "$len / 1000000" | bc -l 2>/dev/null)
[ -z "$len_sec" ] || [ "$len_sec" = "0" ] && { echo 0; exit; }
echo "$pos $len_sec" | awk '{printf "%d", ($1/$2)*100}'
