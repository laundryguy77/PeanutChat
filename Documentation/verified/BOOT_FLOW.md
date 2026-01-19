# TuxOS ARM64 Boot Flow Documentation

## Document Information

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Created | 2026-01-18 |
| Platform | ARM64 (Raspberry Pi 4) |
| Status | Verified from source analysis |
| Line Target | 800-1000 lines |

---

## Executive Summary

TuxOS ARM64 implements a streamlined kiosk boot sequence designed for single-application deployment on Raspberry Pi 4. The boot flow progresses through five distinct phases:

1. **PID 1 Init** (`/sbin/init`) - Custom busybox shell script replacing systemd
2. **System Initialization** (`/etc/rc.d/rc.S`) - Mounts, udev, GPU modules, network prep
3. **X11 Startup** (`/etc/rc.d/rc.4`) - D-Bus, dynamic xinitrc generation, X server launch
4. **Desktop Session** (`/etc/xdg/openbox/autostart`) - Input setup, first-run check, browser launch
5. **First-Run Wizard** (`/opt/scripts/first-run`) - Network wizard, device config, SD installation

The ARM64 port differs significantly from x86: no systemd, no XDM, no inittab-based runlevels. Instead, it uses a simple linear script chain that is easier to debug and modify.

---

## Boot Flow Overview Diagram

```
POWER ON
    |
    v
+------------------+
| Raspberry Pi     |
| Bootloader       |
| (GPU firmware)   |
+------------------+
    |
    v
+------------------+
| Linux Kernel     |
| kernel8.img      |
| (aarch64)        |
+------------------+
    |
    v
+------------------+
| Initramfs        |
| initrd.img       |
| (AUFS setup)     |
+------------------+
    |
    v
+----------------------------------------------------------+
|                    UNION ROOTFS                          |
| /sbin/init  ->  rc.S  ->  rc.4  ->  autostart  ->  GUI   |
+----------------------------------------------------------+
    |               |         |           |            |
    v               v         v           v            v
  PID 1          udev      xinit      first-run    browser
 busybox      GPU mods    openbox     welcome     kiosk mode
```

---

## Phase 1: PID 1 Init Script

### File Reference
- **Path:** `/home/culler/saas_dev/pk-port/arm64/003-settings-rootfs/sbin/init`
- **Lines:** 56
- **Interpreter:** `#!/bin/busybox sh`

### Purpose

The init script is PID 1, the first userspace process. It replaces systemd with a simple shell script that:
1. Mounts essential filesystems
2. Runs system initialization (rc.S)
3. Runs graphical startup (rc.4)
4. Enters an eternal wait loop (PID 1 must never exit)

### Detailed Trace

```
[init:7]  echo "[init] Starting PID 1 init script..."
                |
                v
[init:9-11] Remount root read-write
            mount -o remount,rw /
                |
                v
[init:13-22] Mount essential filesystems (if not already mounted):
            - /proc   (proc)
            - /sys    (sysfs)
            - /dev    (devtmpfs)
            - /dev/pts (devpts)
            - /dev/shm (tmpfs)
            - /run    (tmpfs)
                |
                v
[init:24-25] Set PATH and hostname
            export PATH=/sbin:/bin:/usr/sbin:/usr/bin
            echo "kiosk" > /proc/sys/kernel/hostname
                |
                v
[init:32-39] Check and run rc.S
            if [ -x /etc/rc.d/rc.S ]; then
                /etc/rc.d/rc.S
            fi
                |
                v
[init:41-48] Check and run rc.4
            if [ -x /etc/rc.d/rc.4 ]; then
                /etc/rc.d/rc.4
            fi
                |
                v
[init:50-56] Eternal wait loop (zombie reaper)
            while true; do
                wait 2>/dev/null
                sleep 1
            done
```

### Key Implementation Details

| Line | Code | Purpose |
|------|------|---------|
| `init:1` | `#!/bin/busybox sh` | Uses busybox shell, not bash |
| `init:11` | `mount -o remount,rw / 2>/dev/null` | AUFS union is read-only initially |
| `init:15-17` | `mountpoint -q` checks | Prevents double-mounting |
| `init:19` | `mkdir -p /dev/pts /dev/shm /run` | Creates required directories |
| `init:28` | `echo "kiosk" > /proc/sys/kernel/hostname` | Sets hostname without hostname command |
| `init:36` | `/etc/rc.d/rc.S` | Synchronous call - waits for completion |
| `init:45` | `/etc/rc.d/rc.4` | Synchronous call - waits for completion |
| `init:52-56` | `while true; wait; sleep 1; done` | PID 1 must never exit |

### x86 vs ARM64 Differences

| Aspect | x86 | ARM64 |
|--------|-----|-------|
| Init system | inittab + sysvinit | Custom busybox script |
| Runlevels | 4 (GUI) via inittab | None - direct script calls |
| rc.S call | Via `si:S:sysinit:` | Direct call from init |
| rc.4 call | Via `x1:4:respawn:` | Direct call from init |
| Process reaping | Built into sysvinit | Manual `wait` in loop |

