#!/bin/sh
# TuxOS ARM64 Boot Configuration Handler
# Replaces both first-run and update-config from x86 Porteus Kiosk
# Author: Joel (Cornerstone Holdings)
# Version: 5 - Unified boot flow with POSIX compliance fixes
#
# EVERY BOOT:
# 1. Download remote config
# 2. Compare to local config
# 3. If different → update local, rebuild, burn, reboot
# 4. If same → continue boot (exit, let browser launch)

# NOTE: We do NOT use set -e because many commands legitimately return non-zero
# (umount on not-mounted filesystem, grep with no matches, etc.)

# ============================================================================
# CONFIGURATION
# ============================================================================

EXTRAS="/opt/scripts/extras"
LOCAL_CONFIG="/opt/scripts/files/lcon"
LOCAL_CONFIG_FILTERED="/opt/scripts/files/lconc"
REMOTE_CONFIG="/tmp/rcon"
REMOTE_CONFIG_FILTERED="/opt/scripts/files/rconc"
TMP_CONFIG="/tmp/config"
LOG="/mnt/logs/boot-config.log"
BUILD_DIR="/tmp/tuxos-build"
MODULES_DIR="$BUILD_DIR/modules"

# Module server - adjust to your infrastructure
MODULE_SERVER="https://cullerdigitalmedia.com/signage/modules"

# Required modules (in load order)
REQUIRED_MODULES="000-kernel 001-core 002-chrome 003-settings"

# Settings to filter out when comparing configs (volatile/meta settings)
# Note: Uses grep basic regex, | needs to be \|
FILTER_PATTERN="^daemon_\|^burn_dev=\|^md5conf="

# Network timeout (seconds) - matches original autostart 120s wait
NETWORK_TIMEOUT=120

# ============================================================================
# LOGGING AND NOTIFICATIONS
# ============================================================================

# Ensure directories exist (may be on tmpfs)
mkdir -p /opt/scripts/files 2>/dev/null || mkdir -p /tmp/scripts/files 2>/dev/null
if [ ! -d /opt/scripts/files ]; then
    # Fall back to tmp if /opt is read-only
    LOCAL_CONFIG="/tmp/scripts/files/lcon"
    LOCAL_CONFIG_FILTERED="/tmp/scripts/files/lconc"
    REMOTE_CONFIG_FILTERED="/tmp/scripts/files/rconc"
fi

: > "$LOG"
echo "=== TuxOS ARM64 Boot Config ===" >> "$LOG"
echo "Started: $(date)" >> "$LOG"

log() {
    echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"
}

notify() {
    _msg="$1"
    _urgency="${2:-normal}"
    log "NOTIFY [$_urgency]: $_msg"
    if command -v dunstify >/dev/null 2>&1 && [ -n "$DISPLAY" ]; then
        dunstify -C 0 2>/dev/null || true
        dunstify -u "$_urgency" -t 0 "$_msg" 2>/dev/null || true
    fi
}

notify_progress() {
    _percent="$1"
    _message="$2"
    log "PROGRESS [$_percent%]: $_message"
    if command -v dunstify >/dev/null 2>&1 && [ -n "$DISPLAY" ]; then
        dunstify -C 0 2>/dev/null || true
        dunstify -u critical -t 0 "[$_percent%] $_message" 2>/dev/null || true
    fi
}

error_exit() {
    log "FATAL: $*"
    notify "Configuration failed: $*" "critical"
    # Create marker file so autostart knows we failed
    echo "$*" > /tmp/boot-config-failed
    exit 1
}

# ============================================================================
# DOWNLOAD FUNCTIONS
# ============================================================================

download_file() {
    _url="$1"
    _dest="$2"
    _desc="${3:-file}"
    _timeout="${4:-60}"

    log "Downloading $_desc from $_url"

    # Try wget first (more common in embedded systems)
    if command -v wget >/dev/null 2>&1; then
        if wget -T"$_timeout" -t3 -q "$_url" -O "$_dest" 2>>"$LOG"; then
            return 0
        fi
    fi

    # Fallback to curl
    if command -v curl >/dev/null 2>&1; then
        if curl -L -s -m"$_timeout" --retry 3 "$_url" -o "$_dest" 2>>"$LOG"; then
            return 0
        fi
    fi

    return 1
}

