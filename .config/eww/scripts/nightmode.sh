#!/bin/bash
case "$1" in
  toggle)
    if pgrep -x wlsunset > /dev/null; then
      pkill wlsunset
    else
      wlsunset -t 5800 &
    fi
    ;;
  status)
    if pgrep -x wlsunset > /dev/null; then
      echo true
    else
      echo false
    fi
    ;;
esac
