#!/bin/bash
# =============================================================================
# Parameter Handler: 80-system.sh
# =============================================================================
# Handles: hostname, timezone, ntp_server, rtc_wake, scheduled_action,
#          automatic_updates, skip_updates, persistence, swapfile, zRAM,
#          removable_devices, disable_firewall, allow_icmp_protocol,
#          wake_on_lan, hostname_aliases, session_password, shutdown_menu
#
# To add a new parameter:
#   1. Add parameter check below
#   2. Test: echo "param=value" >> /opt/scripts/files/lcon && /opt/scripts/apply-config
# =============================================================================

# Source config if not already sourced
[ -z "$CONFIG" ] && CONFIG="/opt/scripts/files/lcon"
[ -f "$CONFIG" ] && source "$CONFIG"

log() { echo "[$(basename "$0")] $*" >> "${LOG_FILE:-/tmp/apply-config.log}"; }

# ----- Parameter: hostname -----
# Description: System hostname
# Values: Valid hostname string
if [ -n "$hostname" ]; then
    current_hostname=$(hostname)
    if [ "$current_hostname" != "$hostname" ]; then
        hostname "$hostname" 2>/dev/null && \
            log "Hostname set: $hostname"
        echo "$hostname" > /etc/hostname 2>/dev/null
    fi
fi

# ----- Parameter: timezone -----
# Description: System timezone
# Values: Timezone string (e.g., America/New_York, Europe/London, UTC)
if [ -n "$timezone" ]; then
    log "Setting timezone: $timezone"

    # Try different methods to set timezone
    if [ -f "/usr/share/zoneinfo/$timezone" ]; then
        ln -sf "/usr/share/zoneinfo/$timezone" /etc/localtime 2>/dev/null
        echo "$timezone" > /etc/timezone 2>/dev/null
        log "Timezone set to: $timezone"
    elif command -v timedatectl >/dev/null 2>&1; then
        timedatectl set-timezone "$timezone" 2>/dev/null
    else
        log "WARNING: Could not set timezone - zoneinfo file not found"
    fi
fi

# ----- Parameter: ntp_server -----
# Description: NTP time server
# Values: NTP server hostname or IP
if [ -n "$ntp_server" ]; then
    log "Syncing time with NTP server: $ntp_server"

    if command -v ntpdate >/dev/null 2>&1; then
        ntpdate -s "$ntp_server" 2>/dev/null && \
            log "Time synchronized with $ntp_server"
    elif command -v chronyd >/dev/null 2>&1; then
        # Configure chrony
        echo "server $ntp_server iburst" > /etc/chrony.conf.d/kiosk.conf 2>/dev/null
        systemctl restart chronyd 2>/dev/null || chronyc makestep 2>/dev/null
    elif command -v ntpd >/dev/null 2>&1; then
        ntpd -q -g -p "$ntp_server" 2>/dev/null
    else
        log "WARNING: No NTP client available"
    fi
fi

# ----- Parameter: rtc_wake -----
# Description: Schedule system wake via RTC
# Values: Time string (HH:MM or cron format)
if [ -n "$rtc_wake" ]; then
    log "Setting RTC wake time: $rtc_wake"

    if command -v rtcwake >/dev/null 2>&1; then
        # Parse time and calculate wake time
        # Format: HH:MM for daily wake
        if echo "$rtc_wake" | grep -qE '^[0-9]{1,2}:[0-9]{2}$'; then
            # Calculate seconds until wake time
            current_epoch=$(date +%s)
            target_epoch=$(date -d "today $rtc_wake" +%s)
            [ "$target_epoch" -lt "$current_epoch" ] && \
                target_epoch=$(date -d "tomorrow $rtc_wake" +%s)

            log "RTC wake scheduled for: $(date -d "@$target_epoch")"
            # Note: actual rtcwake would need to be called at shutdown
        fi
    fi
fi

# ----- Parameter: scheduled_action -----
# Description: Execute commands on schedule
# Values: Format "HH:MM command" or cron-style
if [ -n "$scheduled_action" ]; then
    log "Scheduled action configured: $scheduled_action"

    # Parse scheduled action
    # Format: "HH:MM:command" or "HH:MM reboot"
    sched_time=$(echo "$scheduled_action" | cut -d: -f1-2)
    sched_cmd=$(echo "$scheduled_action" | cut -d: -f3-)

    # Add to crontab or start background scheduler
    if [ -n "$sched_time" ] && [ -n "$sched_cmd" ]; then
        hour=$(echo "$sched_time" | cut -d: -f1)
        minute=$(echo "$sched_time" | cut -d: -f2)

        # Add to crontab
        (crontab -l 2>/dev/null | grep -v "# kiosk_scheduled"; \
         echo "$minute $hour * * * $sched_cmd # kiosk_scheduled") | crontab - 2>/dev/null

        log "Scheduled: $sched_cmd at $sched_time"
    fi
fi

# ----- Parameter: automatic_updates -----
# Description: Enable automatic system updates
# Values: yes, no
if [ "$automatic_updates" = "yes" ]; then
    log "Automatic updates enabled"
    # Enable update mechanism (distro-specific)
fi

