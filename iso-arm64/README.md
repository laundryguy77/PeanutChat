# Porteus Kiosk ARM64

This directory contains the ARM64 (Raspberry Pi 4) build of Porteus Kiosk, structured to match the original x86 ISO layout.

## Directory Structure

```
iso-arm64/
├── boot/                   # Raspberry Pi boot files
│   ├── kernel8.img         # ARM64 Linux kernel
│   ├── initrd.img          # Initial ramdisk
│   ├── bcm2711-rpi-4-b.dtb # Device tree blob for RPi 4
│   ├── start4.elf          # GPU firmware (standard)
│   ├── start4x.elf         # GPU firmware (extended memory)
│   ├── fixup4.dat          # Firmware fixup (standard)
│   ├── fixup4x.dat         # Firmware fixup (extended memory)
│   ├── config.txt          # RPi boot configuration
│   ├── cmdline.txt         # Kernel command line
│   └── overlays/           # Device tree overlays
├── docs/
│   ├── kiosk.sgn           # Signature file (empty for ARM64)
│   ├── version             # Version string (1.0.0-arm64)
│   ├── default.jpg         # Default background image
│   ├── License.txt         # License information
│   └── GNU_GPL             # GPL license text
├── xzm/
│   ├── 000-kernel.xzm      # Kernel modules
│   ├── 001-core.xzm        # Core system
│   └── 003-settings.xzm    # Kiosk settings
├── make_iso.sh             # ISO creation script
└── README.md               # This file
```

## Differences from x86 Version

| Feature | x86 | ARM64 |
|---------|-----|-------|
| Boot loader | isolinux/UEFI | Raspberry Pi bootloader |
| Kernel | vmlinuz | kernel8.img |
| Device tree | Not needed | bcm2711-rpi-4-b.dtb |
| GPU firmware | Not needed | start4.elf, fixup4.dat |
| ISO bootable | Yes (El Torito) | No (data only) |
| Target hardware | x86 PCs | Raspberry Pi 4 |

## Boot Process Differences

### x86
1. BIOS/UEFI loads isolinux from ISO
2. isolinux loads kernel and initrd
3. Kernel mounts ISO and overlays XZM modules

### ARM64 (Raspberry Pi 4)
1. RPi bootloader reads config.txt from SD card/USB
2. Loads kernel8.img, initrd.img, and DTB
3. Kernel mounts XZM modules from storage

## Creating the ISO

```bash
./make_iso.sh
```

This creates `../kiosk-arm64.iso` with volume label "Kiosk" (required by init scripts).

Note: The ISO is a data ISO only - the Raspberry Pi cannot boot directly from ISO. Instead:

1. Format SD card with FAT32 partition
2. Copy `boot/` contents to SD card root
3. Copy `xzm/` and `docs/` directories to SD card
4. Boot Raspberry Pi 4 from the SD card

## Hardware Requirements

- Raspberry Pi 4 (BCM2711)
- SD card or USB storage (FAT32 formatted)
- Minimum 1GB RAM recommended

## Version

- ARM64 Build: 1.0.0-arm64
- Based on Porteus Kiosk architecture
