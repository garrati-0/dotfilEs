#!/usr/bin/env bash
# rofi-web-search.sh — Search Google via Chrome

QUERY=$(rofi -dmenu \
    -p " Cerca su Google" \
    -theme-str 'listview { lines: 0; }' \
    -theme-str 'mainbox { children: [ inputbar ]; }' \
    -theme-str 'window { width: 500; }')

[ -z "$QUERY" ] && exit 0

# URL-encode the query
ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote_plus('$QUERY'))")

google-chrome "https://www.google.com/search?q=${ENCODED}" &
