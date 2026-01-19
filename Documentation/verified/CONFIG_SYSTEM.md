# TuxOS ARM64 Configuration System Reference

Complete documentation of the configuration system architecture, parameter handlers,
remote configuration polling, and browser configuration.

**Last Updated:** 2026-01-18 | **Status:** Verified

---

## 1. Configuration System Overview

The ARM64 port uses a modular parameter handler architecture that processes config
parameters from local and remote sources, supporting runtime reconfiguration.

### System Components

| Component | Location | Purpose |
|-----------|----------|---------|
| apply-config | `/opt/scripts/apply-config` | Main config applier (75 lines) |
| param-handlers/ | `/opt/scripts/param-handlers/` | 10 handler scripts (~2090 lines) |
| daemon.sh | `/etc/rc.d/local_net.d/daemon.sh` | Remote config polling (65 lines) |
| lcon | `/opt/scripts/files/lcon` | Local configuration (active) |
| rcon | `/opt/scripts/files/rcon` | Remote configuration (downloaded) |

### Configuration Files

| File | Purpose |
|------|---------|
| `/opt/scripts/files/lcon` | Local config (currently active) |
| `/opt/scripts/files/lconc` | Local config minus daemon_ parameters |
| `/opt/scripts/files/rcon` | Remote config (last downloaded) |
| `/opt/scripts/files/rconc` | Remote config minus daemon_ parameters |
| `/tmp/config` | Wizard output (consumed by first-run) |
| `/tmp/apply-config.log` | Handler execution log |

### Configuration Format

```ini
# Network Settings
connection=wifi
dhcp=yes
ssid_name=OfficeWiFi
wpa_password=secretpassword

# Browser Settings
browser=chromium
homepage=https://example.com/kiosk

# Remote Management
kiosk_config=https://config.example.com/kiosk.cfg
daemon_check=5
```

**Rules:** One key=value per line, no spaces around `=`, `#` for comments.

---

## 2. Parameter Handler Architecture

### Handler Execution (apply-config lines 60-71)

```bash
CONFIG="${1:-/opt/scripts/files/lcon}"
HANDLER_DIR="/opt/scripts/param-handlers"

set -a; source "$CONFIG"; set +a  # Export all variables

for handler in "$HANDLER_DIR"/*.sh; do
    [ -x "$handler" ] && "$handler" 2>> "$LOG_FILE"
done
```

### Handler Execution Order

| Handler | File | Lines | Primary Parameters |
|---------|------|-------|-------------------|
| 00-network.sh | `/opt/scripts/param-handlers/00-network.sh` | 310 | connection, dhcp, WiFi, 802.1x |
| 10-proxy.sh | `/opt/scripts/param-handlers/10-proxy.sh` | 143 | proxy_config, proxy |
| 20-browser.sh | `/opt/scripts/param-handlers/20-browser.sh` | 248 | homepage, whitelist, UI settings |
| 30-display.sh | `/opt/scripts/param-handlers/30-display.sh` | 120 | wallpaper, screen_rotate |
| 40-input.sh | `/opt/scripts/param-handlers/40-input.sh` | 221 | keyboard, mouse, touchscreen |
| 50-power.sh | `/opt/scripts/param-handlers/50-power.sh` | 202 | screensaver, dpms, idle |
| 60-audio.sh | `/opt/scripts/param-handlers/60-audio.sh` | 130 | sound_card, volume |
| 70-services.sh | `/opt/scripts/param-handlers/70-services.sh` | 226 | SSH, VNC, printing |
| 80-system.sh | `/opt/scripts/param-handlers/80-system.sh` | 273 | hostname, timezone, firewall |
| 90-custom.sh | `/opt/scripts/param-handlers/90-custom.sh` | 216 | run_command, debug, watchdog |

### Handler Interface Contract

```bash
#!/bin/bash
[ -z "$CONFIG" ] && CONFIG="/opt/scripts/files/lcon"
[ -f "$CONFIG" ] && source "$CONFIG"

log() { echo "[$(basename "$0")] $*" >> "${LOG_FILE:-/tmp/apply-config.log}"; }

if [ -n "$parameter_name" ]; then
    log "Processing: $parameter_name"
    # Apply configuration
fi
```

---

## 3. Handler Parameters Reference

### 00-network.sh - Network Configuration

| Parameter | Lines | Values |
|-----------|-------|--------|
| `connection` | 116-118 | wired, wifi, dialup |
| `network_interface` | 123-125 | eth0, wlan0, end0 |
| `dhcp` | 130-132 | yes, no |
| `ip_address` | 137-163 | IP address |
| `default_gateway` | 168-176 | IP address |
| `dns_server` | 181-190 | Space-separated IPs |
| `ssid_name` | 198-200 | SSID string |
| `hidden_ssid_name` | 205-207 | SSID string |
| `wifi_encryption` | 212-214 | open, wep, wpa, eap-peap |
| `wpa_password` | 226-254 | Password string |
| `wired_authentication` | 267-291 | eapol, none |
| `eapol_username/password` | 270-290 | Credentials |

