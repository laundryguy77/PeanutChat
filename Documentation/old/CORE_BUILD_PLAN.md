# ARM64 001-core.xzm Build Plan

## Overview

This document provides a comprehensive plan for building the 001-core.xzm module for ARM64 (Raspberry Pi 4/5). Based on analysis of the x86_64 module, we need to source 104 binaries and 459 libraries for ARM64.

**Target Output:** `/home/culler/saas_dev/pk-port/arm64/output/001-core.xzm`
**Estimated Size:** ~45-50 MB compressed (vs 64 MB x86_64 original)
**Extracted Size:** ~200 MB (vs 288 MB x86_64)

---

## Quick Start

```bash
cd /home/culler/saas_dev/pk-port/arm64/scripts

# 1. Initialize directory structure
./setup-directories.sh

# 2. Download ARM64 packages (method 2 = direct download, no root)
./download-packages.sh 2

# 3. Extract packages to rootfs
./extract-packages.sh

# 4. Build custom packages (optional, requires cross-compiler)
./build-custom-packages.sh all

# 5. Create the squashfs module
./build-core-module.sh
```

### Build Scripts Reference

| Script | Purpose |
|--------|---------|
| `setup-directories.sh` | Create directory structure |
| `download-packages.sh` | Download ARM64 .deb packages |
| `extract-packages.sh` | Extract and assemble rootfs |
| `build-custom-packages.sh` | Compile packages not in repos |
| `build-core-module.sh` | Create final 001-core.xzm |

---

## 1. Package Source Strategy

### Primary Source: Debian ARM64 (bookworm)

Using Debian bookworm ARM64 repositories provides:
- Stable, well-tested packages
- Full glibc compatibility
- Proper dependency resolution
- Compatible with Raspberry Pi OS

**Repository URLs:**
```
http://deb.debian.org/debian bookworm main contrib non-free
http://deb.debian.org/debian-security bookworm-security main
http://archive.raspberrypi.org/debian bookworm main  # For RPi-specific
```

---

## 2. Complete Package List

### 2.1 Core System (CRITICAL)

| Package | Description | Priority |
|---------|-------------|----------|
| libc6 | GNU C Library | CRITICAL |
| libc-bin | GNU C Library binaries | CRITICAL |
| locales | GNU C Library localization | HIGH |
| busybox | Swiss army knife utilities | CRITICAL |
| kmod | Tools for managing Linux kernel modules | CRITICAL |
| udev | /dev and hotplug management daemon | CRITICAL |
| systemd-sysv | System V init compatibility | CRITICAL |
| util-linux | Miscellaneous system utilities | CRITICAL |
| dhcpcd5 | DHCP client daemon | HIGH |
| iproute2 | Network tools | HIGH |
| procps | Process utilities | HIGH |

### 2.2 Display System (CRITICAL)

| Package | Description | Priority |
|---------|-------------|----------|
| xserver-xorg-core | Xorg X server core | CRITICAL |
| xserver-xorg-input-evdev | X.Org evdev input driver | CRITICAL |
| xserver-xorg-input-libinput | X.Org libinput driver | HIGH |
| xserver-xorg-video-fbdev | X.Org fbdev video driver | HIGH |
| libgl1-mesa-dri | DRI modules for Mesa | CRITICAL |
| libgl1-mesa-glx | Mesa OpenGL runtime | CRITICAL |
| libegl1-mesa | Mesa EGL runtime | HIGH |
| libgbm1 | Generic buffer management | HIGH |
| libdrm2 | Direct Rendering Manager | CRITICAL |
| libdrm-amdgpu1 | AMD GPU DRM (remove later) | LOW |
| x11-xserver-utils | X server utilities | HIGH |
| x11-utils | X11 utilities | HIGH |
| xauth | X authority file utility | HIGH |
| xinit | X server startup | HIGH |

### 2.3 X11 Libraries (CRITICAL)

