# Porteus Kiosk Boot and Reconfiguration Analysis

## Overview

This document traces the complete boot sequence, configuration management, and reconfiguration process for Porteus Kiosk 4.9.0.

### Note on Custom vs Original Files

This ISO (TuxOS_v2.iso) is a customized version of Porteus Kiosk. The following references are **custom additions** made years ago and are NOT part of the original Porteus Kiosk distribution:

- `cullerdigitalmedia.com` - Custom domain
- `pod9.gsiresource.com` - Custom FTP server
- `carerite.greysignal.com` - Custom config server
- `prestige.greysignal.com` - Custom config server
- Associated credentials for the above services
- The `zz-settings.xzm` module containing custom wizard and daemon scripts

The core boot mechanism, AUFS overlay system, and module loading (sections 1-6) reflect standard Porteus Kiosk architecture.

---

## 1. BOOT SEQUENCE - Power On to UI

### Phase 1: Bootloader (BIOS/UEFI)

**Files:**
- `boot/isolinux/isolinux.cfg` (BIOS)
- `boot/isolinux/grub.cfg` (UEFI)

**Kernel Parameters:**
```
quiet first_run run_splash mem_encrypt=off amd_iommu=off
```

### Phase 2: Initramfs (`boot/initrd.xz`)

**Key Files Inside:**
- `/init` - Main boot script (146 lines)
- `/fatal` - Error handler (49 lines)
- `/bin/busybox` - BusyBox v1.24.2 (32-bit i386, statically linked)

**Init Script Flow:**
1. Install busybox applets
2. Mount /proc, /sys, /dev
3. Create RAM disk: `mount -t tmpfs -o size=75% tmpfs /memory`
4. Create directories: `/memory/{xino,changes,images,copy2ram}`
5. Detect boot media via `blkid` (label="Kiosk") OR PXE via `http_server=`
6. Check for signature file: `first_run` or `kiosk.sgn` in docs/
7. Mount boot media to `/mnt/$DEV`
8. **Recovery Check:** If partition 4 is "StorageBkp" and boot failed 5+ times, restore from backup ISO
9. Early module mount: `000-kernel.xzm` → `/opt/000`, `001-core.xzm` → `/opt/001`
10. GPU detection via lspci, load video driver
11. Display splash screen via `fbv`
12. Copy all modules to `/memory/copy2ram`
13. Build AUFS union: `mount -t aufs -o nowarn_perm,xino=...,br:/memory/changes=rw aufs /union`
14. Mount each XZM as squashfs, add to AUFS
15. Switch root: `exec /sbin/switch_root /union /sbin/init`

### Phase 3: System Init (`/sbin/init` from 001-core.xzm)

**File:** `/tmp/003-settings/squashfs-root/etc/inittab`
- Default runlevel: 4 (GUI)
- Executes: `rc.S` → `rc.M` → `rc.4`

**rc.S (System Init):**
- Installs busybox applets
- Mounts proc, sys, devtmpfs
- Starts udevd
- Runs `/opt/scripts/persistence` if configured
- Skips setup if `first_run=yes` in `/opt/scripts/extras`
- Runs scripts in `/etc/rc.d/local_cli.d/`

**rc.M (Multi-User):**
- Sets hostname to "kiosk"
- Starts crond, rsyslogd
- Starts networking: `/etc/rc.d/rc.inet1`
- Starts dbus-daemon
- Enables firewall, ACPI
- Optionally creates swap/zRAM

**rc.4 (GUI):**
- Starts X via `/usr/bin/xdm` wrapper
- xdm loops: `su - -c "/usr/bin/startx -- -nolisten tcp vt7"`

### Phase 4: X Session Init

**File:** `/tmp/003-settings/squashfs-root/etc/X11/xinit/xinitrc`
```bash
# Skip during first run:
if ! grep -q "^first_run=yes" /opt/scripts/extras; then
    . /etc/profile.d/variables.sh
    for script in `ls -1 /etc/rc.d/local_gui.d`; do . /etc/rc.d/local_gui.d/$script; done
fi
dbus-launch --exit-with-session /usr/bin/openbox-session
```

### Phase 5: Desktop Session (`/etc/xdg/openbox/autostart`)

**293 lines of initialization:**

