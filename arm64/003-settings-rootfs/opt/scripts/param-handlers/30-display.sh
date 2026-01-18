#!/bin/bash
# =============================================================================
# Parameter Handler: 30-display.sh
# =============================================================================
# Handles: wallpaper, screen_settings, screen_rotate
#
# To add a new parameter:
#   1. Add parameter check below
#   2. Test: echo "param=value" >> /opt/scripts/files/lcon && /opt/scripts/apply-config
# =============================================================================

# Source config if not already sourced
[ -z "$CONFIG" ] && CONFIG="/opt/scripts/files/lcon"
[ -f "$CONFIG" ] && source "$CONFIG"

log() { echo "[$(basename "$0")] $*" >> "${LOG_FILE:-/tmp/apply-config.log}"; }

# Ensure DISPLAY is set for X commands
export DISPLAY="${DISPLAY:-:0}"

# ----- Parameter: wallpaper -----
# Description: Desktop background image URL
# Values: URL to image file (jpg, png)
if [ -n "$wallpaper" ]; then
    log "Setting wallpaper: $wallpaper"

    WALLPAPER_DIR="/usr/share/wallpapers"
    WALLPAPER_FILE="$WALLPAPER_DIR/custom_wallpaper"

    # Download wallpaper if URL
    if echo "$wallpaper" | grep -qE '^https?://'; then
        mkdir -p "$WALLPAPER_DIR"

        # Determine extension from URL
        ext="${wallpaper##*.}"
        [ "$ext" = "$wallpaper" ] && ext="jpg"
        WALLPAPER_FILE="$WALLPAPER_DIR/custom_wallpaper.$ext"

        if wget -q -O "$WALLPAPER_FILE" "$wallpaper" 2>/dev/null; then
            log "Downloaded wallpaper to: $WALLPAPER_FILE"
        else
            log "WARNING: Failed to download wallpaper"
            WALLPAPER_FILE=""
        fi
    elif [ -f "$wallpaper" ]; then
        WALLPAPER_FILE="$wallpaper"
    fi

    # Apply wallpaper using feh
    if [ -n "$WALLPAPER_FILE" ] && [ -f "$WALLPAPER_FILE" ]; then
        if command -v feh >/dev/null 2>&1; then
            feh --bg-scale "$WALLPAPER_FILE" 2>/dev/null && log "Wallpaper applied"
        else
            log "WARNING: feh not available for setting wallpaper"
        fi
    fi
fi

# ----- Parameter: screen_settings -----
# Description: Screen resolution and positioning
# Values: WIDTHxHEIGHT or WIDTHxHEIGHT+X+Y for positioning
if [ -n "$screen_settings" ]; then
    log "Applying screen settings: $screen_settings"

    if command -v xrandr >/dev/null 2>&1; then
        # Get primary output
        output=$(xrandr 2>/dev/null | grep " connected" | head -1 | cut -d' ' -f1)

        if [ -n "$output" ]; then
            # Parse resolution and position
            if echo "$screen_settings" | grep -qE '^[0-9]+x[0-9]+\+'; then
                # Has position: WIDTHxHEIGHT+X+Y
                resolution=$(echo "$screen_settings" | cut -d'+' -f1)
                position=$(echo "$screen_settings" | sed 's/^[^+]*//')
                xrandr --output "$output" --mode "$resolution" --pos "${position#+}" 2>/dev/null
            else
                # Just resolution
                xrandr --output "$output" --mode "$screen_settings" 2>/dev/null
            fi
            log "Screen settings applied to $output"
        else
            log "WARNING: No display output found"
        fi
    else
        log "WARNING: xrandr not available"
    fi
fi

# ----- Parameter: screen_rotate -----
# Description: Screen rotation
# Values: normal, left, right, inverted (or 0, 90, 180, 270)
if [ -n "$screen_rotate" ]; then
    log "Rotating screen: $screen_rotate"

    if command -v xrandr >/dev/null 2>&1; then
        # Get primary output
        output=$(xrandr 2>/dev/null | grep " connected" | head -1 | cut -d' ' -f1)

        if [ -n "$output" ]; then
            # Normalize rotation value
            case "$screen_rotate" in
                0|normal)   rotation="normal" ;;
                90|left)    rotation="left" ;;
                180|inverted) rotation="inverted" ;;
                270|right)  rotation="right" ;;
                *)          rotation="$screen_rotate" ;;
            esac

            xrandr --output "$output" --rotate "$rotation" 2>/dev/null && \
                log "Screen rotated: $rotation on $output"
        else
            log "WARNING: No display output found"
        fi
    else
        log "WARNING: xrandr not available"
    fi
fi

log "Display handler completed"