| Package | Description | Priority |
|---------|-------------|----------|
| libx11-6 | X11 client-side library | CRITICAL |
| libxext6 | X11 extension library | CRITICAL |
| libxrender1 | X Rendering Extension | CRITICAL |
| libxrandr2 | X RandR extension | HIGH |
| libxinerama1 | X Xinerama extension | HIGH |
| libxcursor1 | X cursor library | HIGH |
| libxcomposite1 | X Composite extension | HIGH |
| libxdamage1 | X Damage extension | HIGH |
| libxfixes3 | X11 fixes extension | HIGH |
| libxi6 | X11 Input extension | HIGH |
| libxkbcommon0 | XKB keyboard library | HIGH |
| libxcb1 | X C Binding | CRITICAL |
| libxcb-render0 | XCB render extension | HIGH |
| libxcb-shm0 | XCB shared memory | HIGH |

### 2.4 Window Manager & Desktop (CRITICAL)

| Package | Description | Priority |
|---------|-------------|----------|
| openbox | Lightweight window manager | CRITICAL |
| libgtk2.0-0 | GTK+ 2.0 library | CRITICAL |
| libgtk-3-0 | GTK+ 3.0 library | CRITICAL |
| libglib2.0-0 | GLib library | CRITICAL |
| libgdk-pixbuf-2.0-0 | GDK Pixbuf library | CRITICAL |
| libcairo2 | Cairo 2D graphics | CRITICAL |
| libpango-1.0-0 | Pango text layout | CRITICAL |
| libpangocairo-1.0-0 | Pango Cairo binding | HIGH |
| libatk1.0-0 | ATK accessibility | HIGH |
| libfontconfig1 | Font configuration | CRITICAL |
| libfreetype6 | FreeType font engine | CRITICAL |
| libharfbuzz0b | OpenType shaping | HIGH |
| fonts-dejavu-core | DejaVu fonts | HIGH |

### 2.5 Networking (HIGH)

| Package | Description | Priority |
|---------|-------------|----------|
| curl | Command line URL tool | HIGH |
| libcurl4 | cURL library | HIGH |
| wget | Network downloader | HIGH |
| openssl | SSL utilities | HIGH |
| libssl3 | SSL library | CRITICAL |
| ca-certificates | CA certificates | HIGH |
| libnss3 | Network Security Services | CRITICAL |
| libnspr4 | NetScape Portable Runtime | CRITICAL |
| iptables | IP packet filter | HIGH |
| rsync | Fast file copying | HIGH |
| ethtool | Ethernet tool | MEDIUM |
| stunnel4 | SSL tunnel | MEDIUM |
| sshpass | Non-interactive SSH auth | LOW |
| openssh-client | SSH client | MEDIUM |

### 2.6 Audio (HIGH)

| Package | Description | Priority |
|---------|-------------|----------|
| libasound2 | ALSA library | HIGH |
| alsa-utils | ALSA utilities | HIGH |
| libasound2-plugins | ALSA plugins | MEDIUM |
| libpulse0 | PulseAudio client library | MEDIUM |

### 2.7 D-Bus (CRITICAL)

| Package | Description | Priority |
|---------|-------------|----------|
| dbus | D-Bus message bus | CRITICAL |
| libdbus-1-3 | D-Bus library | CRITICAL |
| libdbus-glib-1-2 | D-Bus GLib bindings | HIGH |
| dbus-x11 | D-Bus X11 session | HIGH |

### 2.8 Desktop Utilities (MEDIUM)

| Package | Description | Priority |
|---------|-------------|----------|
| tint2 | Lightweight panel | MEDIUM |
| dunst | Notification daemon | MEDIUM |
| xcompmgr | X compositor | LOW |
| conky | System monitor | LOW |
| feh | Image viewer | MEDIUM |
| yad | Yet Another Dialog | MEDIUM |
| mc | Midnight Commander | LOW |
| rsyslog | System logging | MEDIUM |
| cron | Task scheduler | MEDIUM |
| acpid | ACPI daemon | LOW |
| ntpdate | NTP time sync | MEDIUM |
| logrotate | Log rotation | LOW |

### 2.9 Compression & Archives (MEDIUM)

