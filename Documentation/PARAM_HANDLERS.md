# ARM64 Port: Extensible Parameter Handler System

## Overview

The ARM64 port uses an extensible parameter handler architecture for processing configuration parameters from remote config files (`kiosk_config`). This design makes adding new parameters simple - just edit the appropriate handler script.

**Scope:** Remote config parameters only. Server-based parameters (`kiosk_server`, `client_id`) are out of scope.

**Status:** Integration verified and deployed (2026-01-13)

---

## Boot Flow

The verified boot flow order:

```
autostart → DPMS off → network wait → NTP → first-run → update-config → apply-config → local_net.d hooks → browser
```

---

## Architecture

### Design Goals

1. **Easy to add new parameters** - Single location to register new parameter handlers
2. **Modular** - Each parameter category has its own handler script
3. **Consistent** - All parameters processed the same way
4. **Testable** - Individual handlers can be tested in isolation

### Directory Structure

```
/opt/scripts/
├── param-handlers/           # Parameter handler scripts
│   ├── 00-network.sh         # Connection, DHCP, IP, WiFi
│   ├── 10-proxy.sh           # Proxy settings
│   ├── 20-browser.sh         # Browser selection, homepage, whitelist
│   ├── 30-display.sh         # Screen rotation, resolution, wallpaper
│   ├── 40-input.sh           # Keyboard, mouse, touchscreen
│   ├── 50-power.sh           # DPMS, screensaver, idle actions
│   ├── 60-audio.sh           # Sound card, volume
│   ├── 70-services.sh        # SSH, VNC, printing
│   ├── 80-system.sh          # Hostname, timezone, NTP, scheduled
│   └── 90-custom.sh          # run_command, debug
├── apply-config              # Main config applier (calls handlers)
├── daemon.sh                 # Calls apply-config on change
├── files/
│   └── lcon                  # Local config (active configuration)
└── ...
```

---

## Core Components

### apply-config Script

**Location:** `/opt/scripts/apply-config`

The main config applier that sources the config file and runs all handlers in order.

```bash
#!/bin/bash
# Apply configuration parameters from lcon
# Called by daemon.sh when config changes, and by autostart at boot

CONFIG="${1:-/opt/scripts/files/lcon}"
HANDLER_DIR="/opt/scripts/param-handlers"

# Source config file to get all parameters as shell variables
[ -f "$CONFIG" ] && source "$CONFIG"

# Export for handler scripts
export CONFIG DISPLAY=:0

# Run all handlers in order (numeric prefix determines order)
for handler in "$HANDLER_DIR"/*.sh; do
    [ -x "$handler" ] && "$handler"
done
```

### Handler Execution Order

Handlers execute in numeric order based on their prefix:

| Order | Handler | Purpose |
|-------|---------|---------|
| 00 | network.sh | Network must be configured first |
| 10 | proxy.sh | Proxy needed before browser |
| 20 | browser.sh | Browser config after network/proxy |
| 30 | display.sh | Display settings |
| 40 | input.sh | Input device configuration |
| 50 | power.sh | Power management and idle |
| 60 | audio.sh | Audio configuration |
| 70 | services.sh | SSH, VNC, printing |
| 80 | system.sh | System-level settings |
| 90 | custom.sh | Custom commands run last |

---

## Integration Points

### daemon.sh Integration

The config daemon polls for remote config changes and calls `apply-config`:

```bash
# When config changes detected:
/opt/scripts/apply-config
```

**daemon.sh Enhancements:**

| Parameter | Behavior |
|-----------|----------|
| `daemon_force_reboot=yes` | Triggers 30s countdown then reboot |
| `daemon_message=<text>` | Shows notification via dunstify |

The daemon calls `apply-config` after detecting any config change, before handling force reboot or message parameters.

### autostart Integration

The autostart script calls `apply-config` at boot:

```bash
# At boot, apply initial configuration
/opt/scripts/apply-config
```

---

## Adding New Parameters

### Step-by-Step Guide

