#!/bin/bash
# =============================================================================
# Parameter Handler: 50-power.sh
# =============================================================================
# Handles: screensaver_idle, screensaver_archive, screensaver_archive_update,
#          slide_duration, slide_random, screensaver_video, screensaver_webpage,
#          dpms_idle, freeze_idle, standby_idle, suspend_idle, halt_idle,
#          session_idle, session_idle_action, session_idle_forced
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

# ----- Parameter: screensaver_idle -----
# Description: Activate screensaver after idle time
# Values: Minutes (0 = disabled)
if [ -n "$screensaver_idle" ]; then
    log "Screensaver idle: $screensaver_idle minutes"

    if [ "$screensaver_idle" -gt 0 ] 2>/dev/null; then
        # Configure xscreensaver or start custom screensaver
        timeout_sec=$((screensaver_idle * 60))

        # Set X screensaver timeout
        xset s "$timeout_sec" "$timeout_sec" 2>/dev/null

        # If using xscreensaver
        if command -v xscreensaver >/dev/null 2>&1; then
            # Update xscreensaver settings
            mkdir -p /home/guest
            cat > /home/guest/.xscreensaver << EOF
timeout: 0:$screensaver_idle:00
mode: blank
EOF
        fi
    else
        # Disable screensaver
        xset s off 2>/dev/null
    fi
fi

# ----- Parameter: screensaver_archive -----
# Description: ZIP file containing slideshow images
# Values: URL to ZIP file
if [ -n "$screensaver_archive" ]; then
    log "Screensaver archive: $screensaver_archive"

    SLIDE_DIR="/tmp/screensaver_slides"
    mkdir -p "$SLIDE_DIR"

    # Download and extract archive
    if wget -q -O /tmp/slides.zip "$screensaver_archive" 2>/dev/null; then
        unzip -o -q /tmp/slides.zip -d "$SLIDE_DIR" 2>/dev/null
        rm -f /tmp/slides.zip
        log "Screensaver slides extracted to $SLIDE_DIR"
    else
        log "WARNING: Failed to download screensaver archive"
    fi
fi

# ----- Parameter: screensaver_archive_update -----
# Description: Auto-update slideshow at interval
# Values: Minutes between updates
if [ -n "$screensaver_archive_update" ]; then
    log "Screensaver archive update interval: $screensaver_archive_update minutes"
    # Would set up periodic re-download
fi

# ----- Parameter: slide_duration -----
# Description: Duration each slide is shown
# Values: Seconds
if [ -n "$slide_duration" ]; then
    log "Slide duration: $slide_duration seconds"
fi

# ----- Parameter: slide_random -----
# Description: Randomize slide order
# Values: yes, no
if [ "$slide_random" = "yes" ]; then
    log "Random slide order enabled"
fi

# ----- Parameter: screensaver_video -----
# Description: Video file for screensaver
# Values: URL or path to video file
if [ -n "$screensaver_video" ]; then
    log "Screensaver video: $screensaver_video"

    VIDEO_FILE="/tmp/screensaver_video"

    # Download if URL
    if echo "$screensaver_video" | grep -qE '^https?://'; then
        ext="${screensaver_video##*.}"
        wget -q -O "${VIDEO_FILE}.${ext}" "$screensaver_video" 2>/dev/null && \
            log "Screensaver video downloaded"
    fi
fi

# ----- Parameter: screensaver_webpage -----
# Description: Webpage displayed as screensaver
# Values: URL
if [ -n "$screensaver_webpage" ]; then
    log "Screensaver webpage: $screensaver_webpage"
fi

# ----- Parameter: dpms_idle -----
# Description: Turn off monitor after idle time
# Values: Minutes (0 = disabled)
if [ -n "$dpms_idle" ]; then
    log "DPMS idle: $dpms_idle minutes"

    if [ "$dpms_idle" -gt 0 ] 2>/dev/null; then
        timeout_sec=$((dpms_idle * 60))
        xset dpms "$timeout_sec" "$timeout_sec" "$timeout_sec" 2>/dev/null
        xset +dpms 2>/dev/null
        log "DPMS enabled: monitor off after $dpms_idle minutes"
    else
        xset -dpms 2>/dev/null
        log "DPMS disabled"
    fi
fi

# ----- Parameter: freeze_idle -----
# Description: Freeze kiosk after idle time
# Values: Minutes
if [ -n "$freeze_idle" ]; then
    log "Freeze idle: $freeze_idle minutes"
    # Would set up xautolock or similar
fi

# ----- Parameter: standby_idle -----
# Description: Standby mode after idle time
# Values: Minutes
if [ -n "$standby_idle" ]; then
    log "Standby idle: $standby_idle minutes"
fi

# ----- Parameter: suspend_idle -----
# Description: Suspend system after idle time
# Values: Minutes
if [ -n "$suspend_idle" ]; then
    log "Suspend idle: $suspend_idle minutes"

    if [ "$suspend_idle" -gt 0 ] 2>/dev/null; then
        timeout_sec=$((suspend_idle * 60))

        if command -v xautolock >/dev/null 2>&1; then
            killall xautolock 2>/dev/null
            xautolock -time "$suspend_idle" -locker "systemctl suspend" &
            log "Suspend after $suspend_idle minutes of inactivity"
        fi
    fi
fi

# ----- Parameter: halt_idle -----
# Description: Power off after idle time
# Values: Minutes
if [ -n "$halt_idle" ]; then
    log "Halt idle: $halt_idle minutes"

    if [ "$halt_idle" -gt 0 ] 2>/dev/null; then
        if command -v xautolock >/dev/null 2>&1; then
            killall xautolock 2>/dev/null
            xautolock -time "$halt_idle" -locker "poweroff" &
            log "Shutdown after $halt_idle minutes of inactivity"
        fi
    fi
fi

# ----- Parameter: session_idle -----
# Description: Restart session after idle time
# Values: Minutes
if [ -n "$session_idle" ]; then
    log "Session idle: $session_idle minutes"
fi

# ----- Parameter: session_idle_action -----
# Description: Action when session idle
# Values: restart, lock
if [ -n "$session_idle_action" ]; then
    log "Session idle action: $session_idle_action"
fi

# ----- Parameter: session_idle_forced -----
# Description: Force session restart at interval
# Values: Minutes
if [ -n "$session_idle_forced" ]; then
    log "Forced session restart: every $session_idle_forced minutes"
fi

log "Power handler completed"