| Package | Description | Priority |
|---------|-------------|----------|
| squashfs-tools | SquashFS tools | HIGH |
| xz-utils | XZ compression | HIGH |
| gzip | GNU zip | HIGH |
| bzip2 | Block-sorting compressor | MEDIUM |
| unzip | De-archiver for .zip | MEDIUM |
| p7zip | 7-Zip archiver | LOW |
| cpio | Archive tool | HIGH |

---

## 3. Packages Requiring Compilation

These packages are not available in standard repositories and must be compiled from source:

| Package | Source | Build Difficulty | Notes |
|---------|--------|------------------|-------|
| gtkdialog | https://github.com/01micko/gtkdialog | Medium | GTK dialog builder |
| hsetroot | https://github.com/himdel/hsetroot | Easy | Wallpaper setter |
| fbv | http://s-tech.elsat.net.pl/fbv/ | Easy | Framebuffer viewer |
| xvkbd | http://t-sato.in.coocan.jp/xvkbd/ | Medium | Virtual keyboard |
| xlock | xlockmore package | Medium | Screen locker |

### Build Instructions for Custom Packages

#### gtkdialog
```bash
git clone https://github.com/01micko/gtkdialog.git
cd gtkdialog
./autogen.sh
./configure --prefix=/usr --sysconfdir=/etc
make -j$(nproc)
make DESTDIR=/tmp/gtkdialog install
```

#### hsetroot
```bash
git clone https://github.com/himdel/hsetroot.git
cd hsetroot
make
make DESTDIR=/tmp/hsetroot PREFIX=/usr install
```

#### fbv
```bash
wget http://s-tech.elsat.net.pl/fbv/fbv-1.0b.tar.gz
tar xzf fbv-1.0b.tar.gz
cd fbv-1.0b
./configure --prefix=/usr
make
make DESTDIR=/tmp/fbv install
```

---

## 4. Packages to Remove (x86-specific)

These x86-specific components should NOT be included:

| Component | Reason |
|-----------|--------|
| v86d | x86 VESA BIOS emulator |
| intel_drv.so | Intel GPU driver |
| amdgpu_drv.so | AMD GPU driver |
| ati_drv.so | ATI driver |
| nouveau_drv.so | NVIDIA driver |
| vesa_drv.so | VESA driver |
| i915_dri.so, i965_dri.so, iris_dri.so | Intel DRI |
| radeon_dri.so, radeonsi_dri.so | AMD DRI |
| nouveau_dri.so | NVIDIA DRI |
| isohybrid | x86 boot tool |

---

## 5. Download and Extraction Scripts

### 5.1 Directory Structure Setup

```bash
#!/bin/bash
# setup-directories.sh

BASEDIR="/home/culler/saas_dev/pk-port/arm64"

mkdir -p "$BASEDIR/packages/debs"
mkdir -p "$BASEDIR/packages/extracted"
mkdir -p "$BASEDIR/rootfs"
mkdir -p "$BASEDIR/build-source"
mkdir -p "$BASEDIR/output"
```

### 5.2 Package Download Script

See `/home/culler/saas_dev/pk-port/arm64/scripts/download-packages.sh`

### 5.3 Package Extraction Script

See `/home/culler/saas_dev/pk-port/arm64/scripts/extract-packages.sh`

### 5.4 Build Core Module Script

See `/home/culler/saas_dev/pk-port/arm64/scripts/build-core-module.sh`

---

## 6. Alternative: Debootstrap Approach

For a cleaner dependency resolution, use debootstrap to create a minimal system:

```bash
# Requires sudo and qemu-user-static for ARM64 emulation on x86_64 host
sudo apt-get install debootstrap qemu-user-static binfmt-support

# Create minimal ARM64 rootfs
sudo debootstrap --arch=arm64 --variant=minbase \
    --include=openbox,xserver-xorg-core,libgtk-3-0,dbus,libasound2 \
    bookworm /home/culler/saas_dev/pk-port/arm64/rootfs \
    http://deb.debian.org/debian

# Then strip unnecessary files and add custom packages
```

