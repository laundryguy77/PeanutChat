# iso-arm64 and arm64 Directory Map Report

Generated: 2026-01-17
Source: /home/culler/saas_dev/pk-port/

---

## Executive Summary

This report documents the complete directory structure for the ARM64 TuxOS port, including:
- **iso-arm64/**: Staging directory containing final bootable image components (135 MB compiled modules)
- **arm64/**: Source build directories containing rootfs sources, build scripts, and outputs

The system uses a modular SquashFS (.xzm) architecture with AUFS union mount for a live kiosk environment targeting Raspberry Pi 4.

---

## Part 1: iso-arm64 Directory (Final Image Staging)

### Overview

```
iso-arm64/                          # Final bootable image staging (56 MB total)
├── boot/                           # RPi4 bootloader and kernel files
│   ├── kernel8.img                # ARM64 kernel (6.1.93-v8+)
│   ├── initrd.img                 # Initial ramdisk
│   ├── bcm2711-rpi-4-b.dtb        # BCM2711 device tree blob
│   ├── config.txt                 # RPi boot configuration
│   ├── cmdline.txt                # Kernel command line parameters
│   ├── start4.elf / start4x.elf   # GPU firmware files
│   ├── fixup4.dat / fixup4x.dat   # Firmware fixup tables
│   └── overlays/                  # Device tree overlays
│       ├── vc4-kms-v3d.dtbo       # VC4 graphics overlay
│       └── dwc2.dtbo               # USB OTG overlay
├── xzm/                           # SquashFS modules (135 MB)
│   ├── 000-kernel.xzm            # Kernel modules (19 MB)
│   ├── 001-core.xzm              # Core system binaries/libs (109 MB)
│   ├── 003-settings.xzm          # Kiosk scripts/configs (7.0 MB)
│   ├── 08-ssh.xzm                # SSH utilities (372 KB)
│   └── firmware.xzm              # WiFi firmware (364 KB)
├── docs/                          # License and documentation
│   ├── version                   # Version: "1.0.0-arm64"
│   ├── License.txt               # License information
│   ├── GNU_GPL                   # GPL license text
│   ├── kiosk.sgn                 # Signature file (empty)
│   └── default.jpg               # Default background image
├── firmware-rootfs/              # Broadcom WiFi firmware
│   └── lib/firmware/brcm/
│       ├── brcmfmac43455-sdio.bin
│       ├── brcmfmac43455-sdio.clm_blob
│       └── brcmfmac43455-sdio.raspberrypi,4-model-b.txt
├── make_img.sh                   # Script to create SD card image
├── make_iso.sh                   # Script to create ISO data file
└── README.md                     # Documentation
```

### Module Summary Table

| Module | Size | Purpose | Load Order |
|--------|------|---------|-----------|
| 000-kernel.xzm | 19 MB | Kernel modules (lib/modules/6.1.93-v8+/) | 1 |
| 001-core.xzm | 109 MB | System binaries, libraries, packages | 2 |
| 003-settings.xzm | 7.0 MB | Init scripts, kiosk configs, GUI apps | 3 |
| 08-ssh.xzm | 372 KB | SSH server and utilities | 4 |
| firmware.xzm | 364 KB | Broadcom WiFi firmware | - |
| **Total** | **~136 MB** | **Complete kiosk system** | - |

### Boot Directory Details

**File Listing:**
- `kernel8.img` - ARM64 Linux kernel
- `initrd.img` - Initial ramdisk (loaded by bootloader)
- `config.txt` - RPi firmware configuration (enables VC4, sets GPU memory to 128MB)
- `cmdline.txt` - Kernel params: `console=serial0,115200 console=tty1 root=/dev/ram0 debug net.ifnames=0 biosdevname=0`
- `bcm2711-rpi-4-b.dtb` - Broadcom BCM2711 device tree
- `start4.elf` / `start4x.elf` - GPU firmware (standard/extended memory)
- `fixup4.dat` / `fixup4x.dat` - Firmware fixup tables
- `overlays/vc4-kms-v3d.dtbo` - DRM VC4 graphics driver overlay
- `overlays/dwc2.dtbo` - USB OTG controller overlay

### XZM Module Expansion

**000-kernel.xzm Contents:**
```
lib/modules/6.1.93-v8+/
├── kernel/                    # Loadable kernel modules
│   ├── arch/arm64/           # ARM64-specific modules
│   ├── crypto/               # Cryptography modules
│   ├── drivers/              # Hardware drivers
│   │   ├── block/            # Block device drivers
│   │   ├── net/              # Network drivers
│   │   ├── gpu/              # GPU drivers
│   │   ├── usb/              # USB controllers
│   │   ├── i2c/              # I2C bus drivers
│   │   ├── spi/              # SPI bus drivers
│   │   └── input/            # Input device drivers
│   ├── fs/                   # Filesystem modules
│   ├── lib/                  # Library modules
│   └── net/                  # Networking modules
├── modules.dep.bin           # Module dependency cache
├── modules.alias             # Module aliases
├── modules.order             # Module load order
└── modules.builtin           # Built-in modules
```

**001-core.xzm Contents (Sample):**
```
Debian Bookworm ARM64 packages including:
├── bin/                      # Essential binaries
│   ├── bash, dash, sh        # Shells
│   ├── busybox               # Multi-call binary
│   ├── cat, ls, cp, mv, rm   # File operations
│   ├── tar, gzip, bzip2      # Compression
│   ├── grep, sed, awk        # Text processing
│   └── mount, umount         # Filesystem operations
├── etc/                      # Configuration files
│   ├── hostname, hosts       # Network configuration
│   ├── fstab                 # Filesystem table
│   └── profile.d/            # Shell initialization
├── lib/                      # System libraries
│   ├── libc.so.6             # C library (GLIBC 2.36)
│   ├── libm.so.6             # Math library
│   └── aarch64-linux-gnu/    # ARM64 architecture libs
├── usr/bin/                  # User binaries
│   ├── chromium / chromium-browser  # Browser
│   ├── X, Xvfb, Xwayland    # X11 servers
│   ├── openbox               # Window manager
│   ├── gtkdialog             # Dialog framework
│   └── [many other utilities]
├── usr/lib/                  # User libraries
│   ├── X11/                  # X11 libraries
│   ├── gtk/                  # GTK libraries
│   └── aarch64-linux-gnu/    # ARM64 libs
└── usr/share/                # Data files
    ├── pixmaps/              # Images/icons
    ├── man/                  # Manual pages
    └── wallpapers/           # Desktop backgrounds
```

**003-settings.xzm Contents (Detailed):**
```
003-settings.xzm (7.0 MB - PRIMARY KIOSK CONFIGURATION MODULE)
├── sbin/
│   ├── init                  # PID 1 init script (busybox sh)
│   │   └── Purpose: Initialize filesystems, mount proc/sys/dev, run rc.S then rc.4
│   └── udhcpc                # DHCP client (symlink to busybox)
├── bin/
│   └── busybox               # Multi-call binary for shell operations
├── etc/
│   ├── inittab               # Init configuration
│   ├── machine-id            # Machine identifier
│   ├── resolv.conf           # DNS configuration
│   ├── profile.d/
│   │   └── variables.sh      # Shell environment variables
│   ├── rc.d/                 # RCNG startup scripts
│   │   ├── rc.S              # System initialization (mounts, udev, kernel modules)
│   │   ├── rc.M              # Multi-user startup
│   │   ├── rc.4              # X11 graphical startup
│   │   ├── rc.4.xinitrc      # X11 initialization (openbox, kiosk app)
│   │   ├── rc.6              # Shutdown/reboot
│   │   ├── rc.inet1          # Network configuration
│   │   ├── rc.FireWall       # Firewall setup
│   │   ├── local_cli.d/      # CLI-only hook directory
│   │   │   ├── cli_commands  # User-defined CLI startup
│   │   │   └── .gitkeep
│   │   ├── local_gui.d/      # GUI hook directory
│   │   │   ├── gui_commands  # User-defined GUI startup
│   │   │   └── .gitkeep
│   │   ├── local_net.d/      # Network hook directory
│   │   │   ├── daemon.sh     # Remote config polling daemon
│   │   │   ├── net_commands  # User-defined network startup
│   │   │   └── .gitkeep
│   │   └── local_shutdown.d/ # Shutdown hook directory
│   │       └── shutdown_commands
│   ├── X11/
│   │   └── xorg.conf.d/
│   │       ├── 10-inputs.conf      # Keyboard/mouse configuration
│   │       └── 99-fbdev-fallback.conf
│   └── xdg/openbox/
│       └── autostart         # Post-openbox startup script
├── lib/aarch64-linux-gnu/    # PAM authentication libraries
│   ├── libpam.so.0.85.1      # PAM library (v0.85.1)
│   ├── libpam_misc.so.0.82.1 # PAM misc library
│   ├── libpamc.so.0.82.1     # PAM client library
│   └── libcom_err.so.2.1     # Error library
├── usr/bin/
│   └── gtkdialog             # GTK dialog generator
├── usr/lib/
│   ├── aarch64-linux-gnu/    # ARM64-specific libraries
│   └── sasl2/                # SASL authentication
├── usr/share/
│   ├── doc/                  # Documentation
│   ├── icons/                # Icon files
│   ├── lintian/              # Lint files
│   ├── man/                  # Manual pages
│   ├── pixmaps/              # Images and icons
│   ├── pkgconfig/            # Package config files
│   ├── udhcpc/               # DHCP client scripts
│   └── wallpapers/           # Desktop wallpapers
├── var/lib/dbus/             # D-Bus runtime data
└── opt/scripts/              # KIOSK APPLICATION SCRIPTS
    ├── first-run             # Kiosk first-run wizard orchestrator (299 bytes)
    ├── first-run.backup      # Backup of original x86 binary
    ├── welcome               # Network configuration wizard (615 lines)
    ├── welcome.backup        # Backup of original
    ├── wizard                # Device configuration wizard (298 lines, gtkdialog-based)
    ├── wizard-now            # Trigger wizard from running session (32 lines)
    ├── gui-app               # Browser launcher wrapper (332 lines)
    ├── boot-capture          # Boot event capture/logging (263 lines)
    ├── flow-logger           # Event flow logging utility (113 lines)
    ├── daemon.sh             # Remote config polling daemon (126 lines)
    ├── apply-config          # Configuration applier (74 lines)
    ├── update-config         # Config update handler (496 lines)
    ├── arm64-boot-config.sh  # ARM64-specific boot config (592 lines)
    ├── extras                # Extension hooks marker
    ├── param-handlers/       # Configuration parameter handlers (10 scripts, 1992 lines total)
    │   ├── 00-network.sh     # Network configuration (222 lines)
    │   ├── 10-proxy.sh       # Proxy settings (142 lines)
    │   ├── 20-browser.sh     # Browser configuration (247 lines)
    │   ├── 30-display.sh     # Display settings (119 lines)
    │   ├── 40-input.sh       # Input device configuration (220 lines)
    │   ├── 50-power.sh       # Power management (201 lines)
    │   ├── 60-audio.sh       # Audio configuration (129 lines)
    │   ├── 70-services.sh    # Service management (225 lines)
    │   ├── 80-system.sh      # System settings (272 lines)
    │   └── 90-custom.sh      # Custom parameters (215 lines)
    └── files/                # Support files for scripts
        ├── lcon.default      # Default lconky configuration
        ├── greyos_reboot     # Reboot utility
        └── wizard/           # Wizard data files
            ├── wizard-functions   # Common wizard functions (101KB)
            ├── keyboards.txt      # Keyboard layout data (18KB)
            ├── timezones.txt      # Timezone data (8.9KB)
            ├── license-*.txt      # License files (various)
            │   ├── license-GoogleChrome.txt (43KB)
            │   ├── license-AdobeFlash.txt (35KB)
            │   └── license-CitrixReceiver.txt (1.3KB)
            ├── tooltip-*.txt      # Tooltip data
            │   ├── tooltip-mem.txt
            │   ├── tooltip-freeze.txt
            │   └── tooltip-standby.txt
            └── printers.d/        # Printer driver configurations
                ├── cups           # CUPS driver
                ├── hplip          # HP LaserJet printer
                ├── dymo-cups-drivers
                ├── zebra          # Zebra printers
                ├── star           # Star printers
                ├── bixolon        # Bixolon printers
                ├── bematech       # Bematech printers
                ├── xerox-drivers  # Xerox printer drivers
                ├── sato           # Sato printers
                ├── splix          # Samsung laser printers
                ├── pnm2ppa        # HP inkjet printers
                └── foomatic       # Generic printer database
```

**08-ssh.xzm Contents:**
```
08-ssh.xzm (372 KB)
├── etc/ssh/
│   ├── sshd_config           # SSH server configuration
│   ├── sshd_config.d/        # SSH config.d directory
│   └── moduli               # DH moduli for key exchange
├── etc/rc.d/local_cli.d/
│   └── start-ssh            # SSH startup hook
├── usr/sbin/
│   └── sshd                 # SSH server daemon
└── usr/lib/openssh/
    └── ssh-session-cleanup  # SSH session cleanup utility
```

**firmware.xzm Contents:**
```
firmware.xzm (364 KB - WiFi Firmware)
└── lib/firmware/brcm/
    ├── brcmfmac43455-sdio.bin                        # WiFi driver firmware
    ├── brcmfmac43455-sdio.clm_blob                   # Country locale module
    └── brcmfmac43455-sdio.raspberrypi,4-model-b.txt  # Board-specific config
```

---

## Part 2: arm64 Directory (Source Build System)

### Overview

```
arm64/                                  # Build source directory (523 MB)
├── rootfs/                            # Main system root filesystem (450 MB)
├── 003-settings-rootfs/              # Kiosk settings/scripts source (44 MB)
├── 000-kernel-rootfs/                # Kernel modules source (26 MB)
├── 08-ssh-rootfs/                    # SSH utilities source (1.9 MB)
├── boot/                             # Boot files source
├── scripts/                          # Build scripts (6 scripts)
├── output/                           # Compiled XZM modules (219 MB)
├── packages/                         # Downloaded packages
├── build-source/                     # Build intermediate files
├── config/                           # Configuration files
└── [build artifacts and documentation]
```

### Source Rootfs Directories

#### A. rootfs/ (450 MB)

The complete Debian Bookworm ARM64 base system:

**Top-level directories:**
- `bin/` - Essential shell binaries (bash, dash, busybox, compression tools, utilities)
- `etc/` - System configuration files (passwd, group, fstab, network, audio configs)
- `lib/` - System libraries (libc, math, crypto, kernel modules)
- `usr/` - User programs and libraries (X11, GTK, network utilities, browsers)
- `var/` - Variable data (logs, caches, temporary files)
- `dev/`, `proc/`, `sys/`, `run/`, `tmp/` - Virtual and temporary filesystems
- `home/`, `root/` - User home directories
- `media/`, `mnt/` - Mount points

**Key subdirectories:**
```
rootfs/
├── etc/
│   ├── alsa/               # Audio configuration
│   ├── dbus-1/             # D-Bus configuration
│   ├── default/            # Default tool configurations
│   ├── dhcp/               # DHCP client configs
│   └── [many system configs]
├── usr/bin/                # User-space binaries
│   ├── chromium            # Web browser
│   ├── X                   # X11 server
│   ├── openbox             # Window manager
│   ├── gtkdialog           # Dialog generator
│   └── [hundreds of utilities]
├── usr/lib/
│   ├── X11/                # X11 libraries
│   ├── gtk-3.0/            # GTK3 libraries
│   ├── aarch64-linux-gnu/  # ARM64-specific libraries
│   └── [system libraries]
└── usr/share/
    ├── pixmaps/            # Icon/image files
    ├── applications/       # Application definitions
    ├── wallpapers/         # Desktop backgrounds
    └── man/                # Manual documentation
```

#### B. 003-settings-rootfs/ (44 MB)

Kiosk-specific configuration and scripts overlay:

**Directory tree:**
```
003-settings-rootfs/
├── sbin/init               # Custom init (PID 1)
├── etc/rc.d/               # Startup/shutdown scripts
├── opt/scripts/            # Kiosk application scripts
├── etc/xdg/openbox/        # Window manager config
├── etc/X11/xorg.conf.d/    # X11 configuration
└── [PAM libraries and data]
```

**Scripts inventory (14 scripts, 4040 lines total):**

| Script | Lines | Purpose |
|--------|-------|---------|
| `arm64-boot-config.sh` | 592 | ARM64-specific boot configuration |
| `update-config` | 496 | Handle remote configuration updates |
| `welcome` | 615 | Network setup wizard (Ethernet/WiFi) |
| `welcome.backup` | 641 | Backup of original x86 version |
| `wizard` | 298 | Device configuration GTKDialog |
| `gui-app` | 332 | Browser launcher wrapper |
| `boot-capture` | 263 | Boot event logging |
| `first-run` | 13 | Orchestrator (calls welcome → wizard) |
| `first-run.backup` | 444 | Backup of original x86 binary |
| `daemon.sh` | 126 | Remote config polling daemon |
| `flow-logger` | 113 | Event flow logging |
| `apply-config` | 74 | Configuration applier |
| `wizard-now` | 32 | Trigger wizard from session |
| `extras` | 1 | Extension hooks marker |

**Param handlers (10 scripts, 1992 lines total):**

Configuration parameter handlers for remote management:

| Handler | Lines | Purpose |
|---------|-------|---------|
| `00-network.sh` | 222 | Network interface, IP, routing |
| `10-proxy.sh` | 142 | HTTP/HTTPS/SOCKS proxy settings |
| `20-browser.sh` | 247 | Chromium flags, homepage, cache |
| `30-display.sh` | 119 | Screen resolution, rotation, timeout |
| `40-input.sh` | 220 | Keyboard layout, mouse settings |
| `50-power.sh` | 201 | Suspend, hibernation, DPMS |
| `60-audio.sh` | 129 | Volume, mic, default devices |
| `70-services.sh` | 225 | Service enable/disable |
| `80-system.sh` | 272 | Hostname, timezone, NTP |
| `90-custom.sh` | 215 | User-defined parameters |

**Wizard support files:**
- `wizard-functions` - Common functions (101KB)
- `keyboards.txt` - 250+ keyboard layouts (18KB)
- `timezones.txt` - Timezone database (8.9KB)
- Printer configuration files (cups, hplip, zebra, star, etc.)
- License files (Chrome, Flash, Citrix)
- Tooltip data files

#### C. 000-kernel-rootfs/ (26 MB)

Kernel modules for Linux 6.1.93-v8+ (ARM64 Raspberry Pi):

**Structure:**
```
000-kernel-rootfs/lib/modules/6.1.93-v8+/
├── kernel/
│   ├── arch/arm64/crypto/    # ARM64 crypto accelerators
│   ├── arch/arm64/lib/       # ARM64 library functions
│   ├── crypto/               # Software crypto (AES, ChaCha20, etc.)
│   ├── drivers/
│   │   ├── block/            # RAID, dm, etc.
│   │   ├── net/              # Networking drivers
│   │   ├── gpu/              # Graphics drivers
│   │   ├── usb/              # USB controllers
│   │   ├── i2c/              # I2C bus
│   │   ├── spi/              # SPI bus
│   │   ├── input/            # Input devices
│   │   ├── sound/            # Audio drivers
│   │   ├── video/            # Video drivers
│   │   └── [many more]
│   ├── fs/                   # Filesystem modules
│   ├── lib/                  # Library modules
│   ├── net/
│   │   ├── ipv4/             # IPv4 networking
│   │   ├── ipv6/             # IPv6 networking
│   │   ├── netfilter/        # Firewall
│   │   ├── sched/            # Traffic scheduling
│   │   └── [networking]
│   └── mm/                   # Memory management
├── modules.dep.bin          # Binary dependency cache
├── modules.alias            # Module aliases
├── modules.order            # Load order
└── modules.builtin          # Built-in modules
```

**Key modules included:**
- Filesystem: ext4, btrfs, vfat, ntfs
- Networking: WiFi drivers, ethernet, PPP
- Graphics: DRM, VC4 (Raspberry Pi GPU)
- Sound: ALSA, USB audio
- Input: HID, USB input
- Crypto: AES, SHA, etc.

#### D. 08-ssh-rootfs/ (1.9 MB)

SSH server and utilities:

**Contents:**
```
08-ssh-rootfs/
├── etc/ssh/
│   ├── sshd_config          # SSH daemon configuration
│   ├── moduli              # DH key exchange parameters
│   └── sshd_config.d/      # Config drop-in directory
├── etc/rc.d/local_cli.d/
│   └── start-ssh           # SSH startup hook
├── usr/sbin/
│   └── sshd                # SSH server daemon
└── usr/lib/openssh/
    └── ssh-session-cleanup # Session cleanup utility
```

#### E. boot/ (Source boot files)

Raspberry Pi bootloader and kernel files:

**Contents:**
```
boot/
├── kernel8.img             # ARM64 kernel
├── initrd.img              # Initial ramdisk
├── bcm2711-rpi-4-b.dtb     # Device tree
├── config.txt              # Boot configuration
├── cmdline.txt             # Kernel command line
├── start4.elf / start4x.elf # GPU firmware
├── fixup4.dat / fixup4x.dat # Firmware fixup
├── overlays/
│   ├── vc4-kms-v3d.dtbo    # VC4 graphics
│   └── dwc2.dtbo           # USB OTG
└── FIRMWARE_NEEDED.txt     # Firmware notes
```

### Build Scripts

Located in `arm64/scripts/`:

| Script | Purpose | Lines |
|--------|---------|-------|
| `build-003-settings.sh` | Build 003-settings.xzm from source | 85 |
| `build-core-module.sh` | Build 001-core.xzm from rootfs | 189 |
| `download-packages.sh` | Download Debian packages for rootfs | 281 |
| `extract-packages.sh` | Extract .deb files to rootfs | 137 |
| `build-custom-packages.sh` | Build custom packages from source | 215 |
| `setup-directories.sh` | Initialize directory structure | 40 |

**Build workflow:**
```
1. setup-directories.sh  → Create output, staging directories
2. download-packages.sh  → Fetch ARM64 .deb packages from Debian Bookworm
3. extract-packages.sh   → dpkg-deb -x to rootfs/
4. build-custom-packages.sh → Build local packages (if needed)
5. build-core-module.sh  → mksquashfs rootfs/ → 001-core.xzm
6. build-003-settings.sh → mksquashfs 003-settings-rootfs/ → 003-settings.xzm
7. Copy .xzm files to ../iso-arm64/xzm/
```

### Output Directory

**Location:** `arm64/output/`
**Size:** 219 MB (compiled modules)

**Contents:**

| File | Size | Source | Purpose |
|------|------|--------|---------|
| `001-core.xzm` | 109 MB | `rootfs/` | Main system (latest: Jan 17 10:36) |
| `003-settings.xzm` | 7.0 MB | `003-settings-rootfs/` | Kiosk scripts (latest: Jan 15 17:41) |
| `000-kernel.xzm` | 19 MB | `000-kernel-rootfs/` | Kernel modules (latest: Jan 15 17:08) |
| `08-ssh.xzm` | 372 KB | `08-ssh-rootfs/` | SSH utilities (latest: Jan 15 17:07) |
| `kiosk-arm64.iso` | 85 MB | `iso-arm64/` | ISO data file (latest: Jan 13 08:40) |

### Additional Directories

**Other important build directories:**

- `build-source/` - Linux kernel source build artifacts
- `packages/` - Downloaded package cache
- `config/` - Configuration templates
- `scripts/` - Build and utility scripts
- `kernel-build/` - Kernel compilation intermediate files
- `staging/` - Module staging area

---

## Part 3: Boot Flow Integration

### Boot Sequence

```
Raspberry Pi 4 Power-on
    ↓
RPi Bootloader reads config.txt from FAT32 partition
    ↓
Load GPU firmware (start4.elf) + load kernel8.img
    ↓
GPU initializes, passes to ARM CPU
    ↓
Kernel boots with cmdline.txt parameters
    ↓
Kernel mounts initrd.img (from initrd.img)
    ↓
/sbin/init (PID 1) from 003-settings.xzm starts
    ↓
init mounts /proc, /sys, /dev, /run
    ↓
Runs /etc/rc.d/rc.S (system init)
    ↓
rc.S loads kernel modules from 000-kernel.xzm
    ↓
Runs /etc/rc.d/rc.4 (X11 startup)
    ↓
rc.4 starts X11, opens Openbox window manager
    ↓
Openbox runs autostart hook
    ↓
First-run wizard or direct kiosk launch
    ↓
Browser displays configured URL
```

### AUFS Union Mount Structure

After kernel loads, AUFS creates union mount:

```
Lower layers (read-only SquashFS):
  Layer 3: 000-kernel.xzm (kernel modules)
  Layer 2: 001-core.xzm (base system)
  Layer 1: 003-settings.xzm (kiosk configs)
           └─ Contains /sbin/init, /etc/rc.d/, /opt/scripts/

Upper layer (read-write tmpfs in RAM):
  Mounted at /
  Allows boot-time modifications without persisting

Union result at /: Read-write filesystem combining all layers
```

---

## Part 4: Key Script Functions

### Kiosk Script Call Chain

```
1. /sbin/init (PID 1)
   │
   ├─→ /etc/rc.d/rc.S (system initialization)
   │    ├─ Mount filesystems
   │    ├─ Load kernel modules
   │    ├─ Start udev
   │    └─ Run /etc/rc.d/local_cli.d/cli_commands
   │
   └─→ /etc/rc.d/rc.4 (X11 startup)
        ├─ Start X11 display server
        ├─ Start Openbox window manager
        ├─ Run /etc/rc.d/local_gui.d/gui_commands
        ├─ Execute /etc/rc.d/rc.4.xinitrc
        │   └─ Launch /opt/scripts/gui-app (browser wrapper)
        │       └─ Start Chromium with configured URL
        │
        └─ Post-Openbox phase
             ├─ Execute /etc/xdg/openbox/autostart
             └─ Start /etc/rc.d/local_net.d/daemon.sh
                 └─ Remote config polling daemon
```

### First-Run Wizard Flow

```
Boot → /sbin/init → rc.4 (X11 startup)
                        ↓
                   /opt/scripts/first-run
                        ↓
                   /opt/scripts/welcome
                   (Network Configuration)
                   ├─ Ethernet/WiFi selection
                   ├─ DHCP/Static IP config
                   └─ Save network settings
                        ↓
                   /opt/scripts/wizard
                   (Device Configuration)
                   ├─ Password entry
                   ├─ Device type selection
                   ├─ Facility/location
                   └─ Install config
                        ↓
                   System configured, reboot or continue
```

### Remote Configuration Pipeline

```
daemon.sh (polls every 60 seconds)
    ↓
Fetch config from remote server (HTTP GET)
    ↓
Update /etc/device-config.json (or similar)
    ↓
Call /opt/scripts/apply-config
    ↓
For each changed parameter:
    Call matching param-handler:
    ├─ 00-network.sh → Configure networking
    ├─ 20-browser.sh → Update browser settings
    ├─ 80-system.sh  → Update hostname/timezone
    └─ etc.
    ↓
Apply changes without reboot (live reconfig)
```

---

## Part 5: File Size Summary

### Source Sizes

| Component | Size | Notes |
|-----------|------|-------|
| rootfs/ | 450 MB | Debian Bookworm ARM64 base |
| 003-settings-rootfs/ | 44 MB | Kiosk scripts and configs |
| 000-kernel-rootfs/ | 26 MB | Kernel modules for 6.1.93-v8+ |
| 08-ssh-rootfs/ | 1.9 MB | SSH utilities |
| **Total source** | **521 MB** | Before compression |

### Compiled Module Sizes

| Module | Size | Compression | Source Size |
|--------|------|-------------|-------------|
| 001-core.xzm | 109 MB | -Xbcj arm -comp xz | 450 MB |
| 003-settings.xzm | 7.0 MB | -comp xz | 44 MB |
| 000-kernel.xzm | 19 MB | -comp xz | 26 MB |
| 08-ssh.xzm | 372 KB | -comp xz | 1.9 MB |
| firmware.xzm | 364 KB | -comp xz | 364 KB |
| **Total modules** | **136 MB** | 4.3x compression | 522 MB |

### Staging Directory (iso-arm64/)

| Component | Size |
|-----------|------|
| xzm/ (modules) | 136 MB |
| boot/ | ~4 MB |
| firmware-rootfs/ | ~200 KB |
| docs/ | ~100 KB |
| **Total staging** | **~140 MB** |

---

## Part 6: Critical Build Flags Reference

### mksquashfs Configuration

Used in `build-core-module.sh` and `build-003-settings.sh`:

```bash
mksquashfs SOURCE_DIR OUTPUT.xzm \
  -force-uid 0 -force-gid 0    # CRITICAL: Force root ownership
  -comp xz -b 256K              # XZ compression with 256KB blocks
  -Xbcj arm                     # ARM binary filter (001-core only)
  -noappend                     # Clean rebuild (don't append)
```

**Critical flags:**
- `-force-uid 0 -force-gid 0` - Ensures files boot as root (MUST INCLUDE)
- `-comp xz` - XZ compression for better ratio than gzip
- `-Xbcj arm` - ARM instruction filter for binaries (001-core)
- `-noappend` - Rebuild from scratch, don't append to existing

---

## Part 7: GLIBC Compatibility Note

**IMPORTANT:** All Debian packages must use **GLIBC 2.36** (Bookworm standard).

Source: `/home/culler/saas_dev/pk-port/arm64/rootfs/`
- Debian Bookworm ARM64 provides GLIBC 2.36
- Do NOT mix with Ubuntu packages (use 2.38)
- All compiled binaries and .deb packages must be ARM64 architecture

Check compatibility:
```bash
objdump -T /path/to/binary | grep GLIBC_
```

---

## Summary

This comprehensive directory map documents:

1. **iso-arm64/** - The final bootable staging directory containing:
   - Raspberry Pi bootloader files
   - 5 SquashFS modules (135 MB total)
   - Firmware and documentation

2. **arm64/** - The source build system containing:
   - Source rootfs directories (521 MB)
   - Build scripts for module compilation
   - Compiled output modules (219 MB)

3. **Boot integration:**
   - RPi bootloader → kernel → /sbin/init → rc.S/rc.4 → GUI app
   - AUFS union mount of SquashFS layers
   - Remote configuration polling daemon

4. **Kiosk application stack:**
   - 14 main scripts (4040 lines)
   - 10 parameter handlers (1992 lines)
   - GTKDialog-based wizards
   - Chromium browser in fullscreen kiosk mode

The ARM64 port maintains compatibility with the original x86 architecture while adapting specifically for Raspberry Pi 4 hardware (BCM2711).
