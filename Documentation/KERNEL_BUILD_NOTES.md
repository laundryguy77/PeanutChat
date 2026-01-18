# ARM64 Kernel Build Notes - AUFS for RPi 4

## Recommended Configuration

- **Kernel:** RPi 6.1.y branch (LTS)
- **AUFS:** aufs-standalone aufs6.1 branch
- **Target:** Raspberry Pi 4 (BCM2711)
- **Architecture:** ARM64 (aarch64)

## Build Environment Setup

```bash
# Install cross-compiler (Ubuntu/Debian)
sudo apt install gcc-aarch64-linux-gnu make git bc bison flex libssl-dev

# Clone RPi kernel
git clone --depth=1 --branch rpi-6.1.y https://github.com/raspberrypi/linux
cd linux

# Clone AUFS patches
git clone git://github.com/sfjro/aufs-standalone.git ../aufs-standalone
cd ../aufs-standalone && git checkout origin/aufs6.1 && cd ../linux
```

## Apply AUFS Patches

```bash
# Apply in this order
patch -p1 < ../aufs-standalone/aufs6-kbuild.patch
patch -p1 < ../aufs-standalone/aufs6-base.patch
patch -p1 < ../aufs-standalone/aufs6-mmap.patch
patch -p1 < ../aufs-standalone/aufs6-standalone.patch

# Copy AUFS source files
cp -r ../aufs-standalone/fs/aufs fs/
cp ../aufs-standalone/include/uapi/linux/aufs_type.h include/uapi/linux/
```

## Configure Kernel

```bash
# Start with RPi 4 default config
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- bcm2711_defconfig

# Enable required options
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- menuconfig
```

### Required Config Options

```
CONFIG_AUFS_FS=m              # AUFS as module
CONFIG_SQUASHFS=y             # Squashfs support
CONFIG_SQUASHFS_XZ=y          # XZ compression
CONFIG_TMPFS=y                # Tmpfs support
CONFIG_DEVTMPFS=y             # Devtmpfs
CONFIG_DEVTMPFS_MOUNT=y       # Auto-mount devtmpfs
CONFIG_DRM_VC4=y              # RPi GPU driver
```

## Build Kernel

```bash
# Build kernel image
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j$(nproc) Image

# Build modules
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j$(nproc) modules

# Build device tree blobs
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j$(nproc) dtbs
```

## Output Files

After build:
- `arch/arm64/boot/Image` → rename to `kernel8.img`
- `arch/arm64/boot/dts/broadcom/bcm2711-rpi-4-b.dtb`
- Modules in various directories

## Install to SD Card

```bash
# Mount boot partition
sudo mount /dev/sdX1 /mnt/boot

# Copy kernel
sudo cp arch/arm64/boot/Image /mnt/boot/kernel8.img

# Copy DTB
sudo cp arch/arm64/boot/dts/broadcom/bcm2711-rpi-4-b.dtb /mnt/boot/

# Install modules to root partition
sudo mount /dev/sdX2 /mnt/root
sudo make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
    INSTALL_MOD_PATH=/mnt/root modules_install
```

## Known Issues

### Kernel 6.3+ Unmount Bug
Linux 6.3.0 introduced a regression where AUFS mounts cannot be unmounted during shutdown. Stick to 6.1.y or apply the fix from [issue #29](https://github.com/sfjro/aufs-standalone/issues/29).

### Patch Application Failures
If patches don't apply cleanly:
1. Try an earlier kernel version (6.0.y)
2. Check [aufs-standalone issues](https://github.com/sfjro/aufs-standalone/issues) for fixes
3. Manual patch resolution may be needed

## Testing AUFS

```bash
# Load module
sudo modprobe aufs

# Test union mount
mkdir -p /tmp/lower /tmp/upper /tmp/union
sudo mount -t aufs -o br=/tmp/upper=rw:/tmp/lower=ro none /tmp/union

# Verify
mount | grep aufs
ls /tmp/union

# Test unmount
sudo umount /tmp/union
```

## References

- [AUFS Standalone](https://github.com/sfjro/aufs-standalone)
- [RPi Kernel Docs](https://www.raspberrypi.com/documentation/computers/linux_kernel.html)
- [AUFS SourceForge](https://aufs.sourceforge.net/)
