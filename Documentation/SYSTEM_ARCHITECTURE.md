# TuxOS ARM64 Port - Complete System Reference

## Document Purpose

This document provides complete context for the TuxOS (Porteus Kiosk derivative) ARM64 port project. Feed this to any AI assistant or developer to align their understanding with the established architecture.

---

## Project Overview

**Goal:** Port TuxOS from x86_64 to ARM64 (Raspberry Pi 4)

**TuxOS** is a customized Porteus Kiosk - a locked-down Linux distribution designed for kiosk/digital signage deployments. It boots into a fullscreen browser pointing to a configured URL, with remote configuration management.

**Key Challenge:** The original system includes proprietary x86 binaries (`first-run`, `update-config`) that handle system installation and reconfiguration. These cannot run on ARM64 and must be replaced with shell script equivalents.

---

## The Core Concept (CRITICAL)

### Every Boot Does This:

```
┌─────────────────────────────────────────────────────────────────┐
│                      EVERY BOOT                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Download remote config from server                          │
│        │                                                        │
│        ▼                                                        │
│  2. Compare to local (known) config                             │
│        │                                                        │
│        ├─── [SAME] ────────► Continue boot (launch browser)     │
│        │                                                        │
│        └─── [DIFFERENT] ──► Update local config                 │
│                                   │                             │
│                                   ▼                             │
│                             Reconfigure system                  │
│                                   │                             │
│                                   ▼                             │
│                             Download modules                    │
│                                   │                             │
│                                   ▼                             │
│                             Burn to partition                   │
│                                   │                             │
│                                   ▼                             │
│                                Reboot                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### "First Run" Is Not Special

"First run" is simply when **no local config exists yet**. The comparison always shows "different" → triggers install.

There is no separate first-run vs update-config logic. It's ONE flow:
- Config different? → Rebuild and burn
- Config same? → Continue to browser

---

## System Architecture

### Boot Sequence

```
Power On
    │
    ▼
Bootloader (Pi: config.txt + kernel8.img)
    │
    ▼
Kernel + initramfs
    │
    ▼
Mount SquashFS modules via AUFS union
    │
    ▼
/sbin/init → rc.S → rc.M → rc.4
    │
    ▼
X11 + Openbox window manager
    │
    ▼
/etc/xdg/openbox/autostart
    │
    ├── Input/screen setup
    ├── Network wait
    ├── *** BOOT CONFIG CHECK *** ←── This is where the magic happens
    │         │
    │         ├── [Config same] → Continue
    │         └── [Config different] → Rebuild, burn, reboot
    │
    ▼
gui-app → Browser launch (kiosk mode)
```

### Filesystem Structure

TuxOS uses **SquashFS modules** union-mounted via AUFS:

```
/porteuskiosk/
├── 000-kernel.xzm      # Kernel modules, firmware
├── 001-core.xzm        # Base system (busybox, libs)
├── 002-chrome.xzm      # Browser (Chromium)
└── 003-settings.xzm    # Config, scripts, customizations

These are read-only, layered together with a tmpfs for writes.
```

### Key Files

| File | Purpose |
|------|---------|
| `/opt/scripts/extras` | Device state: boot_dev, config URL, config name |
| `/opt/scripts/files/lcon` | Local config (last known good) |
| `/opt/scripts/files/lconc` | Local config filtered (for comparison) |
| `/opt/scripts/files/rconc` | Remote config filtered (for comparison) |
| `/tmp/config` | Wizard output (first boot only) |
| `/etc/xdg/openbox/autostart` | Desktop session startup script |

---

## Remote Configuration

### Config URL Structure

TuxOS fetches config from URLs like:
```
http://cullerdigitalmedia.com/signage/{facility}/{facility}_ds{num}.txt
http://cullerdigitalmedia.com/kc/{facility}/{facility}_ks{num}.txt
```

The URL is determined by:
1. **First boot:** Wizard writes `kiosk_config=URL` to `/tmp/config`
2. **Subsequent boots:** Read from `/opt/scripts/extras`

### Config File Format

```ini
# Browser settings
homepage=http://your-kiosk-url.com/signage
browser_zoom=100
fullscreen=yes
disable_navigation=yes

# Scheduled maintenance
scheduled_action=Sunday-03:00 action:reboot