1. **Lines 1-44:** Input device configuration, keyboard layout
2. **Lines 46-66:** Screen setup, rotation, brightness
3. **Lines 68-95:** Wallpaper, transparency, DPMS, sound
4. **Line 97:** `[ -e /opt/scripts/first-run ] && su -c /opt/scripts/first-run`
5. **Lines 99-104:** Wait for network gateway (120s timeout)
6. **Lines 107-108:** NTP time sync
7. **Lines 110-118:** Proxy PAC download via `pkget`
8. **Line 121:** `[ -e /opt/scripts/update-config ] && su -c /opt/scripts/update-config`
9. **Line 124:** `[ -e /opt/scripts/update ] && su -c /opt/scripts/update`
10. **Lines 126-136:** Start SSH, VNC, pktunnel if configured
11. **Line 139:** Source all scripts in `/etc/rc.d/local_net.d/` (includes daemon.sh)
12. **Lines 141+:** Printing, scheduled actions, screensaver, etc.

### Phase 6: Browser Launch

**File:** `/tmp/003-settings/squashfs-root/opt/scripts/gui-app`
- Infinite loop that:
  - Restores guest home from backup
  - Optionally runs session-manager for password
  - Launches browser: `su - guest -c "firefox"`

---

## 2. CONFIGURATION FILES

### Runtime Config Files

| File | Purpose |
|------|---------|
| `/opt/scripts/extras` | Runtime config flags (first_run, boot_dev, etc.) |
| `/opt/scripts/files/lcon` | Local config (current active config) |
| `/opt/scripts/files/lconc` | Local config minus daemon_ lines (for comparison) |
| `/opt/scripts/files/rcon` | Remote config (downloaded) |
| `/opt/scripts/files/rconc` | Remote config minus daemon_ lines (for comparison) |
| `/tmp/config` | Wizard output (temporary) |

### Key Config Parameters

From daemon.sh analysis:
- `kiosk_config=` - URL to fetch remote config from
- `daemon_check=` - Check interval in minutes
- `daemon_force_reboot=yes` - Force immediate reboot on config change
- `daemon_message=` - Display notification message
- `burn_dev=` - Target device for burning (filtered from config)

---

## 3. REMOTE CONFIG MONITORING (daemon.sh)

**File:** `/home/culler/saas_dev/pk-port/iso/xzm/zz-settings/etc/rc.d/local_net.d/daemon.sh`

### Flow:
```
1. Read kiosk_config URL from /opt/scripts/files/lcon
2. Sleep for daemon_check minutes
3. Loop forever:
   a. Setup proxy (if proxy.pac exists)
   b. Download config: wget -T20 -t3 "$kiosk_config?kiosk=$PCID" → /root/config
   c. Process: fromdos, sanitize, save to /opt/scripts/files/rcon
   d. Handle [[GLOBAL]] and [[PCID]] sections
   e. Create comparison files (strip daemon_, burn_dev, md5conf lines)
   f. Compare MD5: lconc vs rconc
   g. If different:
      - If daemon_force_reboot=yes: notify, sleep 30s, init 6
      - Else: show message, launch greyos_reboot
   h. Sleep daemon_check minutes (default 5m)
```

### wget Command:
```bash
wget --no-http-keep-alive --no-cache --no-check-certificate -T20 -t3 -q
```

---

## 4. SCHEDULED REBOOT (greyos_reboot)

**File:** `/home/culler/saas_dev/pk-port/iso/xzm/zz-settings/opt/scripts/files/greyos_reboot`

```bash
# Target time: 23:59
# Sleep 6 minutes (debounce)
# Calculate minutes until 23:59
# Sleep until 23:59
# Sleep 3 more hours (until 3:00 AM)
# Execute: init 6
```

---

## 5. RECONFIGURATION MECHANISM

### Observed Reconfiguration Process

When the remote config file changes, the following sequence occurs (confirmed via screenshots):

**Stage 1: Detection & Notification**
- Blue notification banner: "Performing system reconfiguration - please do not turn off the PC."
- TuxOS splash screen displays with cloud logo and animated binary numbers

**Stage 2: Component Download**
- Blue banner: "Downloading additional components ..."
- Red banner shows progress: "[100%] Downloading 002-chrome.xzm component ..."
- Components are downloaded from the remote server as needed

**Stage 3: ISO Burning**
- Red notification banner: "Burning ISO on /dev/sda2 - this may take a while ..."
- The new ISO is written directly to **partition 2** of the boot device (e.g., `/dev/sda2`)
- This is the system partition, not the storage/backup partition