**Key Function (lines 47-67):**
```bash
check_internet() {
    for endpoint in $CONNECTIVITY_ENDPOINTS; do
        if $wget_cmd --spider "$endpoint" 2>/dev/null; then
            INTERNET_REACHABLE=yes; return 0
        fi
    done
    return 1
}
```

### 10-proxy.sh - Proxy Configuration

| Parameter | Lines | Values |
|-----------|-------|--------|
| `proxy_config` | 21-34 | PAC file URL |
| `proxy` | 39-108 | [user:pass@]host:port |
| `proxy_exceptions` | 113-140 | Comma-separated hosts |

Applies to: environment variables, `/etc/profile.d/proxy.sh`, `/etc/chromium-flags.conf`, Firefox user.js

### 20-browser.sh - Browser Configuration

| Parameter | Lines | Values |
|-----------|-------|--------|
| `browser` | 35-37 | firefox, chrome, chromium |
| `homepage` | 42-53 | URL or space-separated URLs |
| `whitelist` | 58-63 | Space-separated URL patterns |
| `blacklist` | 68-73 | Space-separated URL patterns |
| `disable_private_mode` | 78-81 | yes, no |
| `password_manager` | 86-89 | yes, no |
| `browser_language` | 94-96 | Language code (en-US) |
| `import_certificates` | 115-132 | URL to cert file |
| `disable_zoom_controls` | 144-146 | yes, no |
| `browser_zoom_level` | 151-153 | 0.8 to 2.0 |
| `disable_navigation_bar` | 193-195 | yes, no |
| `toggle_tabs` | 214-217 | Seconds |
| `refresh_webpage` | 222-225 | Seconds |
| `virtual_keyboard` | 230-238 | yes, no |
| `allow_media_devices` | 243-245 | yes, no |

### 30-display.sh - Display Configuration

| Parameter | Lines | Values |
|-----------|-------|--------|
| `wallpaper` | 24-57 | URL or path to image |
| `screen_settings` | 62-87 | WIDTHxHEIGHT[+X+Y] |
| `screen_rotate` | 92-117 | normal, left, right, inverted |

Uses: `feh --bg-scale`, `xrandr --output --mode/--rotate`

### 40-input.sh - Input Device Configuration

| Parameter | Lines | Values |
|-----------|-------|--------|
| `disable_input_devices` | 27-61 | keyboard, mouse, touchscreen, all |
| `primary_keyboard_layout` | 66-73 | us, de, fr, gb |
| `secondary_keyboard_layout` | 78-87 | Layout code |
| `disable_numlock` | 92-100 | yes, no |
| `hide_mouse` | 105-134 | yes, no, or timeout seconds |
| `mouse_cursor_size` | 139-150 | normal, large, or pixels |
| `mouse_speed` | 155-176 | 0-100 |
| `right_mouse_click` | 181-191 | yes, no |
| `touchscreen_calibration` | 196-218 | Matrix or URL |

### 50-power.sh - Power Management

| Parameter | Lines | Values |
|-----------|-------|--------|
| `screensaver_idle` | 27-50 | Minutes (0 = disabled) |
| `screensaver_archive` | 55-69 | URL to ZIP |
| `slide_duration` | 82-84 | Seconds |
| `screensaver_video` | 96-107 | URL or path |
| `dpms_idle` | 119-131 | Minutes |
| `suspend_idle` | 151-163 | Minutes |
| `halt_idle` | 168-178 | Minutes |
| `session_idle` | 183-185 | Minutes |
| `session_idle_action` | 190-192 | restart, lock |

### 60-audio.sh - Audio Configuration

| Parameter | Lines | Values |
|-----------|-------|--------|
| `default_sound_card` | 21-60 | Device name or index |
| `default_microphone` | 65-90 | Device name or index |
| `volume_level` | 95-127 | 0-100 |

Supports: ALSA (`amixer`), PulseAudio (`pactl`)

### 70-services.sh - Services Configuration

| Parameter | Lines | Values |
|-----------|-------|--------|
| `additional_components` | 27-29 | ssh, vnc, printing |
| `root_password` | 34-38 | Password string |
| `ssh_port` | 56-57 | Port (default: 22) |
| `ssh_localhost_only` | 61-65 | yes, no |
| `vnc_port` | 107 | Port (default: 5900) |
| `vnc_password` | 122-130 | Password string |
| `vnc_interactive` | 135-138 | yes, no |
| `printer_connection` | 189-197 | usb://, socket://, lpd:// |
| `paper_size` | 202-204 | Letter, A4, Legal |
| `silent_printing` | 209-211 | yes, no |

