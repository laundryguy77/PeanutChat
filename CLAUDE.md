# TuxOS ARM64 Port - Claude Instructions

## Project Overview

This is an ARM64 port of TuxOS (Porteus Kiosk derivative) for Raspberry Pi 4. The system uses SquashFS modules (.xzm) with AUFS union mount for a live kiosk environment.

**Goal:** A locked-down kiosk that boots into a fullscreen browser pointing to a configured URL, with remote configuration management.

---

## Critical Rule: Module Modification Workflow

**NEVER modify files directly in `iso-arm64/xzm/` or extract modules there.**
**ALWAYS modify the source directories in `arm64/` and rebuild.**

### Source → Staging Flow

```
arm64/rootfs/             → build → arm64/output/001-core.xzm     → copy → iso-arm64/xzm/
arm64/003-settings-rootfs/ → build → arm64/output/003-settings.xzm → copy → iso-arm64/xzm/
arm64/000-kernel-rootfs/  → build → arm64/output/000-kernel.xzm   → copy → iso-arm64/xzm/
arm64/08-ssh-rootfs/      → build → arm64/output/08-ssh.xzm       → copy → iso-arm64/xzm/
arm64/boot/               → copy  → iso-arm64/boot/
```

### Module Source Directories

| Module | Source Directory | Contains |
|--------|------------------|----------|
| 001-core.xzm | `arm64/rootfs/` | Main system (binaries, libraries, packages) |
| 003-settings.xzm | `arm64/003-settings-rootfs/` | Init scripts, rc.d, kiosk scripts, configs |
| 000-kernel.xzm | `arm64/000-kernel-rootfs/` | Kernel modules (lib/modules/6.1.93-v8+/) |
| 08-ssh.xzm | `arm64/08-ssh-rootfs/` | SSH utilities |

### Key Files for Kiosk Behavior (in 003-settings-rootfs/)

- `/sbin/init` - Custom init script (PID 1, busybox sh)
- `/etc/rc.d/rc.S` - System initialization (mounts, udev, modules)
- `/etc/rc.d/rc.4` - X11 session startup
- `/opt/scripts/first-run` - First-run wizard orchestrator
- `/opt/scripts/welcome` - Network configuration wizard (8-page GTKDialog)
- `/opt/scripts/wizard` - TuxOS device configuration wizard
- `/opt/scripts/update-config` - Configuration updater/reconfiguration handler
- `/etc/xdg/openbox/autostart` - Post-openbox startup
- `/etc/rc.d/local_net.d/daemon.sh` - Remote config polling daemon

---

## Build Workflow

### Division of Labor

| Steps | Who | What |
|-------|-----|------|
| 1-2 | **Claude Code** | Modify source, rebuild modules, copy to staging |
| 3-4 | **User** | Build image (sudo), burn to SD (sudo) |

### Claude Code Does (Steps 1-2)

**Rebuild 003-settings.xzm (scripts/configs):**
```bash
cd /home/culler/saas_dev/pk-port/arm64
./scripts/build-003-settings.sh
cp output/003-settings.xzm ../iso-arm64/xzm/
```

**Rebuild 001-core.xzm (packages/libraries):**
```bash
cd /home/culler/saas_dev/pk-port/arm64
./scripts/build-core-module.sh
cp output/001-core.xzm ../iso-arm64/xzm/
```

### User Does (Steps 3-4)
```bash
sudo bash /home/culler/saas_dev/pk-port/iso-arm64/make_img.sh
sudo bash /home/culler/saas_dev/pk-port/burn_sd.sh
```

---

## mksquashfs Critical Flags

**ALWAYS include these flags when building modules:**
```bash
-force-uid 0 -force-gid 0  # CRITICAL: Forces root ownership
-comp xz -b 256K           # Compression settings
-Xbcj arm                  # ARM binary filter (for 001-core)
-noappend                  # Clean rebuild
```

**Missing `-force-uid 0 -force-gid 0` causes permission failures at boot.**

---

## Package Installation

To add Debian packages:
```bash
# Download ARM64 .deb from Debian Bookworm (user may need to download manually due to sandbox)
# Extract to source rootfs:
dpkg-deb -x /path/to/package_arm64.deb /home/culler/saas_dev/pk-port/arm64/rootfs/
# Then rebuild 001-core.xzm
```

**GLIBC Version:** Debian Bookworm uses GLIBC 2.36. Do NOT mix with Ubuntu packages (2.38).

---

## Change Tracking

**Use git commits for all changes.** After making significant changes:

```bash
cd /home/culler/saas_dev/pk-port
git add -A
git commit -m "Description of what changed and why"
```

Commit messages should be descriptive:
- "Add libfoo to 001-core for browser support"
- "Fix network interface detection in rc.S (eth0→end0)"
- "Simplify first-run wizard flow"

---

## Documentation Reference

### Key Reference Documents (in Documentation/)

| Document | Purpose |
|----------|---------|
| `SYSTEM_ARCHITECTURE.md` | Complete system reference - architecture, boot flow, config format |
| `BOOT_SEQUENCE.md` | Detailed boot sequence and reconfiguration analysis |
| `BINARY_ANALYSIS.md` | Analysis of first-run/update-config binaries |
| `ARM_PORTING_NOTES.md` | x86 dependencies and ARM solutions |
| `SCRIPTS_REFERENCE.md` | Script inventory and hook points |
| `PARAM_REFERENCE.md` | Remote config parameter reference |
| `GUI_APP_BROWSER_FLAGS.md` | Chromium flags and config mapping |
| `ARM64_BOOT_CONFIG_TESTS.md` | Test scenarios for boot configuration |

### Build Procedure
| Document | Purpose |
|----------|---------|
| `ISO_BUILD_PROCEDURE.md` | Full build procedure and workflow |

### Goal UI Reference
Screenshots of intended wizard flow: `screenshots/ui1-5.webp`

---

## Target UI Flow (from screenshots)

```
first-run → welcome (Ethernet/WiFi selection)
         → Connection Confirmation
         → wizard (Password entry)
         → Device Config (Type/Facility/Number)
         → Install to SD card
```

---

## User Preferences

- Always use subagents when possible for parallel operations
- External wget may require user to download manually (sandbox restriction)
- Commit changes to git with descriptive messages
- GLIBC 2.36 only - no Ubuntu packages
