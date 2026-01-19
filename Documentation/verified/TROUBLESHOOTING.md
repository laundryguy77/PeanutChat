# TuxOS ARM64 Troubleshooting Guide

## Document Information

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Created | 2026-01-19 |
| Platform | ARM64 (Raspberry Pi 4) |
| Status | Verified from debugging sessions |

---

## Table of Contents

1. [Wizard and UI Issues](#1-wizard-and-ui-issues)
2. [Network Issues](#2-network-issues)
3. [Display Issues](#3-display-issues)
4. [Boot Issues](#4-boot-issues)
5. [Browser Issues](#5-browser-issues)
6. [Configuration Issues](#6-configuration-issues)
7. [Debugging Commands Quick Reference](#7-debugging-commands-quick-reference)

---

## 1. Wizard and UI Issues

### 1.1 Welcome Wizard Opens on Wrong Page

**Symptom:**
- Welcome wizard opens on page 7 instead of page 0
- User cannot select Ethernet/WiFi options
- Wizard shows confirmation page immediately

**Cause:**
GTKDialog 0.8.3 notebook widget initialization bug. The `page="0"` attribute in the notebook tag is ignored when the widget first renders. GTKDialog reads the `<input file>` value before the notebook is fully initialized.

**Location:**
File: `/opt/scripts/welcome`
Lines: 91-97 (notebook definition)

**Solution:**
1. Pre-create the page tracking file before launching GTKDialog
2. Ensure the file contains "0" (not empty)
3. Add a small delay or use timer widget workaround

```bash
# In first-run, before calling welcome:
mkdir -p /tmp/knet
printf '0' > /tmp/knet/.knetPage
sync
```

Or use the timer widget workaround in welcome:
```xml
<timer visible="false" milliseconds="100">
  <action>echo 0 > /tmp/knet/.knetPage</action>
  <action>refresh:nPage</action>
</timer>
```

**Verification:**
```bash
cat /tmp/knet/.knetPage  # Should show: 0
# Launch wizard and verify it starts on page 0
```

---

### 1.2 GTKDialog Not Displaying

**Symptom:**
- Wizard script runs but no window appears
- Log shows gtkdialog started but no output
- Script hangs waiting for dialog

**Cause:**
Missing DISPLAY environment variable, missing libraries, or X server not running.

**Location:**
File: `/opt/scripts/welcome`
Lines: 663 (gtkdialog invocation)

**Solution:**
1. Ensure DISPLAY is set:
```bash
export DISPLAY=:0
```

2. Check gtkdialog dependencies:
```bash
ldd /usr/bin/gtkdialog | grep "not found"
```

3. Verify X server is running:
```bash
ps aux | grep Xorg
xdpyinfo | head -5
```

**Verification:**
```bash
DISPLAY=:0 gtkdialog --version
# Should output version number
```

---

### 1.3 Wizard Icons Not Displaying

**Symptom:**
- Wizard buttons appear but icons are blank/missing
- Layout looks broken without images

**Cause:**
Icon files not found in expected locations.

**Location:**
File: `/opt/scripts/files/wizard/`
Referenced in: `/opt/scripts/welcome`, `/opt/scripts/wizard`

**Solution:**
1. Verify icon files exist:
```bash
ls -la /opt/scripts/files/wizard/*.png
ls -la /usr/share/pixmaps/kiosk-*.png
```

2. Check icon paths in wizard XML match actual locations

3. Ensure icons are readable:
```bash
file /opt/scripts/files/wizard/*.png
```

**Verification:**
```bash
# All icons should be valid PNG files
for f in /opt/scripts/files/wizard/*.png; do
    file "$f" | grep -q "PNG image" && echo "OK: $f" || echo "BAD: $f"
done
```

---

### 1.4 Password Entry Not Working in Wizard

**Symptom:**
- Cannot type in password field
- Password comparison always fails
- Wizard loops indefinitely

**Cause:**
Entry widget visibility setting or signal handler not triggering.

**Location:**
File: `/opt/scripts/wizard`
Lines: 71-85 (password entry widget)

**Solution:**
1. Verify the entry widget has correct attributes:
```xml
<entry visibility="false">
  <variable>CID</variable>
  <action signal="changed">echo $CID > $TMPDIR/configuration.id</action>
</entry>
```

2. Check temp directory is writable:
```bash
touch /tmp/kwiz.$$/test && rm /tmp/kwiz.$$/test
```

**Verification:**
```bash
# After entering password in wizard:
cat /tmp/kwiz.$$/configuration.id
# Should contain entered password
```

---

## 2. Network Issues

### 2.1 Ethernet Interface Not Detected

**Symptom:**
- No network connectivity after boot
- `ip link` shows only loopback
- Scripts report "no interface found"

**Cause:**
Network driver module not loaded, or interface enumeration failing.

**Location:**
File: `/etc/rc.d/rc.S`
Lines: 99-147 (network setup)

**Solution:**
1. Verify network module is loaded:
```bash
lsmod | grep genet     # RPi 4
lsmod | grep smsc95xx  # RPi 3
lsmod | grep lan78xx   # RPi 3B+
```

2. Load module manually if missing:
```bash
modprobe bcm_genet  # RPi 4
modprobe smsc95xx   # RPi 3
```

3. Check device tree:
```bash
ls /sys/firmware/devicetree/base/soc/ethernet*
```

**Verification:**
```bash
ip link show
# Should show eth0 or end0 interface
```

---

### 2.2 Wrong Interface Name (eth0 vs end0)

**Symptom:**
- Scripts reference eth0 but interface is end0
- Network configuration fails
- DHCP doesn't start on correct interface

**Cause:**
Debian's predictable network interface naming creates end0 instead of eth0 on RPi 4.

**Location:**
File: `/etc/rc.d/rc.S`
Lines: 103-113 (get_eth_iface function)

**Solution:**
1. Use dynamic interface detection (preferred):
```bash
get_eth_iface() {
    for iface in /sys/class/net/*; do
        iface=$(basename "$iface")
        [ "$iface" = "lo" ] && continue
        [ -d "/sys/class/net/$iface/wireless" ] && continue
        [ -e "/sys/class/net/$iface/device" ] || continue
        echo "$iface"
        return
    done
}
```

2. Or disable predictable names via cmdline.txt:
```
net.ifnames=0
```

**Verification:**
```bash
ls /sys/class/net/
# Identify the correct interface name
cat /sys/class/net/*/address | head -1
# Verify MAC address matches expected
```

---

### 2.3 DHCP Not Obtaining Address

**Symptom:**
- Interface is up but no IP address
- `ip addr` shows no inet address
- Network timeout in autostart

**Cause:**
DHCP client not running, or DHCP server not responding.

**Location:**
File: `/etc/rc.d/rc.S`
Lines: 139 (dhcpcd invocation)

**Solution:**
1. Check dhcpcd is running:
```bash
ps aux | grep dhcpcd
```

2. Restart DHCP:
```bash
killall dhcpcd
dhcpcd -b eth0  # or end0
```

3. Check for DHCP server response:
```bash
dhcpcd -T eth0  # Test mode
```

4. Check dhcpcd logs:
```bash
cat /var/log/dhcpcd.log
```

**Verification:**
```bash
ip addr show eth0
# Should show inet 192.168.x.x or similar
route -n
# Should show default gateway
```

---

### 2.4 WiFi Not Connecting

**Symptom:**
- WiFi network selected but no connection
- wpa_supplicant not running
- No wireless interface visible

**Cause:**
Missing firmware, driver not loaded, or wpa_supplicant configuration error.

**Location:**
File: `/opt/scripts/welcome`
Lines: WiFi configuration section

**Solution:**
1. Load WiFi modules:
```bash
modprobe brcmfmac
```

2. Check firmware:
```bash
ls /lib/firmware/brcm/brcmfmac43455-sdio.*
```

3. Verify interface exists:
```bash
iw dev
```

4. Start wpa_supplicant manually:
```bash
wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant.conf
```

**Verification:**
```bash
iw dev wlan0 link
# Should show connected SSID
```

---

## 3. Display Issues

### 3.1 Black Screen After X Starts

**Symptom:**
- Console output stops, screen goes black
- X appears to start (process running) but nothing displays
- No error messages visible

**Cause:**
GPU modules not loaded, framebuffer not initialized, or X configuration error.

**Location:**
File: `/etc/rc.d/rc.S`
Lines: 69-97 (GPU module loading)
File: `/etc/rc.d/rc.4`
Lines: 144-152 (X startup)

**Solution:**
1. Verify GPU modules:
```bash
lsmod | grep vc4
lsmod | grep v3d
lsmod | grep drm
```

2. Check framebuffer:
```bash
ls -la /dev/fb*
ls -la /dev/dri/card*
```

3. Check Xorg log:
```bash
cat /mnt/logs/Xorg.0.log | grep -i error
cat /mnt/logs/Xorg.0.log | grep "(EE)"
```

4. Try basic X test:
```bash
DISPLAY=:0 xterm &
```

**Verification:**
```bash
DISPLAY=:0 xdpyinfo | head -10
# Should show display info
```

---

### 3.2 Wrong Resolution

**Symptom:**
- Display is too small, too large, or wrong aspect ratio
- UI elements cut off or scaled incorrectly

**Cause:**
HDMI mode not set correctly in config.txt.

**Location:**
File: `/boot/config.txt`

**Solution:**
1. Set specific resolution in config.txt:
```ini
# For 1920x1080
hdmi_group=2
hdmi_mode=82

# Force HDMI even without monitor
hdmi_force_hotplug=1
```

2. Or use automatic detection:
```ini
# Remove hdmi_group and hdmi_mode lines
# Let firmware auto-detect
```

3. Common modes:
```
hdmi_mode=82  # 1920x1080 60Hz
hdmi_mode=85  # 1280x720 60Hz
hdmi_mode=16  # 1024x768 60Hz
```

**Verification:**
```bash
xrandr
# Shows current resolution and available modes
```

---

### 3.3 Screen Goes Blank (DPMS)

**Symptom:**
- Screen blanks after inactivity
- Kiosk becomes unusable without input

**Cause:**
DPMS (Display Power Management) or screensaver enabled.

**Location:**
File: `/etc/xdg/openbox/autostart`
Lines: 52-54 (DPMS disable)

**Solution:**
Ensure these commands run in autostart:
```bash
xset -dpms
xset s 0
xset s noblank
xset s off
```

**Verification:**
```bash
DISPLAY=:0 xset q | grep -A2 "DPMS"
# Should show "DPMS is Disabled"
```

---

## 4. Boot Issues

### 4.1 System Hangs at "Waiting for network..."

**Symptom:**
- Boot stalls with network waiting message
- Progress stops for 120 seconds
- Eventually times out and continues

**Cause:**
Network interface not obtaining gateway, DHCP timeout.

**Location:**
File: `/etc/xdg/openbox/autostart`
Lines: 79-101 (network wait loop)

**Solution:**
1. Check cable connection
2. Verify DHCP server is responding
3. Reduce timeout in autostart if needed:
```bash
# Change SLEEP=120 to SLEEP=30 for faster timeout
```

4. Skip network wait for local testing:
```bash
# Add default route manually
ip route add default via 192.168.1.1
```

**Verification:**
```bash
route -n | grep UG
# Should show default gateway
ping -c1 8.8.8.8
# Should succeed if internet connected
```

---

### 4.2 GPU Modules Not Loading

**Symptom:**
- `/dev/dri/card0` doesn't exist
- X fails to start
- lsmod shows no vc4 module

**Cause:**
Module loading failed or dependencies missing.

**Location:**
File: `/etc/rc.d/rc.S`
Lines: 69-97 (GPU module loading)

**Solution:**
1. Load modules manually in order:
```bash
modprobe drm
modprobe drm_kms_helper
modprobe vc4
modprobe v3d
```

2. Check for errors:
```bash
dmesg | grep -i drm
dmesg | grep -i vc4
```

3. Verify device tree overlay:
```bash
# In config.txt:
dtoverlay=vc4-kms-v3d
```

**Verification:**
```bash
ls -la /dev/dri/
# Should show card0, renderD128
lsmod | grep vc4
# Should show vc4 module loaded
```

---

### 4.3 Boot Loop / Kernel Panic

**Symptom:**
- System reboots repeatedly
- Kernel panic message briefly visible
- Never reaches login/GUI

**Cause:**
Corrupted filesystem, missing init, or kernel mismatch.

**Location:**
Boot partition (FAT32), kernel8.img, initrd.img

**Solution:**
1. Connect serial console (GPIO pins 14/15)
2. Check kernel messages
3. Verify kernel matches modules:
```bash
# On working system:
uname -r
ls /lib/modules/
# Version should match
```

4. Rebuild initrd if needed

**Verification:**
```bash
# From serial console, check last messages
# Look for "Kernel panic" or "VFS: Cannot open root device"
```

---

### 4.4 AUFS Mount Failure

**Symptom:**
- Boot fails with AUFS error
- "No such device" for AUFS
- Falls back to busybox shell

**Cause:**
AUFS module not compiled into kernel or not in initramfs.

**Location:**
File: Kernel config, initrd

**Solution:**
1. Verify AUFS is available:
```bash
cat /proc/filesystems | grep aufs
modprobe aufs
```

2. Check kernel config:
```bash
zcat /proc/config.gz | grep AUFS
# Should show CONFIG_AUFS_FS=y or =m
```

3. If module, ensure it's in initramfs

**Verification:**
```bash
mount | grep aufs
# Should show union mount
```

---

## 5. Browser Issues

### 5.1 Homepage Not Loading

**Symptom:**
- Browser starts but shows error page
- "This site can't be reached"
- Blank white screen

**Cause:**
Network not ready, DNS not configured, or homepage URL invalid.

**Location:**
File: `/etc/xdg/openbox/autostart`
Lines: 123-171 (browser launch)
File: `/opt/scripts/files/lcon` (local config)

**Solution:**
1. Verify network is working:
```bash
ping -c1 google.com
```

2. Check DNS:
```bash
cat /etc/resolv.conf
nslookup google.com
```

3. Verify homepage setting:
```bash
grep "^homepage=" /opt/scripts/files/lcon
```

4. Test URL manually:
```bash
curl -I https://example.com
```

**Verification:**
```bash
# Homepage should be accessible:
curl -s https://your-homepage.com | head -10
```

---

### 5.2 Browser Crashes on Startup

**Symptom:**
- Browser window appears briefly then closes
- "Aw, Snap!" error page
- Browser process exits immediately

**Cause:**
Missing libraries, insufficient memory, or sandbox issues.

**Location:**
File: `/opt/scripts/gui-app`
File: `/etc/xdg/openbox/autostart`

**Solution:**
1. Check browser dependencies:
```bash
ldd /opt/google/chrome/chrome | grep "not found"
ldd /usr/bin/chromium | grep "not found"
```

2. Disable sandbox if running as root:
```bash
chromium --no-sandbox --disable-gpu-sandbox
```

3. Check memory:
```bash
free -m
# Ensure sufficient RAM
```

4. Check Chromium crash logs:
```bash
ls ~/.config/chromium/Crash\ Reports/
```

**Verification:**
```bash
# Start browser manually with verbose output:
chromium --no-sandbox --enable-logging=stderr --v=1 2>&1 | head -50
```

---

### 5.3 Browser Not Fullscreen

**Symptom:**
- Browser starts but not in kiosk mode
- Window has borders, address bar visible
- Can access browser settings

**Cause:**
Kiosk flags not passed to browser.

**Location:**
File: `/opt/scripts/gui-app`
File: `/etc/xdg/openbox/autostart`

**Solution:**
Ensure browser is launched with kiosk flags:
```bash
# Chrome
/opt/google/chrome/chrome --kiosk --no-first-run --disable-translate --disable-infobars "$URL"

# Chromium
chromium --kiosk --no-first-run --disable-translate --disable-infobars "$URL"

# Firefox
firefox --kiosk "$URL"
```

**Verification:**
```bash
ps aux | grep -E 'chrome|chromium|firefox' | grep kiosk
# Should show --kiosk flag in command line
```

---

## 6. Configuration Issues

### 6.1 Remote Config Not Applied

**Symptom:**
- Kiosk doesn't use remote configuration
- Falls back to default settings
- Config URL appears unreachable

**Cause:**
Network timing, URL incorrect, or config format invalid.

**Location:**
File: `/opt/scripts/arm64-boot-config.sh`
File: `/etc/rc.d/local_net.d/daemon.sh`

**Solution:**
1. Check config URL is accessible:
```bash
curl -v "https://your-config-server.com/kiosk/config.txt"
```

2. Verify config format:
```
homepage=https://example.com
browser=chrome
network_interface=eth0
```

3. Check for download errors:
```bash
cat /mnt/logs/daemon.log
```

**Verification:**
```bash
# Compare local config to remote:
cat /opt/scripts/files/lcon
curl https://your-config-server.com/kiosk/config.txt
```

---

### 6.2 Config Polling Failures

**Symptom:**
- Config updates not being applied
- daemon.sh not running
- Stale configuration

**Cause:**
Daemon not started or crashing.

**Location:**
File: `/etc/rc.d/local_net.d/daemon.sh`

**Solution:**
1. Check daemon is running:
```bash
ps aux | grep daemon.sh
```

2. Check daemon log:
```bash
cat /mnt/logs/daemon.log
```

3. Restart daemon:
```bash
/etc/rc.d/local_net.d/daemon.sh &
```

**Verification:**
```bash
# Monitor daemon activity:
tail -f /mnt/logs/daemon.log
```

---

### 6.3 Parameter Handler Errors

**Symptom:**
- Specific config parameters not working
- Partial configuration applied
- Handler script errors in log

**Cause:**
Handler script syntax error or missing dependency.

**Location:**
File: `/opt/scripts/param-handlers/XX-name.sh`

**Solution:**
1. Run handler manually:
```bash
export connection="dhcp"
export ip_address="192.168.1.100"
/opt/scripts/param-handlers/00-network.sh
echo $?  # Check exit code
```

2. Check handler syntax:
```bash
bash -n /opt/scripts/param-handlers/00-network.sh
```

**Verification:**
```bash
# Run all handlers with test config:
for h in /opt/scripts/param-handlers/*.sh; do
    echo "Running $h"
    bash "$h"
done
```

---

## 7. Debugging Commands Quick Reference

### System Status
```bash
uname -a
cat /proc/cpuinfo | head -10
free -m
df -h
cat /proc/cmdline
uptime
dmesg | tail -50
```

### Process Debugging
```bash
ps aux
pstree -p
top -bn1 | head -20
```

### Network Debugging
```bash
ip link show
ip addr show
ip route show
cat /etc/resolv.conf
ping -c3 8.8.8.8
curl -I https://google.com
ss -tulpn
```

### Display Debugging
```bash
DISPLAY=:0 xdpyinfo | head -20
DISPLAY=:0 xrandr
cat /mnt/logs/Xorg.0.log | grep -E "(EE)|error"
lsmod | grep -E "drm|vc4|v3d"
ls -la /dev/dri/
```

### Module Debugging
```bash
lsmod
modinfo vc4
dmesg | grep -i "module"
```

### GTKDialog Debugging
```bash
which gtkdialog
gtkdialog --version
ldd /usr/bin/gtkdialog
DISPLAY=:0 gtkdialog --help
```

### Log File Locations
```bash
cat /mnt/logs/rc4.log
cat /mnt/logs/xinitrc.log
cat /mnt/logs/autostart.log
cat /mnt/logs/welcome-debug.log
cat /mnt/logs/flow.log
cat /mnt/logs/Xorg.0.log
```

### Boot Capture
```bash
/opt/scripts/boot-capture all
cat /mnt/logs/boot-capture.log
```

---

## Cross-References

| Issue | Related Documentation |
|-------|----------------------|
| Boot flow | [BOOT_FLOW.md](BOOT_FLOW.md) |
| Script details | [SCRIPTS_REFERENCE.md](SCRIPTS_REFERENCE.md) |
| Config parameters | [CONFIG_SYSTEM.md](CONFIG_SYSTEM.md) |
| x86/ARM differences | [X86_ARM64_DIFF.md](X86_ARM64_DIFF.md) |

---

## Document Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-19 | 1.0 | Initial creation from debugging sessions |
