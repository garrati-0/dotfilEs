#!/bin/bash
# CPU usage (integer %)
grep 'cpu ' /proc/stat | awk '{
  idle=$5; total=$2+$3+$4+$5+$6+$7+$8
  print int(100 - idle*100/total)
}'
