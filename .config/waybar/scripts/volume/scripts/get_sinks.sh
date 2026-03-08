#!/bin/bash
DEFAULT_SINK=$(LC_ALL=C pactl get-default-sink 2>/dev/null)
LC_ALL=C pactl -f json list sinks 2>/dev/null | jq -c --arg def "$DEFAULT_SINK" '[.[] | {id: .name, name: .description, is_default: (.name == $def)}]'
