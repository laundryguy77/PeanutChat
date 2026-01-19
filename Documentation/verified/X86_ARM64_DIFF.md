# x86 vs ARM64 Architecture Comparison

## Document Information

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Created | 2026-01-19 |
| Platform | ARM64 (Raspberry Pi 4) vs x86 (Porteus Kiosk) |
| Status | Verified from source analysis |

---

## 1. Summary

This document details the key architectural differences between the x86 Porteus Kiosk and the ARM64 TuxOS port for Raspberry Pi 4. These differences affect boot sequence, initialization, hardware detection, file paths, and build procedures.

**Key Differences Overview:**
- Boot chain: BIOS/UEFI vs VideoCore GPU firmware
- Init system: sysvinit with inittab vs busybox shell script
- Display startup: XDM display manager vs direct xinit
- Library paths: `/lib64` vs `/lib/aarch64-linux-gnu`
- Hardware detection: PCI enumeration vs Device Tree

---

## 2. Boot Architecture Comparison

### Boot Chain

| Aspect | x86 | ARM64 |
|--------|-----|-------|
| Boot firmware | BIOS/UEFI | VideoCore GPU firmware |
| Bootloader | isolinux/GRUB | config.txt + start.elf |
| Kernel format | bzImage | Image or Image.gz |
| Kernel parameter source | grub.cfg/isolinux.cfg | cmdline.txt |
| Device discovery | PCI enumeration | Device Tree (.dtb) |
| Initramfs format | initrd.xz | initrd.img |

### Boot Files

| File Type | x86 Location | ARM64 Location |
|-----------|--------------|----------------|
| Kernel | `boot/vmlinuz` | `boot/kernel8.img` |
| Initramfs | `boot/initrd.xz` | `boot/initrd.img` |
| Boot config | `boot/grub/grub.cfg` | `boot/config.txt` |
| Kernel params | In bootloader config | `boot/cmdline.txt` |
| Device tree | Not used | `boot/*.dtb`, `boot/overlays/` |

### x86 Boot Chain
```
BIOS/UEFI
    |
    v
isolinux/GRUB (reads grub.cfg)
    |
    v
vmlinuz (bzImage format)
    |
    v
initrd.xz (AUFS setup)
    |
    v
switch_root to union filesystem
```

### ARM64 Boot Chain
```
VideoCore GPU bootloader
    |
    v
start.elf (reads config.txt)
    |
    v
kernel8.img (Image format)
    |
    v
initrd.img (AUFS setup)
    |
    v
switch_root to union filesystem
```

### RPi config.txt Example
```ini
# Kernel and boot
kernel=kernel8.img
initramfs initrd.img followkernel
arm_64bit=1

# GPU and display
gpu_mem=128
hdmi_force_hotplug=1
dtoverlay=vc4-kms-v3d

# Console
enable_uart=1
```

---

## 3. Init System Differences

| Aspect | x86 | ARM64 |
|--------|-----|-------|
| Init type | sysvinit + inittab | Custom busybox shell script |
| Runlevels | 0-6 via inittab | None - direct script calls |
| rc.S trigger | `si:S:sysinit:/etc/rc.d/rc.S` | Direct call from init |
| rc.4 trigger | `x1:4:respawn:/usr/bin/xdm` | Direct call from init |
| Process reaping | Built into sysvinit | Manual `wait` loop in init |
| Respawn mechanism | `respawn` in inittab | None (scripts run once) |

### x86 Inittab Style
```
# /etc/inittab
id:4:initdefault:
si:S:sysinit:/etc/rc.d/rc.S
su:S:wait:/etc/rc.d/rc.K
rc:2345:wait:/etc/rc.d/rc.M
x1:4:respawn:/usr/bin/xdm -nodaemon
```

### ARM64 Init Script
```bash
#!/bin/busybox sh
# /sbin/init - PID 1

# Mount essential filesystems
mount -o remount,rw /
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev

# Run initialization scripts directly
[ -x /etc/rc.d/rc.S ] && /etc/rc.d/rc.S
[ -x /etc/rc.d/rc.4 ] && /etc/rc.d/rc.4

# PID 1 must never exit
while true; do
    wait 2>/dev/null
    sleep 1
done
```

