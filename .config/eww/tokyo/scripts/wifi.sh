#!/bin/bash
case "$1" in
  toggle)
    state=$(nmcli radio wifi)
    if [ "$state" = "enabled" ]; then
      nmcli radio wifi off
    else
      nmcli radio wifi on
    fi
    ;;
  status)
    if [ "$(nmcli radio wifi)" = "enabled" ]; then
      echo true
    else
      echo false
    fi
    ;;
esac