**Stage 4: Reboot**
- System reboots into the newly burned configuration

### Key Technical Details

- **Target partition:** `/dev/sdX2` (partition 2, the system partition)
- **Config check trigger:** On boot, the remote config URL is fetched and compared to local config
- **Notification system:** Uses `dunstify` for desktop notifications (red = critical, blue = info)

### Complete Reconfiguration Flow

```
RECONFIGURATION SEQUENCE
========================

[Running System]
       │
       ▼
[daemon.sh polling loop] (every daemon_check minutes)
       │
       ├── Download: wget "$kiosk_config?kiosk=$PCID" → /root/config
       ├── Process: fromdos, sanitize → /opt/scripts/files/rcon
       ├── Filter: strip daemon_, burn_dev=, md5conf= → rconc
       └── Compare: md5sum lconc vs rconc
                    │
        ┌───────────┴───────────┐
        │                       │
   [No Change]            [Config Changed]
        │                       │
   [Sleep & Loop]         daemon_force_reboot=yes?
                                │
                    ┌───────────┴───────────┐
                    │                       │
               [YES]                    [NO]
                    │                       │
          dunstify "System               dunstify message
          maintenance..."                      │
                    │                   /opt/scripts/files/greyos_reboot &
             sleep 30s                  (schedule for 3:00 AM)
                    │                       │
               init 6 ◄─────────────────────┘
                    │
                    ▼
              [REBOOT]
                    │
                    ▼
[Boot Sequence - Phases 1-5]
                    │
                    ▼
[autostart line 97: first-run check]
[ -e /opt/scripts/first-run ] && su -c /opt/scripts/first-run
                    │
                    ▼
[autostart line 121: update-config check]
[ -e /opt/scripts/update-config ] && su -c /opt/scripts/update-config
                    │
                    ▼
[SERVER-PROVISIONED SCRIPT EXECUTES]
(Downloads new config, creates ISO, burns to burn_dev)
                    │
                    ▼
cat new_system.iso > /dev/$burn_dev
sync
                    │
                    ▼
              init 6
                    │
                    ▼
[Boot with new configuration]
```

### Key Finding: Server-Provisioned Scripts

The actual reconfiguration/burning scripts are **NOT in the base modules**. They are:

1. **Provisioned by the Kiosk Server** via:
   - `pkget` with `server://` URLs (SSH tunnel)
   - Direct download from `kiosk_config` URL
   - Stored in persistent partition 4 (StorageBkp)

2. **Executed conditionally** at boot:
   - `/opt/scripts/first-run` - Initial device setup
   - `/opt/scripts/update-config` - Reconfiguration handler
   - `/opt/scripts/update` - Paid subscription updates

3. **Use disk write mechanism from initrd recovery logic:**
   ```bash
   # From /init lines 68-86 (recovery mode):
   cat $storage/System-Backup/system-backup.iso > /dev/$DEV
   sync
   ```

### Autostart Hooks for Reconfiguration

**File:** `/etc/xdg/openbox/autostart`

```bash
# Line 97 - First run wizard (server-provisioned)
[ -e /opt/scripts/first-run ] && su -c /opt/scripts/first-run

# Line 121 - Auto reconfiguration (server-provisioned)
[ -e /opt/scripts/update-config ] && su -c /opt/scripts/update-config

# Line 124 - Auto update (paid subscription, server-provisioned)
[ -e /opt/scripts/update ] && su -c /opt/scripts/update
```

### first_run Kernel Parameter

The boot config includes `first_run` as a kernel parameter:

```
# isolinux.cfg / grub.cfg:
quiet first_run run_splash mem_encrypt=off amd_iommu=off
```

**Effect on boot (in /init):**
```bash
egrep -qo " first_run( |\$)" /proc/cmdline && sgn=first_run || sgn=kiosk.sgn
```

- If `first_run` param present → search for `docs/first_run` signature file
- If absent → search for `docs/kiosk.sgn` signature file

**Effect on runtime (in rc.S and xinitrc):**
```bash
if ! grep -q "^first_run=yes" /opt/scripts/extras; then
    # Normal boot - run local CLI/GUI scripts
    for script in `ls -1 /etc/rc.d/local_cli.d`; do . $script; done
fi
```

