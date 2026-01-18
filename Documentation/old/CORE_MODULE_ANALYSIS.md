# 001-core.xzm Module Analysis for ARM64 Porting

## Executive Summary

The 001-core.xzm module contains the complete userland for Porteus Kiosk, including glibc, X11 server, window manager, GUI toolkit, and essential utilities. This analysis identifies all components and provides recommendations for ARM64 porting.

**Key Statistics:**
- Compressed size: 64 MB (squashfs)
- Extracted size: 288 MB
- Total files: 4,524
- Total directories: 293
- Total symlinks: 696
- ELF executables: 104
- Shared libraries: 459

---

## 1. Module Structure

```
squashfs-root/
├── bin/          (6.6 MB) - Core binaries (kmod, lsblk, monr)
├── sbin/         (2.2 MB) - System binaries (init, udev, dhcpcd)
├── lib64/        (7.6 MB) - Core libraries (glibc, kmod, udev)
├── usr/
│   ├── bin/      (12 MB)  - User binaries (Xorg, openbox, curl)
│   ├── sbin/     (2.1 MB) - System utilities (lspci, rsyslogd)
│   └── lib64/    (233 MB) - All shared libraries
└── etc/          - Configuration files
```

---

## 2. Component Categorization

### 2.1 CRITICAL - System Boot (Must Have)

| Component | Files | Size | ARM64 Source |
|-----------|-------|------|--------------|
| **glibc 2.32** | libc-2.32.so, ld-linux-x86-64.so.2, libpthread, libm, libdl, etc. | ~8 MB | Raspberry Pi OS / Buildroot |
| **init (systemd/sysvinit)** | /sbin/init | 49 KB | Raspberry Pi OS |
| **udev 247** | udevd, libudev.so | ~425 KB | Raspberry Pi OS |
| **kmod** | /bin/kmod (modprobe, insmod, lsmod) | 130 KB | Raspberry Pi OS |
| **util-linux** | lsblk, fdisk, logger, mcookie | ~500 KB | Raspberry Pi OS |
| **dhcpcd** | /sbin/dhcpcd | 217 KB | Raspberry Pi OS |

**glibc Components (lib64/):**
```
ld-2.32.so                 (177 KB) - Dynamic linker
libc-2.32.so              (1.8 MB) - C library
libpthread-2.32.so        (148 KB) - Threading
libm-2.32.so              (1.3 MB) - Math library
libdl-2.32.so              (14 KB) - Dynamic loading
librt-2.32.so              (36 KB) - Realtime
libresolv-2.32.so          (85 KB) - DNS resolver
libnss_*.so                        - Name service switch
```

### 2.2 CRITICAL - Display System (Must Have)

| Component | Files | Size | ARM64 Source |
|-----------|-------|------|--------------|
| **Xorg 1.20.x** | /usr/bin/Xorg | ~3 MB binary | Raspberry Pi OS |
| **Mesa 20.x** | libGL, libEGL, libgbm, DRI drivers | ~45 MB | Raspberry Pi OS (vc4/v3d) |
| **libdrm** | libdrm.so + vendor libs | ~300 KB | Raspberry Pi OS |
| **X11 libraries** | libX11, libXext, libXrender, etc. | ~15 MB | Raspberry Pi OS |
| **XCB libraries** | libxcb*.so | ~3 MB | Raspberry Pi OS |

**X11 Video Drivers (usr/lib64/xorg/modules/drivers/):**
```
amdgpu_drv.so      - AMD GPU (not needed for ARM)
ast_drv.so         - ASPEED (not needed)
ati_drv.so         - ATI/AMD (not needed)
fbdev_drv.so       - Framebuffer (USEFUL for ARM)
intel_drv.so       - Intel (not needed)
modesetting_drv.so - Generic KMS (CRITICAL for ARM)
nouveau_drv.so     - NVIDIA (not needed)
vesa_drv.so        - VESA (not applicable to ARM)
```

**X11 Input Drivers (usr/lib64/xorg/modules/input/):**
```
evdev_drv.so       - Generic input (CRITICAL)
synaptics_drv.so   - Touchpads (optional)
wacom_drv.so       - Wacom tablets (optional)
elographics_drv.so - Touchscreen (may need)
```

