#!/bin/bash

# Get the artUrl using playerctl
art_url=$(playerctl metadata mpris:artUrl 2>/dev/null)
status=$(playerctl status 2>/dev/null)

if [ "$status" = "Stopped" ] || [ -z "$art_url" ]; then
    echo ""
    exit 0
fi

# Clean up url if needed
art_url=$(echo "$art_url" | sed 's/file:\/\///g')

# If it's a local file, directly echo it
if [[ "$art_url" == /* ]]; then
    if [ -f "$art_url" ]; then
        echo "$art_url"
        exit 0
    else
        echo ""
        exit 0
    fi
fi

# If it's a web URL (e.g. Spotify Web or YouTube on browser)
cache_dir="/tmp/eww_cover"
mkdir -p "$cache_dir"
cover_path="$cache_dir/cover.png"
url_file="$cache_dir/last_url.txt"

# Check if URL changed
if [ -f "$url_file" ]; then
    last_url=$(cat "$url_file")
    if [ "$last_url" = "$art_url" ] && [ -f "$cover_path" ]; then
        echo "$cover_path"
        exit 0
    fi
fi

# Download new cover
wget -q -T 3 -O "$cover_path" "$art_url" && echo "$art_url" > "$url_file"

if [ -f "$cover_path" ]; then
    echo "$cover_path"
else
    echo ""
fi