When `first_run=yes` is in `/opt/scripts/extras`, CLI and GUI initialization scripts are skipped.

### pkget Download Utility

**File:** `/opt/scripts/pkget`

Dual-mode file downloader:

```bash
# Mode 1: SSH tunnel (server:// URLs)
if [ "`echo $1 | cut -c1-9`" = "server://" ]; then
    dfile=`echo $1 | sed 's_server://__'`
    sshpass -p 9Se-7c.fgLa scp -P 9999 kiosk@127.0.0.1:hosts/files/$dfile $2
fi

# Mode 2: HTTP/HTTPS/FTP
wget --no-http-keep-alive --no-cache --no-check-certificate -q -T20 -t5 $1 -O $2
```

**Files downloaded via pkget:**

| File | Caller | Destination |
|------|--------|-------------|
| proxy.pac | autostart:113 | `/opt/scripts/proxy.pac` |
| brpref | autostart:246 | `/tmp/pref` → browser prefs |
| arch.zip | screensaver-slideshow | `/opt/scripts/files/arch.zip` |
| authorized_keys | pktunnel | `/root/.ssh/authorized_keys` |
| certificates | import-certificates | `/tmp/cert` → `/etc/ssl/certs/` |

### Dynamic Script Generation

**File:** `/opt/scripts/screen-setup` (line 394)

The system can generate executable scripts from configuration:
```bash
[ "$sset" ] && echo -e "#!/bin/sh\n\n# Setup screen:\n/opt/scripts/screen-setup-parse $sset\nhsetroot -fill /usr/share/wallpapers/default.jpg" > /etc/rc.d/local_net.d/screen_settings.sh
```

This creates `/etc/rc.d/local_net.d/screen_settings.sh` which runs on subsequent boots.

### Wizard Configuration Output

The wizard scripts write to `/tmp/config`:

```bash
# From wizard lines 182, 192, 286:
echo burn_dev=$tblTarget >> /tmp/config
echo kiosk_config="$FINCONFIG" >> /tmp/config
```

The `burn_dev` variable specifies the target device for ISO burning (e.g., `/dev/sdb`).

### Recovery Mechanism (Initrd)

**File:** `/init` (lines 68-86)

If boot fails 5+ times, automatic recovery from backup:

```bash
storage=/opt/storage
trg=`echo /dev/$DEV | sed 's/2$/4/'`  # Partition 4

if blkid $trg | grep -q "StorageBkp"; then
    mount $trg $storage
    if [ -e $storage/System-Backup/system-backup.iso ]; then
        if [ "`grep -c booting $storage/System-Backup/boot.log`" -gt 5 ]; then
            echo "Restoring system image from the backup..."
            cat $storage/System-Backup/system-backup.iso > /dev/$DEV
            sync
            reboot -f
        fi
    fi
fi
```

This is the **only ISO writing logic found in the modules** and uses `cat ISO > /dev/DEVICE` for disk writes.

---

## 6. PERSISTENCE MECHANISM

**File:** `/tmp/003-settings/squashfs-root/opt/scripts/persistence`

- Creates partition 4 on boot device if not exists
- Formats with XFS
- Mounts to `/opt/storage`
- Optionally binds persistent folders (e.g., /home)

### Partition Layout:
- Partition 2: Boot/system ISO
- Partition 4: StorageBkp (persistent storage)

---

## 7. REMOTE MANAGEMENT (pktunnel)

**File:** `/tmp/003-settings/squashfs-root/usr/sbin/pktunnel`

Establishes reverse SSH tunnel to Porteus Kiosk Server:
- Server: `kiosk@127.0.0.1:9999` (via stunnel)
- Password: `9Se-7c.fgLa` (hardcoded)
- Downloads SSH keys from server
- Creates reverse tunnel for remote SSH access
- Reports kiosk status, config name, browser version

---

## 8. EXTERNAL URLs

### FTP Server (pod9.gsiresource.com)
- `ftp://pod9.gsiresource.com/isofiles/drivekey.txt`
- `ftp://pod9.gsiresource.com/isofiles/clients.txt`
- `ftp://pod9.gsiresource.com/isofiles/num.txt`
- `ftp://pod9.gsiresource.com/isofiles/dev.txt`
- `ftp://pod9.gsiresource.com/isofiles/fac.txt`

**Credentials:** `kiosk_images` / `$3Cur1ty$`