# Daemon settings (filtered during comparison)
daemon_check=5
daemon_force_reboot=yes
```

### Config Comparison

Before comparing, these settings are **filtered out** (they're meta/volatile):
- `daemon_*` (polling interval, force flags)
- `burn_dev=` (install target)
- `md5conf=` (hash metadata)

This prevents unnecessary rebuilds when only operational settings change.

---

## extras File

The `/opt/scripts/extras` file tracks device state:

### First Boot (from ISO)
```ini
first_run=yes
```

### After Installation
```ini
boot_dev=/dev/sda2
kiosk_config_name=loom_ds1.txt
kiosk_config_url=http://cullerdigitalmedia.com/signage/loom/loom_ds1.txt
homepage=http://example.com/signage
scheduled_action=Sunday-03:00 action:reboot
```

---

## Wizard Flow (First Boot Only)

On first boot, before the config check runs:

```
wizard-now    →  "Launch wizard" dialog
     │
     ▼
welcome       →  Network configuration (wired/wifi, DHCP/static)
     │
     ▼
wizard        →  Device selection (facility, device type, number)
     │
     ▼
Writes /tmp/config:
    burn_dev=sda
    kiosk_config=http://cullerdigitalmedia.com/signage/loom/loom_ds1.txt
```

The boot config script then reads `/tmp/config` to get the URL and target device.

---

## Reconfiguration Process

When config differs, the system:

### 1. Shows Notifications
```
[Blue]  "Performing system reconfiguration - please do not turn off the PC."
[Blue]  "Downloading additional components ..."
[Red]   "[50%] Downloading 002-chrome.xzm component ..."
[Red]   "Burning ISO on /dev/sda2 - this may take a while ..."
[Blue]  "Reconfiguration complete. System will reboot."
```

### 2. Downloads Modules
From module server (e.g., `http://cullerdigitalmedia.com/tuxos/arm64/`):
- 000-kernel.xzm
- 001-core.xzm
- 002-chrome.xzm
- 003-settings.xzm

### 3. Burns to Target

**x86 Method:**
```bash
# Build ISO and write raw to partition
mkisofs -o /tmp/new.iso [options] /tmp/build
cat /tmp/new.iso > /dev/sda2
```