---

## Phase 2: System Initialization (rc.S)

### File Reference
- **Path:** `/home/culler/saas_dev/pk-port/arm64/003-settings-rootfs/etc/rc.d/rc.S`
- **Lines:** 153
- **Interpreter:** `#!/bin/sh`

### Purpose

rc.S initializes the system hardware and services:
1. Mounts virtual filesystems (/proc, /sys, /dev)
2. Creates runtime directories
3. Starts udev for device management
4. Loads GPU kernel modules (vc4, v3d)
5. Configures network interface
6. Runs ldconfig

### Detailed Trace

```
[rc.S:5]   echo "=== rc.S: Starting system initialization ==="
                |
                v
[rc.S:7-24] Mount virtual filesystems:
            mount -t proc proc /proc           [rc.S:8]
            mount -t sysfs sysfs /sys          [rc.S:9]
            mount -t devtmpfs devtmpfs /dev    [rc.S:10]
            mkdir -p /dev/pts /dev/shm         [rc.S:13]
            mount -t devpts devpts /dev/pts    [rc.S:14]
            mount -t tmpfs tmpfs /dev/shm      [rc.S:15]
            mount -t tmpfs tmpfs /tmp          [rc.S:19]
            mount -t tmpfs tmpfs /run          [rc.S:23]
                |
                v
[rc.S:25-31] Create runtime directories:
            mkdir -p /run/dbus /run/lock /run/user /run/udev
            mkdir -p /var/log /var/tmp
            mkdir -p /tmp/.X11-unix
            chmod 1777 /tmp/.X11-unix
            ln -sf /run /var/run
                |
                v
[rc.S:33-36] Redirect output and set hostname:
            exec >/dev/console 2>&1
            hostname kiosk
                |
                v
[rc.S:38-67] Start udev:
            /lib/systemd/systemd-udevd --daemon  [rc.S:44]
            sleep 2                               [rc.S:45]
            udevadm trigger --action=add          [rc.S:56]
            udevadm settle --timeout=10           [rc.S:57]
                |
                v
[rc.S:69-97] Load GPU kernel modules:
            modprobe drm                          [rc.S:73]
            modprobe drm_kms_helper                [rc.S:75]
            modprobe vc4                           [rc.S:77]
            modprobe v3d                           [rc.S:79]
            udevadm trigger --subsystem-match=drm  [rc.S:83]
            udevadm settle --timeout=5             [rc.S:84]
                |
                v
[rc.S:99-147] Setup networking:
            get_eth_iface()                       [rc.S:103-113]
            Wait for interface (10 retries)       [rc.S:116-125]
            ip link set "$ETH_IFACE" up           [rc.S:133]
            /usr/sbin/dhcpcd -b "$ETH_IFACE" &    [rc.S:139]
                |
                v
[rc.S:149-152] Finalize:
            ldconfig
            echo "System initialization complete"
```

### Network Interface Detection

The script auto-detects the first Ethernet interface:

```bash
# rc.S:103-113
get_eth_iface() {
    for iface in /sys/class/net/*; do
        iface=$(basename "$iface")
        [ "$iface" = "lo" ] && continue              # Skip loopback
        [ -d "/sys/class/net/$iface/wireless" ] && continue  # Skip WiFi
        [ -e "/sys/class/net/$iface/device" ] || continue    # Skip virtual
        echo "$iface"
        return
    done
}
```

On Raspberry Pi 4, this typically returns `eth0` or `end0`.

### GPU Module Loading

The vc4 and v3d modules are required for hardware-accelerated graphics:

| Module | Purpose | Line |
|--------|---------|------|
| `drm` | Direct Rendering Manager base | `rc.S:73` |
| `drm_kms_helper` | Kernel Mode Setting helper | `rc.S:75` |
| `vc4` | VideoCore 4 GPU driver | `rc.S:77` |
| `v3d` | VideoCore 3D acceleration | `rc.S:79` |

After loading, the script re-triggers udev to create `/dev/dri/card*` nodes (`rc.S:83-84`).

### x86 vs ARM64 Differences

| Aspect | x86 | ARM64 |
|--------|-----|-------|
| GPU modules | Varies (Intel/AMD/NVIDIA) | vc4, v3d (Pi-specific) |
| Network interface | eth0 (predictable names) | end0 or eth0 |
| DHCP client | dhcpcd or udhcpc | dhcpcd preferred |
| Persistence script | `/opt/scripts/persistence` | Not used (simplified) |

---

## Phase 3: X11 Startup (rc.4)

### File Reference
- **Path:** `/home/culler/saas_dev/pk-port/arm64/003-settings-rootfs/etc/rc.d/rc.4`
- **Lines:** 153
- **Interpreter:** `#!/bin/bash`

### Purpose

rc.4 starts the graphical environment:
1. Mounts persistent log partition
2. Initializes debugging (boot-capture, flow-logger)
3. Starts D-Bus system daemon
4. Creates dynamic xinitrc script
5. Launches X server with Openbox

### Detailed Trace

