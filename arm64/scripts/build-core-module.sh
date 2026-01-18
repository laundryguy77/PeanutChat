#!/bin/bash
#
# build-core-module.sh - Build 001-core.xzm for ARM64
#
# This script takes the assembled rootfs and creates the final
# squashfs module for Porteus Kiosk ARM64.
#

set -e

BASEDIR="/home/culler/saas_dev/pk-port/arm64"
ROOTFS="$BASEDIR/rootfs"
OUTPUTDIR="$BASEDIR/output"
OUTPUT="$OUTPUTDIR/001-core.xzm"

echo "=== ARM64 001-core.xzm Builder ==="
echo "Source: $ROOTFS"
echo "Output: $OUTPUT"
echo ""

# Check for rootfs
if [[ ! -d "$ROOTFS" ]]; then
    echo "Error: Rootfs not found at $ROOTFS"
    echo "Run extract-packages.sh first"
    exit 1
fi

# Check for mksquashfs
if ! command -v mksquashfs &> /dev/null; then
    echo "Error: mksquashfs not found"
    echo "Install with: sudo apt-get install squashfs-tools"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUTDIR"

# Pre-build cleanup
echo "=== Pre-Build Cleanup ==="

# 1. Remove documentation (optional - comment out to keep)
echo "Removing documentation..."
rm -rf "$ROOTFS"/usr/share/doc/* 2>/dev/null || true
rm -rf "$ROOTFS"/usr/share/man/* 2>/dev/null || true
rm -rf "$ROOTFS"/usr/share/info/* 2>/dev/null || true
rm -rf "$ROOTFS"/usr/share/gtk-doc/* 2>/dev/null || true

# 2. Remove unnecessary locales (keep en_US only)
echo "Cleaning locales..."
if [[ -d "$ROOTFS/usr/share/locale" ]]; then
    find "$ROOTFS/usr/share/locale" -mindepth 1 -maxdepth 1 \
        -type d ! -name "en" ! -name "en_US" ! -name "en_US.UTF-8" \
        -exec rm -rf {} \; 2>/dev/null || true
fi

# 3. Remove X86-specific drivers and files
echo "Removing x86-specific components..."

# X86 Xorg video drivers
rm -f "$ROOTFS"/usr/lib/*/xorg/modules/drivers/intel_drv.so 2>/dev/null || true
rm -f "$ROOTFS"/usr/lib/*/xorg/modules/drivers/amdgpu_drv.so 2>/dev/null || true
rm -f "$ROOTFS"/usr/lib/*/xorg/modules/drivers/ati_drv.so 2>/dev/null || true
rm -f "$ROOTFS"/usr/lib/*/xorg/modules/drivers/nouveau_drv.so 2>/dev/null || true
rm -f "$ROOTFS"/usr/lib/*/xorg/modules/drivers/vesa_drv.so 2>/dev/null || true
rm -f "$ROOTFS"/usr/lib/*/xorg/modules/drivers/vmware_drv.so 2>/dev/null || true
rm -f "$ROOTFS"/usr/lib/*/xorg/modules/drivers/qxl_drv.so 2>/dev/null || true

