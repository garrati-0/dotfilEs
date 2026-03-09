#!/bin/bash
# RAM usage (integer %)
free | awk '/^Mem/ { print int($3/$2 * 100) }'