### HTTP Config Servers
- `http://admin:412Grey$ignal412$@carerite.greysignal.com/`
- `http://admin:412Grey$ignal412$@prestige.greysignal.com/`

---

## 9. XZM MODULE STRUCTURE

| Priority | Module | Size | Purpose |
|----------|--------|------|---------|
| 1 | 000-kernel.xzm | 41M | Kernel modules, firmware |
| 2 | 001-core.xzm | 47M | Base system (glibc, init, utils) |
| 3 | 002-chrome.xzm | 65M | Google Chrome |
| 4 | 003-settings.xzm | 1.2M | Configuration, startup scripts |
| 5 | 004-wifi.xzm | 1.8M | WiFi tools |
| 6 | 06-fonts.xzm | 34M | Fonts |
| 7 | 08-ssh.xzm | 1.2M | OpenSSH |
| 8 | 09-x11vnc.xzm | 616K | VNC server |
| 9 | firmware.xzm | 8M | Broadcom firmware |
| 10 | NextWindow-5.3.9.xzm | 940K | Touch driver |
| Last | zz-settings.xzm | 12K | Custom scripts overlay |

---

## 10. KEY SCRIPTS INVENTORY

### Boot Scripts (initrd.xz)
| Script | Lines | Purpose |
|--------|-------|---------|
| `/init` | 146 | Boot orchestrator |
| `/fatal` | 49 | Error handler |

### System Init (003-settings.xzm)
| Script | Purpose |
|--------|---------|
| `/etc/rc.d/rc.S` | System init |
| `/etc/rc.d/rc.M` | Multi-user init |
| `/etc/rc.d/rc.4` | GUI init |
| `/etc/rc.d/rc.inet1` | Network init |
| `/etc/X11/xinit/xinitrc` | X session init |
| `/etc/xdg/openbox/autostart` | Desktop session init (293 lines) |

### Runtime Scripts (003-settings.xzm)
| Script | Purpose |
|--------|---------|
| `/opt/scripts/gui-app` | Browser launcher loop |
| `/opt/scripts/session-manager` | Password authentication |
| `/opt/scripts/persistence` | Persistent storage setup |
| `/opt/scripts/pkget` | File download utility |
| `/opt/scripts/scheduled-action` | Scheduled command execution |
| `/usr/sbin/pktunnel` | Reverse SSH tunnel |

### Config Scripts (zz-settings.xzm)
| Script | Purpose |
|--------|---------|
| `/etc/rc.d/local_net.d/daemon.sh` | Remote config polling |
| `/opt/scripts/welcome` | Network wizard (27KB) |
| `/opt/scripts/wizard` | Device wizard (9.6KB) |
| `/opt/scripts/wizard-now` | Wizard launcher |
| `/opt/scripts/files/greyos_reboot` | Scheduled reboot |

---

## 11. ANALYSIS SUMMARY

### Resolved Questions

1. **How is the new ISO burned?**
   - ISO is burned directly to **partition 2** of the boot device (e.g., `/dev/sda2`)
   - Confirmed via screenshot: "Burning ISO on /dev/sda2 - this may take a while ..."
   - Likely uses `cat ISO > /dev/sdX2` (same pattern as recovery mechanism in initrd:80)
   - Components (XZM modules) are downloaded before burning
   - Actual burning script is server-provisioned (not in base modules)

2. **Where do runtime scripts come from?**
   - Downloaded via `pkget` from Kiosk Server (`server://` URLs)
   - Or fetched via HTTP from `kiosk_config` URL
   - Stored in persistent partition 4 (StorageBkp)

3. **How does /tmp/config become persistent?**
   - Wizard writes to `/tmp/config`
   - Server-provisioned script reads `/tmp/config`
   - Creates new ISO with embedded config
   - Burns to `burn_dev` device
   - New config persists in the ISO

### Unresolved - Burning Script Location

**The actual burning/installation script is NOT in the base ISO modules.**

Exhaustive search confirmed:
- No `mkisofs` calls in any runtime script (only in `make_iso.sh` build script)
- No `dd` or `cat > /dev/` in zz-settings or 003-settings (except initrd recovery)
- `gtk_sISO()` in wizard-functions is a UI stub - writes `save_path=` but nothing reads it
- `/opt/scripts/first-run`, `/opt/scripts/update-config`, `/opt/scripts/update` do NOT exist in modules

