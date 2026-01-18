# TuxOS ARM64 Boot Structure for Raspberry Pi 4

## Overview

This document describes the boot partition structure for TuxOS ARM64 on Raspberry Pi 4. The RPi boot mechanism differs significantly from x86 - instead of BIOS/UEFI with isolinux/GRUB, the RPi uses its VideoCore GPU to load firmware and kernel.

## Boot Chain Comparison

### x86 (Original TuxOS)
```
BIOS/UEFI -> isolinux/GRUB -> vmlinuz -> initrd.xz -> /init -> switch_root
```

### Raspberry Pi 4 ARM64
```
GPU bootloader -> start4.elf -> kernel8.img -> initrd.img -> /init -> switch_root
```

## Boot Directory Structure

```
arm64/boot/
├── config.txt           # RPi boot configuration (created)
├── cmdline.txt          # Kernel command line parameters (created)
├── FIRMWARE_NEEDED.txt  # List of required firmware files (created)
├── overlays/            # Device tree overlays directory (created)
│   └── (device tree overlay .dtbo files go here)
├── kernel8.img          # ARM64 kernel (TO BUILD - from kernel-build/)
├── initrd.img           # ARM64 initramfs (TO BUILD - from initrd-work/)
├── start4.elf           # GPU firmware for RPi 4 (TO DOWNLOAD)
├── fixup4.dat           # GPU memory fixup for RPi 4 (TO DOWNLOAD)
├── start4x.elf          # GPU firmware with extra codecs (TO DOWNLOAD)
├── fixup4x.dat          # GPU memory fixup for extra codecs (TO DOWNLOAD)
└── bcm2711-rpi-4-b.dtb  # Device tree blob for RPi 4 (TO DOWNLOAD)
```

## Files Created

### config.txt
RPi boot configuration file. Key settings:
- `kernel=kernel8.img` - ARM64 kernel image
- `initramfs initrd.img followkernel` - Load initramfs after kernel in memory
- `arm_64bit=1` - Enable 64-bit mode
- `gpu_mem=128` - Allocate 128MB for GPU (needed for browser/graphics)
- `dtoverlay=vc4-kms-v3d` - Enable DRM VC4 V3D driver for graphics
- `hdmi_force_hotplug=1` - Force HDMI output even without monitor at boot
- `enable_uart=1` - Enable serial console for debugging

### cmdline.txt
Kernel command line parameters:
- `quiet` - Suppress most kernel messages
- `loglevel=3` - Only show error messages
- `first_run` - Signal first boot (triggers setup wizard)
- `run_splash` - Display boot splash screen

This replaces the isolinux kernel parameters from x86.

### FIRMWARE_NEEDED.txt
Documents the firmware files that need to be downloaded from the RPi firmware repository.

## Files Still Needed

### From Raspberry Pi Firmware Repository
Download from: https://github.com/raspberrypi/firmware/tree/master/boot

| File | Purpose | Required |
|------|---------|----------|
| start4.elf | GPU firmware for RPi 4 | YES |
| fixup4.dat | Memory mapping for RPi 4 | YES |
| start4x.elf | GPU firmware with codec support | Optional |
| fixup4x.dat | Memory mapping for codec version | Optional |
| bcm2711-rpi-4-b.dtb | Device tree for RPi 4 Model B | YES |

Download commands:
```bash
cd arm64/boot
wget https://github.com/raspberrypi/firmware/raw/master/boot/start4.elf
wget https://github.com/raspberrypi/firmware/raw/master/boot/fixup4.dat
wget https://github.com/raspberrypi/firmware/raw/master/boot/bcm2711-rpi-4-b.dtb
```

### From Kernel Build
These will be generated when the kernel is built:

| File | Source | Notes |
|------|--------|-------|
| kernel8.img | kernel-build/linux/arch/arm64/boot/Image | May need renaming |
| Device tree overlays | kernel-build/linux/arch/arm64/boot/dts/overlays/*.dtbo | Optional |

### From Initramfs Build
| File | Source | Notes |
|------|--------|-------|
| initrd.img | Generated from initrd-work/ | ARM64 initramfs with modified /init |

## Boot Partition Layout

The boot partition should be FAT32 formatted (required by RPi firmware).

Recommended partition scheme for SD card or USB:
```
/dev/sdX1  - FAT32 boot partition (~256MB)
/dev/sdX2  - System partition (ISO or ext4)
/dev/sdX3  - (reserved)
/dev/sdX4  - StorageBkp persistent storage (XFS)
```

## Key Differences from x86

| Aspect | x86 TuxOS | RPi ARM64 TuxOS |
|--------|-----------|-----------------|
| Boot firmware | BIOS/UEFI | VideoCore GPU |
| Bootloader | isolinux/GRUB | config.txt + start4.elf |
| Kernel format | bzImage | Image (uncompressed) |
| Kernel location | boot/vmlinuz | boot/kernel8.img |
| Initramfs | boot/initrd.xz | boot/initrd.img |
| Boot config | isolinux.cfg/grub.cfg | config.txt |
| Kernel params | In bootloader config | cmdline.txt |
| Device discovery | PCI enumeration (lspci) | Device tree |
| Graphics driver | i915/nouveau/uvesafb | vc4-drm |

## Status

| Item | Status |
|------|--------|
| Boot directory structure | CREATED |
| config.txt | CREATED |
| cmdline.txt | CREATED |
| overlays/ directory | CREATED |
| FIRMWARE_NEEDED.txt | CREATED |
| RPi firmware files | NOT DOWNLOADED (manual download required) |
| kernel8.img | PENDING (kernel build) |
| initrd.img | PENDING (initramfs build) |
| Device tree blobs | NOT DOWNLOADED |

## Next Steps

1. Download RPi firmware files (start4.elf, fixup4.dat, bcm2711-rpi-4-b.dtb)
2. Complete kernel build and copy kernel8.img
3. Build ARM64 initramfs with modified /init script
4. Test boot on Raspberry Pi 4 hardware

## References

- ARM_PORTING_NOTES.md - Section 6 (Boot Architecture Differences)
- KIOSK_BOOT_ANALYSIS.md - Original x86 boot analysis
- https://www.raspberrypi.com/documentation/computers/config_txt.html
- https://github.com/raspberrypi/firmware

---
Created: 2026-01-12
Purpose: Document RPi 4 boot structure for TuxOS ARM64 port