```
[rc.4:5-11] Mount persistent log partition:
            mkdir -p /mnt/logs
            for dev in /dev/mmcblk0p4 /dev/sda4; do
                mount "$dev" /mnt/logs && break
            done
                |
                v
[rc.4:13-21] Initialize debugging:
            /opt/scripts/boot-capture init        [rc.4:14]
            /opt/scripts/boot-capture system      [rc.4:15]
            /opt/scripts/boot-capture scripts     [rc.4:16]
            source /opt/scripts/flow-logger       [rc.4:19]
            flow-logger init                      [rc.4:20]
            flow_enter "rc.4"                     [rc.4:21]
                |
                v
[rc.4:35-52] Start D-Bus system daemon:
            export HOME=/root USER=root           [rc.4:36-37]
            if ! pidof dbus-daemon; then
                dbus-daemon --system              [rc.4:45]
            fi
                |
                v
[rc.4:54-132] Create dynamic xinitrc:
            cat > /tmp/.xinitrc << 'XINIT'
            #!/bin/sh
            # ... (see below for full content)
            XINIT
            chmod +x /tmp/.xinitrc
                |
                v
[rc.4:144-152] Launch X server:
            touch /root/.Xauthority
            chmod 600 /root/.Xauthority
            xinit /tmp/.xinitrc -- /usr/lib/xorg/Xorg :0 vt1 \
                -nolisten tcp -logfile "$XORG_LOG" &
```

### Dynamic xinitrc Content

The xinitrc is generated as a heredoc at `rc.4:56-129`:

```bash
#!/bin/sh
# Diagnostic xinitrc for Porteus Kiosk ARM64

touch /mnt/logs/xinitrc_started

exec >> /mnt/logs/xinitrc.log 2>&1
set -x

echo "=== xinitrc starting ==="
echo "DISPLAY=$DISPLAY"

# Set library path
export LD_LIBRARY_PATH=/usr/lib/aarch64-linux-gnu:/lib/aarch64-linux-gnu:/usr/lib:/lib

# Run ldconfig
ldconfig

# Verify openbox
which openbox
ldd /usr/bin/openbox 2>&1 | grep -i "not found" || echo "All libraries found"

# Start D-Bus session
eval $(dbus-launch --sh-syntax)
export DBUS_SESSION_BUS_ADDRESS

# Set background
xsetroot -solid "#404040"

# Start openbox with autostart
/usr/bin/openbox --startup /usr/lib/aarch64-linux-gnu/openbox-autostart &
OPENBOX_PID=$!

wait $OPENBOX_PID
```

### Key Implementation Details

| Line | Code | Purpose |
|------|------|---------|
| `rc.4:6-10` | Loop over `/dev/mmcblk0p4`, `/dev/sda4` | Tries SD card first, then USB |
| `rc.4:19` | `source /opt/scripts/flow-logger` | Loads logging functions |
| `rc.4:45` | `dbus-daemon --system` | Required for desktop services |
| `rc.4:56` | `cat > /tmp/.xinitrc << 'XINIT'` | Heredoc creates startup script |
| `rc.4:73-74` | `export LD_LIBRARY_PATH=...` | ARM64 library paths |
| `rc.4:109` | `openbox --startup /usr/lib/aarch64-linux-gnu/openbox-autostart` | Triggers autostart |
| `rc.4:149` | `xinit ... &` | Runs in background so rc.4 returns |

### x86 vs ARM64 Differences

| Aspect | x86 | ARM64 |
|--------|-----|-------|
| Display manager | XDM (`/usr/bin/xdm`) | None - direct xinit |
| xinitrc | Static `/etc/X11/xinit/xinitrc` | Dynamic `/tmp/.xinitrc` |
| Library path | `/usr/lib` | `/usr/lib/aarch64-linux-gnu` |
| Openbox autostart path | `/usr/libexec/openbox-autostart` | `/usr/lib/aarch64-linux-gnu/openbox-autostart` |
| VT | vt7 | vt1 |

---

## Phase 4: Desktop Session (autostart)

### File Reference
- **Path:** `/home/culler/saas_dev/pk-port/arm64/003-settings-rootfs/etc/xdg/openbox/autostart`
- **Lines:** 179
- **Interpreter:** `#!/bin/sh`

### Purpose

The autostart script runs after Openbox is ready:
1. Sets up input devices (keyboard, mouse)
2. Configures screen (backlight, DPMS)
3. Runs boot-capture in background
4. Checks for and runs first-run wizard
5. Waits for network gateway
6. Runs boot configuration script
7. Launches browser in kiosk mode

### Detailed Trace

