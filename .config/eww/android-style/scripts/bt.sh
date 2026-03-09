#!/bin/bash
case "$1" in
  toggle)
    state=$(rfkill list bluetooth | grep -c 'yes')
    if [ "$state" -gt 0 ]; then
      rfkill unblock bluetooth
    else
      rfkill block bluetooth
    fi
    ;;
  status)
    state=$(rfkill list bluetooth | grep -c 'yes')
    if [ "$state" -gt 0 ]; then
      echo false
    else
      echo true
    fi
    ;;
esac