### Key Differences Explained

**Runlevels:** x86 uses traditional SysV runlevels (4 for GUI). ARM64 has no concept of runlevels; scripts are called directly in sequence.

**Respawning:** On x86, XDM is marked `respawn` so if it crashes, init restarts it. On ARM64, there's no automatic respawning - scripts run once.

**Process Reaping:** PID 1 must reap zombie processes. sysvinit does this automatically; the ARM64 init script uses an explicit `wait` loop.

---

## 4. X11 and Display Startup

| Aspect | x86 | ARM64 |
|--------|-----|-------|
| Display manager | XDM (`/usr/bin/xdm`) | None - direct xinit |
| xinitrc location | `/etc/X11/xinit/xinitrc` (static) | `/tmp/.xinitrc` (dynamic) |
| X server launch | Via XDM | Direct `xinit` call from rc.4 |
| Virtual terminal | vt7 | vt1 |
| GPU driver loading | PCI-based detection | Static module load (vc4, v3d) |
| Openbox autostart | `/usr/libexec/openbox-autostart` | `/usr/lib/aarch64-linux-gnu/openbox-autostart` |

### x86 X Startup
```
init (inittab)
    |
    v
/usr/bin/xdm (respawning)
    |
    v
startx wrapper
    |
    v
xinit /etc/X11/xinit/xinitrc -- /usr/bin/X :0 vt7
    |
    v
openbox --startup /usr/libexec/openbox-autostart
```

### ARM64 X Startup
```
/etc/rc.d/rc.4
    |
    v
xinit /tmp/.xinitrc -- /usr/lib/xorg/Xorg :0 vt1
    |
    v
openbox --startup /usr/lib/aarch64-linux-gnu/openbox-autostart
```

### Why Dynamic xinitrc?

The ARM64 port generates `/tmp/.xinitrc` at runtime because:
1. Allows runtime customization based on hardware detection
2. Sets ARM64-specific library paths
3. Includes debugging and logging dynamically
4. Avoids modifying the read-only SquashFS base

---

## 5. File Path Differences

### Library Paths

| Type | x86 | ARM64 |
|------|-----|-------|
| Primary lib | `/lib64`, `/usr/lib64` | `/lib/aarch64-linux-gnu`, `/usr/lib/aarch64-linux-gnu` |
| Dynamic linker | `/lib64/ld-linux-x86-64.so.2` | `/lib/ld-linux-aarch64.so.1` |
| pkg-config path | `/usr/lib64/pkgconfig` | `/usr/lib/aarch64-linux-gnu/pkgconfig` |

### Boot Layout

| Component | x86 ISO | ARM64 SD Card |
|-----------|---------|---------------|
| Boot partition | Part of ISO | FAT32 partition 1 |
| System modules | `xzm/` in ISO | ext4 partition 2 `/xzm/` |
| Logs/recovery | Partition 4 | Partition 4 |
| Boot files | `boot/` | Partition 1 root |

### XZM Module Paths

| Module | x86 Source | ARM64 Source |
|--------|------------|--------------|
| 001-core | `xzm/001-core.xzm` | `arm64/rootfs/` -> `arm64/output/001-core.xzm` |
| 003-settings | `xzm/003-settings.xzm` | `arm64/003-settings-rootfs/` -> `arm64/output/003-settings.xzm` |
| 000-kernel | `xzm/000-kernel.xzm` | `arm64/000-kernel-rootfs/` -> `arm64/output/000-kernel.xzm` |

### LD_LIBRARY_PATH

ARM64 scripts must set:
```bash
export LD_LIBRARY_PATH=/usr/lib/aarch64-linux-gnu:/lib/aarch64-linux-gnu:/usr/lib:/lib
```

---

## 6. Driver and Hardware Differences

### GPU

| Aspect | x86 | ARM64 |
|--------|-----|-------|
| Detection method | `lspci | grep 0300:` | Device Tree / static |
| Common drivers | i915 (Intel), nouveau (NVIDIA), radeon (AMD) | vc4, v3d |
| Framebuffer fallback | uvesafb (requires v86d) | simplefb (built-in) |
| Module loading | Based on PCI vendor:device ID | Static modprobe in rc.S |
| Acceleration | Varies by vendor | VideoCore 3D via v3d |

