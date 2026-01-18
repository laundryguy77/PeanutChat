# Porteus Kiosk Binary Analysis: first-run and update-config

## Overview

Based on analyzing captured runtime data, here's what these proprietary Porteus Kiosk binaries do.

## Boot Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           FIRST BOOT                                      │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  1. autostart runs                                                        │
│        │                                                                  │
│        ▼                                                                  │
│  2. wizard-now shows "Launch wizard" dialog                               │
│        │                                                                  │
│        ▼                                                                  │
│  3. welcome runs (network config wizard)                                  │
│        │ Writes to /tmp/config:                                          │
│        │   - connection=wired/wifi                                        │
│        │   - dhcp=yes (or manual IP settings)                            │
│        │   - proxy settings                                               │
│        ▼                                                                  │
│  4. wizard runs (TuxOS device selection)                                  │
│        │ Appends to /tmp/config:                                         │
│        │   - burn_dev=sda                                                │
│        │   - kiosk_config=http://cullerdigitalmedia.com/kc/.../xxx.txt   │
│        ▼                                                                  │
│  5. first-run binary executes                                             │
│        │                                                                  │
│        └──────────────────────────────────────────────────────────────────┤
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                        SUBSEQUENT BOOTS                                   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  1. autostart runs                                                        │
│        │                                                                  │
│        ▼                                                                  │
│  2. update-config binary executes                                         │
│        │ Reads kiosk_config_name from /opt/scripts/extras                │
│        │ Downloads config, applies changes                                │
│        ▼                                                                  │
│  3. Browser/kiosk launches with applied settings                          │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

## /opt/scripts/extras State Progression

This file tracks the device state:

```
# Initial (from ISO):
first_run=yes

# After first-run completes:
boot_dev=/dev/sda2
kiosk_config_name=loom_ds1.txt

# After update-config applies remote config:
boot_dev=/dev/sda2
kiosk_config_name=loom_ds1.txt
scheduled_action=Sunday-03:00 action:reboot
```

## /tmp/config Format (from wizard)

Written by welcome + wizard scripts:

```
# Network settings (from welcome):
connection=wired
dhcp=yes
# OR for manual:
# ipaddress=192.168.1.100
# netmask=255.255.255.0
# gateway=192.168.1.1
# dns1=8.8.8.8

# Proxy (optional):
# proxy=192.168.1.20:3128

# Device settings (from wizard):
burn_dev=sda
kiosk_config=http://cullerdigitalmedia.com/signage/loom/loom_ds1.txt
```

## Remote Config File Format

The URL in kiosk_config points to a .txt file like:

```
# Example: loom_ds1.txt
homepage=http://example.com/signage
scheduled_action=Sunday-03:00 action:reboot
# Other possible settings:
# fullscreen=yes
# disable_navigation=yes
# browser_zoom=100
# idle_action=screensaver
# etc.
```

---

## What first-run Does

**Trigger**: Called from autostart when `/opt/scripts/extras` contains `first_run=yes`

**Inputs**:
- `/opt/scripts/extras` - checks for `first_run=yes`
- `/tmp/config` - reads burn_dev and kiosk_config URL

**Actions**:
1. Verify `first_run=yes` in extras
2. Parse `/tmp/config` for:
   - `burn_dev` - target disk device
   - `kiosk_config` - URL to remote configuration file
3. Install OS to target device:
   - Partition the disk
   - Copy ISO contents / create bootable system
   - Set up boot loader
4. Download config file from `kiosk_config` URL
5. Extract filename from URL → `kiosk_config_name`
6. Update `/opt/scripts/extras`:
   - Remove `first_run=yes`
   - Add `boot_dev=/dev/XXX`
   - Add `kiosk_config_name=XXX.txt`
7. Possibly reboot into installed system

**Outputs**:
- Installed OS on target disk
- Updated `/opt/scripts/extras`

---

## What update-config Does

**Trigger**: Called from autostart on every boot (after first-run is complete)

**Inputs**:
- `/opt/scripts/extras` - reads `kiosk_config_name`
- Remote server - downloads config file

**Actions**:
1. Read `kiosk_config_name` from extras
2. Construct full URL (base URL + config name)
   - Base URL is likely stored elsewhere or hardcoded
   - Your TuxOS uses: `http://cullerdigitalmedia.com/...`
3. Download the remote config file
4. Parse each line as `key=value`
5. Apply settings to the system:
   - Update browser homepage/URL
   - Set scheduled actions (reboot times, etc.)
   - Configure display settings
   - etc.
6. Update `/opt/scripts/extras` with any persistent settings

**Outputs**:
- Applied system configuration
- Updated `/opt/scripts/extras` (adds settings like scheduled_action)

---

## Config Settings Observed

From captured data, these settings are used:

| Setting | Example | Purpose |
|---------|---------|---------|
| `boot_dev` | `/dev/sda2` | Installed system partition |
| `kiosk_config_name` | `loom_ds1.txt` | Name of remote config file |
| `scheduled_action` | `Sunday-03:00 action:reboot` | Weekly reboot schedule |

The Porteus Kiosk documentation lists many more possible settings.

---

## Shell Script Replacement Strategy

Since you control the server and don't need:
- Porteus licensing
- Porteus server communication
- Proprietary installation logic

You can replace these with shell scripts that:

### first-run.sh
```bash
#!/bin/sh
# Read /tmp/config
# Extract kiosk_config URL
# Download config file
# Save kiosk_config_name to extras
# Apply initial settings
# Remove first_run=yes flag
```

### update-config.sh
```bash
#!/bin/sh
# Read kiosk_config_name from extras
# Download config from your server
# Compare with previous (optional)
# Apply settings line by line
# Update extras with persistent settings
```

See the provided `arm64-first-run.sh` and `arm64-update-config.sh` for implementations.

---

## Key URLs for TuxOS

Based on your wizard:

| Device Type | URL Pattern |
|-------------|-------------|
| Kiosk | `http://cullerdigitalmedia.com/kc/{facility}/{facility}_ks{num}.txt` |
| Digital Signage | `http://cullerdigitalmedia.com/signage/{facility}/{facility}_ds{num}.txt` |
| Education | `http://cullerdigitalmedia.com/kc/{facility}_ed.txt` |
| Medcart | `http://cullerdigitalmedia.com/kc/{facility}/{facility}_mc{num}.txt` |
| Treatment | `http://cullerdigitalmedia.com/kc/{facility}/{facility}_tc{num}.txt` |
| NurseStation | `http://cullerdigitalmedia.com/kc/{facility}/{facility}_ns{num}.txt` |
| Bedboard | `http://cullerdigitalmedia.com/kc/{facility}/{facility}_stats.txt` |
| ActivityPro | `http://cullerdigitalmedia.com/activitypro/{facility}.txt` |
| Resident Room | `http://cullerdigitalmedia.com/kc/{facility}/{facility}_rr{num}.txt` |

Supporting files:
- `http://cullerdigitalmedia.com/files/fac.txt` - facility list
- `http://cullerdigitalmedia.com/files/dev.txt` - device types
- `http://cullerdigitalmedia.com/files/num.txt` - device numbers
- `http://cullerdigitalmedia.com/files/key.txt` - wizard password