```
[autostart:1-19] Initialize logging:
                LOG="/mnt/logs/autostart.log"
                exec >> "$LOG" 2>&1
                set -x
                echo "=== AUTOSTART STARTING $(date) ==="
                echo "PID: $$, USER: $(whoami), DISPLAY: $DISPLAY"
                    |
                    v
[autostart:21-22] Source variables:
                [ -f /etc/profile.d/variables.sh ] && . /etc/profile.d/variables.sh
                    |
                    v
[autostart:28-30] Input setup:
                setxkbmap -layout us
                xmodmap -e "pointer = 1 2 32 4 5 6 7..."
                    |
                    v
[autostart:32-35] Screen setup:
                for x in /sys/class/backlight/*; do
                    echo "$(cat "$x/max_brightness")" > "$x/brightness"
                done
                    |
                    v
[autostart:37-50] D-Bus and notification daemon:
                if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
                    eval $(dbus-launch --sh-syntax)
                fi
                dunst &                            [autostart:47]
                    |
                    v
[autostart:52-54] Disable screen saver:
                xset -dpms
                xset s 0
                xset s noblank
                    |
                    v
[autostart:56-61] Boot capture (background):
                /opt/scripts/boot-capture init &
                /opt/scripts/boot-capture system &
                /opt/scripts/boot-capture display &
                    |
                    v
[autostart:63-77] First-run check:
                if [ -e /opt/scripts/first-run ]; then
                    log "Running first-run wizard..."
                    /opt/scripts/first-run           [autostart:68]
                    log "first-run exited with code: $?"
                fi
                    |
                    v
[autostart:79-101] Wait for network gateway:
                GTW=0; SLEEP=120
                while [ "$GTW" -lt 1 ] && [ "$SLEEP" -gt 0 ]; do
                    GTW=$(route -n | grep -c " UG ")
                    [ "$GTW" -lt 1 ] && sleep 1
                    SLEEP=$((SLEEP - 1))
                done
                    |
                    v
[autostart:103-121] Run boot config:
                BOOT_CONFIG="/opt/scripts/arm64-boot-config.sh"
                if [ -x "$BOOT_CONFIG" ]; then
                    "$BOOT_CONFIG"
                fi
                    |
                    v
[autostart:123-171] Launch browser:
                HOMEPAGE=$(grep "^homepage=" "$LCON" | cut -d= -f2-)
                if [ -x /opt/scripts/gui-app ]; then
                    /opt/scripts/gui-app &
                else
                    $BROWSER --kiosk "$HOMEPAGE" &
                fi
                    |
                    v
[autostart:176-178] Keep session alive:
                while true; do sleep 60; done
```

### First-Run Detection

The first-run check at `autostart:66-69`:

```bash
if [ -e /opt/scripts/first-run ]; then
    log "Running first-run wizard..."
    /opt/scripts/first-run
    log "first-run exited with code: $?"
fi
```

This is a **synchronous call** - autostart blocks until first-run completes.

### Network Wait Loop

The network wait at `autostart:79-101` waits up to 120 seconds for a default gateway:

```bash
GTW=0
SLEEP=120
while [ "$GTW" -lt 1 ] && [ "$SLEEP" -gt 0 ]; do
    GTW=$(route -n 2>/dev/null | grep -c " UG " | tr -d '[:space:]')
    GTW=${GTW:-0}
    if [ "$GTW" -lt 1 ]; then
        if [ "$SLEEP" = "60" ]; then
            # At 60s mark, restart networking
            [ -x /etc/rc.d/rc.inet1 ] && /etc/rc.d/rc.inet1
        fi
        sleep 1
        SLEEP=$((SLEEP - 1))
    fi
done
```

### Browser Detection and Launch

At `autostart:138-170`, the script detects available browsers:

```bash
if [ -x /opt/google/chrome/chrome ]; then
    BROWSER="chrome"
elif command -v chromium >/dev/null 2>&1; then
    BROWSER="chromium"
elif command -v firefox >/dev/null 2>&1; then
    BROWSER="firefox"
fi

if [ -x /opt/scripts/gui-app ]; then
    /opt/scripts/gui-app &
else
    case "$BROWSER" in
        chrome)
            /opt/google/chrome/chrome --kiosk --no-first-run \
                --disable-translate --disable-infobars "$HOMEPAGE" &
            ;;
        ...
    esac
fi
```

### x86 vs ARM64 Differences

| Aspect | x86 | ARM64 |
|--------|-----|-------|
| Line count | ~293 | 179 |
| first-run check | `su -c /opt/scripts/first-run` | Direct call (already root) |
| update-config | Separate script | Unified `arm64-boot-config.sh` |
| update script | Separate script | Unified `arm64-boot-config.sh` |
| Session keep-alive | `while true; sleep 60` | Same |

---

## Phase 5: First-Run Wizard

### File Reference
- **Path:** `/home/culler/saas_dev/pk-port/arm64/003-settings-rootfs/opt/scripts/first-run`
- **Lines:** 476+
- **Interpreter:** `#!/bin/sh` (calls bash scripts)

### Purpose

The first-run script orchestrates initial device configuration:
1. Creates default `/tmp/log/md5` for kiosk version
2. Generates machine ID from MAC address
3. Calls welcome script (network configuration)
4. Processes network configuration
5. Calls wizard script (device configuration)
6. Downloads required components
7. Burns SD card with configured system

### Detailed Trace

