#!/bin/bash
if command -v nvidia-smi &> /dev/null; then
  nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | awk '{print $1}'
elif ls /sys/class/drm/card*/device/gpu_busy_percent &> /dev/null; then
  cat /sys/class/drm/card*/device/gpu_busy_percent | head -n1
else
  echo "0"
fi
