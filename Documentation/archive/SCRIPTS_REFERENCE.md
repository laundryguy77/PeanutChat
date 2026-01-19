# Porteus Kiosk Scripts Reference

## Overview

Complete inventory of scripts, their locations, and purposes in the Porteus Kiosk system.

---

## 1. HOOK DIRECTORIES

The system provides three hook points for custom scripts:

| Hook Directory | Execution Point | User Context | Timing |
|----------------|-----------------|--------------|--------|
| `/etc/rc.d/local_cli.d/` | rc.S (line 40) | root | Early boot, before X11 |
| `/etc/rc.d/local_gui.d/` | xinitrc (line 16) | guest | After X11 init, before WM |
| `/etc/rc.d/local_net.d/` | autostart (line 139) | guest | After network available |

### Hook Execution Model
- Scripts are **sourced** (`. script`), not executed as subprocesses
- Variables persist to subsequent scripts
- Alphabetical execution order
- Errors don't stop subsequent scripts
- Must be POSIX shell compatible

---

## 2. SERVER-PROVISIONED SCRIPT HOOKS

These scripts are checked at boot but are **NOT in the base ISO** - they're downloaded from the Kiosk Server:

| Script | Check Location | Purpose |
|--------|----------------|---------|
| `/opt/scripts/first-run` | autostart:97 | Initial device setup wizard |
| `/opt/scripts/update-config` | autostart:121 | Reconfiguration on config change |
| `/opt/scripts/update` | autostart:124 | Paid subscription updates |

**Autostart code:**
```bash
# Line 97
[ -e /opt/scripts/first-run ] && su -c /opt/scripts/first-run

# Line 121
[ -e /opt/scripts/update-config ] && su -c /opt/scripts/update-config

# Line 124
[ -e /opt/scripts/update ] && su -c /opt/scripts/update
```

---

## 3. BOOT SCRIPTS (initrd.xz)

| Script | Lines | Purpose |
|--------|-------|---------|
| `/init` | 146 | Main boot orchestrator |
| `/fatal` | 49 | Error handler, displays message and halts |

### /init Key Functions
- `nap()` - Delay with counter display
- `search()` - Find boot ISO by label
- `lazy()` - Retry search with delays
- `escape()` - Error shutdown handler

### /init Key Sections
- Lines 1-13: Mount /proc, /sys, /dev
- Lines 45-46: Create RAM disk (75% of memory)
- Lines 49-59: PXE network boot path
- Lines 60-86: Local boot + recovery check
- Lines 87-108: GPU detection (x86-specific)
- Lines 115-131: AUFS union and module mounting
- Line 140: switch_root to /union

---

## 4. SYSTEM INIT SCRIPTS (003-settings.xzm)

| Script | Lines | Purpose |
|--------|-------|---------|
| `/etc/rc.d/rc.S` | ~45 | System initialization |
| `/etc/rc.d/rc.M` | ~72 | Multi-user setup |
| `/etc/rc.d/rc.4` | ~19 | GUI startup |
| `/etc/rc.d/rc.inet1` | ~18 | Network interface setup |
| `/etc/rc.d/rc.FireWall` | ~60 | Firewall rules |
| `/etc/rc.d/rc.sound` | ~40 | Audio initialization |
| `/etc/rc.d/rc.sshd` | ~20 | SSH daemon control |
| `/etc/rc.d/rc.vncd` | ~20 | VNC daemon control |
| `/etc/rc.d/rc.stunnel` | ~20 | SSL tunnel control |