```
[first-run:6-11] Setup version file:
                mkdir -p /tmp/log
                if [ ! -f /tmp/log/md5 ]; then
                    echo "kiosk_version=Client" > /tmp/log/md5
                fi
                    |
                    v
[first-run:13-28] Get machine ID:
                version=$(grep kiosk_version /tmp/log/md5 | cut -d= -f2-)
                fmac=$(ip link | grep 'link/ether' | head -n1 | awk '{print $2}')
                fID="$(echo `echo $fmac | cut -c1,3,5,7,9,11,13`...)"
                sed -i 's/NOT_AVAILABLE/'$fID'/g' /etc/version
                    |
                    v
[first-run:39] Define cleanup function:
                cleanup() {
                    killall firefox chrome
                    rm -rf $pth /mnt/VER /tmp/config* /tmp/md5sum /tmp/log
                    rm -f /opt/scripts/first-run /opt/scripts/wizard
                }
                    |
                    v
[first-run:40-189] Define welcome() function:
                welcome() {
                    killall dhcpcd wpa_supplicant wvdial
                    rm -f /etc/resolv.conf
                    mkdir -p /tmp/knet
                    printf '0' > /tmp/knet/.knetPage
                    /opt/scripts/welcome              [first-run:51]
                    # ... process config values ...
                }
                    |
                    v
[first-run:227] Call welcome:
                welcome
                    |
                    v
[first-run:228-232] Choose browser module:
                if [ $browser = chrome ]; then
                    rm -f $pth/xzm/002-firefox.xzm
                else
                    rm -f $pth/xzm/002-chrome.xzm
                fi
                    |
                    v
[first-run:233-237] Run wizard:
                sh /opt/scripts/wizard
                while [ -e /tmp/wizard-lock ]; do
                    rm -r /tmp/kwiz.*
                    sh /opt/scripts/wizard
                done
                    |
                    v
[first-run:262-298] Download components:
                for x in $components; do
                    fetch_component
                done
                    |
                    v
[first-run:338-454] Burn to SD card:
                burn_ISO()
```

### Welcome Script Call

At `first-run:40-189`, the welcome() function:

```bash
welcome() {
    killall dhcpcd wpa_supplicant wvdial 2>/dev/null
    killall dhcpcd wpa_supplicant wvdial 2>/dev/null
    rm -f /etc/resolv.conf /etc/ppp/resolv.conf
    unset http_proxy https_proxy ftp_proxy no_proxy

    # ARM64 FIX: Pre-create page file
    mkdir -p /tmp/knet
    printf '0' > /tmp/knet/.knetPage
    sync

    # Call welcome script
    /opt/scripts/welcome >>/mnt/logs/welcome.log 2>&1

    # Read values from /tmp/config
    value() { grep "^$1=" /tmp/config | head -n1 | cut -d= -f2-; }
    iface=$(value network_interface)
    ip=$(value ip_address)
    # ... more values ...
}
```

### Wizard Script Call

At `first-run:233-237`:

```bash
sh /opt/scripts/wizard >/dev/null 2>&1
while [ -e /tmp/wizard-lock ]; do
    rm -r /tmp/kwiz.*
    sh /opt/scripts/wizard >/dev/null 2>&1
done
```

The loop allows users to restart the wizard if needed.

### SD Card Burning (ARM64 Specific)

At `first-run:338-454`, the `burn_ISO()` function handles Raspberry Pi SD card installation:

```bash
burn_ISO() {
    local burn_dev="$burn"

    # Validate target device
    if [ ! -b "/dev/$burn_dev" ]; then
        dunstify -u critical "Target device /dev/$burn_dev not found!"
        return 1
    fi

    # Partition naming (mmcblk0p1 vs sda1)
    case "$burn_dev" in
        mmcblk*|nvme*) prtt="p" ;;
        *) prtt="" ;;
    esac

    # Partition the device
    sfdisk "/dev/$burn_dev" << EOF
label: dos
unit: sectors
1 : size=64M, type=c, bootable
2 : size=${data_size}M, type=83
4 : size=64M, type=83
EOF

    # Format partitions
    mkfs.vfat -F 32 -n "BOOT" "/dev/${burn_dev}${prtt}1"
    mkfs.ext4 -L "Kiosk" "/dev/${burn_dev}${prtt}2"
    mkfs.ext4 -L "StorageBkp" "/dev/${burn_dev}${prtt}4"

    # Copy boot files
    mount "/dev/${burn_dev}${prtt}1" /mnt/burn_boot
    cp /mnt/ISO/boot/* /mnt/burn_boot/

    # Copy system files
    mount "/dev/${burn_dev}${prtt}2" /mnt/burn_data
    cp -r /mnt/kiosk/xzm /mnt/burn_data/
    cp -r /mnt/kiosk/docs /mnt/burn_data/

    reboot
}
```

---

## Sub-Phase 5a: Welcome Script (Network Wizard)

### File Reference
- **Path:** `/home/culler/saas_dev/pk-port/arm64/003-settings-rootfs/opt/scripts/welcome`
- **Lines:** 679
- **Interpreter:** `#!/bin/bash`

### Purpose