**Conclusion:** The burning scripts are either:
1. Downloaded from the Porteus Kiosk Server via SSH tunnel (port 9999)
2. Part of a paid/premium feature not included in this ISO
3. Created by external deployment tooling

**To capture these scripts:** Install the OS on a flash drive and extract all files from the installed system, particularly `/opt/scripts/` and `/opt/storage/`

### Server-Provisioned Scripts (NOT in modules)

These scripts are downloaded from the Kiosk Server at boot:

| Script | Purpose | Trigger |
|--------|---------|---------|
| `/opt/scripts/first-run` | Initial device setup wizard | autostart:97 |
| `/opt/scripts/update-config` | Reconfiguration handler | autostart:121 |
| `/opt/scripts/update` | Paid subscription updates | autostart:124 |
| `/opt/scripts/extras` | Runtime config flags | Created during setup |

### Key Architecture Insight

The Porteus Kiosk system is designed for **centralized management**:

1. **Base ISO** contains all runtime code EXCEPT the reconfiguration logic
2. **Kiosk Server** provisions the burning/update scripts per-device
3. **pktunnel** provides bidirectional SSH tunnel for server communication
4. **daemon.sh** polls for config changes and triggers reboot
5. **On reboot**, server-provisioned scripts handle the actual reconfiguration

This architecture means the **burning logic is intentionally external** to prevent unauthorized modifications to deployed kiosks.

---

## 12. EMBEDDED CREDENTIALS (Security Note)

The following credentials are hardcoded in the scripts:

| Credential | Location | Purpose |
|------------|----------|---------|
| `kiosk_images:$3Cur1ty$` | wizard:12-13, 113-115 | FTP access to pod9.gsiresource.com |
| `prestige:$3Cur1ty$` | wizard:212-214 | FTP access for prestige client |
| `admin:412Grey$ignal412$` | wizard:208, 215 | HTTP Basic Auth for config servers |
| `9Se-7c.fgLa` | pkget:8, pktunnel:111 | SSH password for kiosk server tunnel |

### SSH Tunnel Configuration

```
Server: 127.0.0.1:9999 (localhost, via stunnel)
Username: kiosk
Password: 9Se-7c.fgLa
Remote Path: hosts/files/<filename>
Options: -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null
```

---

## 13. RASPBERRY PI PORTING NOTES

See `docs/ARM_PORTING_NOTES.md` for detailed ARM porting analysis including:
- x86-specific code locations in /init (lspci, uvesafb, v86d)
- Library and loader path changes for aarch64
- Kernel and module rebuild requirements
- RPi boot architecture differences (U-Boot vs isolinux)
- Estimated 2,400+ binaries requiring recompilation

---

## 14. KNOWLEDGE GAPS

### kiosk.sgn File

**Location:** `docs/kiosk.sgn` (or `docs/first_run` on fresh installs)

**What we know:**
- Encrypted with AES-256-CBC, Base64 encoded, MD5 key derivation
- Password is the boot device path (determined from `session-manager` script analysis)
- Contains two encrypted chunks separated by marker: `clwrosKXGt0bChL2njIXjANuvHRbWKPeTbkN3lVlWu/ZB6TCPO54F0/LKk2H+lkk`
- File size varies: template ISOs ~545 bytes, installed system ~1650 bytes
- Referenced in initrd `/init` script for boot media detection

**What we don't know:**
- Exact purpose of the encrypted contents
- What data is stored in each chunk
- Why the file grows after installation
- Whether it contains config data, license info, or device identification

**Working theory:** The kiosk.sgn file may be related to the server-provisioned scripts - possibly containing either:
1. Credentials needed to download the missing scripts (first-run, update-config, update)
2. The scripts themselves in encrypted form

This would explain why the file grows after installation (scripts added) and why it's encrypted (protect server credentials). Decryption analysis in progress.

### Server-Provisioned Scripts

These scripts are executed at boot if present, but are **NOT included in the base ISO modules**. They are downloaded from the Porteus Kiosk Server at runtime.

| Script | Trigger | Purpose (assumed) |
|--------|---------|-------------------|
| `/opt/scripts/first-run` | autostart:97 | Initial device setup, first-time configuration |
| `/opt/scripts/update-config` | autostart:121 | Handles reconfiguration when remote config changes |
| `/opt/scripts/update` | autostart:124 | Paid subscription updates |

**What we don't know:**
- Exact contents of these scripts

