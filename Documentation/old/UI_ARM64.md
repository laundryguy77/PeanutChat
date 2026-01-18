# TuxOS ARM64 Kiosk UI Flow Specification

**Version:** 1.1
**Date:** 2026-01-15
**Purpose:** Complete specification of the GTKDialog UI flow for TuxOS ARM64 Kiosk first-run setup (Raspberry Pi 4)

> **KEY DIFFERENCES FROM x86:** This ARM64 port has a SIGNIFICANTLY SIMPLIFIED first-run flow.
> The `first-run` script goes directly to `welcome` then `wizard`, without the `wizard-now`
> prompt or 30-second timeout. Network configuration is attempted inline after `welcome` completes.

---

## CRITICAL: Current State vs Goal State

### Boot Test Reality (2026-01-15)

**What Actually Happens:**

| Stage | Status | Issue |
|-------|--------|-------|
| Kernel boot | OK | DRM modules (vc4, v3d) load successfully |
| Network | FAILED | Script waits for `eth0` but kernel renames it to `end0` |
| X11/Openbox | OK | Desktop launches |
| Wallpaper (feh) | FAILED | `libldap-2.5.so.0` missing |
| GTK Themes | FAILED | Adwaita and hicolor themes missing |
| Wizard Page | WRONG | Shows **Page 7 (Confirmation)** instead of **Page 0 (Connection Choice)** |
| System Time | FAILED | Shows `01 Jan 1970 00:00` - RTC not set |

**Screenshot Evidence:**

```
boot_test1.webp: "Waiting for eth0... (1-10)" → "ERROR: eth0 not found!"
                  Available interfaces: end0  lo  wlan0

boot_test2.webp: DEBUG TERMINAL showing:
                  - feh: error libldap-2.5.so.0 not found
                  - WARNING: Could not find theme Adwaita
                  - WARNING: Could not find theme hicolor
                  - WARNING: Invalid theme index: -1

boot_test3.webp: Wizard shows "Confirmation" page (Page 7)
                  - Missing: Ethernet/WiFi selection buttons
                  - Date: 01 Jan 1970 00:00
```

### Goal State (ui1-5.webp)

**Expected Flow:**

| Screen | Title | Purpose |
|--------|-------|---------|
| ui1 | "TuxOS Wizard" | Connection type choice (Ethernet / Wifi buttons) |
| ui2 | "Connection Confirmation" | Shows `connection=wired` |
| ui3 | "TuxOS Wizard - Authorization Page" | Password entry |
| ui4 | "TuxOS Wizard" (Device Config) | Device Type/Facility/Device Number dropdowns |
| ui5 | "TuxOS Wizard" (Device Config) | Populated: Digital Signage / LAUNDROMAT / 1 |

### Gap Analysis

| Component | Current | Goal | Fix Required |
|-----------|---------|------|--------------|
| Network interface | eth0 (missing) | end0 | Add `net.ifnames=0` to cmdline.txt OR fix scripts |
| libldap | Missing | Present | Add `libldap-2.5-0` to 001-core.xzm |
| GTK themes | Missing | Present | Add `adwaita-icon-theme`, `hicolor-icon-theme` |
| Wizard start page | Page 7 | Page 0 | Fix `$TMP/.knetPage` initialization |
| System time | 1970 | Current | Add `fake-hwclock` or NTP earlier |
| Wallpaper | Black | Binary pattern | Fix feh dependency |

### Root Cause #1: eth0 → end0 Breaks Everything

The kernel's predictable network interface naming renames `eth0` to `end0`. This cascades:

```
FAILURE CASCADE:
───────────────────────────────────────────────────────────────────────
1. rc.S line 103-110:  Waits for eth0 → times out (10 seconds wasted)
2. rc.S line 124:      dhcpcd -b eth0 → fails silently
3. first-run line 49:  ifconfig eth0 up → fails
4. first-run line 52:  dhcpcd -q eth0 → fails
5. wizard line 109:    curl .../key.txt → no network → uses fallback
6. wizard line 210-212: curl .../dev.txt, fac.txt, num.txt → EMPTY DROPDOWNS
```

**Fix:** Add to `/boot/cmdline.txt`:
```
net.ifnames=0 biosdevname=0
```

### Root Cause #2: Wizard Page Display Issue

The wizard shows Page 7 (Confirmation) because either:
1. `$TMP/.knetPage` file doesn't exist or contains wrong value
2. The temp directory `/tmp/knet` has stale data
3. GTKDialog notebook widget fails to read page monitor file
4. Missing GTK themes cause rendering failure

**In `/opt/scripts/welcome` line 64:**
```bash
echo 0 > $TMP/.knetPage  # Should set page to 0
```

### Root Cause #3: Goal UI is DIFFERENT from Current Code

**Critical Finding:** The goal UI (ui1-5.webp) shows a **different, simpler wizard** than what's currently implemented.

| Aspect | Goal UI | Current Code |
|--------|---------|--------------|
| Title | "TuxOS Wizard" | "Porteus Kiosk Wizard" |
| Connection wizard | 2 simple pages | 8-page notebook |
| Proxy settings | Not shown | Page 5 |
| Browser choice | Not shown | Page 6 |
| Flow | Linear, simple | Complex notebook |

**Goal UI Flow (from screenshots):**
```
ui1: TuxOS Wizard
     - "Welcome to the TuxOS wizard. This wizard will assist you..."
     - Two large buttons: [Ethernet] [Wifi]
     - Buttons: [Restart] [Set keyboard layout] [Virtual keyboard] [Next]

ui2: Connection Confirmation
     - "Please confirm your choice of connection..."
     - Shows: "connection=wired"
     - Buttons: [Restart] [Virtual keyboard] [Next]

ui3: TuxOS Wizard - Authorization Page
     - "Please enter the password below..."
     - Entry field with default "000000000"
     - Button: [Install OS]

ui4-5: TuxOS Wizard (Device Config)
     - Device Type dropdown
     - Facility dropdown
     - Device Number dropdown
     - Block device table
     - Button: [Install OS]
```

**Current Code Flow:**
```
welcome script (8 pages):
  Page 0: Wired/Wireless choice
  Page 1: Dialup config
  Page 2: DHCP/Manual choice
  Page 3: Manual IP config
  Page 4: WiFi details
  Page 5: Proxy settings        ← Not in goal UI
  Page 6: Browser choice        ← Not in goal UI
  Page 7: Confirmation

wizard script (2 dialogs):
  Dialog 1: Authorization
  Dialog 2: Device Config
```

**The goal requires either:**
1. A NEW simplified `welcome` script matching the goal UI
2. OR significant modifications to the existing 8-page wizard

---

## Table of Contents