GTKDialog-based network configuration wizard with 8 pages:
- Page 0: Ethernet/WiFi selection
- Page 1: Dialup configuration
- Page 2: DHCP/Manual choice
- Page 3: Manual IP configuration
- Page 4: Wireless password entry
- Page 5: Proxy settings
- Page 6: Browser choice
- Page 7: Confirmation/Report

### Key Implementation

```bash
# welcome:60-72 - Setup TMP directory
[ -d $TMP ] && rm -rf $TMP
mkdir $TMP
echo 0 > $TMP/.knetPage      # Initialize page to 0

# welcome:87-629 - Build WIZARD_PRE GTKDialog XML
export WIZARD_PRE='
<window title="TuxOS Wizard" ...>
<vbox>
<notebook page="0" show-tabs="false" ...>
  <!-- Page 0: Welcome -->
  <!-- Page 1: Dialup -->
  <!-- Page 2: DHCP/Manual -->
  <!-- Page 3: Manual config -->
  <!-- Page 4: Wireless -->
  <!-- Page 5: Proxy -->
  <!-- Page 6: Browser -->
  <!-- Page 7: Confirm -->
</notebook>
</vbox>
</window>'

# welcome:663 - Launch GTKDialog
echo "$WIZARD_PRE" | sed '/^##/d' | \
    gtkdialog -i /opt/scripts/files/wizard/wizard-functions -s -c > $TMP/output

# welcome:678 - Copy report to config
cp -a /tmp/report /tmp/config
```

### Page Navigation

The notebook widget uses a hidden file (`$TMP/.knetPage`) to track the current page:

```xml
<notebook page="0" show-tabs="false" ...>
  <variable>nPage</variable>
  <input file>$TMP/.knetPage</input>
</notebook>
```

Button actions write to this file and refresh:
```xml
<button>
  <label>Ethernet</label>
  <action>echo 7 > $TMP/.knetPage</action>
  <action>refresh:nPage</action>
</button>
```

---

## Sub-Phase 5b: Wizard Script (Device Configuration)

### File Reference
- **Path:** `/home/culler/saas_dev/pk-port/arm64/003-settings-rootfs/opt/scripts/wizard`
- **Lines:** 322
- **Interpreter:** `#!/bin/sh`

### Purpose

GTKDialog-based device configuration with password protection:
1. Authorization page (password entry)
2. Device configuration (Type/Facility/Number)
3. Target device selection for installation

### Key Implementation

```bash
# wizard:34 - Initialize page
echo 0 > $TMPDIR/.knetPage

# wizard:36-53 - Refresh block devices
refresh_block_devices() {
    lsblk -d -o NAME,TYPE,MODEL,SIZE | egrep -v 'NAME|loop|rom' > $TMPDIR/block.txt
}

# wizard:71-122 - Build WIZARD_MAIN dialog
WIZARD_MAIN='
<window title="TuxOS Wizard" ...>
  <text><label>Please enter the password...</label></text>
  <entry visibility="false">
    <variable>CID</variable>
    <action signal="changed">echo $CID > $TMPDIR/configuration.id</action>
  </entry>
  <button>
    <label>Install OS</label>
    <action function="exit">finished</action>
  </button>
</window>'

# wizard:124-128 - Fetch password key
if curl cullerdigitalmedia.com/peanutos/files/key.txt >> $TMPDIR/drivekey.txt; then
    continue
else
    echo P@ss3264 > $TMPDIR/drivekey.txt
fi

# wizard:140-322 - Password check loop
while ([ "$CID" != "$DRIVEKEY" ]); do
    gtkdialog ... > $TMPDIR/output
    CID=$(cat $TMPDIR/configuration.id)

    if [ "$CID" = "$DRIVEKEY" ]; then
        # Show device config dialog
        export DIALOG='...'
        gtkdialog --program DIALOG

        # Build config URL based on device type
        if [ "$DEVTYPE" = "Kiosk" ]; then
            FINCONFIG="$BASEURL/kc/$FACNAM/$FACNAM_ks$DEVNUM.txt"
        fi

        # Write to config
        echo burn_dev="$tblTarget" >> /tmp/config
        echo kiosk_config="$FINCONFIG" >> /tmp/config
    fi
done
```

---

## x86 Process Tree Reference

From `term_out.txt` analysis, the x86 process hierarchy is:

```
PID 1: init [4]
  |
  +-- PID 358: /bin/sh /usr/bin/xdm
        |
        +-- PID 363: bash -c /usr/bin/startx -- -nolisten tcp vt7
              |
              +-- PID 376: /bin/sh /usr/bin/startx
                    |
                    +-- PID 424: xinit /etc/X11/xinit/xinitrc -- /usr/bin/X :0
                          |
                          +-- PID 425: /usr/bin/X :0 -nolisten tcp vt7
                          |
                          +-- PID 438: /bin/sh /etc/X11/xinit/xinitrc
                                |
                                +-- PID 440: /usr/bin/openbox --startup /usr/libexec/openbox-autostart
                                      |
                                      +-- PID 449: /bin/sh /usr/libexec/openbox-autostart
                                            |
                                            +-- PID 458: sh /etc/xdg/openbox/autostart
                                                  |
                                                  +-- PID 4358: bash -c /opt/scripts/first-run
                                                        |
                                                        +-- PID 4359: /bin/ash /opt/scripts/first-run
                                                              |
                                                              +-- PID 4426: sh /opt/scripts/welcome
                                                                    |
                                                                    +-- PID 4484: gtkdialog -i wizard-functions -s -c
                                                              |
                                                              +-- PID 23914: sh /opt/scripts/wizard
                                                                    |
                                                                    +-- PID 7253: gtkdialog -i wizard-functions -s -c
```