### 80-system.sh - System Configuration

| Parameter | Lines | Values |
|-----------|-------|--------|
| `hostname` | 24-31 | String |
| `timezone` | 36-49 | America/New_York, etc. |
| `ntp_server` | 54-69 | Hostname or IP |
| `rtc_wake` | 74-91 | HH:MM |
| `scheduled_action` | 96-115 | HH:MM:command |
| `swapfile` | 142-157 | Size in MB |
| `zRAM` | 162-185 | Percentage or MB |
| `disable_firewall` | 198-208 | yes, no |
| `wake_on_lan` | 224-234 | yes, no |
| `hostname_aliases` | 239-255 | IP:hostname pairs |

### 90-custom.sh - Custom Commands

| Parameter | Lines | Values |
|-----------|-------|--------|
| `run_command` | 28-35 | Shell command(s) |
| `kernel_parameters` | 41-46 | Boot parameter string |
| `gpu_driver` | 51-71 | auto, vc4, fbdev, modesetting |
| `debug` | 76-145 | yes, no |
| `hardware_video_decode` | 150-167 | yes, no |
| `watchdog` | 172-213 | yes, no, or timeout seconds |

**Debug Report Contents (lines 81-139):**
- System info (uname, os-release)
- CPU/Memory/Disk usage
- Network configuration (ip addr, route, resolv.conf)
- Display configuration (xrandr)
- Loaded kernel modules
- Process list
- Configuration file (passwords masked)
- Recent logs (apply-config.log, Xorg.log, dmesg)

**Watchdog Implementation (lines 172-213):**
```bash
if [ "$timeout" -gt 0 ]; then
    if [ -c /dev/watchdog ]; then
        (while true; do echo "1" > /dev/watchdog; sleep $((timeout/2)); done) &
    fi
fi
```

---

## 4. Remote Configuration System

### daemon.sh Polling (lines 18-62)

**File:** `/etc/rc.d/local_net.d/daemon.sh` (65 lines)

**Initialization (lines 1-10):**
```bash
lcon=/opt/scripts/files/lcon
config="`grep ^kiosk_config= $lcon | head -n1 | cut -d= -f2-`"
pcid=`grep ^ID: /etc/version | cut -d' ' -f2`
wget="wget --no-http-keep-alive --no-cache --no-check-certificate"
```

**Polling Loop:**
1. Sleep `daemon_check` minutes
2. Append device ID: `$config?kiosk=$pcid` (except FTP)
3. Retry connection up to 14 times with 2s delay
4. Download to `/root/config-TIMESTAMP`
5. Sanitize: `fromdos` (3x), remove special chars
6. Handle GLOBAL sections if present
7. Compare `md5sum lconc` vs `rconc`
8. If different: reboot or schedule via greyos_reboot

**GLOBAL Section Processing (lines 36-42):**
```bash
if grep -q '^\[\[.*GLOBAL.*\]\]' $rcon; then
    sed -n '/^\[\[.*'$pcid'.*\]\]/,/^$/p' $rcon > /tmp/conf
    sed -e '/^\[\[.*GLOBAL.*\]\]/d' -e '/^\[\[/q' $rcon >> /tmp/conf
    mv /tmp/conf $rcon
fi
```

**Config Change Detection (lines 49-58):**
```bash
if [ `md5sum $lconc | cut -d" " -f1` != `md5sum $rconc | cut -d" " -f1` ]; then
    [ "`grep ^daemon_force_reboot=yes $rcon`" ] && { sleep 30; init 6; }
    /opt/scripts/files/greyos_reboot &
fi
```

### Daemon-Specific Parameters

| Parameter | Description | Values |
|-----------|-------------|--------|
| `kiosk_config` | Remote config URL | URL |
| `daemon_check` | Polling interval | Minutes (default: 5) |
| `daemon_force_reboot` | Immediate reboot | yes, no |
| `daemon_message` | Display notification | String |

---

## 5. Browser Configuration

### Chromium Kiosk Flags

| Flag | Purpose |
|------|---------|
| `--kiosk` | Fullscreen mode, no decorations |
| `--no-first-run` | Skip welcome screen |
| `--disable-infobars` | Disable info bars |
| `--noerrdialogs` | Suppress error dialogs |
| `--disable-translate` | No translation prompts |
| `--disable-sync` | No Google sync |
| `--use-gl=egl` | EGL for Pi4 GPU |
| `--enable-features=VaapiVideoDecoder` | Hardware video decode |

### Config to Flags Mapping

