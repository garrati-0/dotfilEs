#!/bin/bash
if eww active-windows | grep -q "control-center"; then
    eww close control-center 2>/dev/null
else
    eww open control-center 2>/dev/null
fi
