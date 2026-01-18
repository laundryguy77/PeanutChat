#!/bin/bash
# =============================================================================
# Parameter Handler: 40-input.sh
# =============================================================================
# Handles: disable_input_devices, primary_keyboard_layout,
#          secondary_keyboard_layout, disable_numlock, hide_mouse,
#          mouse_cursor_size, mouse_speed, right_mouse_click,
#          touchscreen_calibration
#
# To add a new parameter:
#   1. Add parameter check below
#   2. Test: echo "param=value" >> /opt/scripts/files/lcon && /opt/scripts/apply-config
# =============================================================================

# Source config if not already sourced
[ -z "$CONFIG" ] && CONFIG="/opt/scripts/files/lcon"
[ -f "$CONFIG" ] && source "$CONFIG"

log() { echo "[$(basename "$0")] $*" >> "${LOG_FILE:-/tmp/apply-config.log}"; }

# Ensure DISPLAY is set
export DISPLAY="${DISPLAY:-:0}"

# ----- Parameter: disable_input_devices -----
# Description: Disable keyboard/mouse/touchscreen
# Values: keyboard, mouse, touchscreen, all (comma-separated)
if [ -n "$disable_input_devices" ]; then
    log "Disabling input devices: $disable_input_devices"

    if command -v xinput >/dev/null 2>&1; then
        # Get list of input devices
        devices=$(xinput list --short 2>/dev/null)

        if echo "$disable_input_devices" | grep -qi "keyboard\|all"; then
            # Disable keyboards (but not virtual keyboards)
            echo "$devices" | grep -i "keyboard" | grep -v "Virtual" | while read -r line; do
                id=$(echo "$line" | grep -oP 'id=\K[0-9]+')
                [ -n "$id" ] && xinput disable "$id" 2>/dev/null
            done
            log "Keyboards disabled"
        fi

        if echo "$disable_input_devices" | grep -qi "mouse\|all"; then
            # Disable mice/pointers
            echo "$devices" | grep -iE "mouse|pointer" | while read -r line; do
                id=$(echo "$line" | grep -oP 'id=\K[0-9]+')
                [ -n "$id" ] && xinput disable "$id" 2>/dev/null
            done
            log "Mouse disabled"
        fi

        if echo "$disable_input_devices" | grep -qi "touchscreen\|all"; then
            # Disable touchscreens
            echo "$devices" | grep -i "touch" | while read -r line; do
                id=$(echo "$line" | grep -oP 'id=\K[0-9]+')
                [ -n "$id" ] && xinput disable "$id" 2>/dev/null
            done
            log "Touchscreen disabled"
        fi
    fi
fi

# ----- Parameter: primary_keyboard_layout -----
# Description: Primary keyboard layout
# Values: Layout code (us, de, fr, gb, etc.)
if [ -n "$primary_keyboard_layout" ]; then
    log "Setting primary keyboard layout: $primary_keyboard_layout"

    if command -v setxkbmap >/dev/null 2>&1; then
        setxkbmap "$primary_keyboard_layout" 2>/dev/null && \
            log "Keyboard layout set: $primary_keyboard_layout"
    fi
fi

# ----- Parameter: secondary_keyboard_layout -----
# Description: Secondary keyboard layout (Ctrl+Space to switch)
# Values: Layout code
if [ -n "$secondary_keyboard_layout" ]; then
    log "Adding secondary keyboard layout: $secondary_keyboard_layout"

    if command -v setxkbmap >/dev/null 2>&1; then
        primary="${primary_keyboard_layout:-us}"
        setxkbmap -layout "$primary,$secondary_keyboard_layout" \
                  -option "grp:ctrl_space_toggle" 2>/dev/null && \
            log "Dual keyboard layout: $primary + $secondary_keyboard_layout"
    fi
fi

# ----- Parameter: disable_numlock -----
# Description: Disable numlock on boot
# Values: yes, no
if [ "$disable_numlock" = "yes" ]; then
    log "Disabling numlock"

    if command -v numlockx >/dev/null 2>&1; then
        numlockx off 2>/dev/null
    elif command -v xdotool >/dev/null 2>&1; then
        xdotool key Num_Lock 2>/dev/null  # Toggle if on
    fi
fi