| Config Parameter | Chromium Flag(s) |
|-----------------|------------------|
| `fullscreen=no` | `--start-maximized` |
| `browser_zoom_level=150` | `--force-device-scale-factor=1.5` |
| `disable_navigation_bar=yes` | `--app=URL` |
| `disable_zoom_controls=yes` | `--disable-pinch` |
| `hide_mouse=yes` | `--cursor=none` |
| `enable_file_protocol=yes` | `--allow-file-access-from-files` |
| `allow_popup_windows=yes` | `--disable-popup-blocking` |
| `disable_gpu=yes` | `--disable-gpu --disable-software-rasterizer` |

### Chromium Policy File

**Location:** `/etc/chromium/policies/managed/policy.json`

| Config Setting | Policy Key |
|---------------|------------|
| `whitelist` | `URLAllowlist` |
| `blacklist` | `URLBlocklist` |
| `disable_private_mode=yes` | `IncognitoModeAvailability: 1` |
| `password_manager=yes` | `PasswordManagerEnabled: true` |

### Homepage Resolution Priority

1. `/tmp/kiosk_url.env` - `KIOSK_URL="..."`
2. `/opt/scripts/files/lcon` - `homepage=URL`
3. `/opt/scripts/extras` - `homepage=URL`
4. Default: `about:blank`

---

## 6. Configuration Flow

### Boot-Time Flow

```
rc.S -> rc.M -> rc.4 -> xinitrc -> autostart
                                      |
    +---> first-run (if exists) -> welcome wizard -> /tmp/config
    +---> Network wait (120s)
    +---> apply-config -> handlers 00-90
    +---> local_net.d -> daemon.sh (background)
    +---> gui-app (browser)
```

### Remote Update Flow

```
daemon.sh loop -> Sleep -> wget config -> Sanitize -> Compare md5
                                                          |
    +---> Same: continue loop
    +---> Different: daemon_force_reboot? -> reboot
                     else -> greyos_reboot (3:00 AM)
```

---

## 7. Adding New Parameters

To add a new parameter to the configuration system:

1. **Identify the handler** - Choose based on parameter category (network, browser, etc.)

2. **Edit the handler script** in `/opt/scripts/param-handlers/`:
```bash
# Parameter: new_param
# Description: Does something useful
# Values: value1, value2
if [ -n "$new_param" ]; then
    log "Processing: $new_param"
    case "$new_param" in
        value1) do_action_1 ;;
        value2) do_action_2 ;;
    esac
fi
```

3. **Test the parameter:**
```bash
echo "new_param=value1" >> /opt/scripts/files/lcon
/opt/scripts/apply-config
tail -f /tmp/apply-config.log
```

4. **Rebuild the module:**
```bash
cd /home/culler/saas_dev/pk-port/arm64
./scripts/build-003-settings.sh
cp output/003-settings.xzm ../iso-arm64/xzm/
```

No changes required to apply-config, daemon.sh, or autostart.

---

## Related Documentation

- [SCRIPTS_REFERENCE.md](../SCRIPTS_REFERENCE.md) - Boot scripts and execution timeline
- [PARAM_REFERENCE.md](../PARAM_REFERENCE.md) - Complete parameter reference
- [GUI_APP_BROWSER_FLAGS.md](../GUI_APP_BROWSER_FLAGS.md) - Browser flags details
- [PARAM_HANDLERS.md](../PARAM_HANDLERS.md) - Handler architecture overview

---

## Source File Summary

| File | Location | Lines |
|------|----------|-------|
| apply-config | `/opt/scripts/apply-config` | 75 |
| 00-network.sh | `/opt/scripts/param-handlers/00-network.sh` | 310 |
| 10-proxy.sh | `/opt/scripts/param-handlers/10-proxy.sh` | 143 |
| 20-browser.sh | `/opt/scripts/param-handlers/20-browser.sh` | 248 |
| 30-display.sh | `/opt/scripts/param-handlers/30-display.sh` | 120 |
| 40-input.sh | `/opt/scripts/param-handlers/40-input.sh` | 221 |
| 50-power.sh | `/opt/scripts/param-handlers/50-power.sh` | 202 |
| 60-audio.sh | `/opt/scripts/param-handlers/60-audio.sh` | 130 |
| 70-services.sh | `/opt/scripts/param-handlers/70-services.sh` | 226 |
| 80-system.sh | `/opt/scripts/param-handlers/80-system.sh` | 273 |
| 90-custom.sh | `/opt/scripts/param-handlers/90-custom.sh` | 216 |
| daemon.sh | `/etc/rc.d/local_net.d/daemon.sh` | 65 |
| **Total** | | **2,230** |

---

## Document History

- **Created:** 2026-01-18
- **Purpose:** Comprehensive configuration system documentation
- **Sources Analyzed:** 10 param handlers, apply-config, daemon.sh, existing documentation
