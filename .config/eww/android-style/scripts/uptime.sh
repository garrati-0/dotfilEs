#!/bin/bash
uptime -p | sed 's/^up //; s/ years\?/y/g; s/ weeks\?/w/g; s/ days\?/d/g; s/ hours\?/h/g; s/ minutes\?/m/g; s/,\s*//g'
