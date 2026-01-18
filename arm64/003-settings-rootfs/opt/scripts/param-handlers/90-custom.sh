#!/bin/bash
# =============================================================================
# Parameter Handler: 90-custom.sh
# =============================================================================
# Handles: run_command, kernel_parameters, gpu_driver, debug,
#          hardware_video_decode, watchdog
#
# This handler runs LAST (90-*) to allow custom commands to override
# any settings from previous handlers.
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

# ----- Parameter: run_command -----
# Description: Execute custom command(s) at startup
# Values: Shell command(s) - can be semicolon or newline separated
if [ -n "$run_command" ]; then
    log "Executing custom command: $run_command"

    # Execute in background to not block handler
    eval "$run_command" >> /tmp/run_command.log 2>&1 &

    log "Custom command started in background"
fi

# ----- Parameter: kernel_parameters -----
# Description: Custom Linux boot parameters
# Values: Kernel parameter string
# Note: These can only be applied on next boot, not runtime
if [ -n "$kernel_parameters" ]; then
    log "Kernel parameters (will apply on next boot): $kernel_parameters"

    # Store for boot configuration update
    echo "$kernel_parameters" > /tmp/kernel_parameters_pending
fi

# ----- Parameter: gpu_driver -----
# Description: Graphics driver selection
# Values: auto, vc4, fbdev, modesetting
if [ -n "$gpu_driver" ]; then
    log "GPU driver: $gpu_driver"

    # For ARM64/RPi, common drivers are vc4 and fbdev
    case "$gpu_driver" in
        vc4)
            # VC4 is the standard RPi GPU driver
            modprobe vc4 2>/dev/null
            modprobe v3d 2>/dev/null
            ;;
        fbdev)
            # Fallback framebuffer driver
            ;;
        modesetting)
            # Generic modesetting driver
            ;;
        auto)
            # Let the system auto-detect
            ;;
    esac
fi

# ----- Parameter: debug -----
# Description: Generate debug/diagnostic report
# Values: yes, no
if [ "$debug" = "yes" ]; then
    log "Generating debug report"

    DEBUG_FILE="/tmp/kiosk_debug_$(date +%Y%m%d_%H%M%S).txt"

    {
        echo "=== Kiosk Debug Report ==="
        echo "Date: $(date)"
        echo ""

        echo "=== System Info ==="
        uname -a
        cat /etc/os-release 2>/dev/null
        echo ""

        echo "=== CPU Info ==="
        cat /proc/cpuinfo | head -20
        echo ""

        echo "=== Memory ==="
        free -h
        echo ""

        echo "=== Disk Usage ==="
        df -h
        echo ""

        echo "=== Network ==="
        ip addr
        ip route
        cat /etc/resolv.conf
        echo ""

        echo "=== Display ==="
        if command -v xrandr >/dev/null 2>&1; then
            xrandr 2>/dev/null
        fi
        echo ""

        echo "=== Loaded Modules ==="
        lsmod
        echo ""

        echo "=== Process List ==="
        ps aux
        echo ""

        echo "=== Config File ==="
        cat "$CONFIG" 2>/dev/null | grep -v password
        echo ""

        echo "=== Recent Logs ==="
        tail -100 /tmp/apply-config.log 2>/dev/null
        echo ""

        echo "=== Xorg Log ==="
        tail -50 /var/log/Xorg.0.log 2>/dev/null
        echo ""

        echo "=== dmesg (last 100 lines) ==="
        dmesg | tail -100
        echo ""

    } > "$DEBUG_FILE" 2>&1

    log "Debug report saved to: $DEBUG_FILE"

    # Show notification
    dunstify -u normal "Debug report saved to $DEBUG_FILE" 2>/dev/null || true
fi

# ----- Parameter: hardware_video_decode -----
# Description: Enable GPU video acceleration
# Values: yes, no
if [ "$hardware_video_decode" = "yes" ]; then
    log "Enabling hardware video decode"

    # For RPi4 with VC4 driver
    if grep -q "BCM2711\|BCM2712" /proc/cpuinfo 2>/dev/null; then
        # V4L2 video decode is available on RPi4
        modprobe bcm2835-codec 2>/dev/null
        modprobe rpivid-mem 2>/dev/null

        # Set environment for Chromium hardware acceleration
        export LIBVA_DRIVER_NAME=v4l2
    fi

    # General VA-API setup
    if [ -d /dev/dri ]; then
        chmod 666 /dev/dri/* 2>/dev/null
    fi
fi

# ----- Parameter: watchdog -----
# Description: Enable hardware watchdog for auto-reboot on hang
# Values: yes, no, or timeout in seconds
if [ -n "$watchdog" ]; then
    log "Watchdog: $watchdog"

    case "$watchdog" in
        yes)
            timeout=60  # Default 60 second timeout
            ;;
        no)
            # Disable watchdog
            if [ -c /dev/watchdog ]; then
                echo "V" > /dev/watchdog 2>/dev/null  # Magic close to disable
            fi
            timeout=0
            ;;
        *)
            # Assume it's a timeout value
            timeout="$watchdog"
            ;;
    esac

    if [ "$timeout" -gt 0 ] 2>/dev/null; then
        # Enable hardware watchdog
        if [ -c /dev/watchdog ]; then
            # Start watchdog daemon
            if command -v watchdog >/dev/null 2>&1; then
                watchdog -t "$timeout" /dev/watchdog &
                log "Watchdog enabled with ${timeout}s timeout"
            else
                # Simple watchdog keep-alive in background
                (
                    while true; do
                        echo "1" > /dev/watchdog 2>/dev/null
                        sleep $((timeout / 2))
                    done
                ) &
                log "Simple watchdog started with ${timeout}s timeout"
            fi
        else
            log "WARNING: /dev/watchdog not available"
        fi
    fi
fi

log "Custom handler completed"