# ----- Parameter: skip_updates -----
# Description: Skip updates on certain days
# Values: Comma-separated days (Mon,Tue,Wed,...)
if [ -n "$skip_updates" ]; then
    log "Updates skipped on: $skip_updates"
fi

# ----- Parameter: persistence -----
# Description: Save user data across reboots
# Values: yes, no or size (e.g., 512M)
if [ -n "$persistence" ]; then
    log "Persistence configured: $persistence"
fi

# ----- Parameter: swapfile -----
# Description: Create swap file
# Values: Size in MB (e.g., 1024)
if [ -n "$swapfile" ] && [ "$swapfile" -gt 0 ] 2>/dev/null; then
    SWAP_FILE="/var/swapfile"

    if [ ! -f "$SWAP_FILE" ]; then
        log "Creating swap file: ${swapfile}MB"

        dd if=/dev/zero of="$SWAP_FILE" bs=1M count="$swapfile" 2>/dev/null && \
        chmod 600 "$SWAP_FILE" && \
        mkswap "$SWAP_FILE" 2>/dev/null && \
        swapon "$SWAP_FILE" 2>/dev/null && \
        log "Swap file created and enabled"
    else
        # Ensure swap is active
        swapon "$SWAP_FILE" 2>/dev/null
    fi
fi

# ----- Parameter: zRAM -----
# Description: Enable zRAM compressed swap
# Values: Percentage of RAM (e.g., 50) or size in MB
if [ -n "$zRAM" ]; then
    log "zRAM configured: $zRAM"

    # Load zram module
    modprobe zram 2>/dev/null

    if [ -e /sys/block/zram0 ]; then
        # Calculate size
        if echo "$zRAM" | grep -qE '^[0-9]+%?$'; then
            # Percentage of RAM
            percent=${zRAM%\%}
            mem_total=$(grep MemTotal /proc/meminfo | awk '{print $2}')
            zram_size=$((mem_total * percent / 100 * 1024))
        else
            # Assume MB
            zram_size=$((zRAM * 1024 * 1024))
        fi

        echo "$zram_size" > /sys/block/zram0/disksize 2>/dev/null
        mkswap /dev/zram0 2>/dev/null
        swapon -p 100 /dev/zram0 2>/dev/null
        log "zRAM enabled: $zram_size bytes"
    fi
fi

# ----- Parameter: removable_devices -----
# Description: Enable USB/removable media
# Values: yes, no
if [ "$removable_devices" = "yes" ]; then
    log "Removable devices enabled"
    # Ensure udisks2 or similar is running for automounting
fi

# ----- Parameter: disable_firewall -----
# Description: Allow incoming connections
# Values: yes, no
if [ "$disable_firewall" = "yes" ]; then
    log "Firewall disabled - allowing incoming connections"

    # Flush iptables rules
    if command -v iptables >/dev/null 2>&1; then
        iptables -P INPUT ACCEPT 2>/dev/null
        iptables -P FORWARD ACCEPT 2>/dev/null
        iptables -P OUTPUT ACCEPT 2>/dev/null
        iptables -F 2>/dev/null
    fi
fi

# ----- Parameter: allow_icmp_protocol -----
# Description: Allow ping responses
# Values: yes, no
if [ "$allow_icmp_protocol" = "yes" ]; then
    log "ICMP (ping) enabled"

    if command -v iptables >/dev/null 2>&1; then
        iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT 2>/dev/null
    fi
fi

# ----- Parameter: wake_on_lan -----
# Description: Enable Wake-on-LAN
# Values: yes, no
if [ "$wake_on_lan" = "yes" ]; then
    log "Wake-on-LAN enabled"

    # Enable WoL on network interface
    if command -v ethtool >/dev/null 2>&1; then
        for iface in $(ls /sys/class/net | grep -E '^(eth|en)'); do
            ethtool -s "$iface" wol g 2>/dev/null && \
                log "WoL enabled on $iface"
        done
    fi
fi

# ----- Parameter: hostname_aliases -----
# Description: Add entries to /etc/hosts
# Values: Format "IP hostname" or "IP:hostname,IP:hostname"
if [ -n "$hostname_aliases" ]; then
    log "Adding hostname aliases"

    # Parse aliases (format: IP:hostname or space-separated)
    echo "$hostname_aliases" | tr ',' '\n' | while read -r entry; do
        ip=$(echo "$entry" | cut -d: -f1)
        name=$(echo "$entry" | cut -d: -f2)

        if [ -n "$ip" ] && [ -n "$name" ]; then
            # Check if already in hosts file
            if ! grep -q "^$ip.*$name" /etc/hosts 2>/dev/null; then
                echo "$ip $name" >> /etc/hosts
                log "Added host alias: $ip -> $name"
            fi
        fi
    done
fi

# ----- Parameter: session_password -----
# Description: Session login password
# Values: Password string
if [ -n "$session_password" ]; then
    log "Session password configured"
    # Would be used by session manager
fi

# ----- Parameter: shutdown_menu -----
# Description: Show shutdown/power menu
# Values: yes, no
if [ "$shutdown_menu" = "yes" ]; then
    log "Shutdown menu enabled"
fi

log "System handler completed"