### rc.S Flow
1. Install busybox applets
2. Mount filesystems
3. Start udevd
4. Run persistence script
5. Check first_run flag
6. Execute `/etc/rc.d/local_cli.d/*` scripts (HOOK #1)

### rc.M Flow
1. Set hostname
2. Configure timezone
3. Start cron, syslog
4. Start networking
5. Start D-Bus
6. Configure firewall

### rc.4 Flow
1. Start watch-xorg (error recovery)
2. Launch xdm (X server)

---

## 5. X SESSION SCRIPTS (003-settings.xzm)

| Script | Lines | Purpose |
|--------|-------|---------|
| `/etc/X11/xinit/xinitrc` | ~21 | X session initialization |
| `/etc/xdg/openbox/autostart` | 292 | Desktop session setup |

### xinitrc Flow
1. Source variables.sh
2. Execute `/etc/rc.d/local_gui.d/*` scripts (HOOK #2)
3. Launch openbox-session via dbus-launch

### autostart Flow (292 lines)
```
Lines 1-44:   Input device configuration
Lines 46-66:  Screen setup, rotation, brightness
Lines 68-95:  Wallpaper, transparency, DPMS, sound
Line 97:      first-run check (server-provisioned)
Lines 99-104: Network wait loop (120s timeout)
Lines 107-108: NTP time sync
Lines 110-118: Proxy PAC download
Line 121:     update-config check (server-provisioned)
Line 124:     update check (server-provisioned)
Lines 126-136: SSH, VNC, pktunnel startup
Line 139:     Execute local_net.d/* scripts (HOOK #3)
Lines 141+:   Printing, scheduled actions, screensaver
Line 292:     Launch gui-app (browser)
```

### ARM64 Boot Flow (Verified)

```
autostart → DPMS off → network wait → NTP → first-run → update-config → apply-config → local_net.d hooks → browser
```

---

## 6. RUNTIME SCRIPTS (003-settings.xzm)

| Script | Lines | Purpose |
|--------|-------|---------|
| `/opt/scripts/apply-config` | ~20 | Config parameter applier (ARM64) |
| `/opt/scripts/gui-app` | ~18 | Browser launcher loop |
| `/opt/scripts/persistence` | ~50 | Persistent storage setup |
| `/opt/scripts/screen-setup` | ~400 | Dynamic screen configuration |
| `/opt/scripts/session-manager` | ~100 | Password authentication |
| `/opt/scripts/pkget` | ~20 | Secure file download utility |
| `/opt/scripts/scheduled-action` | - | Scheduled command execution |
| `/usr/sbin/pktunnel` | 117 | Reverse SSH tunnel to server |

### apply-config (ARM64 Port)

Sources the config file and runs all parameter handlers:

```bash
# Called by daemon.sh on config change, and by autostart at boot
for handler in /opt/scripts/param-handlers/*.sh; do
    [ -x "$handler" ] && "$handler"
done
```

See [PARAM_HANDLERS.md](PARAM_HANDLERS.md) for handler architecture and [PARAM_REFERENCE.md](PARAM_REFERENCE.md) for parameter reference.

### gui-app Loop
```bash
while true; do
    # Clean guest home
    rm -rf /home/guest
    cp -a /opt/scripts/guest /home/guest
    chown -R guest:guest /home/guest

    # Launch browser
    su - guest -c "firefox"
done
```

### pkget Dual-Mode Downloader
```bash
# Mode 1: SSH tunnel (server:// URLs)
if [ "`echo $1 | cut -c1-9`" = "server://" ]; then
    dfile=`echo $1 | sed 's_server://__'`
    sshpass -p <password> scp -P 9999 kiosk@127.0.0.1:hosts/files/$dfile $2
fi

# Mode 2: HTTP/HTTPS/FTP
wget --no-http-keep-alive --no-cache --no-check-certificate -q -T20 -t5 $1 -O $2
```

---

## 7. CUSTOM OVERLAY SCRIPTS (zz-settings.xzm)

| Script | Lines | Purpose |
|--------|-------|---------|
| `/etc/rc.d/local_net.d/daemon.sh` | 65 | Remote config polling |
| `/opt/scripts/welcome` | 617 | Network setup wizard |
| `/opt/scripts/wizard` | ~385 | Device installation wizard |
| `/opt/scripts/wizard-now` | 27 | Wizard launcher |
| `/opt/scripts/files/greyos_reboot` | 23 | Scheduled reboot |

### daemon.sh Config Polling Loop
```
Every daemon_check minutes:
1. Download config: wget "$kiosk_config?kiosk=$PCID" → /root/config
2. Sanitize: fromdos, remove special chars
3. Save to /opt/scripts/files/rcon
4. Filter: strip daemon_*, burn_dev=, md5conf=
5. Compare: md5sum lconc vs rconc
6. If different:
   - Copy rcon to lcon
   - Call /opt/scripts/apply-config (ARM64)
   - daemon_force_reboot=yes → sleep 30s, init 6
   - daemon_message set → display notification
   - else → schedule reboot for 3:00 AM
```

### greyos_reboot Scheduled Reboot
```bash
# Wait 6 minutes (debounce)
sleep 360

# Calculate time until 23:59
# Sleep until 23:59
# Sleep 3 more hours (until 3:00 AM)

init 6  # Reboot
```

---

## 8. WIZARD SYSTEM

### GTKDialog Integration
```bash
gtkdialog -i /opt/scripts/files/wizard/wizard-functions -s -c
```

### Wizard Functions Library
- **Location:** `/opt/scripts/files/wizard/wizard-functions`
- **Lines:** 2,259
- **Functions:** 40+ GTK helper functions

### Key Wizard Functions
| Function | Purpose |
|----------|---------|
| `gtk_yesno()` | Yes/No confirmation |
| `gtk_warning()` | Warning message |
| `gtk_entry_box()` | Text input |
| `gtk_password()` | Password entry |
| `gtk_list()` | Multi-line display |
| `process_settings()` | Assemble /tmp/config |
| `get_essid()` | WiFi scanning |
| `get_report()` | Build final report |

### Wizard Output Format (/tmp/config)
```ini
# Network
network_interface=wlan0
connection=wifi
dhcp=yes
wifi_encryption=wpa
wpa_password=<password>
ssid_name=<ssid>

# System
browser=chrome
hostname=<hostname>
homepage=<url>

# Remote Management
kiosk_config=<config_url>
daemon_check=5

# Device
burn_dev=sdb
```

---

## 9. CONFIGURATION FILES

### Runtime Config Locations

| File | Purpose |
|------|---------|
| `/opt/scripts/extras` | Runtime flags (first_run, boot_dev) |
| `/opt/scripts/files/lcon` | Local config (current active) |
| `/opt/scripts/files/lconc` | Local config minus daemon_ lines |
| `/opt/scripts/files/rcon` | Remote config (downloaded) |
| `/opt/scripts/files/rconc` | Remote config minus daemon_ lines |
| `/tmp/config` | Wizard output (temporary) |

### Config Parameters by Category

See [PARAM_REFERENCE.md](PARAM_REFERENCE.md) for complete parameter documentation.

**Network:**
- `network_interface`, `connection`, `dhcp`
- `ip_address`, `netmask`, `gateway`, `dns_server`
- `wifi_encryption`, `wpa_password`, `ssid_name`

**System:**
- `browser`, `homepage`, `hostname`
- `timezone`, `root_password`

**Daemon:**
- `kiosk_config` - Remote config URL
- `daemon_check` - Polling interval (minutes)
- `daemon_force_reboot` - Immediate reboot on change
- `daemon_message` - Notification message

**Device:**
- `burn_dev` - Target device for ISO burning

---

## 10. ISO BUILD SCRIPT (make_iso.sh)

**Location:** `/home/culler/saas_dev/pk-port/iso/make_iso.sh`

### mkisofs Command
```bash
mkisofs -o ../GreyOS_v20.iso \
  -l -J -joliet-long -R -D \
  -A "Kiosk" -V "Kiosk" \
  -no-emul-boot -boot-info-table -boot-load-size 4 \
  -b boot/isolinux/isolinux.bin \
  -c boot/isolinux/isolinux.boot \
  -eltorito-alt-boot -eltorito-platform 0xEF \
  -eltorito-boot boot/isolinux/efi/efiboot.img \
  -no-emul-boot .
```

### Parameter Reference
| Parameter | Purpose |
|-----------|---------|
| `-l -J -joliet-long -R` | Long filename support |
| `-A "Kiosk"` | Application identifier |
| `-V "Kiosk"` | Volume label (used by blkid) |
| `-b boot/isolinux/isolinux.bin` | BIOS bootloader |
| `-eltorito-boot .../efiboot.img` | UEFI bootloader |

---

## 11. EXECUTION TIMELINE

| Time | Script | User | Event |
|------|--------|------|-------|
| 0s | init | - | Kernel loads initramfs |
| 0-1s | init | root | Mount /proc, /sys, /dev |
| 1-2s | init | root | Create RAM disk, find ISO |
| 2-3s | init | root | Mount modules, build AUFS |
| 3s | init | root | switch_root to /union |
| 3-4s | rc.S | root | System init, HOOK #1 |
| 4-5s | rc.M | root | Networking, daemons |
| 5-6s | rc.4 | root | Start X server |
| 6-7s | xinitrc | guest | X session init, HOOK #2 |
| 7-8s | autostart | guest | Screen setup |
| 8-9s | autostart | guest | first-run check |
| 9-14s | autostart | guest | Network wait (up to 120s) |
| 14s | autostart | guest | update-config check |
| 14s | autostart | guest | HOOK #3 (daemon.sh) |
| 15s+ | gui-app | guest | Browser launched |

---

## Related Documentation

- [PARAM_HANDLERS.md](PARAM_HANDLERS.md) - Extensible parameter handler architecture (ARM64)
- [PARAM_REFERENCE.md](PARAM_REFERENCE.md) - Complete parameter reference tables
- [ARM_PORTING_NOTES.md](ARM_PORTING_NOTES.md) - ARM64 porting notes

---

## Document History
- Created: 2026-01-12
- Updated: 2026-01-13 - Added apply-config and parameter handler references (ARM64)
- Updated: 2026-01-13 - Added verified ARM64 boot flow
- Purpose: Complete script inventory and reference
