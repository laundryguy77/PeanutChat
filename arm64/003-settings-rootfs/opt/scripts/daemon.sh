#!/bin/bash
# =============================================================================
# daemon.sh - Configuration polling daemon for Porteus Kiosk ARM64
# =============================================================================
# Polls remote config URL at intervals and triggers reconfiguration when
# config changes. Supports daemon_force_reboot and daemon_message parameters.
#
# Config file: /opt/scripts/files/lcon
# Remote config: /opt/scripts/files/rcon
# =============================================================================

LCON="/opt/scripts/files/lcon"
RCON="/opt/scripts/files/rcon"
LCONC="/opt/scripts/files/lconc"  # Filtered local config for comparison
RCONC="/opt/scripts/files/rconc"  # Filtered remote config for comparison
CHECK_INTERVAL=60
LOG_FILE="/tmp/daemon.log"

log() {
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $*" >> "$LOG_FILE"
}

log "=== daemon.sh started ==="

# Function to filter config for comparison
# Excludes: daemon_*, burn_dev=, md5conf= (these shouldn't trigger reconfiguration)
filter_config() {
    local input="$1"
    grep -v '^daemon_\|^burn_dev=\|^md5conf=' "$input" 2>/dev/null | sort
}

# Function to show notification
notify() {
    local urgency="${1:-normal}"
    local message="$2"
    log "NOTIFY [$urgency]: $message"
    dunstify -u "$urgency" "$message" 2>/dev/null || true
}

while true; do
    # Read config URL from local config
    CONFIG_URL=$(grep "^kiosk_config=" "$LCON" 2>/dev/null | cut -d= -f2-)

    if [ -n "$CONFIG_URL" ]; then
        log "Polling config from: $CONFIG_URL"

        # Download remote config
        if wget -q -T 30 -O "$RCON.tmp" "$CONFIG_URL" 2>/dev/null; then
            if [ -s "$RCON.tmp" ]; then
                mv "$RCON.tmp" "$RCON"
                log "Remote config downloaded successfully"

                # Create filtered versions for comparison
                filter_config "$LCON" > "$LCONC"
                filter_config "$RCON" > "$RCONC"

                # Compare filtered configs using MD5
                lcon_md5=$(md5sum "$LCONC" 2>/dev/null | cut -d' ' -f1)
                rcon_md5=$(md5sum "$RCONC" 2>/dev/null | cut -d' ' -f1)

                if [ "$lcon_md5" != "$rcon_md5" ]; then
                    log "Config changed (local: $lcon_md5, remote: $rcon_md5)"

                    # Check for daemon_message in remote config
                    daemon_message=$(grep "^daemon_message=" "$RCON" 2>/dev/null | cut -d= -f2-)
                    if [ -n "$daemon_message" ]; then
                        notify "normal" "$daemon_message"
                    fi

                    # Check for daemon_force_reboot
                    if grep -q "^daemon_force_reboot=yes" "$RCON" 2>/dev/null; then
                        log "daemon_force_reboot=yes detected"
                        notify "critical" "Configuration changed. System will reboot in 30 seconds..."

                        # Update local config before reboot
                        cp "$RCON" "$LCON"

                        # Apply config changes
                        /opt/scripts/apply-config "$RCON" 2>/dev/null

                        # Countdown and reboot
                        sleep 30
                        sync
                        init 6
                        exit 0
                    fi

                    # Normal update: apply config and trigger update-config if present
                    notify "normal" "Configuration update detected..."

                    # Apply the new config parameters
                    /opt/scripts/apply-config "$RCON" 2>/dev/null &

                    # If update-config exists, run it (for module updates/ISO rebuild)
                    if [ -x /opt/scripts/update-config ]; then
                        log "Triggering update-config"
                        /opt/scripts/update-config &
                    fi

                    # Update local config after successful processing
                    cp "$RCON" "$LCON"
                else
                    log "Config unchanged"
                fi
            else
                log "WARNING: Downloaded config is empty"
                rm -f "$RCON.tmp"
            fi
        else
            log "WARNING: Failed to download config from $CONFIG_URL"
        fi
    else
        log "No kiosk_config URL configured, skipping poll"
    fi

    # Get check interval from config (default 60 seconds)
    interval=$(grep "^daemon_check=" "$LCON" 2>/dev/null | cut -d= -f2-)
    if [ -n "$interval" ] && [ "$interval" -gt 0 ] 2>/dev/null; then
        CHECK_INTERVAL=$interval
    fi

    log "Sleeping for $CHECK_INTERVAL seconds"
    sleep "$CHECK_INTERVAL"
done