**DRI Drivers (usr/lib64/dri/) - For 3D acceleration:**
```
i915_dri.so, i965_dri.so, iris_dri.so    - Intel (not needed)
nouveau_dri.so, nouveau_vieux_dri.so     - NVIDIA (not needed)
r200_dri.so, r300_dri.so, r600_dri.so    - AMD (not needed)
radeon_dri.so, radeonsi_dri.so           - AMD (not needed)
kms_swrast_dri.so, swrast_dri.so         - Software (USEFUL)
vmwgfx_dri.so                            - VMware (not needed)
```

**ARM64 Replacement:** Need vc4_dri.so and v3d_dri.so from Raspberry Pi Mesa build.

### 2.3 CRITICAL - Window Manager & UI (Must Have)

| Component | Files | Size | ARM64 Source |
|-----------|-------|------|--------------|
| **openbox** | /usr/bin/openbox | 326 KB | Raspberry Pi OS / Alpine |
| **libobrender** | libobrender.so.32 | ~120 KB | Build with openbox |
| **libobt** | libobt.so.2 | ~80 KB | Build with openbox |
| **GTK+ 2.0** | libgtk-x11-2.0.so | ~2.4 MB | Raspberry Pi OS |
| **GTK+ 3.0** | libgtk-3.so | ~3.5 MB | Raspberry Pi OS |
| **gtkdialog** | /usr/bin/gtkdialog | 256 KB | Need to compile |
| **cairo** | libcairo.so | ~1 MB | Raspberry Pi OS |
| **pango** | libpango*.so | ~600 KB | Raspberry Pi OS |
| **gdk-pixbuf** | libgdk_pixbuf-2.0.so | ~150 KB | Raspberry Pi OS |
| **glib 2.66** | libglib-2.0.so, libgio-2.0.so | ~3 MB | Raspberry Pi OS |

### 2.4 IMPORTANT - Networking (Required for Kiosk)

| Component | Files | Size | ARM64 Source |
|-----------|-------|------|--------------|
| **curl 7.74** | /usr/bin/curl, libcurl.so | ~650 KB | Raspberry Pi OS |
| **wget** | /usr/bin/wget | Included in busybox | Raspberry Pi OS |
| **OpenSSL 1.1.1** | libssl.so, libcrypto.so | ~3 MB | Raspberry Pi OS |
| **NSS** | libnss3.so, libssl3.so | ~2 MB | Raspberry Pi OS |
| **iptables** | xtables-legacy-multi | ~62 KB | Raspberry Pi OS |
| **stunnel** | /usr/bin/stunnel | Part of curl | Raspberry Pi OS |
| **rsync** | /usr/bin/rsync | ~300 KB | Raspberry Pi OS |
| **ethtool** | /usr/sbin/ethtool | ~467 KB | Raspberry Pi OS |
| **sshpass** | /usr/bin/sshpass | ~15 KB | Raspberry Pi OS |

### 2.5 IMPORTANT - Audio (Required for Kiosk)

| Component | Files | Size | ARM64 Source |
|-----------|-------|------|--------------|
| **ALSA** | libasound.so.2, alsamixer, amixer, aplay | ~1.5 MB | Raspberry Pi OS |
| **PulseAudio libs** | libpulse*.so | ~500 KB | Raspberry Pi OS |
| **apulse** | Shim for apps expecting PulseAudio | Script | Portable |
| **volumeicon** | /usr/bin/volumeicon | ~50 KB | Raspberry Pi OS |

### 2.6 IMPORTANT - D-Bus & IPC (Required)

| Component | Files | Size | ARM64 Source |
|-----------|-------|------|--------------|
| **D-Bus** | dbus-daemon, libdbus-1.so | ~500 KB | Raspberry Pi OS |
| **dbus-glib** | libdbus-glib-1.so | ~144 KB | Raspberry Pi OS |

### 2.7 NICE TO HAVE - Desktop Utilities

| Component | Files | Size | ARM64 Source |
|-----------|-------|------|--------------|
| **tint2** | /usr/bin/tint2 (panel) | ~150 KB | Raspberry Pi OS / Alpine |
| **dunst** | /usr/bin/dunst (notifications) | ~76 KB | Raspberry Pi OS / Alpine |
| **hsetroot** | /usr/bin/hsetroot (wallpaper) | ~23 KB | Compile from source |
| **xcompmgr** | /usr/bin/xcompmgr (compositor) | ~30 KB | Raspberry Pi OS |
| **xlock** | /usr/bin/xlock (screen lock) | ~150 KB | Compile from source |
| **conky** | /usr/bin/conky (system monitor) | ~822 KB | Raspberry Pi OS |
| **yad** | /usr/bin/yad (dialogs) | ~100 KB | Raspberry Pi OS |
| **feh** | /usr/bin/feh (image viewer) | ~159 KB | Raspberry Pi OS |
| **fbv** | /usr/bin/fbv (framebuffer viewer) | ~23 KB | Compile from source |