download_module() {
    _module="$1"
    _dest="$MODULES_DIR/${_module}.xzm"
    _url="$MODULE_SERVER/${_module}.xzm"

    notify_progress "0" "Downloading ${_module}.xzm component ..."

    if ! download_file "$_url" "$_dest" "${_module}.xzm"; then
        log "Server download failed, trying local copy..."

        # Try to copy from current system
        _current_module=""
        for _path in /mnt/live/memory/data/porteuskiosk /porteuskiosk; do
            if [ -f "$_path/${_module}.xzm" ]; then
                _current_module="$_path/${_module}.xzm"
                break
            fi
        done

        if [ -n "$_current_module" ]; then
            log "Copying $_module from $_current_module"
            cp "$_current_module" "$_dest"
        else
            return 1
        fi
    fi

    log "Module $_module ready ($(du -h "$_dest" 2>/dev/null | cut -f1))"
    return 0
}

# ============================================================================
# CONFIG FUNCTIONS
# ============================================================================

# Filter config for comparison (remove volatile settings)
filter_config() {
    _input="$1"
    _output="$2"

    # Remove comments, blank lines, filtered patterns, normalize line endings, sort
    grep -v "^#" "$_input" 2>/dev/null | \
    grep -v "^$" | \
    grep -v "$FILTER_PATTERN" | \
    tr -d '\r' | \
    sort > "$_output"
}

# Get config URL - from wizard output, extras, or reconstruct
get_config_url() {
    _url=""

    # First check wizard output (first boot)
    if [ -f "$TMP_CONFIG" ]; then
        _url=$(grep "^kiosk_config=" "$TMP_CONFIG" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d ' \t\r')
    fi

    # Then check extras (subsequent boots)
    if [ -z "$_url" ] && [ -f "$EXTRAS" ]; then
        _url=$(grep "^kiosk_config_url=" "$EXTRAS" 2>/dev/null | cut -d= -f2-)
    fi

    # Fallback: reconstruct from config name
    if [ -z "$_url" ] && [ -f "$EXTRAS" ]; then
        _name=$(grep "^kiosk_config_name=" "$EXTRAS" 2>/dev/null | cut -d= -f2-)
        if [ -n "$_name" ]; then
            _base="http://cullerdigitalmedia.com"
            # Extract facility from config name pattern
            _facility=$(echo "$_name" | sed 's/_[a-z][a-z][0-9]*\.txt$//' | sed 's/_stats\.txt$//' | sed 's/_ed\.txt$//')

            case "$_name" in
                *_ds*.txt) _url="$_base/signage/$_facility/$_name" ;;
                *_ks*.txt|*_mc*.txt|*_tc*.txt|*_ns*.txt|*_rr*.txt) _url="$_base/kc/$_facility/$_name" ;;
                *) _url="$_base/kc/$_name" ;;
            esac
        fi
    fi

    echo "$_url"
}

# Get target device for burning
get_burn_device() {
    _dev=""

    # From wizard output (first boot) - this is the BASE device
    if [ -f "$TMP_CONFIG" ]; then
        _dev=$(grep "^burn_dev=" "$TMP_CONFIG" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d ' \t\r')
    fi

    # From extras (subsequent boots) - this is the PARTITION
    if [ -z "$_dev" ] && [ -f "$EXTRAS" ]; then
        _dev=$(grep "^boot_dev=" "$EXTRAS" 2>/dev/null | cut -d= -f2-)
    fi

    # Normalize - remove /dev/ prefix for consistency
    echo "$_dev" | sed 's|^/dev/||'
}

# ============================================================================
# PARTITION AND INSTALL FUNCTIONS
# ============================================================================

# Get partition naming convention for a device
# Returns: p for nvme/mmcblk (e.g., mmcblk0p1), empty for others (e.g., sda1)
get_partition_separator() {
    _device="$1"
    case "$_device" in
        mmcblk*|nvme*) echo "p" ;;
        *) echo "" ;;
    esac
}

