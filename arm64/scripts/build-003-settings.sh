#!/bin/bash
#
# build-003-settings.sh - Build 003-settings.xzm for ARM64
#
# This script packages the settings rootfs (init scripts, rc.d,
# openbox config, etc.) into a squashfs module.
#

set -e

BASEDIR="/home/culler/saas_dev/pk-port/arm64"
ROOTFS="$BASEDIR/003-settings-rootfs"
OUTPUTDIR="$BASEDIR/output"
OUTPUT="$OUTPUTDIR/003-settings.xzm"

echo "=== ARM64 003-settings.xzm Builder ==="
echo "Source: $ROOTFS"
echo "Output: $OUTPUT"
echo ""

# Check for rootfs
if [[ ! -d "$ROOTFS" ]]; then
    echo "Error: Settings rootfs not found at $ROOTFS"
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

# Ensure scripts are executable
echo "=== Setting Permissions ==="
chmod +x "$ROOTFS"/sbin/init 2>/dev/null || true
chmod +x "$ROOTFS"/etc/rc.d/rc.* 2>/dev/null || true
chmod +x "$ROOTFS"/etc/rc.d/rc.inet1 2>/dev/null || true
chmod +x "$ROOTFS"/etc/rc.d/rc.FireWall 2>/dev/null || true
chmod +x "$ROOTFS"/opt/scripts/* 2>/dev/null || true
chmod +x "$ROOTFS"/etc/xdg/openbox/autostart 2>/dev/null || true

echo ""
echo "=== Source Size ==="
du -sh "$ROOTFS"

# Build squashfs
echo ""
echo "=== Building SquashFS Module ==="

# Remove old output if exists
rm -f "$OUTPUT"

# Build with XZ compression (same settings as 001-core)
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
unsquashfs -s "$OUTPUT" 2>/dev/null | head -10

echo ""
echo "Key files in module:"
unsquashfs -l "$OUTPUT" 2>/dev/null | grep -E "(sbin/init|rc\.[0-9SM]|autostart|first-run)" | head -20

echo ""
echo "=== Ready ==="
echo ""
echo "Copy to iso-arm64/xzm/:"
echo "  cp $OUTPUT /home/culler/saas_dev/pk-port/iso-arm64/xzm/"
echo ""
