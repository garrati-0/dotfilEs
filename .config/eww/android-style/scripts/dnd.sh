#!/bin/bash
case "$1" in
  toggle)
    swaync-client -d -sw
    ;;
  status)
    state=$(swaync-client -D -sw)
    if [ "$state" = "true" ]; then
      echo true
    else
      echo false
    fi
    ;;
esac