# Partition device for Pi4 (only on first boot)
partition_device() {
    _device="$1"
    _sep=$(get_partition_separator "$_device")

    log "Partitioning /dev/$_device for Raspberry Pi 4..."
    notify "Partitioning /dev/$_device ..." "critical"

    # Unmount any existing partitions
    umount "/dev/${_device}"* 2>/dev/null || true

    # Clear existing partition table
    dd if=/dev/zero of="/dev/$_device" bs=1M count=4 2>>"$LOG"
    sync

    # Create MBR partition table
    # Part 1: 256MB FAT32 (boot)
    # Part 2: Rest ext4 (root)
    parted -s "/dev/$_device" mklabel msdos
    parted -s "/dev/$_device" mkpart primary fat32 1MiB 257MiB
    parted -s "/dev/$_device" mkpart primary ext4 257MiB 100%
    parted -s "/dev/$_device" set 1 boot on
    parted -s "/dev/$_device" set 1 lba on

    sync
    sleep 2

    # Determine partition names
    _boot_part="/dev/${_device}${_sep}1"
    _root_part="/dev/${_device}${_sep}2"

    log "Formatting boot partition (FAT32): $_boot_part"
    mkfs.vfat -F 32 -n BOOT "$_boot_part" 2>>"$LOG"

    log "Formatting root partition (ext4): $_root_part"
    mkfs.ext4 -F -L TuxOS "$_root_part" 2>>"$LOG"

    sync
    log "Partitioning complete"

    # Return the root partition path
    echo "$_root_part"
}

# Install boot files for Pi4
install_boot_files() {
    _boot_mount="$1"
    _root_part="$2"

    log "Installing boot files..."

    # Copy from current /boot
    for _f in kernel8.img bcm2711-rpi-4-b.dtb bcm2711-rpi-cm4.dtb start4.elf fixup4.dat bootcode.bin; do
        if [ -f "/boot/$_f" ]; then
            cp "/boot/$_f" "$_boot_mount/"
            log "  Copied $_f"
        fi
    done

    # Copy overlays
    if [ -d "/boot/overlays" ]; then
        cp -r "/boot/overlays" "$_boot_mount/"
        log "  Copied overlays/"
    fi

    # Create cmdline.txt for installed system
    cat > "$_boot_mount/cmdline.txt" << EOF
coherent_pool=1M 8250.nr_uarts=1 snd_bcm2835.enable_headphones=0 console=tty1 root=${_root_part} rootfstype=ext4 rootwait quiet net.ifnames=0 biosdevname=0
EOF

    # Ensure config.txt exists
    if [ ! -f "$_boot_mount/config.txt" ]; then
        cp "/boot/config.txt" "$_boot_mount/" 2>/dev/null || true
    fi

    sync
}