### 2.8 NICE TO HAVE - System Utilities

| Component | Files | Size | ARM64 Source |
|-----------|-------|------|--------------|
| **mc** | /usr/bin/mc (file manager) | ~835 KB | Raspberry Pi OS |
| **rsyslogd** | /usr/sbin/rsyslogd | ~630 KB | Raspberry Pi OS |
| **crond** | /usr/sbin/crond | ~53 KB | Raspberry Pi OS |
| **acpid** | /usr/sbin/acpid | ~53 KB | Raspberry Pi OS |
| **ntpdate** | /usr/sbin/ntpdate | ~60 KB | Raspberry Pi OS |
| **logrotate** | /usr/bin/logrotate | ~73 KB | Raspberry Pi OS |
| **fromdos** | /usr/bin/fromdos | ~15 KB | Raspberry Pi OS |

### 2.9 X86-SPECIFIC (Must Replace or Remove)

| Component | Files | Notes |
|-----------|-------|-------|
| **v86d** | /sbin/v86d | x86 VESA BIOS emulator - NOT NEEDED on ARM |
| **lspci** | /usr/sbin/lspci | PCI bus tool - Limited use on ARM (use device tree) |
| **isohybrid** | /usr/bin/isohybrid | x86 boot hybrid - NOT NEEDED |
| **mkisofs (32-bit)** | /usr/bin/mkisofs | Statically linked i386 - Need ARM64 version |
| **Intel GPU drivers** | i915_dri.so, intel_drv.so | NOT NEEDED |
| **AMD GPU drivers** | radeon*.so, amdgpu*.so | NOT NEEDED |
| **NVIDIA drivers** | nouveau*.so | NOT NEEDED |

### 2.10 STATICALLY LINKED BINARIES (Special Handling)

These binaries are statically linked and must be completely rebuilt:

| Binary | Architecture | Size | Notes |
|--------|--------------|------|-------|
| /sbin/ldconfig | x86_64 | 892 KB | Part of glibc - get from ARM64 glibc |
| /sbin/v86d | x86_64 | 99 KB | x86-only VESA daemon - REMOVE |
| /usr/bin/mkisofs | i386 (32-bit) | 400 KB | Need ARM64 cdrtools package |
| /bin/monr | x86_64 (static-pie) | 6 MB | Unknown purpose - investigate |

---

## 3. Package Manifest

### 3.1 Raspberry Pi OS Packages (Recommended Primary Source)

```bash
# Core system
libc6 glibc
systemd-sysv init
udev
kmod
util-linux
dhcpcd5

# Display
xserver-xorg-core
xserver-xorg-video-fbdev
xserver-xorg-video-modesetting
mesa-va-drivers
libgl1-mesa-dri
libdrm2
libx11-6
libxcb1

# Desktop
openbox
libgtk2.0-0
libgtk-3-0
libglib2.0-0
libcairo2
libpango-1.0-0

# Networking
curl
libcurl4
openssl
libssl1.1
iptables
stunnel4
rsync
ethtool

# Audio
libasound2
alsa-utils

# D-Bus
dbus
libdbus-1-3
libdbus-glib-1-2

# Utilities
tint2
dunst
conky
feh
mc
rsyslog
cron
acpid
ntp
logrotate
```

### 3.2 Must Compile from Source

| Package | Reason | Estimated Effort |
|---------|--------|------------------|
| gtkdialog | Not in standard repos | Medium (GTK dependency) |
| hsetroot | Not in standard repos | Easy |
| fbv | Framebuffer viewer | Easy |
| xvkbd | Virtual keyboard | Medium |
| xlock | Screen locker | Medium |
| monr | Unknown binary | Investigate first |

### 3.3 Alpine Linux Alternative (Smaller Footprint)

For a more minimal system, Alpine Linux ARM64 packages could be used:

```bash
# Core (musl-based, smaller than glibc)
musl musl-utils
busybox
openrc

# X11
xorg-server
mesa-dri-vc4
mesa-gl

# Desktop
openbox
gtk+2.0
gtk+3.0

# Note: Alpine uses musl instead of glibc
# This may cause compatibility issues with some binaries
```

---

## 4. ARM64-Specific Requirements

### 4.1 Raspberry Pi GPU Support

Replace x86 GPU drivers with:

```
/usr/lib/aarch64-linux-gnu/dri/vc4_dri.so      # RPi 3 and earlier
/usr/lib/aarch64-linux-gnu/dri/v3d_dri.so      # RPi 4
```

### 4.2 Dynamic Linker Path Change

| x86_64 | ARM64 |
|--------|-------|
| /lib64/ld-linux-x86-64.so.2 | /lib/ld-linux-aarch64.so.1 |
| /usr/lib64/ | /usr/lib/aarch64-linux-gnu/ |

### 4.3 Kernel Modules

The 001-core.xzm does NOT contain kernel modules (those are in 000-kernel.xzm).
No changes needed in this module for kernel modules.

---

## 5. Recommended Approach

### Option A: Raspberry Pi OS Base (Recommended)

**Pros:**
- All packages pre-built for ARM64
- Tested on Raspberry Pi hardware
- Full glibc compatibility
- Good community support

**Cons:**
- Larger than minimal systems
- Some packages may have extra dependencies

**Estimated Effort:** 2-3 weeks

**Steps:**
1. Start with Raspberry Pi OS Lite
2. Install required packages
3. Strip unnecessary files
4. Create squashfs module
5. Test boot integration

### Option B: Buildroot Custom Build

**Pros:**
- Complete control over all packages
- Minimal footprint possible
- No unnecessary dependencies

**Cons:**
- Longer build time
- More expertise required
- Need to configure each package

**Estimated Effort:** 4-6 weeks

**Steps:**
1. Configure Buildroot for RPi 4
2. Select required packages
3. Add custom packages (gtkdialog, etc.)
4. Build complete system
5. Extract and create squashfs

### Option C: Alpine Linux ARM64

**Pros:**
- Very small footprint (musl libc)
- Modern package management
- Good ARM64 support

**Cons:**
- musl vs glibc compatibility issues
- May need to rebuild some applications

**Estimated Effort:** 3-4 weeks

---

## 6. Size Estimates for ARM64

| Category | x86_64 Size | ARM64 Estimate | Notes |
|----------|-------------|----------------|-------|
| glibc | 8 MB | 8 MB | Similar |
| X11 server | 3 MB | 3 MB | Similar |
| Mesa | 45 MB | 20 MB | Only vc4/v3d needed |
| GTK+ | 6 MB | 6 MB | Similar |
| Networking | 5 MB | 5 MB | Similar |
| Utilities | 10 MB | 10 MB | Similar |
| **TOTAL** | **288 MB** | **~200 MB** | After removing x86-only drivers |

Compressed size estimate: ~45-50 MB (vs 64 MB original)

---

## 7. Critical Path Dependencies

```
glibc
├── All userland binaries
├── kmod
├── udev
└── dhcpcd

X11 (Xorg)
├── Mesa (libGL, libEGL)
│   └── libdrm
├── Input drivers (evdev)
├── Video driver (modesetting/fbdev)
└── libX11, libXext, etc.

openbox (Window Manager)
├── GTK+ 2.0
│   ├── glib
│   ├── cairo
│   └── pango
└── X11 libraries

Browser (in 002-chrome.xzm)
├── GTK+ 3.0
├── NSS/NSPR
├── D-Bus
└── Audio (ALSA/Pulse)
```

---

## 8. Files to Investigate

### 8.1 Unknown Binary: monr

```
/bin/monr: ELF 64-bit LSB pie executable, x86-64, static-pie linked
Size: 6 MB
```

This large statically-linked binary needs investigation:
- What is its purpose?
- Is it required for kiosk operation?
- Can it be replaced with standard tools?

### 8.2 uClibc Loader

```
/lib64/ld-uClibc.so.0: 21 KB
/lib64/libc.so.0: 237 KB
```

These are uClibc libraries (alternative to glibc). May be used by some statically compiled tools. Need to verify if any binaries depend on these.

---

## 9. Next Steps

1. **Verify monr binary purpose** - Run strings/strace on x86 system
2. **Create package list** - Map each binary to its source package
3. **Test with Raspberry Pi OS** - Install packages, verify functionality
4. **Build custom gtkdialog** - Compile for ARM64
5. **Create test squashfs** - Package and test boot
6. **Integrate with init** - Modify /init for ARM64 paths
7. **Test full boot cycle** - Verify kiosk functionality

---

## Document History

- Created: 2026-01-12
- Purpose: ARM64 porting analysis for 001-core.xzm module
- Source: /home/culler/saas_dev/pk-port/iso/xzm/001-core.xzm
