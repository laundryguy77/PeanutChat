#!/bin/sh
# =============================================================================
# variables.sh - Environment variables for Porteus Kiosk ARM64
# =============================================================================
# Sourced by shells to provide consistent paths and settings.
# Based on x86 Porteus Kiosk with ARM64 adaptations.
# =============================================================================

export \
autostart=/etc/xdg/openbox/autostart \
scripts=/opt/scripts \
profile=/home/guest/.mozilla/firefox/default \
pprofile=/opt/scripts/guest/.mozilla/firefox/default \
json=/etc/chromium/policies/managed/policy.json \
chflags=/etc/chromium-flags.conf \
LCON=/opt/scripts/files/lcon \
RCON=/opt/scripts/files/rcon \
DISPLAY=:0