# X86 DRI drivers (keep swrast for software rendering)
rm -f "$ROOTFS"/usr/lib/*/dri/i915_dri.so 2>/dev/null || true
rm -f "$ROOTFS"/usr/lib/*/dri/i965_dri.so 2>/dev/null || true
rm -f "$ROOTFS"/usr/lib/*/dri/iris_dri.so 2>/dev/null || true
rm -f "$ROOTFS"/usr/lib/*/dri/radeon_dri.so 2>/dev/null || true
rm -f "$ROOTFS"/usr/lib/*/dri/radeonsi_dri.so 2>/dev/null || true
rm -f "$ROOTFS"/usr/lib/*/dri/r200_dri.so 2>/dev/null || true
rm -f "$ROOTFS"/usr/lib/*/dri/r300_dri.so 2>/dev/null || true
rm -f "$ROOTFS"/usr/lib/*/dri/r600_dri.so 2>/dev/null || true
rm -f "$ROOTFS"/usr/lib/*/dri/nouveau_dri.so 2>/dev/null || true
rm -f "$ROOTFS"/usr/lib/*/dri/nouveau_vieux_dri.so 2>/dev/null || true
rm -f "$ROOTFS"/usr/lib/*/dri/vmwgfx_dri.so 2>/dev/null || true

# X86-only binaries
rm -f "$ROOTFS"/sbin/v86d 2>/dev/null || true
rm -f "$ROOTFS"/usr/bin/isohybrid 2>/dev/null || true

# 4. Strip binaries (optional - significant size reduction)
echo "Stripping binaries..."
if command -v aarch64-linux-gnu-strip &> /dev/null; then
    STRIP_CMD="aarch64-linux-gnu-strip"
else
    # Use regular strip - may not work on ARM64 binaries from x86 host
    STRIP_CMD="strip"
    echo "Warning: Using local strip, may not work on ARM64 binaries"
fi

# Strip executables
find "$ROOTFS" -type f -executable -exec file {} \; 2>/dev/null | \
    grep "ELF.*aarch64" | cut -d: -f1 | \
    while read -r f; do
        $STRIP_CMD --strip-unneeded "$f" 2>/dev/null || true
    done

# Strip shared libraries
find "$ROOTFS" -name "*.so*" -type f -exec file {} \; 2>/dev/null | \
    grep "ELF.*aarch64" | cut -d: -f1 | \
    while read -r f; do
        $STRIP_CMD --strip-unneeded "$f" 2>/dev/null || true
    done

# 5. Remove empty directories (except essential mount points)
echo "Removing empty directories..."
find "$ROOTFS" -type d -empty -delete 2>/dev/null || true

# 5b. Recreate essential mount point directories (required for init)
echo "Creating essential mount point directories..."
mkdir -p "$ROOTFS"/{dev,proc,sys,tmp,run,mnt,media,root,home}
mkdir -p "$ROOTFS"/var/{log,run,lock,tmp,cache,lib}
chmod 1777 "$ROOTFS/tmp" 2>/dev/null || true
chmod 1777 "$ROOTFS/var/tmp" 2>/dev/null || true
# Add .keep files so mksquashfs preserves empty directories
for dir in dev proc sys tmp run mnt media root home; do
    touch "$ROOTFS/$dir/.keep" 2>/dev/null || true
done

# 6. Remove package management files (we don't need apt in the final system)
echo "Removing package management data..."
rm -rf "$ROOTFS"/var/lib/apt 2>/dev/null || true
rm -rf "$ROOTFS"/var/lib/dpkg 2>/dev/null || true
rm -rf "$ROOTFS"/var/cache/apt 2>/dev/null || true

echo ""
echo "=== Size After Cleanup ==="
du -sh "$ROOTFS"

# Build squashfs
echo ""
echo "=== Building SquashFS Module ==="

# Remove old output if exists
rm -f "$OUTPUT"

# Build with XZ compression
echo "Creating squashfs with XZ compression..."
mksquashfs "$ROOTFS" "$OUTPUT" \
    -comp xz \
    -b 256K \
    -Xbcj arm \
    -no-exports \
    -no-recovery \
    -always-use-fragments \
    -force-uid 0 \
    -force-gid 0

echo ""
echo "=== Build Complete ==="
echo ""
echo "Output file: $OUTPUT"
ls -lh "$OUTPUT"
echo ""

# Verify the module
echo "=== Module Verification ==="
echo "Checking squashfs contents..."

# Get module info
unsquashfs -s "$OUTPUT" 2>/dev/null | head -20

echo ""
echo "File count in module:"
unsquashfs -l "$OUTPUT" 2>/dev/null | wc -l

echo ""
echo "=== Module Ready ==="
echo ""
echo "The 001-core.xzm module is ready for testing."
echo ""
echo "To test on Raspberry Pi:"
echo "1. Copy $OUTPUT to the Porteus boot media"
echo "2. Ensure 000-kernel.xzm is also present"
echo "3. Boot and verify X11 starts"
echo ""
echo "To inspect contents:"
echo "  unsquashfs -l $OUTPUT | less"
echo "  unsquashfs -d /tmp/test-core $OUTPUT"
