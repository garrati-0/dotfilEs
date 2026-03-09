#!/bin/bash
case "$1" in
  toggle)
    if rfkill list | grep -q 'Soft blocked: yes'; then
      rfkill unblock all
    else
      rfkill block all
    fi
    ;;
  status)
    if rfkill list | grep -q 'Soft blocked: yes'; then
      echo true
    else
      echo false
    fi
    ;;
esac