**What we CAN infer from screenshots and analysis:**
- Downloads XZM components (shows "Downloading 002-chrome.xzm component")
- Uses `mkisofs` to build ISO (parameters in make_iso.sh)
- Burns directly to partition 2: `cat new.iso > /dev/sda2` (from screenshot)
- Uses `dunstify` for notifications (red = critical, blue = info)
- Syncs and reboots after burning

**Potential approach:** Write replacement scripts based on observed behavior - see Section 15.

---

## 15. WRITING REPLACEMENT SCRIPTS

Based on screenshots and analysis, we have enough information to write our own versions of the server-provisioned scripts.

### update-config Script Requirements

```bash
#!/bin/bash
# /opt/scripts/update-config - Reconfiguration handler

# 1. Read configuration
source /opt/scripts/files/lcon
BURN_DEV=$(grep ^burn_dev= /opt/scripts/files/lcon | cut -d= -f2)

# 2. Show notification
dunstify -u normal "Performing system reconfiguration - please do not turn off the PC."

# 3. Download updated components
dunstify -u normal "Downloading additional components ..."
for xzm in 000-kernel 001-core 002-chrome 003-settings; do
    dunstify -u critical "[downloading] $xzm.xzm component ..."
    pkget "$COMPONENT_URL/$xzm.xzm" "/tmp/build/xzm/$xzm.xzm"
done

# 4. Build ISO (parameters from make_iso.sh)
mkisofs -o /tmp/new_system.iso \
  -l -J -joliet-long -R -D -A "Kiosk" -V "Kiosk" \
  -no-emul-boot -boot-info-table -boot-load-size 4 \
  -b boot/isolinux/isolinux.bin -c boot/isolinux/isolinux.boot \
  /tmp/build

# 5. Burn to device
dunstify -u critical "Burning ISO on /dev/${BURN_DEV}2 - this may take a while ..."
cat /tmp/new_system.iso > /dev/${BURN_DEV}2
sync

# 6. Reboot
init 6
```

### first-run Script Requirements

Would handle initial device registration and wizard launch. Likely:
1. Display setup wizard
2. Collect device configuration
3. Write initial config to `/opt/scripts/files/lcon`
4. Download and install required components
5. Build and burn initial ISO
6. Reboot into configured system

---

## 16. RELATED DOCUMENTATION

| Document | Location | Purpose |
|----------|----------|---------|
| ARM Porting Notes | `docs/ARM_PORTING_NOTES.md` | x86 dependencies, ARM64 requirements |
| Scripts Reference | `docs/SCRIPTS_REFERENCE.md` | Complete script inventory |
| This Document | `KIOSK_BOOT_ANALYSIS.md` | Boot sequence and architecture |

---

## Document History
- Created: 2024 during ISO analysis
- Updated: 2026-01-12 - Added complete reconfiguration flow, resolved gaps, documented server-provisioned scripts
- Updated: 2026-01-12 - Documented observed reconfiguration process from screenshots (burning to partition 2, component downloads)
- Updated: 2026-01-12 - Split documentation into multiple files, added replacement script templates, comprehensive agent exploration
- Purpose: Trace boot and reconfiguration process for ARM porting project

## Files Analyzed

| File | Location | Lines |
|------|----------|-------|
| init | boot/initrd.xz | 146 |
| fatal | boot/initrd.xz | 49 |
| daemon.sh | xzm/zz-settings/etc/rc.d/local_net.d/ | 65 |
| greyos_reboot | xzm/zz-settings/opt/scripts/files/ | 23 |
| wizard | xzm/zz-settings/opt/scripts/ | ~385 |
| welcome | xzm/zz-settings/opt/scripts/ | 617 |
| wizard-now | xzm/zz-settings/opt/scripts/ | 27 |
| autostart | 003-settings.xzm:/etc/xdg/openbox/ | 293 |
| pkget | 003-settings.xzm:/opt/scripts/ | ~20 |
| pktunnel | 003-settings.xzm:/usr/sbin/ | 117 |
| rc.S | 003-settings.xzm:/etc/rc.d/ | ~80 |
| xinitrc | 003-settings.xzm:/etc/X11/xinit/ | ~15 |
| screen-setup | 003-settings.xzm:/opt/scripts/ | ~400 |
| persistence | 003-settings.xzm:/opt/scripts/ | ~50 |
