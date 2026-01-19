# ARM Porting Notes - Porteus Kiosk to Raspberry Pi

## Overview

This document details the x86-specific dependencies in Porteus Kiosk that must be addressed for ARM64 (aarch64) porting.

---

## 1. CRITICAL X86 DEPENDENCIES

### In Initramfs (/init)

| Issue | Location | Impact | ARM Solution |
|-------|----------|--------|--------------|
| `lspci` for device enumeration | init:51, 90, 94, 96 | PCI bus required | Use device tree parsing |
| PCI class 0200: (ethernet) | init:51 | PCI-specific | Device tree network nodes |
| PCI class 0300: (GPU) | init:90, 94, 96 | Graphics detection | Device tree GPU nodes |
| `uvesafb` kernel module | init:99 | x86 VBE/BIOS required | Use RPi vc4/drm drivers |
| `v86d` daemon | init:99 | x86 real mode emulation | Not needed on ARM |
| NVIDIA vendor ID 10de check | init:96 | Hardcoded NVIDIA quirk | Remove or adapt |
| x86_64 prefix detection | init:92 | Only checks x86_64 | Add aarch64 handling |
| `ld-linux-x86-64.so.2` loader | init:92, 93 | x86-specific | Use `ld-linux-aarch64.so.1` |
| 1024x768-32 hardcoded mode | init:99 | Arbitrary resolution | Use RPi display detection |

### GPU Detection Code (init:94-99)

**Current x86 code:**
```bash
vga=`lspci | grep 0300: | head -n1 | cut -d: -f3-4 | sed s/:/d0000/g`
[ "$vga" ] && driver="$(grep -i $vga /lib/modules/`uname -r`/modules.alias ...)"
```

**ARM replacement approach:**
```bash
# RPi uses device tree, not PCI
if [ -e /sys/firmware/devicetree/base/soc/gpu ]; then
    driver="vc4"
fi
# Or check for specific SoC
if grep -q "BCM2711" /proc/cpuinfo; then
    driver="vc4"  # RPi 4
fi
```

### Network Detection Code (init:51)

**Current x86 code:**
```bash
for module in `lspci | grep 0200: | cut -d: -f3-4 | sed s/:/d0000/g`; do
    ./busybox modprobe `grep -i $module /lib/modules/.../modules.alias`
done
```

**ARM replacement approach:**
```bash
# Load common ARM network drivers
for module in smsc95xx lan78xx genet; do
    modprobe $module 2>/dev/null
done
```

---

## 2. LIBRARY AND LOADER CHANGES

### Dynamic Linker

| Architecture | Loader Path |
|--------------|-------------|
| x86 (32-bit) | `/lib/ld-linux.so.2` |
| x86_64 | `/lib64/ld-linux-x86-64.so.2` |
| ARM (32-bit) | `/lib/ld-linux-armhf.so.3` |
| ARM64 | `/lib/ld-linux-aarch64.so.1` |

**Required change in init:92:**
```bash
# Current
[ `uname -m` = x86_64 ] && prefix="-x86-64"

# ARM64 version
case `uname -m` in
    x86_64)  loader="ld-linux-x86-64.so.2" ;;
    aarch64) loader="ld-linux-aarch64.so.1" ;;
    armv7l)  loader="ld-linux-armhf.so.3" ;;
esac
```

### Library Paths

| Architecture | Primary Lib Path |
|--------------|------------------|
| x86_64 | `/lib64`, `/usr/lib64` |
| ARM64 | `/lib/aarch64-linux-gnu`, `/usr/lib/aarch64-linux-gnu` |

---

## 3. KERNEL AND MODULE CHANGES

### Current x86 Kernel
- **File:** `boot/vmlinuz` (bzImage format, x86-specific)
- **Version:** 5.10.25-kiosk
- **Modules:** `000-kernel.xzm` contains x86-compiled .ko files

### ARM64 Requirements

| Component | x86 Current | ARM64 Needed |
|-----------|-------------|--------------|
| Kernel format | bzImage | Image.gz or Image |
| Boot method | isolinux/GRUB | U-Boot or RPi bootloader |
| Device tree | Not used | Required (.dtb files) |
| GPU driver | i915/nouveau/radeon | vc4-drm |
| Framebuffer | uvesafb | simplefb or vc4 |

### RPi-Specific Boot Files Needed
```
boot/
├── kernel8.img          # ARM64 kernel (RPi 3/4)
├── bcm2711-rpi-4-b.dtb  # Device tree for RPi 4
├── overlays/            # Device tree overlays
├── config.txt           # RPi boot config
├── cmdline.txt          # Kernel parameters
└── initrd.img           # ARM64 initramfs
```

---

## 4. XZM MODULE REBUILD REQUIREMENTS

All XZM modules must be rebuilt for ARM64:

| Module | Size | Binary Count | Rebuild Notes |
|--------|------|--------------|---------------|
| 000-kernel.xzm | 51MB | ~3,994 | Full kernel rebuild for ARM64 |
| 001-core.xzm | 64MB | ~5,292 | Recompile all userland (glibc, coreutils, etc.) |
| 003-settings.xzm | 1.2MB | ~748 | Scripts mostly portable, check binaries |
| 004-wifi.xzm | 1.6MB | ~595 | WiFi drivers for ARM SoCs |
| 06-fonts.xzm | 34MB | ~287 | Architecture-independent (fonts) |
| 08-ssh.xzm | 1.4MB | ~24 | Recompile OpenSSH |
| 09-x11vnc.xzm | 620KB | ~13 | Recompile x11vnc |
| firmware.xzm | 8MB | ~43 | May need different firmware |
| zz-settings.xzm | 12KB | ~12 | Scripts only, portable |

