#!/bin/bash
# Seek to position given as 0-100
pct="$1"
len=$(playerctl metadata mpris:length 2>/dev/null) || exit
len_sec=$(echo "$len / 1000000" | bc -l)
target=$(echo "$pct $len_sec" | awk '{printf "%.1f", ($1/100)*$2}')
playerctl position "$target"