1. **Identify the parameter category** (network, browser, display, etc.)

2. **Open the appropriate handler** in `/opt/scripts/param-handlers/`

3. **Add the parameter check:**

```bash
# Parameter: new_param
# Description: Does something useful
# Values: value1, value2, value3
if [ -n "$new_param" ]; then
    case "$new_param" in
        value1) do_action_1 ;;
        value2) do_action_2 ;;
        *)      log "Unknown new_param value: $new_param" ;;
    esac
fi
```

4. **Test the parameter:**

```bash
echo "new_param=value1" >> /opt/scripts/files/lcon
/opt/scripts/apply-config
```

5. **Done.** No changes to daemon.sh or autostart needed.

### Creating a New Handler Category

If the parameter doesn't fit existing categories:

1. Create `/opt/scripts/param-handlers/XX-newcategory.sh`
2. Use numeric prefix to control execution order (00 = first, 90 = last)
3. Make executable: `chmod +x XX-newcategory.sh`
4. Follow the handler template below

---

## Handler Template

```bash
#!/bin/bash
# Parameter Handler: XX-category.sh
# Handles: param1, param2, param3
#
# To add a new parameter:
# 1. Add parameter check below
# 2. Test: echo "param=value" >> /opt/scripts/files/lcon && /opt/scripts/apply-config

# Source config if not already sourced
[ -z "$CONFIG" ] && CONFIG="/opt/scripts/files/lcon"
[ -f "$CONFIG" ] && source "$CONFIG"

log() { echo "[$(basename $0)] $*" >> /tmp/apply-config.log; }

# ----- Parameter: example_param -----
# Description: Example parameter
# Values: yes, no
if [ -n "$example_param" ]; then
    case "$example_param" in
        yes) log "Enabling example feature"; do_enable ;;
        no)  log "Disabling example feature"; do_disable ;;
    esac
fi
```

---

## Testing and Verification

### Manual Testing

```bash
# Test apply-config with custom config file
/opt/scripts/apply-config /path/to/test-lcon

# Test individual handler
/opt/scripts/param-handlers/30-display.sh

# View handler logs
tail -f /tmp/apply-config.log
```

### Build and Deploy

```bash
# Rebuild settings module after changes
cd /home/culler/saas_dev/pk-port/arm64
mksquashfs 003-settings-rootfs 003-settings.xzm -comp xz -noappend
```

### Integration Test Checklist

- [x] daemon.sh detects config change and calls apply-config
- [x] autostart calls apply-config at boot
- [x] Correct boot flow order verified
- [ ] Browser launches with correct homepage
- [ ] Screen rotation applies correctly
- [ ] SSH starts when configured
- [ ] VNC starts when configured
- [ ] Adding new parameter to handler works without other changes

---

## Hook Directories

Supporting hook directories for custom scripts:

| Directory | Purpose |
|-----------|---------|
| `/etc/rc.d/local_cli.d/` | CLI hook scripts (early boot) |
| `/etc/rc.d/local_gui.d/` | GUI hook scripts (after X11) |
| `/etc/rc.d/local_net.d/` | Network hook scripts (after network) |

---

## Files Reference

### Deployed Files (Verified 2026-01-13)

| File | Status |
|------|--------|
| `/opt/scripts/apply-config` | Executable |
| `/opt/scripts/param-handlers/*.sh` | 10 handlers |
| `/etc/profile.d/variables.sh` | Created |
| `/opt/scripts/daemon.sh` | Enhanced with daemon_force_reboot, daemon_message, apply-config calls |
| `/etc/xdg/openbox/autostart` | Correct boot flow order |

### Module Build

```
003-settings.xzm: 1.12 MB (35% compression)
Synced to: iso-content/xzm/, final/boot/xzm/, image/xzm/, output/
```

---

## See Also

- [PARAM_REFERENCE.md](PARAM_REFERENCE.md) - Complete parameter reference tables
- [SCRIPTS_REFERENCE.md](SCRIPTS_REFERENCE.md) - Boot scripts and execution timeline
