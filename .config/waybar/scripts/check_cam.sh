#!/bin/bash
# Controlla se la webcam è in uso
if fuser /dev/video* >/dev/null 2>&1; then
    echo '{"alt": "active", "class": "active", "tooltip": "Fotocamera in uso"}'
else
    echo '{"alt": "inactive", "class": "inactive", "tooltip": ""}'
fi
