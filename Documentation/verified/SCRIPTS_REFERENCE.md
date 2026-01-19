# TuxOS ARM64 Scripts Reference

Complete inventory and documentation of scripts in the TuxOS ARM64 kiosk system.

**Source Directory:** `/home/culler/saas_dev/pk-port/arm64/003-settings-rootfs/opt/scripts/`

**Last Updated:** 2026-01-18

---

## Table of Contents

1. [Script Inventory](#1-script-inventory)
2. [Script Call Graph](#2-script-call-graph)
3. [Key Script Documentation](#3-key-script-documentation)
   - [first-run](#31-first-run)
   - [welcome](#32-welcome)
   - [wizard](#33-wizard)
   - [arm64-boot-config.sh](#34-arm64-boot-configsh)
   - [apply-config](#35-apply-config)
   - [update-config](#36-update-config)
   - [gui-app](#37-gui-app)
   - [daemon.sh](#38-daemonsh)
4. [Parameter Handlers](#4-parameter-handlers)
5. [Helper Scripts](#5-helper-scripts)
6. [Debugging Scripts](#6-debugging-scripts)
7. [GTKDialog Patterns](#7-gtkdialog-patterns)
8. [Error Handling Patterns](#8-error-handling-patterns)
9. [Configuration Files](#9-configuration-files)

---

## 1. Script Inventory

Complete inventory of all scripts in `/opt/scripts/` with verified line counts.

| Script | Lines | Size | Purpose | Dependencies |
|--------|-------|------|---------|--------------|
| `first-run` | 476 | 21,763 bytes | Wizard orchestrator, SD card installer | welcome, wizard, openssl, sfdisk, mkfs |
| `welcome` | 679 | 29,946 bytes | 8-page network configuration wizard | gtkdialog, wizard-functions |
| `wizard` | 322 | 9,937 bytes | TuxOS device selection wizard | gtkdialog, wizard-functions, curl |
| `arm64-boot-config.sh` | 593 | 17,855 bytes | Unified boot configuration handler | wget/curl, parted, mkfs |
| `update-config` | 302 | 21,693 bytes | Configuration update handler | wget, openssl, mkisofs |
| `apply-config` | 75 | 2,278 bytes | Parameter handler orchestrator | param-handlers/*.sh |
| `daemon.sh` | 127 | 4,736 bytes | Remote config polling daemon | wget, apply-config |
| `gui-app` | 333 | 11,622 bytes | Browser launcher loop | chromium, su |
| `flow-logger` | 114 | 2,819 bytes | Script flow logging utility | - |
| `boot-capture` | 264 | 7,349 bytes | Boot state capture for debugging | - |
| `debug` | 133 | 3,575 bytes | System debugging information collector | sensors, lspci, xinput |
| `exit-kiosk` | 64 | 2,340 bytes | Shutdown/logout menu | gtkdialog |
| `pkget` | 62 | 2,637 bytes | Secure file download utility | wget, sshpass |
| `wizard-now` | 33 | 1,212 bytes | Network wizard launcher prompt | gtkdialog |
| `xvkbd` | 33 | 806 bytes | Virtual keyboard launcher | xvkbd |
| `extras` | 1 | 14 bytes | Runtime state file (first_run, boot_dev) | - |

### Parameter Handlers (in `/opt/scripts/param-handlers/`)

| Handler | Lines | Size | Parameters Handled |
|---------|-------|------|-------------------|
| `00-network.sh` | 311 | 9,825 bytes | connection, dhcp, ip_address, network_interface, gateway, dns, wifi_*, eapol_* |
| `10-proxy.sh` | ~120 | 4,565 bytes | proxy, proxy_config, proxy_exceptions |
| `20-browser.sh` | 248 | 7,993 bytes | browser, homepage, whitelist, blacklist, zoom, user_agent |
| `30-display.sh` | ~110 | 4,241 bytes | screen_rotation, screen_brightness, dpms, wallpaper |
| `40-input.sh` | ~200 | 8,029 bytes | touchscreen, keyboard_layout, input_calibration |
| `50-power.sh` | ~160 | 6,401 bytes | scheduled_action, idle_action, power_savings |
| `60-audio.sh` | ~115 | 4,459 bytes | audio_volume, mute_audio, audio_output |
| `70-services.sh` | ~180 | 7,264 bytes | ssh_access, vnc_access, printing |
| `80-system.sh` | ~230 | 9,139 bytes | hostname, timezone, root_password, system_updates |
| `90-custom.sh` | ~155 | 6,056 bytes | custom_script, run_command, extra_modules |

### Wizard Support Files (in `/opt/scripts/files/wizard/`)

| File | Lines | Purpose |
|------|-------|---------|
| `wizard-functions` | 2,259 | GTKDialog helper functions library |

---

## 2. Script Call Graph

```
Boot Sequence:
  /sbin/init
    -> /etc/rc.d/rc.S (system init)
      -> /etc/rc.d/rc.M (networking)
        -> /etc/rc.d/rc.4 (X11)
          -> xinitrc
            -> openbox
              -> autostart
                |
                v
    +--- First Boot Path (first_run=yes) ---+
    |                                        |
    | first-run                              |
    |   -> welcome (network wizard)          |
    |   -> wizard-now (prompt)               |
    |   -> set_network() [internal]          |
    |   -> wizard (device selection)         |
    |   -> burn_ISO() [internal]             |
    |   -> reboot                            |
    +----------------------------------------+
    |
    +--- Subsequent Boot Path ---------------+
    |                                        |
    | arm64-boot-config.sh                   |
    |   -> download config                   |
    |   -> compare configs                   |
    |   -> [if changed] perform_reconfiguration()
    |       -> download modules              |
    |       -> partition device              |
    |       -> install_boot_files()          |
    |       -> install_modules()             |
    |       -> reboot                        |
    |   -> [if unchanged] exit               |
    |                                        |
    | daemon.sh (background)                 |
    |   -> poll config                       |
    |   -> apply-config                      |
    |       -> param-handlers/*.sh           |
    |   -> [if force_reboot] init 6          |
    |                                        |
    | gui-app                                |
    |   -> prepare_session()                 |
    |   -> chromium (loop)                   |
    +----------------------------------------+
```

### Detailed Call Relationships

| Caller | Callee | Location | Condition |
|--------|--------|----------|-----------|
| autostart | first-run | line 97 | `-e /opt/scripts/first-run` |
| autostart | arm64-boot-config.sh | after network wait | always |
| autostart | daemon.sh | line 139 | background |
| autostart | gui-app | line 292 | always |
| first-run | welcome | line 51 | always |
| first-run | wizard-now | line 191 | background |
| first-run | wizard | line 233 | always |
| daemon.sh | apply-config | line 81, 94 | on config change |
| daemon.sh | update-config | line 99 | if exists |
| apply-config | param-handlers/*.sh | lines 60-71 | for each handler |
| welcome | wizard-functions | gtkdialog -i | GTKDialog include |
| wizard | wizard-functions | gtkdialog -i | GTKDialog include |

---

## 3. Key Script Documentation

### 3.1 first-run

**File:** `/opt/scripts/first-run`
**Lines:** 476
**Interpreter:** `/bin/sh`

The first-run script is the wizard orchestrator that handles first-boot installation of TuxOS to an SD card.

#### Purpose

1. Display network configuration wizard (welcome)
2. Display device selection wizard (wizard)
3. Download additional components from server
4. Partition and format target SD card
5. Install boot files and modules
6. Encrypt configuration with AES-256-CBC
7. Reboot into installed system

#### Key Variables

```sh
# Line 29
URLP=http://cullerdigitalmedia.com/peanutos

# Line 31
pth=/mnt/kiosk    # Installation mount point

# Line 36
profile=/home/guest/.mozilla/firefox/c3pp43bg.default

# Line 38
supplicant=/etc/wpa_supplicant.conf
```

#### Key Functions

**cleanup()** - Lines 39
```sh
cleanup() {
    cd /
    killall firefox chrome 2>/dev/null
    rm -rf $pth /mnt/VER /tmp/config* /tmp/md5sum /tmp/log \
           /opt/scripts/first-run /opt/scripts/wizard
}
```

**welcome()** - Lines 40-189
- Kills existing network services
- Pre-creates `/tmp/knet/.knetPage` for GTKDialog
- Launches `/opt/scripts/welcome` wizard
- Parses `/tmp/config` for network settings
- Configures WPA supplicant based on encryption type
- Starts network services (dhcpcd or manual IP)

**set_network()** - Lines 190-226
- Launches `wizard-now` prompt in background
- Downloads proxy PAC file if configured
- Tests connectivity to cullerdigitalmedia.com
- Configures browser proxy settings

**fetch_component()** - Lines 262-280
- Downloads module with progress notification
- MD5 verification with retry
- 9 retries with network restart at attempt 4

**burn_ISO()** - Lines 338-453
- ARM64 SD card partitioning:
  - Partition 1: FAT32 boot (64MB)
  - Partition 2: ext4 data (dynamic)
  - Partition 4: ext4 storage (64MB)
- Copies boot files (kernel8.img, DTBs, overlays)
- Copies XZM modules and docs

#### Encryption (Lines 334, 474-476)

```sh
# Forced parameters encryption (line 334)
echo "clwrosKXGt0bChL2njIXjANuvHRbWKPeTbkN3lVlWu" | \
    openssl aes-256-cbc -md MD5 -a -in /tmp/config1 \
    -out $pth/docs/kiosk.sgn1 -pass stdin

# MD5 checksum encryption (line 474)
echo `echo $mac | rev | cut -c1,3,5,7,9,11,13`\
`echo $mac | cut -c1,3,5,7,9,11,13`XzY1 | \
    openssl aes-256-cbc -md MD5 -a -in /tmp/md5sum \
    -out $pth/docs/md5 -pass stdin

# Config file encryption (line 475)
echo `md5sum $pth/docs/md5 | cut -d" " -f1 | tr "a-z" "A-Z"`ZyX9 | \
    openssl aes-256-cbc -md MD5 -a -in /tmp/config \
    -out $pth/docs/config -pass stdin
```

#### Exit Points

| Exit Type | Location | Condition |
|-----------|----------|-----------|
| cleanup + exit | Line 285-286 | Network lost during component download |
| cleanup + exit | Line 290-293 | MD5 mismatch after retries |
| cleanup + exit | Line 293 | Component not found |
| cleanup + exit | Line 299 | pth directory missing |
| reboot | Line 453 | Unconditional after burn_ISO() |

---

### 3.2 welcome

**File:** `/opt/scripts/welcome`
**Lines:** 679
**Interpreter:** `/bin/bash`

8-page GTKDialog wizard for network configuration.

#### Pages (Notebook Tabs)

| Page | Index | Name | Purpose |
|------|-------|------|---------|
| 0 | welcome | Wired/Wireless choice | Initial selection with Ethernet/WiFi buttons |
| 1 | dialup | Modem Configuration | Phone number, username, password |
| 2 | nettype | DHCP/Manual choice | Configure automatically or manually |
| 3 | manual | Manual Configuration | IP, netmask, gateway, DNS fields |
| 4 | wireless | Wireless Details | SSID selection, encryption, password |
| 5 | proxy | Proxy Settings | Manual proxy or PAC URL |
| 6 | browser | Browser Choice | Firefox or Chrome selection |
| 7 | confirm | Final Report | Summary before proceeding |

#### Key Variables (Lines 26-34)

```sh
export TMP=/tmp/knet
export CONF=/tmp/config
export REPORT=/tmp/report
ICONS=/usr/share/pixmaps
WINWIDTH=600
WINHEIGHT=510
```

#### Page Navigation (Lines 92-97)

Timer-based page initialization workaround for GTKDialog 0.8.3:
```xml
<timer visible="false" milliseconds="100">
    <action>echo 0 > '$TMP'/.knetPage</action>
    <action>refresh:nPage</action>
    <action>disable:pageInitTimer</action>
    <variable>pageInitTimer</variable>
</timer>
```

#### Button Actions

**Ethernet button** (Lines 116-138):
```xml
<button image-position="2" tooltip-text="Connect using a wired connection">
    <action>echo "connection=wired" > $TMP/connection.tmp</action>
    <action>echo 7 > '$TMP'/.knetPage</action>
    <action function="enable">butBack</action>
    <action>get_report</action>
    <action>refresh:nPage</action>
</button>
```

**WiFi button** (Lines 140-164):
```xml
<button image-position="2" tooltip-text="Connect using a wireless connection">
    <action>echo "connection=wifi" > $TMP/connection.tmp</action>
    <action>get_essid &</action>
    <action>echo 4 > '$TMP'/.knetPage</action>
    <action function="show">butScanWifi</action>
    <action>refresh:nPage</action>
</button>
```

#### Output Format (/tmp/config)

```ini
connection=wired
dhcp=yes
network_interface=end0
# OR for manual:
ip_address=192.168.1.100
netmask=255.255.255.0
default_gateway=192.168.1.1
dns_server=8.8.8.8 8.8.4.4
# For WiFi:
ssid_name=MyNetwork
wifi_encryption=wpa
wpa_password=secret123
# Proxy:
proxy=192.168.1.20:3128
# Browser:
browser=chrome
```

---

### 3.3 wizard

**File:** `/opt/scripts/wizard`
**Lines:** 322
**Interpreter:** `/bin/sh`

Device selection wizard with password authorization gate.

#### Authorization Gate (Lines 12, 124-151)

```sh
# Line 12 - Password definition
deplvl='$3Cur1ty$'

# Lines 124-128 - Password fetch
if curl cullerdigitalmedia.com/peanutos/files/key.txt >> $TMPDIR/drivekey.txt; then
    continue
else
    echo P@ss3264 > $TMPDIR/drivekey.txt
fi

# Lines 140-151 - Password loop
while ([ "$CID" != "$DRIVEKEY" ]); do
    # Show authorization dialog
    echo "$WIZARD_MAIN" | sed '/^##/d' | gtkdialog -i wizard-functions -s -c
    CID=`cat $TMPDIR/configuration.id`
done
```

#### Device Type URL Mapping (Lines 242-314)

| Device Type | URL Pattern |
|-------------|-------------|
| Kiosk | `$BASEURL/kc/{facility}/{facility}_ks{num}.txt` |
| Digital Signage | `$BASEURL/signage/{facility}/{facility}_ds{num}.txt` |
| Education | `$BASEURL/kc/{facility}_ed.txt` |
| Medcart | `$BASEURL/kc/{facility}/{facility}_mc{num}.txt` |
| Treatment | `$BASEURL/kc/{facility}/{facility}_tc{num}.txt` |
| NurseStation | `$BASEURL/kc/{facility}/{facility}_ns{num}.txt` |
| Bedboard | `$BASEURL/kc/{facility}/{facility}_stats.txt` |
| ActivityPro | `$BASEURL/activitypro/{facility}.txt` |
| Resident Room | `$BASEURL/kc/{facility}/{facility}_rr{num}.txt` |

#### Block Device Detection (Lines 36-53)

```sh
refresh_block_devices() {
    lsblk -d -o NAME,TYPE,MODEL,SIZE 2>/dev/null | \
        egrep -v 'NAME|loop|rom' | \
        tr -s ' ' | \
        sed -e 's/ /_/g' -e 's/_/|/1' -e 's/_/|/1' \
            -e 's/\(.*\)_/\1|/' > $TMPDIR/block.txt

    # Fallback for RPi SD card
    if [ ! -s $TMPDIR/block.txt ]; then
        if [ -b /dev/mmcblk0 ]; then
            echo "mmcblk0|disk|SD_Card|$(lsblk -dn -o SIZE /dev/mmcblk0)" \
                > $TMPDIR/block.txt
        fi
    fi
}
```

#### Output (/tmp/config additions)

```ini
burn_dev=mmcblk0
kiosk_config=http://cullerdigitalmedia.com/signage/facility/facility_ds1.txt
```

---

### 3.4 arm64-boot-config.sh

**File:** `/opt/scripts/arm64-boot-config.sh`
**Lines:** 593
**Interpreter:** `/bin/sh` (POSIX compliant)

Unified boot configuration handler that replaces separate first-run and update-config on subsequent boots.

#### Boot Flow

```
EVERY BOOT:
1. Get config URL from /tmp/config or /opt/scripts/extras
2. Download remote config with network retry logic (120s timeout)
3. Filter and compare to local config
4. If different:
   - Download required modules
   - Partition device (first boot only)
   - Install boot files and modules
   - Reboot
5. If same -> exit (let browser launch)
```

#### Configuration (Lines 20-42)

```sh
EXTRAS="/opt/scripts/extras"
LOCAL_CONFIG="/opt/scripts/files/lcon"
LOCAL_CONFIG_FILTERED="/opt/scripts/files/lconc"
REMOTE_CONFIG="/tmp/rcon"
LOG="/mnt/logs/boot-config.log"
BUILD_DIR="/tmp/tuxos-build"

MODULE_SERVER="https://cullerdigitalmedia.com/signage/modules"
REQUIRED_MODULES="000-kernel 001-core 002-chrome 003-settings"

FILTER_PATTERN="^daemon_\|^burn_dev=\|^md5conf="
NETWORK_TIMEOUT=120
```

#### Key Functions

**download_file()** - Lines 96-119
```sh
download_file() {
    _url="$1"
    _dest="$2"
    _timeout="${4:-60}"

    # Try wget first
    if command -v wget >/dev/null 2>&1; then
        wget -T"$_timeout" -t3 -q "$_url" -O "$_dest" && return 0
    fi

    # Fallback to curl
    if command -v curl >/dev/null 2>&1; then
        curl -L -s -m"$_timeout" --retry 3 "$_url" -o "$_dest" && return 0
    fi

    return 1
}
```

**filter_config()** - Lines 157-167
```sh
filter_config() {
    _input="$1"
    _output="$2"

    grep -v "^#" "$_input" 2>/dev/null | \
    grep -v "^$" | \
    grep -v "$FILTER_PATTERN" | \
    tr -d '\r' | \
    sort > "$_output"
}
```

**partition_device()** - Lines 235-276
- Clears existing partition table
- Creates MBR with parted:
  - Partition 1: 256MB FAT32 (boot)
  - Partition 2: Remaining ext4 (root)
- Formats with mkfs.vfat and mkfs.ext4

**perform_reconfiguration()** - Lines 353-457
- Downloads all required modules
- Partitions device (first boot only)
- Mounts and installs boot files
- Copies modules to root partition
- Updates extras file
- Reboots

#### Exit Points

| Exit Type | Location | Condition |
|-----------|----------|-----------|
| error_exit | Line 472-473 | No config URL found |
| error_exit | Line 499 | Config download failed after timeout |
| exit 0 | Line 540 | Config unchanged |
| reboot | Line 453 | After reconfiguration |

---

### 3.5 apply-config

**File:** `/opt/scripts/apply-config`
**Lines:** 75
**Interpreter:** `/bin/bash`

Parameter handler orchestrator that sources config and runs all handlers.

#### Execution Flow (Lines 29-74)

```sh
# Source config file
CONFIG="${1:-/opt/scripts/files/lcon}"
set -a  # Export all variables
source "$CONFIG"
set +a

# Run all handlers in numeric order
for handler in "$HANDLER_DIR"/*.sh; do
    if [ -x "$handler" ]; then
        "$handler" 2>> "$LOG_FILE"
    fi
done
```

#### Handler Execution Order

```
00-network.sh  -> 10-proxy.sh    -> 20-browser.sh  ->
30-display.sh  -> 40-input.sh    -> 50-power.sh    ->
60-audio.sh    -> 70-services.sh -> 80-system.sh   ->
90-custom.sh
```

---

### 3.6 update-config

**File:** `/opt/scripts/update-config`
**Lines:** 302
**Interpreter:** `/bin/sh`

x86-style configuration update handler (ported to ARM64).

#### Key Functions

**get_config()** - Lines 25-45
- Handles both `server://` (SSH tunnel) and HTTP URLs
- Proxy PAC support via pactester
- Sanitizes config (fromdos, character filtering)

**fetch_component()** - Lines 124-143
- Downloads with progress bar notifications
- MD5 verification
- Network restart at attempt 4

**burn_ISO()** - Lines 144-186
- x86-style ISO burning (not typically used on ARM64)
- Supports partition 2 direct write or fdisk partitioning

#### Config Comparison (Lines 65-66)

```sh
mdl=`grep ^md5conf= $umd5c 2>/dev/null | head -n1 | cut -d= -f2-`
mdr=`md5sum /tmp/config`
[ "$mdl" = "$mdr" ] && { cleanup; exit; }
```

---

### 3.7 gui-app

**File:** `/opt/scripts/gui-app`
**Lines:** 333
**Interpreter:** `/bin/sh`

Browser launcher with infinite restart loop.

#### Config Priority (Lines 73-100)

```sh
get_homepage() {
    # Priority 1: homepage from lcon
    url=$(grep "^homepage=" "$LCON" | tail -1 | cut -d= -f2-)

    # Priority 2: homepage from extras
    [ -z "$url" ] && url=$(grep "^homepage=" "$EXTRAS" | tail -1 | cut -d= -f2-)

    # Priority 3: kiosk_url (alternate name)
    [ -z "$url" ] && url=$(get_setting "kiosk_url")

    # Priority 4: /tmp/kiosk_url.env
    [ -z "$url" ] && [ -f "$KIOSK_ENV" ] && { . "$KIOSK_ENV"; url="$KIOSK_URL"; }

    # Priority 5: Default
    [ -z "$url" ] && url="about:blank"
}
```

#### Chromium Flags (Lines 106-239)

Core kiosk flags:
```sh
flags="$flags --kiosk"
flags="$flags --no-first-run"
flags="$flags --disable-infobars"
flags="$flags --noerrdialogs"
flags="$flags --disable-session-crashed-bubble"
```

Pi4 specific flags:
```sh
# GPU handling
if [ "$disable_gpu" = "yes" ]; then
    flags="$flags --disable-gpu"
else
    flags="$flags --use-gl=egl"
    flags="$flags --enable-features=VaapiVideoDecoder"
fi

# Memory optimization
flags="$flags --disable-dev-shm-usage"
flags="$flags --memory-pressure-off"
```

#### Main Loop (Lines 287-332)

```sh
while true; do
    HOMEPAGE=$(get_homepage)
    CHROMIUM_FLAGS=$(build_chromium_flags)

    prepare_session  # Clean and restore guest home

    if [ "$APP_MODE" = "yes" ]; then
        su - guest -c "$CHROMIUM_BIN $CHROMIUM_FLAGS --app=\"$HOMEPAGE\""
    else
        su - guest -c "$CHROMIUM_BIN $CHROMIUM_FLAGS \"$HOMEPAGE\""
    fi

    sleep 2  # Prevent tight loop on immediate crash
done
```

---

### 3.8 daemon.sh

**File:** `/opt/scripts/daemon.sh`
**Lines:** 127
**Interpreter:** `/bin/bash`

Remote configuration polling daemon.

#### Polling Loop (Lines 42-126)

```sh
while true; do
    CONFIG_URL=$(grep "^kiosk_config=" "$LCON" | cut -d= -f2-)

    if [ -n "$CONFIG_URL" ]; then
        # Download remote config
        wget -q -T 30 -O "$RCON.tmp" "$CONFIG_URL"

        # Filter and compare
        filter_config "$LCON" > "$LCONC"
        filter_config "$RCON" > "$RCONC"

        lcon_md5=$(md5sum "$LCONC" | cut -d' ' -f1)
        rcon_md5=$(md5sum "$RCONC" | cut -d' ' -f1)

        if [ "$lcon_md5" != "$rcon_md5" ]; then
            # Config changed
            if grep -q "^daemon_force_reboot=yes" "$RCON"; then
                notify "critical" "System will reboot in 30 seconds..."
                cp "$RCON" "$LCON"
                /opt/scripts/apply-config "$RCON"
                sleep 30
                init 6
            else
                /opt/scripts/apply-config "$RCON" &
                [ -x /opt/scripts/update-config ] && /opt/scripts/update-config &
                cp "$RCON" "$LCON"
            fi
        fi
    fi

    # Get interval (default 60 seconds)
    interval=$(grep "^daemon_check=" "$LCON" | cut -d= -f2-)
    [ -n "$interval" ] && CHECK_INTERVAL=$interval

    sleep "$CHECK_INTERVAL"
done
```

---

## 4. Parameter Handlers

Parameter handlers in `/opt/scripts/param-handlers/` process configuration parameters.

### Handler Architecture

Each handler follows this pattern:

```sh
#!/bin/bash
# Source config if not already sourced
[ -z "$CONFIG" ] && CONFIG="/opt/scripts/files/lcon"
[ -f "$CONFIG" ] && source "$CONFIG"

log() { echo "[$(basename "$0")] $*" >> "${LOG_FILE:-/tmp/apply-config.log}"; }

# ----- Parameter: parameter_name -----
# Description: What it does
# Values: valid values
if [ -n "$parameter_name" ]; then
    log "Parameter: $parameter_name"
    # Apply the setting
fi
```

### 00-network.sh Key Functions

**check_internet()** - Lines 47-67
```sh
check_internet() {
    CONNECTIVITY_ENDPOINTS="
        http://connectivitycheck.gstatic.com/generate_204
        http://www.msftconnecttest.com/connecttest.txt
        http://captive.apple.com/hotspot-detect.html
    "

    for endpoint in $CONNECTIVITY_ENDPOINTS; do
        if wget --spider "$endpoint" 2>/dev/null; then
            INTERNET_REACHABLE=yes
            return 0
        fi
    done
    return 1
}
```

**get_eth_iface()** - Lines 98-108
```sh
get_eth_iface() {
    for iface in /sys/class/net/*; do
        iface=$(basename "$iface")
        [ "$iface" = "lo" ] && continue
        [ -d "/sys/class/net/$iface/wireless" ] && continue
        echo "$iface"
        return
    done
    echo "eth0"  # Fallback
}
```

### Handler Summary

| Handler | Parameters | Key Actions |
|---------|------------|-------------|
| 00-network.sh | connection, dhcp, ip_address, gateway, dns, wifi_* | Configure interfaces, WPA supplicant |
| 10-proxy.sh | proxy, proxy_config | Set HTTP_PROXY, configure PAC |
| 20-browser.sh | homepage, whitelist, blacklist, zoom | Chromium policies, preferences |
| 30-display.sh | rotation, brightness, dpms | xrandr, xset |
| 40-input.sh | keyboard_layout, touchscreen | setxkbmap, xinput_calibrator |
| 50-power.sh | scheduled_action, idle_action | cron jobs, xautolock |
| 60-audio.sh | audio_volume, mute | amixer, pulseaudio |
| 70-services.sh | ssh_access, vnc_access | Start/stop daemons |
| 80-system.sh | hostname, timezone | hostnamectl, timedatectl |
| 90-custom.sh | custom_script, run_command | Execute user scripts |

---

## 5. Helper Scripts

### pkget

**File:** `/opt/scripts/pkget`
**Lines:** 62

Secure file download utility with dual-mode support.

**Mode 1: SSH Tunnel** (Lines 41-45)
```sh
if [ "`echo $1 | cut -c1-9`" = "server://" ]; then
    dfile=`echo $1 | sed 's_server://__'`
    sshpass -p 9Se-7c.fgLa scp -P 9999 \
        kiosk@127.0.0.1:hosts/files/$dfile $2
fi
```

**Mode 2: HTTP/HTTPS/FTP** (Lines 47-55)
```sh
fetch() {
    wget --no-http-keep-alive --no-cache \
         --no-check-certificate -q -T20 -t5 $1 -O $2
}
```

### wizard-now

**File:** `/opt/scripts/wizard-now`
**Lines:** 33

Simple GTKDialog prompt to launch network wizard.

```xml
<window title="Network Wizard" width-request="400">
    <text>Wait on connection or click to start wizard immediately.</text>
    <button>
        <label>Launch network wizard</label>
        <action>touch /tmp/launch-wizard</action>
        <action>kill wizard-now process</action>
    </button>
</window>
```

### xvkbd

**File:** `/opt/scripts/xvkbd`
**Lines:** 33

Virtual keyboard launcher with openbox window movement fix.

---

## 6. Debugging Scripts

### flow-logger

**File:** `/opt/scripts/flow-logger`
**Lines:** 114

Script flow logging utility for tracing execution.

**Usage:**
```sh
source /opt/scripts/flow-logger
flow_enter "script_name"
flow_checkpoint "script_name" "Reached milestone"
flow_var "script_name" "variable" "$value"
flow_error "script_name" "Error message"
flow_exit "script_name" $?
```

**Log Location:** `/mnt/logs/flow.log`

### boot-capture

**File:** `/opt/scripts/boot-capture`
**Lines:** 264

Comprehensive boot state capture for debugging.

**Commands:**
```sh
boot-capture init     # Initialize capture log
boot-capture system   # Capture system state (uname, env, network)
boot-capture scripts  # Capture all /opt/scripts
boot-capture display  # Capture X/GTK state
boot-capture prereqs  # Check wizard prerequisites
boot-capture xorg     # Capture Xorg log
boot-capture monitor  # Monitor .knetPage changes (live)
boot-capture all      # Full capture
```

**Log Location:** `/mnt/logs/boot-capture.log`

### debug

**File:** `/opt/scripts/debug`
**Lines:** 133

System debugging information collector.

**Output:** `/var/log/debug`

**Sections captured:**
- VERSION, HOSTNAME, UPTIME
- CHEATCODES (/proc/cmdline)
- PROCESSOR, MEMORY/SWAP
- BLOCK DEVICES, MOUNTS
- PROCESSES, LSPCI, LSUSB
- NETWORKING, WIRELESS DATA
- FIREWALL, SERVICES
- SOUND CARDS, INPUT DEVICES
- SCREEN (xrandr), OpenGL
- Xorg.0.log, System logs

---

## 7. GTKDialog Patterns

### Including wizard-functions

```sh
gtkdialog -i /opt/scripts/files/wizard/wizard-functions -s -c
```

### Page Navigation (Notebook)

```xml
<notebook page="0" show-tabs="false" labels="page1|page2|page3">
    <vbox><!-- Page 0 content --></vbox>
    <vbox><!-- Page 1 content --></vbox>
    <vbox><!-- Page 2 content --></vbox>
    <variable>nPage</variable>
    <input file>'$TMP'/.knetPage</input>
</notebook>

<!-- Navigate to page 2 -->
<action>echo 2 > '$TMP'/.knetPage</action>
<action>refresh:nPage</action>
```

### Page Initialization Workaround (GTKDialog 0.8.3)

```xml
<timer visible="false" milliseconds="100">
    <action>echo 0 > '$TMP'/.knetPage</action>
    <action>refresh:nPage</action>
    <action>disable:pageInitTimer</action>
    <variable>pageInitTimer</variable>
</timer>
```

### File Monitoring

```xml
<comboboxtext file-monitor="'$TMP'/essid" auto-refresh="true">
    <input file>'$TMP'/essid</input>
    <variable>essid</variable>
</comboboxtext>
```

### Conditional Actions

```xml
<action condition="command_is_true( [ `grep wifi $TMP/connection.tmp` ] && echo true )">
    echo 4 > $TMP/.knetPage
</action>
```

### Progress Notifications

```sh
VAR=$(dunstify -p -r $VAR -u critical \
    -i $PTH/status/dialog-information.png \
    -h int:value:$percent " Downloading component ...")
```

### Key wizard-functions

| Function | Purpose | Usage |
|----------|---------|-------|
| `gtk_yesno()` | Yes/No dialog | `gtk_yesno "Message" 400` |
| `gtk_warning()` | Warning dialog | `gtk_warning "Title" "Message" 400` |
| `get_device()` | List network interfaces | Populates $TMP/device |
| `get_essid()` | Scan WiFi networks | Populates $TMP/essid |
| `go_forward()` | Navigate to next page | Internal page logic |
| `get_report()` | Build config report | Concatenates *.tmp files |
| `dlist()` | List block devices | Populates $TMPDIR/block.txt |

---

## 8. Error Handling Patterns

### Network Retry Pattern

```sh
TRIES=49
while [ $TRIES -gt 0 ]; do
    wget -q -T20 -t1 --spider "$URL" && break
    dunstify "Not accessible - tries left: $TRIES"
    TRIES=$((TRIES-1))
    sleep 2
done
```

### Component Download with Verification

```sh
fetch_component() {
    DONE=no; TRIES=9
    while [ $TRIES -gt 0 ]; do
        [ $TRIES = 4 ] && restart_net
        wget -O "$dest" "$url"
        [ "$expected_md5" = "$(md5sum "$dest" | cut -d' ' -f1)" ] && {
            DONE=yes; break
        }
        TRIES=$((TRIES-1))
        rm -f "$dest"
    done
}
```

### Cleanup on Exit

```sh
cleanup() {
    cd /
    killall browser 2>/dev/null
    rm -rf /tmp/config* /tmp/log
}
trap 'cleanup' 2 14 15  # INT, ALRM, TERM
```

### Error Exit with Notification

```sh
error_exit() {
    log "FATAL: $*"
    notify "Configuration failed: $*" "critical"
    echo "$*" > /tmp/boot-config-failed
    exit 1
}
```

---

## 9. Configuration Files

### /opt/scripts/extras

Runtime state file tracking device configuration:

```ini
# First boot (from ISO):
first_run=yes

# After installation:
boot_dev=/dev/mmcblk0p2
kiosk_config_name=facility_ds1.txt
kiosk_config_url=http://cullerdigitalmedia.com/signage/facility/facility_ds1.txt

# After config applied:
homepage=https://example.com/signage
scheduled_action=Sunday-03:00 action:reboot
```

### /opt/scripts/files/lcon

Local configuration (current active):

```ini
kiosk_config=http://cullerdigitalmedia.com/signage/facility/facility_ds1.txt
homepage=https://example.com/signage
browser=chrome
daemon_check=60
scheduled_action=Sunday-03:00 action:reboot
```

### /opt/scripts/files/lconc

Filtered local config (for comparison):
- Excludes: `daemon_*`, `burn_dev=`, `md5conf=`
- Sorted alphabetically

### /tmp/config

Wizard output (temporary):

```ini
# Network settings (from welcome):
connection=wired
dhcp=yes

# Device settings (from wizard):
burn_dev=mmcblk0
kiosk_config=http://cullerdigitalmedia.com/signage/facility/facility_ds1.txt
```

---

## Cross-References

- See [PARAM_REFERENCE.md](PARAM_REFERENCE.md) for complete parameter documentation
- See [BOOT_SEQUENCE.md](BOOT_SEQUENCE.md) for boot flow details
- See [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) for overall architecture
- See [ARM_PORTING_NOTES.md](ARM_PORTING_NOTES.md) for x86 vs ARM64 differences

---

## Document History

| Date | Changes |
|------|---------|
| 2026-01-18 | Created comprehensive verified documentation with line counts from source |