### x86 GPU Detection (init:94-99)
```bash
vga=$(lspci | grep 0300: | head -n1 | cut -d: -f3-4 | sed s/:/d0000/g)
[ "$vga" ] && driver="$(grep -i $vga /lib/modules/$(uname -r)/modules.alias ...)"
modprobe $driver
```

### ARM64 GPU Loading (rc.S:69-84)
```bash
modprobe drm
modprobe drm_kms_helper
modprobe vc4
modprobe v3d
udevadm trigger --subsystem-match=drm
udevadm settle --timeout=5
```

### Key Modules

| Function | x86 | ARM64 |
|----------|-----|-------|
| DRM base | drm, drm_kms_helper | drm, drm_kms_helper |
| GPU driver | i915, nouveau, radeon | vc4 |
| 3D acceleration | i915, nouveau, radeon | v3d |
| Audio | snd_hda_intel | snd_bcm2835 |
| USB | xhci_hcd, ehci_hcd | dwc2 |

### Network Interface

| Aspect | x86 | ARM64 |
|--------|-----|-------|
| Detection | `lspci | grep 0200:` | Device Tree enumeration |
| Interface naming | eth0 (traditional) or enpXsY (predictable) | eth0 or end0 |
| Common drivers | e1000e, r8169, igb | genet (RPi4), smsc95xx (RPi3) |
| WiFi drivers | iwlwifi, ath9k | brcmfmac |

### x86 Network Detection (init:51)
```bash
for module in $(lspci | grep 0200: | cut -d: -f3-4 | sed s/:/d0000/g); do
    ./busybox modprobe $(grep -i $module /lib/modules/.../modules.alias)
done
```

### ARM64 Network Detection (rc.S:103-113)
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

---

## 7. Network Interface

See section 6 above for detailed network interface differences.

### Interface Name Summary

| Platform | Typical Name | Driver |
|----------|--------------|--------|
| RPi 3 | eth0 | smsc95xx (USB ethernet) |
| RPi 3B+ | eth0 | lan78xx (USB ethernet) |
| RPi 4 | eth0 or end0 | genet (native Gigabit) |
| x86 Desktop | eth0, enpXsY | Various |

### Handling in Scripts

Scripts should auto-detect rather than hardcode:
```bash
# Bad
ETH_IFACE="eth0"

# Good
ETH_IFACE=$(ls /sys/class/net/ | grep -v lo | grep -v wlan | head -n1)
```

---

## 8. Build System Differences

### mksquashfs Flags

| Flag | x86 | ARM64 |
|------|-----|-------|
| Compression | `-comp xz -b 256K` | `-comp xz -b 256K` |
| BCJ filter | `-Xbcj x86` | `-Xbcj arm` |
| Ownership | Not typically needed | `-force-uid 0 -force-gid 0` (CRITICAL) |
| Architecture check | None | Verify with `file` command |

### ARM64 Build Command
```bash
mksquashfs arm64/003-settings-rootfs arm64/output/003-settings.xzm \
    -comp xz -b 256K -Xbcj arm \
    -force-uid 0 -force-gid 0 \
    -noappend
```

### Why `-force-uid 0 -force-gid 0`?

When building on a non-root system or with files from different sources, SquashFS preserves original ownership. This causes permission failures at boot (e.g., `/etc/shadow` owned by user 1000 instead of root). The `-force-uid 0 -force-gid 0` flags ensure all files are owned by root.

### Module Sources

| Module | x86 Source | ARM64 Source Directory |
|--------|------------|------------------------|
| 000-kernel | Pre-built kernel | `arm64/000-kernel-rootfs/` |
| 001-core | Slackware packages | Debian Bookworm ARM64 packages |
| 003-settings | Scripts/configs | `arm64/003-settings-rootfs/` |

### Package Compatibility

| Aspect | x86 | ARM64 |
|--------|-----|-------|
| Distribution | Slackware | Debian Bookworm |
| GLIBC version | Varies | 2.36 (strict) |
| Package format | .txz | .deb |
| Architecture | x86_64 | aarch64 |