**ARM64 Method (Pi4 can't boot raw ISOs):**
```bash
# Mount partition and update files directly
mount /dev/sda2 /mnt/root
cp modules/*.xzm /mnt/root/porteuskiosk/
cp config /mnt/root/opt/scripts/files/lcon
sync
umount /mnt/root
```

### 4. Reboots
System reboots into the updated configuration.

---

## ARM64/Pi4 Differences

| Aspect | x86 TuxOS | ARM64 TuxOS |
|--------|-----------|-------------|
| Bootloader | isolinux/GRUB | Pi firmware (config.txt) |
| Kernel | vmlinuz | kernel8.img |
| Boot config | isolinux.cfg | cmdline.txt + config.txt |
| Burn method | Raw ISO to partition | Update files on ext4 |
| Partition layout | Single ISO partition | FAT32 boot + ext4 root |

### Pi4 Partition Layout

```
/dev/sda (or /dev/mmcblk0)
├── Partition 1: 256MB FAT32 (boot)
│   ├── kernel8.img
│   ├── *.dtb, overlays/
│   ├── config.txt
│   ├── cmdline.txt
│   └── start4.elf, fixup4.dat
│
└── Partition 2: Remainder ext4 (root)
    ├── porteuskiosk/*.xzm
    ├── opt/scripts/extras
    ├── opt/scripts/files/lcon
    └── docs/kiosk.sgn
```

---

## Implementation: arm64-boot-config.sh

Single unified script that replaces both `first-run` and `update-config`:

```bash
#!/bin/sh
# Called from /etc/xdg/openbox/autostart

# 1. Determine config URL
#    - First boot: from /tmp/config (wizard output)
#    - Subsequent: from /opt/scripts/extras

# 2. Download remote config
#    wget "$CONFIG_URL?kiosk=$DEVICE_ID" -O /tmp/rcon

# 3. Filter and compare
#    - Remove daemon_*, burn_dev, md5conf
#    - Compare filtered local vs remote

# 4. If SAME: exit (browser will launch)

# 5. If DIFFERENT:
#    a. Download XZM modules from MODULE_SERVER
#    b. If first boot: partition device
#    c. Mount root partition
#    d. Update modules and config files
#    e. Sync, unmount
#    f. Reboot
```

### Configuration Variables

```bash
MODULE_SERVER="http://cullerdigitalmedia.com/tuxos/arm64"
REQUIRED_MODULES="000-kernel 001-core 002-chrome 003-settings"
FILTER_PATTERN="^daemon_\|^burn_dev=\|^md5conf="
```

---

## Desktop Notifications

Uses `dunstify` for user feedback:

```bash
# Blue (info)
dunstify -u normal "Message here"

# Red (critical/progress)  
dunstify -u critical "[50%] Downloading component..."
```

---

## Integration Points

### autostart Hook

In `/etc/xdg/openbox/autostart`:
```bash
# Replace:
#   [ -e /opt/scripts/first-run ] && su -c /opt/scripts/first-run
#   [ -e /opt/scripts/update-config ] && su -c /opt/scripts/update-config

# With:
/opt/scripts/arm64-boot-config.sh
```

### gui-app (Browser Launcher)

Should read URL from `/opt/scripts/files/lcon` or `/tmp/kiosk_settings/homepage`:
```bash
KIOSK_URL=$(grep "^homepage=" /opt/scripts/files/lcon | cut -d= -f2-)
chromium-browser --kiosk "$KIOSK_URL"
```

---

## Module Server Setup

Host ARM64 modules at your MODULE_SERVER URL:

```
http://yourserver.com/tuxos/arm64/
├── 000-kernel.xzm    # Kernel 6.1.x for Pi4, modules, firmware
├── 001-core.xzm      # Base system, busybox, libs (ARM64)
├── 002-chrome.xzm    # Chromium browser (ARM64)
└── 003-settings.xzm  # Scripts, configs, customizations
```

---

## Current Port Status

### Working
- ✅ Kernel boot (6.1.93-v8+)
- ✅ SquashFS/AUFS module loading
- ✅ X11 + Openbox
- ✅ Input devices (keyboard/mouse)
- ✅ First-run wizard GUI displays

### Needs Work
- ⚠️ Missing libraries (libiw.so.30, libkeyutils.so.1, libsasl2.so.2)
- ⚠️ Boot config script integration
- ⚠️ ARM64 module hosting
- ⚠️ End-to-end testing

---

## Testing Procedure

### First Boot Test
```bash
# 1. Boot from live ISO/SD with first_run=yes in extras
# 2. Complete wizard flow
# 3. Verify /tmp/config created with burn_dev and kiosk_config
# 4. Verify script partitions target device
# 5. Verify modules downloaded and installed
# 6. Verify reboot into installed system
# 7. Verify extras updated (no first_run=yes)
```

### Config Update Test
```bash
# 1. Boot installed system
# 2. Modify remote config file on server
# 3. Reboot device
# 4. Verify "Configuration CHANGED" in /tmp/boot-config.log
# 5. Verify rebuild and reboot occurs
# 6. Verify new config applied
```

---

## File Reference

### Scripts
| File | Purpose |
|------|---------|
| `/opt/scripts/arm64-boot-config.sh` | Main boot config handler |
| `/etc/xdg/openbox/autostart` | Desktop session startup |
| `/opt/scripts/gui-app` | Browser launcher loop |
| `/opt/scripts/welcome` | Network config wizard |
| `/opt/scripts/wizard` | Device selection wizard |

### Configs
| File | Purpose |
|------|---------|
| `/opt/scripts/extras` | Device state persistence |
| `/opt/scripts/files/lcon` | Local config (known good) |
| `/tmp/config` | Wizard output (temporary) |
| `/boot/config.txt` | Pi boot configuration |
| `/boot/cmdline.txt` | Kernel command line |

### Logs
| File | Purpose |
|------|---------|
| `/tmp/boot-config.log` | Boot config script log |
| `/tmp/autostart.log` | Autostart debug log |

---

## Quick Reference

### The One Rule
**Every boot: Download config → Compare → If different: rebuild, burn, reboot**

### Key URLs (customize for your deployment)
- Config server: `http://cullerdigitalmedia.com/`
- Module server: `http://cullerdigitalmedia.com/tuxos/arm64/`

### Key Files
- Device state: `/opt/scripts/extras`
- Local config: `/opt/scripts/files/lcon`
- Boot script: `/opt/scripts/arm64-boot-config.sh`

---

## Document History

- **Created:** January 2026
- **Purpose:** Capture complete TuxOS ARM64 port architecture
- **Project:** loom-door (Moose Lodge door controller system)
- **Author:** Joel (Cornerstone Holdings) with Claude AI assistance