**Pros:** Automatic dependency resolution, clean system
**Cons:** Requires sudo, larger initial size, needs stripping

---

## 7. File Count and Size Estimates

### By Category

| Category | Files | Estimated Size |
|----------|-------|----------------|
| Core System (glibc, kmod, udev) | ~150 | 15 MB |
| X11 Server + Libraries | ~200 | 25 MB |
| Mesa/DRI (ARM64 only) | ~50 | 20 MB |
| Window Manager (openbox) | ~30 | 2 MB |
| GTK/GUI Libraries | ~300 | 30 MB |
| Networking (curl, ssl, nss) | ~80 | 15 MB |
| Audio (ALSA) | ~40 | 5 MB |
| D-Bus | ~20 | 2 MB |
| Utilities | ~100 | 10 MB |
| Fonts | ~30 | 5 MB |
| Configuration | ~200 | 1 MB |
| **TOTAL** | ~1,200 | ~130 MB |

### After Stripping

- Remove documentation: -10 MB
- Remove locale data (keep en_US): -15 MB
- Remove man pages: -5 MB
- Strip binaries: -10 MB
- **Final Estimate:** ~90 MB extracted

### Compressed Size

Using `mksquashfs -comp xz -b 256K`:
- Estimated compressed: **40-50 MB**

---

## 8. Build Workflow

### Phase 1: Setup (1 hour)
1. Create directory structure
2. Configure ARM64 apt sources
3. Install build dependencies

### Phase 2: Package Download (2 hours)
1. Run package download script
2. Verify all packages downloaded
3. Check for missing dependencies

### Phase 3: Extraction (1 hour)
1. Extract all .deb packages
2. Merge into unified rootfs
3. Resolve library symlinks

### Phase 4: Custom Builds (4 hours)
1. Cross-compile gtkdialog
2. Cross-compile hsetroot
3. Cross-compile fbv
4. Test binaries with qemu-aarch64

### Phase 5: Cleanup (2 hours)
1. Remove x86-specific files
2. Strip binaries
3. Remove unnecessary documentation
4. Fix library paths (lib64 -> lib)

### Phase 6: Configuration (2 hours)
1. Copy Porteus Kiosk configs
2. Adapt paths for ARM64
3. Set up init integration

### Phase 7: Build Module (30 minutes)
1. Create squashfs with xz compression
2. Verify module structure
3. Test module loading

### Phase 8: Testing (4 hours)
1. Boot test on Raspberry Pi
2. Verify X11 starts
3. Test openbox
4. Test networking
5. Test audio

**Total Estimated Time:** 16-20 hours

---

## 9. ARM64 Path Differences

### Library Paths

| x86_64 | ARM64 |
|--------|-------|
| /lib64 | /lib or /lib/aarch64-linux-gnu |
| /usr/lib64 | /usr/lib or /usr/lib/aarch64-linux-gnu |
| /lib64/ld-linux-x86-64.so.2 | /lib/ld-linux-aarch64.so.1 |

### DRI Drivers

| x86_64 | ARM64 |
|--------|-------|
| /usr/lib64/dri/*.so | /usr/lib/aarch64-linux-gnu/dri/*.so |
| i915_dri.so, iris_dri.so | vc4_dri.so, v3d_dri.so |

### Xorg Modules

| x86_64 | ARM64 |
|--------|-------|
| /usr/lib64/xorg/modules/ | /usr/lib/aarch64-linux-gnu/xorg/modules/ |

---

## 10. Next Steps

1. **Execute setup script** - Create directory structure
2. **Run download script** - Fetch all packages
3. **Run extraction script** - Unpack packages
4. **Build custom packages** - Compile from source
5. **Create rootfs** - Assemble all components
6. **Build squashfs** - Create 001-core.xzm
7. **Test on hardware** - Verify on Raspberry Pi

---

## Document History

- Created: 2026-01-12
- Purpose: ARM64 001-core.xzm build planning
- Source Analysis: CORE_MODULE_ANALYSIS.md