**IMPORTANT:** Do not mix Debian Bookworm (GLIBC 2.36) with Ubuntu packages (GLIBC 2.38). This causes runtime failures.

---

## 9. Script Compatibility

### Portable Components

These work without modification on ARM64:

| Component | Reason |
|-----------|--------|
| AUFS union mechanism | Kernel feature |
| SquashFS mounting | Kernel feature |
| Copy-to-RAM logic | Shell script, POSIX |
| Recovery mechanism | Shell script |
| Most shell scripts | POSIX compatible |
| daemon.sh config polling | Pure shell |
| Config file format | Text files |

### Components Requiring Changes

| Component | x86 Dependency | ARM64 Solution |
|-----------|----------------|----------------|
| GPU detection | `lspci` | Device Tree / static load |
| Network detection | PCI enumeration | `/sys/class/net/` enumeration |
| Framebuffer setup | uvesafb + v86d | vc4 / simplefb |
| Library paths | `/lib64` | `/lib/aarch64-linux-gnu` |
| Dynamic linker | `ld-linux-x86-64.so.2` | `ld-linux-aarch64.so.1` |
| GTKDialog binary | x86 binary | ARM64 binary required |

### Script Shebang Compatibility

| Shebang | x86 | ARM64 | Notes |
|---------|-----|-------|-------|
| `#!/bin/sh` | busybox ash | busybox ash | Compatible |
| `#!/bin/bash` | GNU bash | GNU bash | Compatible |
| `#!/bin/busybox sh` | busybox | busybox | Compatible |
| `#!/bin/ash` | May not exist | Symlink to busybox | Add symlink |

---

## 10. Configuration Hook Differences

### Config Application

| Hook | x86 | ARM64 |
|------|-----|-------|
| Config source | Remote URL or local | Same |
| Parameter handlers | `/opt/scripts/param-handlers/` | Same structure |
| Handler execution | Sorted by numeric prefix | Same |
| Network handler | `00-network.sh` | Same (modified for end0) |

### Parameter Handler Differences

The only significant handler change is interface detection:

**x86 00-network.sh:**
```bash
iface=$(echo "$network_interface" | cut -d: -f1)
# Expects eth0 format
```

**ARM64 00-network.sh:**
```bash
iface=$(echo "$network_interface" | cut -d: -f1)
# Works with eth0 or end0
# Additional handling for dynamic interface names
```

### Remote Config Format

The config format is identical between platforms:
```
homepage=https://example.com
browser=chrome
network_interface=eth0
connection=dhcp
```

---

## Summary Table

| Aspect | x86 Porteus Kiosk | ARM64 TuxOS |
|--------|-------------------|-------------|
| Boot firmware | BIOS/UEFI | VideoCore GPU |
| Bootloader | isolinux/GRUB | config.txt + start.elf |
| Kernel format | bzImage | Image |
| Init system | sysvinit + inittab | busybox shell script |
| Display manager | XDM | None (direct xinit) |
| GPU detection | PCI (`lspci`) | Device Tree / static |
| GPU driver | i915/nouveau/radeon | vc4 + v3d |
| Network detection | PCI (`lspci`) | `/sys/class/net/` |
| Dynamic linker | `/lib64/ld-linux-x86-64.so.2` | `/lib/ld-linux-aarch64.so.1` |
| Primary lib path | `/lib64`, `/usr/lib64` | `/lib/aarch64-linux-gnu` |
| mksquashfs BCJ | `-Xbcj x86` | `-Xbcj arm` |
| Force ownership | Not required | `-force-uid 0 -force-gid 0` |
| Base distro | Slackware | Debian Bookworm |
| GLIBC version | Varies | 2.36 |

---

## Related Documentation

- [BOOT_FLOW.md](BOOT_FLOW.md) - Detailed boot sequence
- [SCRIPTS_REFERENCE.md](SCRIPTS_REFERENCE.md) - Script inventory
- [CONFIG_SYSTEM.md](CONFIG_SYSTEM.md) - Configuration system
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions

---

## Document Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-19 | 1.0 | Initial creation from ARM_PORTING_NOTES.md |