1. [Overview](#1-overview)
2. [File Inventory](#2-file-inventory)
3. [Boot Sequence to UI](#3-boot-sequence-to-ui)
4. [Complete UI Flow Diagram](#4-complete-ui-flow-diagram)
5. [Phase 1: Autostart Initialization](#5-phase-1-autostart-initialization)
6. [Phase 2: First-Run Script](#6-phase-2-first-run-script)
7. [Phase 3: Network Wizard (welcome)](#7-phase-3-network-wizard-welcome)
8. [Phase 4: TuxOS Authorization (wizard)](#8-phase-4-tuxos-authorization-wizard)
9. [Phase 5: Device Configuration Dialog](#9-phase-5-device-configuration-dialog)
10. [Remote Files Reference](#10-remote-files-reference)
11. [Configuration Output Format](#11-configuration-output-format)
12. [GTKDialog Function Library](#12-gtkdialog-function-library)
13. [Key Differences from x86](#13-key-differences-from-x86)

---

## 1. Overview

The TuxOS ARM64 Kiosk setup process guides users through network configuration and device provisioning on Raspberry Pi 4 hardware. The flow uses GTKDialog-based UI screens to collect configuration data and write a configuration file that determines the kiosk's behavior.

### High-Level Flow Summary (ARM64)

```
BOOT → RPi Bootloader → kernel8.img → initrd.img (init)
                                           │
                                           ▼
                                    switch_root → /sbin/init
                                           │
                                           ▼
                                      inittab (runlevel 4)
                                           │
                                           ▼
                                    rc.S → rc.M → rc.4
                                           │
                                           ▼
                              xinit → openbox → autostart
                                           │
                                           ▼
                              ┌──────────────────────────┐
                              │  first-run               │  DIRECT CALL (no wizard-now)
                              └────────────┬─────────────┘
                                           │
                                           ▼
                              ┌──────────────────────────┐
                              │  welcome                 │  Network wizard (8 pages)
                              │  (GTKDialog Notebook)    │  Wired/Wireless/DHCP/Manual
                              └────────────┬─────────────┘
                                           │
                                           ▼
                              ┌──────────────────────────┐
                              │  INLINE NETWORK CONFIG   │  first-run applies DHCP/WiFi
                              └────────────┬─────────────┘
                                           │
                                           ▼
                              ┌──────────────────────────┐
                              │  wizard                  │  Authorization + Device Config
                              │  (2 GTKDialog Screens)   │  Password then dropdowns
                              └────────────┬─────────────┘
                                           │
                                           ▼
                              ┌──────────────────────────┐
                              │  /tmp/config             │  Saved to lcon
                              │  /opt/scripts/files/lcon │
                              └──────────────────────────┘
```

---

## 2. File Inventory

### XZM Module Structure

The system is packaged in SquashFS modules:

| Module | Size | Contents |
|--------|------|----------|
| `000-kernel.xzm` | 19MB | Kernel modules |
| `001-core.xzm` | 115MB | Core system (Debian ARM64 base) |
| `003-settings.xzm` | 1.8MB | Kiosk scripts, wizard, icons |
| `08-ssh.xzm` | 389KB | SSH server (optional) |
| `firmware.xzm` | 373KB | Broadcom WiFi firmware |

### Core Scripts (Execution Order)

| Order | File | Location (in 003-settings.xzm) | Purpose |
|-------|------|--------------------------------|---------|
| 1 | `init` | `/boot/initrd.img` → `init` | Initial boot, AUFS setup |
| 2 | `rc.S` | `/etc/rc.d/rc.S` | System init (mount, udev, GPU) |
| 3 | `rc.M` | `/etc/rc.d/rc.M` | Multi-user init (dbus, network) |
| 4 | `rc.4` | `/etc/rc.d/rc.4` | GUI init (xinit, openbox) |
| 5 | `autostart` | `/etc/xdg/openbox/autostart` | Desktop session, launches first-run |
| 6 | `first-run` | `/opt/scripts/first-run` | Orchestrates wizard flow |
| 7 | `welcome` | `/opt/scripts/welcome` | Network wizard (8 pages) |
| 8 | `wizard` | `/opt/scripts/wizard` | TuxOS auth + device config |

### Support Files

| File | Location | Purpose |
|------|----------|---------|
| `wizard-functions` | `/opt/scripts/files/wizard/wizard-functions` | GTKDialog helper functions |
| `lcon.default` | `/opt/scripts/files/lcon.default` | Default configuration template |
| `keyboards.txt` | `/opt/scripts/files/wizard/keyboards.txt` | Keyboard layout options |
| `timezones.txt` | `/opt/scripts/files/wizard/timezones.txt` | Timezone options |
| `license-GoogleChrome.txt` | `/opt/scripts/files/wizard/license-GoogleChrome.txt` | Chrome EULA |

### Remote Files (Downloaded at Runtime)

| File | URL | Purpose |
|------|-----|---------|
| `key.txt` | `https://cullerdigitalmedia.com/files/key.txt` | Authorization password |
| `clients.txt` | `https://cullerdigitalmedia.com/files/clients.txt` | Client list |
| `dev.txt` | `https://cullerdigitalmedia.com/files/dev.txt` | Device type dropdown options |
| `fac.txt` | `https://cullerdigitalmedia.com/files/fac.txt` | Facility dropdown options |
| `num.txt` | `https://cullerdigitalmedia.com/files/num.txt` | Device number dropdown options |

### Temporary Files (Runtime)

| File | Purpose |
|------|---------|
| `/tmp/config` | Final wizard output, becomes `/opt/scripts/files/lcon` |
| `/tmp/report` | Network wizard summary report |
| `/tmp/knet/*` | Network wizard temporary files |
| `/tmp/kwiz.$$/*` | TuxOS wizard temporary files |

---

## 3. Boot Sequence to UI

### 3.1 Raspberry Pi Boot Chain

```
RPi 4 Boot ROM (SoC)
         │
         ▼
    bootcode.bin (SD card)
         │
         ▼
    start4.elf (GPU firmware)
         │
         ├── Reads config.txt
         ├── Loads kernel8.img to RAM
         ├── Loads initrd.img
         └── Loads bcm2711-rpi-4-b.dtb
                │
                ▼
         kernel8.img (Linux 6.x ARM64)
                │
                └── initrd.img uncompressed to /
                        │
                        ▼
                   /init (initramfs init script)
```

### 3.2 Initramfs Init Script

**File:** `initrd.img` → `/init`
**Lines:** 171

The init script performs:

```
1. Install busybox applets
2. Mount /proc, /sys, /dev
3. Create /dev/shm with 1777 permissions
4. Search for boot media:
   - Scan for partition with LABEL containing "Kiosk"
   - Support iso9660, vfat, ext4 filesystems
   - Check for docs/kiosk.sgn signature file
5. Mount tmpfs on /memory (75% of RAM)
6. Create AUFS directories:
   /memory/xino
   /memory/changes
   /memory/images
   /memory/copy2ram
7. GPU initialization (ARM64 specific):
   - Detect BCM2711/BCM2712 via /proc/cpuinfo
   - Load vc4 DRM driver
   - Wait for /dev/fb0
   - Display boot splash (fbi)
8. Copy XZM modules to RAM
9. Mount each XZM as SquashFS
10. Add each to AUFS union overlay
11. exec /sbin/switch_root /union /sbin/init
```

### 3.3 Union Root Init (inittab)

**File:** `/etc/inittab`

```
id:4:initdefault:
si::sysinit:/etc/rc.d/rc.S
rc:2345:wait:/etc/rc.d/rc.M
l0:0:wait:/etc/rc.d/rc.0
l6:6:wait:/etc/rc.d/rc.6
x1:4:respawn:/etc/rc.d/rc.4
```

| Runlevel | Action | Script |
|----------|--------|--------|
| sysinit | System initialization | rc.S |
| 2-5 | Multi-user mode | rc.M |
| 4 | GUI mode (respawn) | rc.4 |
| 0 | Shutdown | rc.0 |
| 6 | Reboot | rc.6 |

### 3.4 rc.S - System Initialization

**File:** `/etc/rc.d/rc.S`
**Lines:** 138

Key operations:

```bash
# Virtual filesystems
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev
mkdir -p /dev/pts /dev/shm
mount -t devpts devpts /dev/pts
mount -t tmpfs tmpfs /dev/shm -o mode=1777

# Temp directories
mkdir -p /tmp /run
mount -t tmpfs tmpfs /tmp -o mode=1777
mount -t tmpfs tmpfs /run -o mode=755

# Start udev (ARM64 uses systemd-udevd)
/lib/systemd/systemd-udevd --daemon
udevadm trigger --action=add
udevadm settle --timeout=10

# GPU kernel modules (ARM64 specific)
modprobe drm
modprobe drm_kms_helper
modprobe vc4
modprobe v3d

# Network setup
# Wait for eth0 (up to 10 seconds)
# Start DHCP on eth0

# Library cache
ldconfig
```

### 3.5 rc.M - Multi-User Init

**File:** `/etc/rc.d/rc.M`
**Lines:** 73

Key operations:

```bash
# Hostname
hostname kiosk

# Timezone (if configured)
ln -sf /usr/share/zoneinfo/$tz /etc/localtime

# Start services
/usr/sbin/crond &
/usr/sbin/rsyslogd &

# D-Bus
/usr/bin/dbus-uuidgen --ensure=/etc/machine-id
/usr/bin/dbus-daemon --system &

# Network
sh /etc/rc.d/rc.inet1 &
ifconfig lo 127.0.0.1

# Firewall
/etc/rc.d/rc.FireWall

# ACPI (power button)
/usr/sbin/acpid -n &
```

### 3.6 rc.4 - GUI Initialization

**File:** `/etc/rc.d/rc.4`
**Lines:** 144

Key operations:

```bash
# Set up environment
export HOME=/root
export USER=root

# Start D-Bus system daemon
dbus-daemon --system

# Create xinitrc
cat > /tmp/.xinitrc << 'XINIT'
    # Set library path
    export LD_LIBRARY_PATH=/usr/lib/aarch64-linux-gnu:/lib/aarch64-linux-gnu:/usr/lib:/lib
    ldconfig

    # Start D-Bus session
    eval $(dbus-launch --sh-syntax)

    # Set background
    xsetroot -solid "#404040"

    # Start openbox
    /usr/bin/openbox &

    # Run autostart
    /etc/xdg/openbox/autostart &

    wait
XINIT

# Start X server
xinit /tmp/.xinitrc -- /usr/lib/xorg/Xorg :0 vt1 -nolisten tcp
```

---

## 4. Complete UI Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AUTOSTART                                       │
│  /etc/xdg/openbox/autostart                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Set wallpaper with feh                                                  │
│  2. Start D-Bus session                                                     │
│  3. Start dunst notification daemon                                         │
│  4. Disable DPMS screen blanking                                            │
│  5. Launch first-run wizard (unconditional)                                 │
│  6. Wait for network (60s timeout)                                          │
│  7. NTP time sync                                                           │
│  8. Apply configuration from lcon                                           │
│  9. Run local_net.d hooks (daemon.sh)                                       │
│  10. Launch browser with homepage                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FIRST-RUN                                       │
│  /opt/scripts/first-run (105 lines)                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  SIMPLIFIED FLOW (compared to x86):                                         │
│  ═══════════════════════════════════════════════════════════════════════════│
│  1. Launch welcome (network wizard) - DIRECT CALL, no wizard-now prompt     │
│  2. Check if /tmp/config was created                                        │
│  3. Apply network config inline:                                            │
│     • If dhcp=yes + wired: dhcpcd -q $iface                                 │
│     • If dhcp=yes + wifi: wpa_supplicant + dhcpcd                           │
│  4. Wait 3 seconds for network                                              │
│  5. Launch wizard (TuxOS authorization)                                     │
│  6. Save /tmp/config to /opt/scripts/files/lcon                             │
│                                                                             │
│  NO wizard-now timeout dialog                                               │
│  NO conditional first-run check                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WELCOME (Network Wizard)                        │
│  /opt/scripts/welcome (640 lines)                                           │
│  8-Page GTKDialog Notebook (600×510 pixels)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PAGE 0: CONNECTION TYPE CHOICE                                             │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Title: "Porteus Kiosk Wizard"                                        │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Text: "Welcome to the Porteus Kiosk setup wizard..."                 │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │  ┌─────────────┐  ┌─────────────┐                                    │  │
│  │  │   [icon]    │  │   [icon]    │                                    │  │
│  │  │   WIRED     │  │  WIRELESS   │  (No dialup option shown)          │  │
│  │  │  160×160    │  │   160×160   │                                    │  │
│  │  │ wired-160   │  │ wifi-160    │                                    │  │
│  │  └─────────────┘  └─────────────┘                                    │  │
│  │                                                                       │  │
│  │  ACTIONS:                                                             │  │
│  │  • Wired:    echo "connection=wired" > $TMP/connection.tmp            │  │
│  │              Go to Page 2 (DHCP/Manual choice)                        │  │
│  │  • Wireless: echo "connection=wifi" > $TMP/connection.tmp             │  │
│  │              Start WiFi scan (get_essid &)                            │  │
│  │              Go to Page 2 (DHCP/Manual choice)                        │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  PAGE 1: DIALUP CONFIGURATION (present but not shown in main flow)          │
│  ═══════════════════════════════════════════════════════════════════════════│
│  Phone number, Username, Password fields                                    │
│                                                                             │
│  PAGE 2: DHCP OR MANUAL CHOICE                                              │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Title: "Network Configuration Type"                                  │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │  ┌─────────────────────┐      ┌─────────────────────┐                │  │
│  │  │       [icon]        │      │       [icon]        │                │  │
│  │  │        DHCP         │      │       MANUAL        │                │  │
│  │  │    internet-160     │      │ network-config-160  │                │  │
│  │  └─────────────────────┘      └─────────────────────┘                │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  [Dropdown: Wired authentication]                                     │  │
│  │     • No authentication (default)                                     │  │
│  │     • EAP over LAN (802.1x)                                          │  │
│  │  Username: [____________] (if 802.1x)                                 │  │
│  │  Password: [____________] (if 802.1x)                                 │  │
│  │                                                                       │  │
│  │  ACTIONS:                                                             │  │
│  │  • DHCP + Wired:    → Page 5 (Proxy)                                 │  │
│  │  • DHCP + Wireless: → Page 4 (WiFi details)                          │  │
│  │  • Manual:          → Page 3 (Manual IP)                             │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  PAGE 3: MANUAL IP CONFIGURATION                                            │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Interface:    [▼ eth0 / wlan0 ]                                     │  │
│  │  IP Address:   [ 192.168.1.2   ]                                     │  │
│  │  Network Mask: [ 255.255.255.0 ]                                     │  │
│  │  Gateway:      [ 192.168.1.1   ]                                     │  │
│  │  DNS Server 1: [ 8.8.8.8       ]                                     │  │
│  │  DNS Server 2: [ 208.67.222.222]                                     │  │
│  │                                                                       │  │
│  │  NEXT: Wired → Page 5, Wireless → Page 4                             │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  PAGE 4: WIRELESS CONNECTION DETAILS                                        │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Title: "Wireless Connection Details"                                 │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  SSID: [▼ scanned networks ]  (auto-refreshing)                      │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  [▶ Enter hidden access point]  (expander)                           │  │
│  │     Hidden SSID: [________________]                                   │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Encryption type: [▼ dropdown ]                                       │  │
│  │     • Open network (default)                                          │  │
│  │     • WEP                                                             │  │
│  │     • WPA/WPA2 Personal                                               │  │
│  │     • WPA/WPA2 Enterprise (PEAP)                                      │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Username:     [____________] (if PEAP)                               │  │
│  │  Password/Key: [____________] (if encrypted)                          │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  MAC address: XX:XX:XX:XX:XX:XX (display)                             │  │
│  │                                                                       │  │
│  │  NEXT: → Page 5 (Proxy)                                               │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  PAGE 5: PROXY SETTINGS                                                     │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  1. Click Next if not using proxy                                     │  │
│  │  2. Manual: [user:pass@ip:port]                                       │  │
│  │     Proxy exceptions: (○) No  (○) Yes → [exception list]             │  │
│  │  3. Automatic: PAC URL [http://...]                                   │  │
│  │                                                                       │  │
│  │  NEXT: → Page 6 (Browser choice)                                      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  PAGE 6: BROWSER CHOICE                                                     │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Title: "Browser choice"                                              │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │  ┌─────────────────────┐      ┌─────────────────────┐                │  │
│  │  │       [icon]        │      │       [icon]        │                │  │
│  │  │      FIREFOX        │      │       CHROME        │                │  │
│  │  │    firefox-160      │      │     chrome-160      │                │  │
│  │  └─────────────────────┘      └─────────────────────┘                │  │
│  │                                                                       │  │
│  │  Firefox: echo "browser=firefox" → Page 7                             │  │
│  │  Chrome:  Show EULA → echo "browser=chrome" → Page 7                  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  PAGE 7: CONFIRMATION                                                       │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Title: "Confirmation"                                                │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │  YOUR FINAL REPORT:                                             │  │  │
│  │  │  connection=wifi                                                │  │  │
│  │  │  dhcp=yes                                                       │  │  │
│  │  │  ssid_name=MyNetwork                                            │  │  │
│  │  │  browser=firefox                                                │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Current date/time: 15 Jan 2026 09:30                                 │  │
│  │                                                                       │  │
│  │  [Next] → EXIT:finished                                               │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  BOTTOM BUTTONS:                                                            │
│  ═══════════════════════════════════════════════════════════════════════════│
│  [Restart] [Set keyboard layout] [Virtual keyboard] [Set time] [Next]      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │  /tmp/config created
                                      │  cp -a /tmp/report /tmp/config
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FIRST-RUN (Network Apply)                       │
│  /opt/scripts/first-run (lines 44-73)                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  INLINE NETWORK CONFIGURATION:                                              │
│  ═══════════════════════════════════════════════════════════════════════════│
│  if dhcp=yes && connection=wired:                                           │
│      iface=$(ip link show | grep "eth|enp|eno")                             │
│      ifconfig $iface up                                                     │
│      dhcpcd -q $iface &                                                     │
│                                                                             │
│  if dhcp=yes && connection=wifi:                                            │
│      iface=$(iwconfig | grep -v "no wireless")                              │
│      ssid=$(grep ssid_name /tmp/config)                                     │
│      pass=$(grep wpa_password /tmp/config)                                  │
│      wpa_passphrase $ssid $pass > /tmp/wpa.conf                             │
│      wpa_supplicant -B -i $iface -c /tmp/wpa.conf                           │
│      sleep 2                                                                │
│      dhcpcd -q $iface &                                                     │
│                                                                             │
│  sleep 3  # Wait for network                                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WIZARD (TuxOS Authorization)                    │
│  /opt/scripts/wizard (306 lines)                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  INITIALIZATION:                                                            │
│  ═══════════════════════════════════════════════════════════════════════════│
│  PCID=$(grep ^ID: /etc/version | cut -d" " -f2)                             │
│  TMPDIR=/tmp/kwiz.$$                                                        │
│  mkdir -p $TMPDIR                                                           │
│  sleep 5  # Wait for network to stabilize                                   │
│                                                                             │
│  # Download authorization key                                               │
│  curl cullerdigitalmedia.com/files/key.txt >> $TMPDIR/drivekey.txt          │
│  # Fallback: echo P@ss3264 > $TMPDIR/drivekey.txt                           │
│                                                                             │
│  # Download client list                                                     │
│  curl cullerdigitalmedia.com/files/clients.txt >> /tmp/clients.txt          │
│  # Fallback: echo laundromat >> /tmp/clients.txt                            │
│                                                                             │
│  # Generate block device list                                               │
│  lsblk -o NAME,TYPE,MODEL,SIZE | egrep -v 'NAME|loop|part|rom' > block.txt  │
│                                                                             │
│  AUTHORIZATION DIALOG (WIZARD_MAIN):                                        │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Window: "TuxOS Wizard" (580×480 pixels)                              │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │  TuxOS Wizard - Authorization Page                                    │  │
│  │  (Note: Typo "Authoization" in actual code)                           │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │  Please enter the password below to proceed with the                  │  │
│  │  setup of this device.                                                │  │
│  │                                                                       │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │  Enter Password:  [ 000000000________________________ ]               │  │
│  │                                                                       │  │
│  │                    [ Install OS ]                                     │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  PASSWORD VALIDATION LOOP:                                                  │
│  ═══════════════════════════════════════════════════════════════════════════│
│  DRIVEKEY=$(cat $TMPDIR/drivekey.txt)  # Expected: "P@ss3264"               │
│  CID=0                                                                      │
│                                                                             │
│  while [ "$CID" != "$DRIVEKEY" ]; do                                        │
│      # Show WIZARD_MAIN dialog                                              │
│      gtkdialog -i wizard-functions -s -c                                    │
│      # Read user input                                                      │
│      CID=$(cat $TMPDIR/configuration.id)                                    │
│      # Loop until match                                                     │
│  done                                                                       │
│                                                                             │
│  EXPECTED PASSWORD: P@ss3264                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │  Password matches
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WIZARD (Device Configuration)                   │
│  /opt/scripts/wizard - DIALOG variable (lines 138-205)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  REMOTE FILE DOWNLOADS:                                                     │
│  ═══════════════════════════════════════════════════════════════════════════│
│  curl cullerdigitalmedia.com/files/num.txt >> /tmp/num.txt                  │
│  curl cullerdigitalmedia.com/files/dev.txt >> /tmp/dev.txt                  │
│  curl cullerdigitalmedia.com/files/fac.txt >> /tmp/fac.txt                  │
│                                                                             │
│  DEVICE CONFIGURATION DIALOG:                                               │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Window: "TuxOS Wizard" (580×500 pixels)                              │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │  Device Type:    [▼ dropdown from dev.txt ]                           │  │
│  │                     • Education                                       │  │
│  │                     • Kiosk                                           │  │
│  │                     • ActivityPro                                     │  │
│  │                     • Medcart                                         │  │
│  │                     • Treatment                                       │  │
│  │                     • NurseStation                                    │  │
│  │                     • Bedboard                                        │  │
│  │                     • Resident Room                                   │  │
│  │                     • Digital Signage                                 │  │
│  │                                                                       │  │
│  │  Facility:       [▼ dropdown from fac.txt ]                           │  │
│  │                                                                       │  │
│  │  Device Number:  [▼ dropdown from num.txt ]                           │  │
│  │                                                                       │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │  Please choose the target device (must have at least                  │  │
│  │  1 GB size) to which you will be installing the kiosk.                │  │
│  │                                                                       │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │ NAME       │ TYPE   │ MODEL                    │ SIZE          │  │  │
│  │  ├─────────────────────────────────────────────────────────────────┤  │  │
│  │  │ mmcblk0    │ disk   │ SD_Card                  │ 32G           │  │  │
│  │  │ sda        │ disk   │ USB_Flash                │ 16G           │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                       │  │
│  │                    [ Install OS ]                                     │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  CONFIG URL CONSTRUCTION:                                                   │
│  ═══════════════════════════════════════════════════════════════════════════│
│  BASEURL='http://cullerdigitalmedia.com/'                                   │
│                                                                             │
│  Device Type        │ URL Pattern                                           │
│  ──────────────────────────────────────────────────────────────────────────│
│  Education          │ {base}kc/{facility}_ed.txt                            │
│  Kiosk              │ {base}kc/{facility}/{facility}_ks{num}.txt            │
│  ActivityPro        │ {base}activitypro/{facility}.txt                      │
│  Medcart            │ {base}kc/{facility}/{facility}_mc{num}.txt            │
│  Treatment          │ {base}kc/{facility}/{facility}_tc{num}.txt            │
│  NurseStation       │ {base}kc/{facility}/{facility}_ns{num}.txt            │
│  Bedboard           │ {base}kc/{facility}/{facility}_stats.txt              │
│  Resident Room      │ {base}kc/{facility}/{facility}_rr{num}.txt            │
│  Digital Signage    │ {base}signage/{facility}/{facility}_ds{num}.txt       │
│                                                                             │
│  OUTPUT TO /tmp/config:                                                     │
│  ═══════════════════════════════════════════════════════════════════════════│
│  echo burn_dev=$tblTarget >> /tmp/config                                    │
│  echo kiosk_config=$FINCONFIG >> /tmp/config                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FIRST-RUN (Save Config)                         │
│  /opt/scripts/first-run (lines 89-104)                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  mkdir -p /opt/scripts/files                                                │
│  cp /tmp/config /opt/scripts/files/lcon                                     │
│  log "Configuration saved to /opt/scripts/files/lcon"                       │
│  log "First-run setup complete"                                             │
│  exit 0                                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AUTOSTART (Continue)                            │
│  /etc/xdg/openbox/autostart (lines 53-135)                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Wait for network (60s timeout)                                          │
│  2. NTP sync                                                                │
│  3. Apply configuration via /opt/scripts/apply-config                       │
│  4. Run hooks from /etc/rc.d/local_net.d/ (includes daemon.sh)              │
│  5. Launch browser (firefox or chromium) with homepage                      │
│  6. Keep session alive (infinite loop)                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Phase 1: Autostart Initialization

### File: `/etc/xdg/openbox/autostart`
### Lines: 136

### Key Operations

```bash
#!/bin/sh
LCON="/opt/scripts/files/lcon"
LOG_FILE="/tmp/autostart.log"

# Display Setup
feh --bg-scale /usr/share/wallpapers/default.jpg &
eval $(dbus-launch --sh-syntax)
dunst &
xset -dpms; xset s off; xset s noblank

# First-run wizard (UNCONDITIONAL in ARM64)
if [ -e /opt/scripts/first-run ]; then
    /opt/scripts/first-run
fi

# Wait for network (60s timeout)
GTW=0; SLEEP=60
while [ $GTW -lt 1 ] && [ $SLEEP -gt 0 ]; do
    GTW=$(route -n | grep -c " UG ")
    [ $GTW -lt 1 ] && { sleep 1; SLEEP=$((SLEEP - 1)); }
done

# NTP sync
ntpdate -s pool.ntp.org &

# Apply configuration
[ -f "$LCON" ] && /opt/scripts/apply-config "$LCON"

# Run hooks (daemon.sh)
for script in /etc/rc.d/local_net.d/*; do
    [ -x "$script" ] && . "$script" &
done

# Launch browser
HOMEPAGE="about:blank"
BROWSER="firefox"
[ -f "$LCON" ] && {
    hp=$(grep "^homepage=" "$LCON" | cut -d= -f2-)
    br=$(grep "^browser=" "$LCON" | cut -d= -f2-)
    [ -n "$hp" ] && HOMEPAGE="$hp"
    [ -n "$br" ] && BROWSER="$br"
}

case "$BROWSER" in
    chrome|chromium)
        chromium --kiosk --no-first-run "$HOMEPAGE" &
        ;;
    firefox)
        firefox --kiosk "$HOMEPAGE" &
        ;;
esac

# Keep session alive
while true; do sleep 60; done
```

### Important Note

The ARM64 version calls `first-run` **unconditionally** from autostart. There is no check for existing configuration before launching the wizard. This is a key difference from x86.

---

## 6. Phase 2: First-Run Script

### File: `/opt/scripts/first-run`
### Lines: 105

### Purpose
Orchestrate the simplified wizard flow without the wizard-now timeout prompt.

### Script Flow

```bash
#!/bin/bash
SCRIPT_DIR=/opt/scripts
CONFIG_DIR="${SCRIPT_DIR}/files"
LOCAL_CONFIG="${CONFIG_DIR}/lcon"

# Step 1: Launch welcome (network wizard) - DIRECT, no wizard-now
"${SCRIPT_DIR}/welcome"

# Check config created
[ ! -f /tmp/config ] && exit 1

# Step 2: Apply network config inline
if grep -q "^dhcp=yes" /tmp/config; then
    if grep -q "^connection=wired" /tmp/config; then
        iface=$(ip link show | grep -E "eth|enp|eno" | head -1 | cut -d: -f2 | tr -d ' ')
        [ -n "$iface" ] && { ifconfig "$iface" up; dhcpcd -q "$iface" & }
    elif grep -q "^connection=wifi" /tmp/config; then
        iface=$(iwconfig 2>/dev/null | grep -v "no wireless" | head -n1 | cut -d" " -f1)
        ssid=$(grep "^ssid_name=" /tmp/config | cut -d= -f2-)
        pass=$(grep "^wpa_password=" /tmp/config | cut -d= -f2-)
        [ -n "$ssid" ] && [ -n "$pass" ] && {
            wpa_passphrase "$ssid" "$pass" > /tmp/wpa.conf
            wpa_supplicant -B -i "$iface" -c /tmp/wpa.conf
            sleep 2
            dhcpcd -q "$iface" &
        }
    fi
fi
sleep 3

# Step 3: Launch wizard (TuxOS authorization)
"${SCRIPT_DIR}/wizard"

# Step 4: Save config
mkdir -p "$CONFIG_DIR"
cp /tmp/config "$LOCAL_CONFIG"

exit 0
```

### Key Differences from x86

| Feature | x86 | ARM64 |
|---------|-----|-------|
| wizard-now prompt | Yes (30s timeout) | **No** |
| Network wait before wizard | No (correct) | No |
| Inline network apply | After all wizards | **Between welcome and wizard** |
| Config existence check | Yes | **No** |

---

## 7. Phase 3: Network Wizard (welcome)

### File: `/opt/scripts/welcome`
### Lines: 640

### Variables

```bash
export TMP=/tmp/knet
export CONF=/tmp/config
export REPORT=/tmp/report
ICONS=/usr/share/pixmaps
WINWIDTH=600
WINHEIGHT=510
```

### Page Navigation

| Page | Name | Purpose |
|------|------|---------|
| 0 | Connection Type | Wired or Wireless choice |
| 1 | Dialup Config | Phone, user, pass (rarely used) |
| 2 | DHCP/Manual | Auto or manual network config |
| 3 | Manual IP | IP, mask, gateway, DNS |
| 4 | Wireless Details | SSID, encryption, password |
| 5 | Proxy Settings | Manual or PAC proxy config |
| 6 | Browser Choice | Firefox or Chrome |
| 7 | Confirmation | Final report display |

### GTKDialog Structure

```xml
<window title="Kiosk Wizard" width-request="600" height-request="510">
<vbox>
  <notebook page="0" show-tabs="false" labels="connection|dialup|config|manual|wificonfig|proxy|browser|confirm">
    <!-- PAGE 0 --> ... connection choice ...
    <!-- PAGE 1 --> ... dialup config ...
    <!-- PAGE 2 --> ... dhcp/manual choice ...
    <!-- PAGE 3 --> ... manual ip config ...
    <!-- PAGE 4 --> ... wifi details ...
    <!-- PAGE 5 --> ... proxy settings ...
    <!-- PAGE 6 --> ... browser choice ...
    <!-- PAGE 7 --> ... confirmation ...
  </notebook>
  <hbox>
    <!-- Navigation buttons -->
    [Restart] [Set keyboard layout] [Virtual keyboard] [Set time] [Re-scan wifi] [Next]
  </hbox>
</vbox>
</window>
```

### Output Variables by Page

**Page 0 (Connection):**
```
connection=wired   OR   connection=wifi
```

**Page 2 (DHCP/Manual):**
```
dhcp=yes
wired_authentication=eapol  (if 802.1x)
eapol_username=xxx
eapol_password=xxx
```

**Page 3 (Manual):**
```
network_interface=eth0
ip_address=192.168.1.2
netmask=255.255.255.0
default_gateway=192.168.1.1
dns_server=8.8.8.8 208.67.222.222
```

**Page 4 (Wireless):**
```
ssid_name=NetworkName
hidden_ssid_name=HiddenNetwork  (if hidden)
wifi_encryption=wpa             (wep|wpa|eap-peap)
wpa_password=xxx                (or wep_key, peap_password)
peap_username=xxx               (if PEAP)
```

**Page 5 (Proxy):**
```
proxy=user:pass@ip:port
proxy_exceptions=127.0.0.1 domain.local
proxy_config=http://domain.com/proxy.pac
```

**Page 6 (Browser):**
```
browser=firefox   OR   browser=chrome
```

### Final Output

When user clicks "Next" on Page 7:
```bash
cp -a /tmp/report /tmp/config
cleanup  # Remove temp files and exit
```

---

## 8. Phase 4: TuxOS Authorization (wizard)

### File: `/opt/scripts/wizard`
### Lines: 306

### Initialization

```bash
PCID=$(grep ^ID: /etc/version | cut -d" " -f2)
TMPDIR=/tmp/kwiz.$$
mkdir -p $TMPDIR
sleep 5  # Wait for network

# Download key (with fallback)
curl cullerdigitalmedia.com/files/key.txt >> $TMPDIR/drivekey.txt || \
    echo P@ss3264 > $TMPDIR/drivekey.txt

# Download clients (with fallback)
curl cullerdigitalmedia.com/files/clients.txt >> /tmp/clients.txt || \
    echo laundromat >> /tmp/clients.txt

# Get drive key
DRIVEKEY=$(cat $TMPDIR/drivekey.txt)

# Generate block device list
lsblk -o NAME,TYPE,MODEL,SIZE | egrep -v 'NAME|loop|part|rom' | \
    tr -s ' ' | sed ... > $TMPDIR/block.txt
```

### Authorization Dialog (WIZARD_MAIN)

```xml
<window title="TuxOS Wizard" width-request="580" height-request="480">
<vbox margin="10">
    <text>"TuxOS Wizard - Authorization Page"</text>
    <text>Please enter the password below...</text>

    <hbox>
        <text>Enter Password:</text>
        <entry>
            <variable>CID</variable>
            <default>000000000</default>
            <action signal="changed">echo $CID > $TMPDIR/configuration.id</action>
        </entry>
    </hbox>

    <button>
        <label>Install OS</label>
        <action function="exit">finished</action>
    </button>
</vbox>
</window>
```

### Password Validation Loop

```bash
CID=0
DRIVEKEY=$(cat $TMPDIR/drivekey.txt)  # "P@ss3264"

while [ "$CID" != "$DRIVEKEY" ]; do
    rm "$TMPDIR"/configuration.id
    touch "$TMPDIR"/configuration.id

    echo "$WIZARD_MAIN" | gtkdialog -i wizard-functions -s -c

    CID=$(cat $TMPDIR/configuration.id)

    if [ "$CID" = "$DRIVEKEY" ]; then
        # Show device config dialog
        ...
    else
        echo "failed"
        # Loop continues
    fi
done
```

---

## 9. Phase 5: Device Configuration Dialog

### File: `/opt/scripts/wizard` (DIALOG variable)

### Remote File Downloads

After password verified:
```bash
touch /tmp/fac.txt /tmp/dev.txt /tmp/num.txt
curl cullerdigitalmedia.com/files/num.txt >> /tmp/num.txt
curl cullerdigitalmedia.com/files/dev.txt >> /tmp/dev.txt
curl cullerdigitalmedia.com/files/fac.txt >> /tmp/fac.txt
```

### Dialog Definition

```xml
<window title="TuxOS Wizard" width-request="580" height-request="500">
<vbox>
    <hbox>
        <text>Device Type:</text>
        <comboboxentry>
            <variable>DEVTYPE</variable>
            <input>cat /tmp/dev.txt</input>
        </comboboxentry>
    </hbox>

    <hbox>
        <text>Facility:</text>
        <comboboxentry>
            <variable>FACNAM</variable>
            <input>cat /tmp/fac.txt</input>
        </comboboxentry>
    </hbox>

    <hbox>
        <text>Device Number:</text>
        <comboboxentry>
            <variable>DEVNUM</variable>
            <input>cat /tmp/num.txt</input>
        </comboboxentry>
    </hbox>

    <text>Please choose the target device...</text>

    <table>
        <variable>tblTarget</variable>
        <label>"NAME|TYPE|MODEL|SIZE"</label>
        <input file>$TMPDIR/block.txt</input>
        <action>echo burn_dev=$tblTarget >> /tmp/config</action>
    </table>

    <button>
        <label>Install OS</label>
        <action>echo burn_dev=$tblTarget >> /tmp/config</action>
        <action function="exit">finished</action>
    </button>
</vbox>
</window>
```

### Config URL Construction

```bash
BASEURL='http://cullerdigitalmedia.com/'

case $DEVTYPE in
    Education)
        FINCONFIG="${BASEURL}kc/${FACNAM,,}_ed.txt"
        ;;
    Kiosk)
        FINCONFIG="${BASEURL}kc/${FACNAM,,}/${FACNAM,,}_ks${DEVNUM}.txt"
        ;;
    ActivityPro)
        FINCONFIG="${BASEURL}activitypro/${FACNAM,,}.txt"
        ;;
    Medcart)
        FINCONFIG="${BASEURL}kc/${FACNAM,,}/${FACNAM,,}_mc${DEVNUM}.txt"
        ;;
    Treatment)
        FINCONFIG="${BASEURL}kc/${FACNAM,,}/${FACNAM,,}_tc${DEVNUM}.txt"
        ;;
    NurseStation)
        FINCONFIG="${BASEURL}kc/${FACNAM,,}/${FACNAM,,}_ns${DEVNUM}.txt"
        ;;
    Bedboard)
        FINCONFIG="${BASEURL}kc/${FACNAM,,}/${FACNAM,,}_stats.txt"
        ;;
    "Resident Room")
        FINCONFIG="${BASEURL}kc/${FACNAM,,}/${FACNAM,,}_rr${DEVNUM}.txt"
        ;;
    "Digital Signage")
        FINCONFIG="${BASEURL}signage/${FACNAM,,}/${FACNAM,,}_ds${DEVNUM}.txt"
        ;;
esac

echo burn_dev="$tblTarget" >> /tmp/config
echo kiosk_config="$FINCONFIG" >> /tmp/config
```

---

## 10. Remote Files Reference

### Authentication

| File | URL | Contents |
|------|-----|----------|
| `key.txt` | `https://cullerdigitalmedia.com/files/key.txt` | `P@ss3264` |

### Dropdown Options

| File | URL | Purpose |
|------|-----|---------|
| `dev.txt` | `https://cullerdigitalmedia.com/files/dev.txt` | Device types |
| `fac.txt` | `https://cullerdigitalmedia.com/files/fac.txt` | Facility names |
| `num.txt` | `https://cullerdigitalmedia.com/files/num.txt` | Device numbers |
| `clients.txt` | `https://cullerdigitalmedia.com/files/clients.txt` | Client list |

### Config URL Patterns

| Device Type | URL Pattern | Example |
|-------------|-------------|---------|
| Education | `{base}kc/{facility}_ed.txt` | `.../kc/sunrise_ed.txt` |
| Kiosk | `{base}kc/{facility}/{facility}_ks{num}.txt` | `.../kc/sunrise/sunrise_ks3.txt` |
| ActivityPro | `{base}activitypro/{facility}.txt` | `.../activitypro/sunrise.txt` |
| Medcart | `{base}kc/{facility}/{facility}_mc{num}.txt` | `.../kc/sunrise/sunrise_mc2.txt` |
| Treatment | `{base}kc/{facility}/{facility}_tc{num}.txt` | `.../kc/sunrise/sunrise_tc1.txt` |
| NurseStation | `{base}kc/{facility}/{facility}_ns{num}.txt` | `.../kc/sunrise/sunrise_ns4.txt` |
| Bedboard | `{base}kc/{facility}/{facility}_stats.txt` | `.../kc/sunrise/sunrise_stats.txt` |
| Resident Room | `{base}kc/{facility}/{facility}_rr{num}.txt` | `.../kc/sunrise/sunrise_rr101.txt` |
| Digital Signage | `{base}signage/{facility}/{facility}_ds{num}.txt` | `.../signage/sunrise/sunrise_ds1.txt` |

---

## 11. Configuration Output Format

### Final `/tmp/config` File

```ini
# Network settings (from welcome)
connection=wifi
dhcp=yes
ssid_name=MyNetwork
wifi_encryption=wpa
wpa_password=secretpassword
browser=firefox

# Device settings (from wizard)
burn_dev=mmcblk0
kiosk_config=http://cullerdigitalmedia.com/kc/sunrise/sunrise_ks3.txt
```

### Config File Locations

| Stage | File | Purpose |
|-------|------|---------|
| Wizard output | `/tmp/config` | Merged network + device config |
| Permanent storage | `/opt/scripts/files/lcon` | Saved by first-run |
| Remote config | `/opt/scripts/files/rcon` | Downloaded by daemon.sh |
| Comparison copy | `/opt/scripts/files/lconc` | For change detection |

### Default Configuration

**File:** `/opt/scripts/files/lcon.default`

```ini
browser=chromium
homepage=https://www.google.com
kiosk_config=
daemon_check=60
hostname=kiosk-arm64
timezone=UTC
```

---

## 12. GTKDialog Function Library

### File: `/opt/scripts/files/wizard/wizard-functions`
### Lines: ~1000+

### Key Functions

#### `gtk_yesno(message, width)`
Display Yes/No confirmation dialog.

#### `get_device()`
Populate interface dropdown based on connection type.

```bash
get_device(){
    if [ $(grep -o wired $TMP/connection.tmp) ]; then
        iwconfig 2>&1 | grep 'no wireless extension' | cut -d" " -f1 > $TMP/device
    elif [ $(grep -o wifi $TMP/connection.tmp) ]; then
        iwconfig 2>/dev/null | cut -d" " -f1 | sed '/^$/d' > $TMP/device
    fi
}
```

#### `get_essid()`
Scan for WiFi networks.

```bash
get_essid(){
    for nic in $(iwconfig 2>/dev/null | cut -d" " -f1 | sed '/^$/d'); do
        ifconfig $nic up
        iwlist $nic scan | egrep 'ESSID|Quality' | ... >> $TMP/essid
    done
}
```

#### `get_report()`
Compile final configuration report.

```bash
get_report(){
    for a in $(ls -rt $TMP/*.tmp); do
        cat $a >> $REPORT
    done
}
```

#### `manual_settings()`
Save manual IP configuration.

```bash
manual_settings(){
    echo "network_interface=$device" > $TMP/device.tmp
    echo "ip_address=$ipaddress" > $TMP/ipaddress.tmp
    echo "netmask=$netmask" > $TMP/netmask.tmp
    echo "default_gateway=$gateway" > $TMP/gateway.tmp
    echo "dns_server=$dns1 $dns2" > $TMP/dns1.tmp
}
```

#### `dlist()`
Generate block device list.

```bash
dlist(){
    lsblk -o NAME,TYPE,MODEL,SIZE | egrep -v 'NAME|loop|part|rom' | \
        tr -s ' ' | sed ... > $TMPDIR/block.txt
}
```

---

## 13. Key Differences from x86

### Summary Table

| Feature | x86 | ARM64 |
|---------|-----|-------|
| Boot loader | isolinux/UEFI | RPi bootloader (start4.elf) |
| Kernel | vmlinuz | kernel8.img |
| Device tree | Not needed | bcm2711-rpi-4-b.dtb |
| Init system | Slackware-style | Same (inittab) |
| GPU initialization | uvesafb/DRM | VC4 DRM (BCM2711) |
| Network drivers | lspci-based | Device tree based |
| **wizard-now prompt** | **Yes (30s timeout)** | **No** |
| **First-run check** | **Checks for lcon** | **Unconditional** |
| **Network apply timing** | **After all wizards** | **Between welcome and wizard** |
| Storage target | /dev/sda typical | /dev/mmcblk0 typical |

### UI Flow Differences

**x86 Flow:**
```
autostart → CHECK LCON → first-run → wizard-now (30s) → welcome → wizard → save
                │
                └─► (if config exists) → browser
```

**ARM64 Flow:**
```
autostart → first-run → welcome → NETWORK APPLY → wizard → save → browser
            (unconditional)        (inline)
```

### Code Differences

**x86 first-run (345 lines):**
- Checks for first-run condition
- Launches wizard-now with 30s timeout
- Waits for `/tmp/launch-wizard` signal
- Validates configuration fields
- Optionally triggers update-config

**ARM64 first-run (105 lines):**
- Direct call to welcome
- Inline network configuration
- Direct call to wizard
- Simple config save

### Why the Differences?

1. **No wizard-now prompt:** The ARM64 port simplifies the flow by assuming all boots need configuration. This may be intentional for embedded/kiosk deployments.

2. **Inline network apply:** Network is configured between welcome and wizard so that the wizard can download remote files (key.txt, dev.txt, etc.).

3. **No first-run check:** Every boot goes through the wizard sequence. This could be a bug or intentional design choice.

---

## Document History

- **2026-01-15 v1.0:** Initial ARM64 specification created
  - Analyzed all scripts in 003-settings.xzm
  - Documented boot sequence differences
  - Mapped complete UI flow
  - Identified key differences from x86

## Source Files Analyzed

| File | Location | Lines |
|------|----------|-------|
| `init` | `initrd.img` | 171 |
| `rc.S` | `003-settings.xzm:/etc/rc.d/` | 138 |
| `rc.M` | `003-settings.xzm:/etc/rc.d/` | 73 |
| `rc.4` | `003-settings.xzm:/etc/rc.d/` | 144 |
| `autostart` | `003-settings.xzm:/etc/xdg/openbox/` | 136 |
| `first-run` | `003-settings.xzm:/opt/scripts/` | 105 |
| `welcome` | `003-settings.xzm:/opt/scripts/` | 640 |
| `wizard` | `003-settings.xzm:/opt/scripts/` | 306 |
| `wizard-functions` | `003-settings.xzm:/opt/scripts/files/wizard/` | ~1000+ |
| `daemon.sh` | `003-settings.xzm:/opt/scripts/` | 127 |
| `apply-config` | `003-settings.xzm:/opt/scripts/` | 75 |