# Install/update modules on root partition
install_modules() {
    _root_mount="$1"

    log "Installing modules..."
    mkdir -p "$_root_mount/porteuskiosk"
    mkdir -p "$_root_mount/opt/scripts/files"
    mkdir -p "$_root_mount/docs"

    _total=$(ls -1 "$MODULES_DIR"/*.xzm 2>/dev/null | wc -l)
    _current=0

    for _xzm in "$MODULES_DIR"/*.xzm; do
        [ -f "$_xzm" ] || continue
        _current=$((_current + 1))
        _name=$(basename "$_xzm")
        _percent=$((_current * 100 / _total))

        notify_progress "$_percent" "Installing $_name ..."
        cp "$_xzm" "$_root_mount/porteuskiosk/"
        log "  Installed $_name"
    done

    # Install config files
    if [ -f "$REMOTE_CONFIG" ]; then
        cp "$REMOTE_CONFIG" "$_root_mount/opt/scripts/files/lcon"
    fi
    if [ -f "${EXTRAS}.new" ]; then
        cp "${EXTRAS}.new" "$_root_mount/opt/scripts/extras"
    fi

    # Signature file
    echo "TuxOS ARM64 $(date '+%Y-%m-%d %H:%M:%S')" > "$_root_mount/docs/kiosk.sgn"

    sync
}

# ============================================================================
# MAIN RECONFIGURATION FLOW
# ============================================================================

perform_reconfiguration() {
    _target="$1"
    _is_first_boot="$2"
    _sep=$(get_partition_separator "$_target")

    log "=== Starting system reconfiguration ==="
    log "Target: $_target, First boot: $_is_first_boot"
    notify "Performing system reconfiguration - please do not turn off the PC." "critical"

    # Create build directory
    rm -rf "$BUILD_DIR"
    mkdir -p "$MODULES_DIR"

    # Download all modules
    notify "Downloading additional components ..." "normal"

    # Count modules using a different method (avoid wc -w whitespace issues)
    _total=0
    for _m in $REQUIRED_MODULES; do
        _total=$((_total + 1))
    done

    _current=0
    for _module in $REQUIRED_MODULES; do
        _current=$((_current + 1))
        _percent=$((_current * 100 / _total))
        notify_progress "$_percent" "Downloading ${_module}.xzm component ..."

        if ! download_module "$_module"; then
            error_exit "Failed to download required module: $_module"
        fi
    done

    # Determine root partition
    if [ "$_is_first_boot" = "yes" ]; then
        # First boot - need to partition, _target is base device
        _root_part=$(partition_device "$_target")
        _boot_part="/dev/${_target}${_sep}1"

        # Mount and install boot files
        _boot_mount="/tmp/install-boot"
        mkdir -p "$_boot_mount"

        if ! mount "$_boot_part" "$_boot_mount" 2>>"$LOG"; then
            error_exit "Failed to mount boot partition $_boot_part"
        fi

        install_boot_files "$_boot_mount" "$_root_part"
        umount "$_boot_mount"
        rmdir "$_boot_mount" 2>/dev/null || true
    else
        # Subsequent boot - _target is already the partition
        _root_part="$_target"
        # Ensure it has /dev/ prefix
        case "$_root_part" in
            /dev/*) ;;
            *) _root_part="/dev/$_root_part" ;;
        esac
    fi

    # Mount root partition
    _root_mount="/tmp/install-root"
    mkdir -p "$_root_mount"

    # Make sure it's not mounted elsewhere
    umount "$_root_part" 2>/dev/null || true

    notify "Burning ISO on $_root_part - this may take a while ..." "critical"

    if ! mount "$_root_part" "$_root_mount" 2>>"$LOG"; then
        error_exit "Failed to mount $_root_part"
    fi

    # Install modules
    install_modules "$_root_mount"

    # Sync and unmount
    log "Syncing filesystem..."
    sync
    umount "$_root_mount"
    rmdir "$_root_mount" 2>/dev/null || true

    # Cleanup
    rm -rf "$BUILD_DIR"

    log "=== Reconfiguration complete ==="
    notify "Reconfiguration complete. System will reboot." "normal"

    # Update live system files
    if [ -f "${EXTRAS}.new" ]; then
        cp "${EXTRAS}.new" "$EXTRAS" 2>/dev/null || true
    fi
    if [ -f "$REMOTE_CONFIG" ]; then
        cp "$REMOTE_CONFIG" "$LOCAL_CONFIG" 2>/dev/null || true
    fi

    # Reboot
    log "Rebooting in 3 seconds..."
    sleep 3
    sync
    reboot

    # Should not reach here
    exit 0
}

# ============================================================================
# MAIN SCRIPT
# ============================================================================

log "=== TuxOS ARM64 Boot Config v5 ==="
log "Architecture: $(uname -m)"

# Get config URL
CONFIG_URL=$(get_config_url)

if [ -z "$CONFIG_URL" ]; then
    log "No config URL available - cannot proceed"
    log "Checked: /tmp/config (kiosk_config=), /opt/scripts/extras (kiosk_config_url=)"
    error_exit "No configuration URL found"
fi

log "Config URL: $CONFIG_URL"

# Get device identifier for URL parameter (Pi serial preferred)
PCID=""
if [ -f /proc/cpuinfo ]; then
    PCID=$(grep -i "^Serial" /proc/cpuinfo 2>/dev/null | cut -d: -f2 | tr -d ' ')
fi
if [ -z "$PCID" ]; then
    PCID=$(cat /sys/class/dmi/id/product_serial 2>/dev/null || hostname)
fi

FETCH_URL="${CONFIG_URL}?kiosk=${PCID}"

log "Device ID: $PCID"
log "Fetch URL: $FETCH_URL"

# Download remote config with network retry logic
log "Downloading remote configuration..."
_retry_count=0
_max_retries=$((NETWORK_TIMEOUT / 10))

while ! download_file "$FETCH_URL" "$REMOTE_CONFIG" "remote config" 30; do
    _retry_count=$((_retry_count + 1))
    if [ $_retry_count -ge $_max_retries ]; then
        error_exit "Failed to download remote config from $CONFIG_URL after ${NETWORK_TIMEOUT}s"
    fi
    log "Attempt $_retry_count failed, waiting for network... (${_retry_count}0s / ${NETWORK_TIMEOUT}s)"
    sleep 10
done

# Sanitize (DOS to Unix line endings) - POSIX compatible
tr -d '\r' < "$REMOTE_CONFIG" > "$REMOTE_CONFIG.tmp" && mv "$REMOTE_CONFIG.tmp" "$REMOTE_CONFIG"

log "Remote config downloaded ($(wc -c < "$REMOTE_CONFIG" | tr -d ' ') bytes)"
log "--- Remote config contents ---"
cat "$REMOTE_CONFIG" >> "$LOG"
log "--- End remote config ---"

# Create filtered version for comparison
filter_config "$REMOTE_CONFIG" "$REMOTE_CONFIG_FILTERED"

# Check if local config exists
IS_FIRST_BOOT="no"
if [ ! -f "$LOCAL_CONFIG" ]; then
    log "No local config - this is first boot"
    IS_FIRST_BOOT="yes"
    : > "$LOCAL_CONFIG_FILTERED"  # Create empty file for comparison
else
    filter_config "$LOCAL_CONFIG" "$LOCAL_CONFIG_FILTERED"
fi

# Compare configs
if cmp -s "$LOCAL_CONFIG_FILTERED" "$REMOTE_CONFIG_FILTERED" 2>/dev/null; then
    log "Configuration unchanged - continuing boot"

    # Still update local config (in case of minor filtered-out changes)
    cp "$REMOTE_CONFIG" "$LOCAL_CONFIG" 2>/dev/null || true

    # Cleanup
    rm -f "$REMOTE_CONFIG"

    # Signal that config check passed
    touch /tmp/config_ok

    log "=== Boot config check complete - no changes ==="
    exit 0
fi

# Config is different - need to reconfigure
log "Configuration CHANGED - reconfiguration required"
log "--- Local config (filtered) ---"
cat "$LOCAL_CONFIG_FILTERED" >> "$LOG"
log "--- Remote config (filtered) ---"
cat "$REMOTE_CONFIG_FILTERED" >> "$LOG"
log "--- End diff ---"

# Get target device
BURN_DEV=$(get_burn_device)

if [ -z "$BURN_DEV" ]; then
    error_exit "No target device found for installation"
fi

log "Target device: $BURN_DEV"
log "First boot: $IS_FIRST_BOOT"

# Extract config name from URL
KIOSK_CONFIG_NAME=$(basename "$CONFIG_URL" | cut -d'?' -f1)

# Prepare new extras file
_sep=$(get_partition_separator "$BURN_DEV")
if [ "$IS_FIRST_BOOT" = "yes" ]; then
    # First boot - BURN_DEV is base device, calculate root partition
    ROOT_PART_NAME="/dev/${BURN_DEV}${_sep}2"
else
    # Subsequent boot - BURN_DEV is already the partition
    ROOT_PART_NAME="$BURN_DEV"
    case "$ROOT_PART_NAME" in
        /dev/*) ;;
        *) ROOT_PART_NAME="/dev/$ROOT_PART_NAME" ;;
    esac
fi

{
    echo "boot_dev=$ROOT_PART_NAME"
    echo "kiosk_config_name=$KIOSK_CONFIG_NAME"
    echo "kiosk_config_url=$CONFIG_URL"
    grep -E "^(homepage|scheduled_action|whitelist|blacklist)=" "$REMOTE_CONFIG" 2>/dev/null || true
} > "${EXTRAS}.new"

log "New extras:"
cat "${EXTRAS}.new" >> "$LOG"

# Perform reconfiguration
perform_reconfiguration "$BURN_DEV" "$IS_FIRST_BOOT"

# Should not reach here (reboot happens in perform_reconfiguration)
exit 0
