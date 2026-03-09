#!/bin/bash
# Close only if it's actually open to avoid spamming stderr
eww active-windows | grep -q "control-center" && eww close control-center 2>/dev/null