### Estimated Binary Recompilation
- **Total unique binaries:** ~2,400+
- **Architecture-independent:** ~300 (fonts, configs, scripts)
- **Requires recompilation:** ~2,100+

---

## 5. FRAMEBUFFER AND DISPLAY

### x86 Current Approach
```bash
# init:99 - x86 VESA framebuffer
test -e /dev/fb0 || {
    cp /opt/001/sbin/v86d /sbin
    modprobe uvesafb mode_option=1024x768-32
}
```

### ARM64 Approach for RPi
```bash
# RPi uses VC4 DRM driver
modprobe vc4
# Or for headless/simple framebuffer
modprobe simplefb
# Display config via config.txt, not kernel params
```

### RPi config.txt Display Settings
```ini
# Force HDMI output
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=82  # 1920x1080@60Hz

# Or use automatic detection
# (no hdmi_* settings)

# GPU memory split
gpu_mem=128
```

---

## 6. BOOT ARCHITECTURE DIFFERENCES

### x86 Boot Chain
```
BIOS/UEFI → isolinux/GRUB → vmlinuz → initrd.xz → /init → switch_root
```

### RPi Boot Chain
```
GPU bootloader → start.elf → kernel8.img → initrd.img → /init → switch_root
```

### Key Differences

| Aspect | x86 | RPi ARM64 |
|--------|-----|-----------|
| Boot firmware | BIOS/UEFI | VideoCore GPU |
| Bootloader | isolinux/GRUB | config.txt + start.elf |
| Kernel format | bzImage | Image/Image.gz |
| Device discovery | PCI enumeration | Device tree |
| Boot config | grub.cfg/isolinux.cfg | config.txt + cmdline.txt |

---

## 7. INIT SCRIPT MODIFICATIONS NEEDED

### High-Priority Changes (Required)

1. **Remove lspci calls** - Replace with device tree parsing
2. **Remove uvesafb/v86d** - Use vc4 or simplefb
3. **Update loader paths** - Add aarch64 support
4. **Update module loading** - ARM-specific drivers

### Medium-Priority Changes (Recommended)

1. **Network driver loading** - Add RPi ethernet drivers
2. **GPU driver loading** - vc4 instead of i915/nouveau
3. **Resolution handling** - Remove hardcoded 1024x768

### Low-Priority Changes (Optional)

1. **Boot media detection** - May need SD card support tweaks
2. **Recovery mechanism** - Should work as-is with partition 4

---

## 8. PORTABLE COMPONENTS (No Changes Needed)

These components should work on ARM64 without modification:

- **AUFS union mechanism** - Kernel feature, works on ARM
- **Squashfs mounting** - Kernel feature, works on ARM
- **Copy-to-RAM logic** - Shell script, portable
- **Recovery mechanism** - `cat ISO > /dev/device` works on ARM
- **Switch root** - Standard Linux, works on ARM
- **Most shell scripts** - POSIX compatible
- **GTKDialog wizards** - Need ARM64 gtkdialog binary
- **daemon.sh config polling** - Pure shell, portable
- **Config file format** - Text files, portable

---

## 9. RECOMMENDED PORTING APPROACH

### Phase 1: Minimal Boot
1. Build ARM64 kernel with AUFS support
2. Create ARM64 initramfs with modified /init
3. Build minimal 001-core.xzm for ARM64
4. Test boot to shell on RPi

### Phase 2: Graphics
1. Add vc4 driver support
2. Test framebuffer display
3. Build X11 components for ARM64
4. Test GUI boot

### Phase 3: Full System
1. Port remaining XZM modules
2. Test wizard and configuration
3. Test reconfiguration mechanism
4. Test recovery/failsafe

### Phase 4: Optimization
1. Tune for RPi performance
2. Add RPi-specific features (GPIO, etc.)
3. Create SD card image builder

---

## 10. REFERENCE: RPi KERNEL CONFIG

Key kernel options for Porteus-style ARM64 system:

```
# Required
CONFIG_AUFS_FS=y          # Or =m with module in initramfs
CONFIG_SQUASHFS=y
CONFIG_SQUASHFS_XZ=y
CONFIG_TMPFS=y
CONFIG_DEVTMPFS=y
CONFIG_DEVTMPFS_MOUNT=y

# RPi-specific
CONFIG_ARCH_BCM2835=y
CONFIG_DRM_VC4=y
CONFIG_SND_BCM2835=y
CONFIG_USB_DWC2=y

# Networking
CONFIG_USB_NET_SMSC95XX=y  # RPi 3 ethernet
CONFIG_USB_NET_LAN78XX=y   # RPi 3B+ ethernet
CONFIG_BCMGENET=y          # RPi 4 ethernet
```

---

## Document History
- Created: 2026-01-12
- Purpose: Track x86 dependencies and ARM64 porting requirements