# ----- Parameter: hide_mouse -----
# Description: Hide mouse cursor
# Values: yes, no, or timeout in seconds
if [ -n "$hide_mouse" ]; then
    log "Mouse cursor hiding: $hide_mouse"

    case "$hide_mouse" in
        yes)
            # Hide immediately using unclutter
            if command -v unclutter >/dev/null 2>&1; then
                killall unclutter 2>/dev/null
                unclutter -idle 0 -root &
                log "Mouse cursor hidden"
            else
                # Alternative: move cursor off screen
                xdotool mousemove 9999 9999 2>/dev/null
            fi
            ;;
        no)
            killall unclutter 2>/dev/null
            ;;
        *)
            # Numeric value = timeout in seconds
            if [ "$hide_mouse" -gt 0 ] 2>/dev/null; then
                if command -v unclutter >/dev/null 2>&1; then
                    killall unclutter 2>/dev/null
                    unclutter -idle "$hide_mouse" -root &
                    log "Mouse cursor hides after ${hide_mouse}s"
                fi
            fi
            ;;
    esac
fi

# ----- Parameter: mouse_cursor_size -----
# Description: Mouse cursor size
# Values: normal, large (or pixel size)
if [ -n "$mouse_cursor_size" ]; then
    log "Mouse cursor size: $mouse_cursor_size"

    case "$mouse_cursor_size" in
        normal) size=24 ;;
        large)  size=48 ;;
        *)      size="$mouse_cursor_size" ;;
    esac

    # Set cursor size via Xresources
    echo "Xcursor.size: $size" | xrdb -merge 2>/dev/null
fi

# ----- Parameter: mouse_speed -----
# Description: Mouse pointer speed
# Values: 0-100 (percentage)
if [ -n "$mouse_speed" ]; then
    log "Mouse speed: $mouse_speed"

    if command -v xinput >/dev/null 2>&1; then
        # Find pointer devices
        for device in $(xinput list --id-only 2>/dev/null); do
            # Check if device has acceleration
            if xinput list-props "$device" 2>/dev/null | grep -qi "accel"; then
                # Convert 0-100 to acceleration multiplier
                # 0 = 0.1x, 50 = 1x, 100 = 3x
                if [ "$mouse_speed" -lt 50 ]; then
                    accel=$(awk "BEGIN {printf \"%.2f\", 0.1 + ($mouse_speed / 50) * 0.9}")
                else
                    accel=$(awk "BEGIN {printf \"%.2f\", 1 + (($mouse_speed - 50) / 50) * 2}")
                fi

                xinput set-prop "$device" "libinput Accel Speed" "$accel" 2>/dev/null || \
                xinput set-prop "$device" "Device Accel Constant Deceleration" "$accel" 2>/dev/null
            fi
        done
    fi
fi

# ----- Parameter: right_mouse_click -----
# Description: Enable right-click context menu
# Values: yes, no
if [ "$right_mouse_click" = "no" ]; then
    log "Disabling right mouse click"

    # Disable button 3 (right click) using xinput
    if command -v xinput >/dev/null 2>&1; then
        for device in $(xinput list --id-only 2>/dev/null); do
            # Remap button 3 to button 1 (effectively disables right-click)
            xinput set-button-map "$device" 1 2 1 2>/dev/null
        done
    fi
fi

# ----- Parameter: touchscreen_calibration -----
# Description: Touchscreen calibration data
# Values: Calibration matrix or calibration file URL
if [ -n "$touchscreen_calibration" ]; then
    log "Touchscreen calibration: $touchscreen_calibration"

    # Check if it's a URL
    if echo "$touchscreen_calibration" | grep -qE '^https?://'; then
        cal_file="/tmp/touchscreen_calibration"
        wget -q -O "$cal_file" "$touchscreen_calibration" 2>/dev/null
    else
        # Assume it's calibration matrix values
        cal_data="$touchscreen_calibration"
    fi

    # Apply calibration using xinput
    if command -v xinput >/dev/null 2>&1; then
        # Find touchscreen device
        touch_id=$(xinput list 2>/dev/null | grep -i "touch" | grep -oP 'id=\K[0-9]+' | head -1)

        if [ -n "$touch_id" ] && [ -n "$cal_data" ]; then
            xinput set-prop "$touch_id" "Coordinate Transformation Matrix" $cal_data 2>/dev/null && \
                log "Touchscreen calibration applied"
        fi
    fi
fi

log "Input handler completed"