### PID Trace Summary

| PID | Process | Parent | File:Line |
|-----|---------|--------|-----------|
| 1 | init | kernel | `/sbin/init` |
| 358 | xdm | 1 | `/usr/bin/xdm` |
| 363 | startx wrapper | 358 | - |
| 376 | startx | 363 | `/usr/bin/startx` |
| 424 | xinit | 376 | `xinit xinitrc -- /usr/bin/X :0` |
| 425 | X server | 424 | `/usr/bin/X :0` |
| 438 | xinitrc | 424 | `/etc/X11/xinit/xinitrc` |
| 440 | openbox | 438 | `xinitrc:20` |
| 449 | openbox-autostart | 440 | `/usr/libexec/openbox-autostart` |
| 458 | autostart | 449 | `/etc/xdg/openbox/autostart` |
| 4358 | first-run wrapper | 458 | `autostart:97` |
| 4359 | first-run | 4358 | `/opt/scripts/first-run` |
| 4426 | welcome | 4359 | `first-run:369` |
| 4484 | gtkdialog | 4426 | `welcome:636` |
| 23914 | wizard | 4359 | `first-run:551` |
| 7253 | gtkdialog | 23914 | `wizard:125` |

---

## ARM64 Process Tree

The ARM64 process tree is simpler due to no XDM:

```
PID 1: /sbin/init (busybox sh)
  |
  +-- /etc/rc.d/rc.S (runs synchronously, exits)
  |
  +-- /etc/rc.d/rc.4 (runs synchronously, returns after X starts)
        |
        +-- xinit /tmp/.xinitrc -- /usr/lib/xorg/Xorg :0 vt1
              |
              +-- /usr/lib/xorg/Xorg :0 vt1 (X server)
              |
              +-- /bin/sh /tmp/.xinitrc
                    |
                    +-- dbus-launch (session bus)
                    |
                    +-- /usr/bin/openbox --startup /usr/lib/aarch64-linux-gnu/openbox-autostart
                          |
                          +-- /bin/sh /usr/lib/aarch64-linux-gnu/openbox-autostart
                                |
                                +-- sh /etc/xdg/openbox/autostart
                                      |
                                      +-- /opt/scripts/first-run
                                            |
                                            +-- /opt/scripts/welcome
                                                  |
                                                  +-- gtkdialog -i wizard-functions -s -c
                                            |
                                            +-- /opt/scripts/wizard
                                                  |
                                                  +-- gtkdialog -i wizard-functions -s -c
                                      |
                                      +-- /opt/scripts/arm64-boot-config.sh
                                      |
                                      +-- browser (chromium/firefox) --kiosk
```

---

## Timing Dependencies

### Critical Order

```
init (PID 1)
  |
  +-- [SYNC] rc.S (must complete before rc.4)
  |     |
  |     +-- udev (must start before modprobe)
  |     +-- GPU modules (must load before X)
  |     +-- dhcpcd (background, async)
  |
  +-- [SYNC] rc.4 (must complete mount/logging before xinit)
        |
        +-- D-Bus system (must start before xinit)
        +-- [ASYNC] xinit (runs in background, rc.4 returns)
              |
              +-- [SYNC] xinitrc (waits for openbox)
                    |
                    +-- [SYNC] openbox (waits for autostart)
                          |
                          +-- [SYNC] autostart
                                |
                                +-- [SYNC] first-run (if exists)
                                |     |
                                |     +-- [SYNC] welcome (GTKDialog)
                                |     +-- [SYNC] wizard (GTKDialog)
                                |     +-- [SYNC] burn_ISO (if burn_dev set)
                                |
                                +-- [SYNC] wait for gateway (120s max)
                                +-- [SYNC] arm64-boot-config.sh
                                +-- [ASYNC] browser (in background)
                                +-- [LOOP] while true; sleep 60
```

### Timing Estimates

| Phase | Duration | Notes |
|-------|----------|-------|
| Kernel boot | ~5s | RPi4 boot time |
| Initramfs | ~10s | AUFS mount |
| rc.S | ~15s | udev, modules, DHCP start |
| rc.4 | ~3s | D-Bus, xinit launch |
| X startup | ~5s | Xorg, openbox init |
| autostart | ~3s | Before first-run check |
| first-run | Variable | User interaction |
| Network wait | 0-120s | Until gateway found |
| Browser launch | ~5s | Chromium cold start |

**Total boot time (no first-run):** ~45 seconds
**Total boot time (with first-run):** Depends on user

