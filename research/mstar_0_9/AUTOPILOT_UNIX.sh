#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 autopilot.py --mode full --output results/latest