---

## Debugging and Logging

### Log File Locations

| Log | Path | Created By |
|-----|------|------------|
| rc.4 log | `/mnt/logs/rc4.log` | `rc.4:23-28` |
| xinitrc log | `/mnt/logs/xinitrc.log` | `/tmp/.xinitrc:64` |
| autostart log | `/mnt/logs/autostart.log` | `autostart:8-10` |
| welcome log | `/mnt/logs/welcome-debug.log` | `welcome:61-62` |
| boot capture | `/mnt/logs/boot-capture.log` | `boot-capture` |
| flow log | `/mnt/logs/flow.log` | `flow-logger` |
| Xorg log | `/mnt/logs/Xorg.0.log` | `rc.4:146` |

### Debug Scripts

**boot-capture** (`/opt/scripts/boot-capture`):
```bash
boot-capture init      # Initialize log
boot-capture system    # Capture system state
boot-capture scripts   # Capture all scripts
boot-capture display   # Capture X/GTK state
boot-capture prereqs   # Check wizard prerequisites
boot-capture all       # Full capture
```

**flow-logger** (`/opt/scripts/flow-logger`):
```bash
source /opt/scripts/flow-logger
flow_enter "script_name"
flow_checkpoint "script_name" "Reached milestone"
flow_exit "script_name" "$?"
```

---

## Cross-Reference Index

### Scripts by Phase

| Phase | Scripts |
|-------|---------|
| Phase 1 | `/sbin/init` |
| Phase 2 | `/etc/rc.d/rc.S` |
| Phase 3 | `/etc/rc.d/rc.4`, `/tmp/.xinitrc` |
| Phase 4 | `/etc/xdg/openbox/autostart` |
| Phase 5 | `/opt/scripts/first-run`, `/opt/scripts/welcome`, `/opt/scripts/wizard` |
| Post-boot | `/opt/scripts/arm64-boot-config.sh`, `/opt/scripts/gui-app` |

### Key Functions

| Function | Script | Line | Purpose |
|----------|--------|------|---------|
| `get_eth_iface()` | `rc.S` | 103-113 | Detect Ethernet interface |
| `log()` | `rc.4` | 26-29 | Log with prefix |
| `cleanup()` | `first-run` | 39 | Remove wizard after install |
| `welcome()` | `first-run` | 40-189 | Network configuration |
| `value()` | `first-run` | 52 | Read config values |
| `burn_ISO()` | `first-run` | 338-454 | SD card installation |
| `refresh_block_devices()` | `wizard` | 37-53 | List available disks |

### Configuration Files

| File | Purpose | Created By |
|------|---------|------------|
| `/tmp/config` | Wizard output | `welcome`, `wizard` |
| `/tmp/report` | Network config summary | `welcome` |
| `/tmp/knet/.knetPage` | Current wizard page | `welcome` |
| `/tmp/kwiz.$$/*` | Wizard temp files | `wizard` |
| `/opt/scripts/files/lcon` | Local config (runtime) | `arm64-boot-config.sh` |

---

## Error Handling

### Common Failure Points

| Failure | Symptom | Check |
|---------|---------|-------|
| No GPU modules | Black screen | `lsmod | grep vc4` |
| No network | Timeout at 120s | `ip link show`, `route -n` |
| gtkdialog missing | Wizard won't start | `which gtkdialog`, `ldd gtkdialog` |
| Missing icons | Blank buttons | Check `/usr/share/pixmaps/` |
| Wrong page | Wizard stuck on page 7 | Check `/tmp/knet/.knetPage` |

### Recovery

If boot fails, the initramfs has recovery logic:
1. Check partition 4 for `StorageBkp` label
2. Count boot failures in `boot.log`
3. If > 5 failures, restore from `system-backup.iso`

---

## Summary Table

| Phase | Script | PID | Duration | Key Action |
|-------|--------|-----|----------|------------|
| 1 | `/sbin/init` | 1 | ~1s | Mount filesystems, call rc.S/rc.4 |
| 2 | `/etc/rc.d/rc.S` | - | ~15s | udev, GPU modules, DHCP |
| 3 | `/etc/rc.d/rc.4` | - | ~3s | D-Bus, xinit, Openbox |
| 4 | `autostart` | - | ~3s | Input, first-run check |
| 5a | `first-run` | - | Variable | Orchestrate wizards |
| 5b | `welcome` | - | User | Network config |
| 5c | `wizard` | - | User | Device config |
| 6 | Browser | - | ~5s | Kiosk mode |

---

## Document Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-18 | 1.0 | Initial creation from source analysis |

---

## Related Documentation

- [SYSTEM_ARCHITECTURE.md](../SYSTEM_ARCHITECTURE.md) - Complete system reference
- [ARM_PORTING_NOTES.md](../ARM_PORTING_NOTES.md) - x86 to ARM64 differences
- [SCRIPTS_REFERENCE.md](../SCRIPTS_REFERENCE.md) - Script inventory
- [PARAM_REFERENCE.md](../PARAM_REFERENCE.md) - Configuration parameters
