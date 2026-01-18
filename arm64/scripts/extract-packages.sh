#!/bin/bash
#
# extract-packages.sh - Extract ARM64 .deb packages to rootfs
#
# This script extracts downloaded Debian packages and assembles them
# into a unified rootfs structure for 001-core.xzm
#

set -e

BASEDIR="/home/culler/saas_dev/pk-port/arm64"
PKGDIR="$BASEDIR/packages/debs"
EXTRACTDIR="$BASEDIR/packages/extracted"
ROOTFS="$BASEDIR/rootfs"

echo "=== ARM64 Package Extractor ==="
echo "Source: $PKGDIR"
echo "Target: $ROOTFS"
echo ""

# Create directories
mkdir -p "$EXTRACTDIR"
mkdir -p "$ROOTFS"

# Count packages
PKG_COUNT=$(ls -1 "$PKGDIR"/*.deb 2>/dev/null | wc -l)

if [[ "$PKG_COUNT" -eq 0 ]]; then
    echo "Error: No .deb packages found in $PKGDIR"
    echo "Run download-packages.sh first"
    exit 1
fi

echo "Found $PKG_COUNT packages to extract"
echo ""

# Extract each package
extract_package() {
    local deb="$1"
    local name=$(basename "$deb" .deb)
    local tmpdir="$EXTRACTDIR/$name"

    echo "Extracting: $name"

    # Create temp directory
    mkdir -p "$tmpdir"

    # Extract using dpkg-deb
    dpkg-deb -x "$deb" "$tmpdir" 2>/dev/null || {
        echo "  Warning: Failed to extract $name"
        return 1
    }

    # Copy to rootfs
    cp -a "$tmpdir"/* "$ROOTFS"/ 2>/dev/null || true

    return 0
}

# Process all packages
EXTRACTED=0
FAILED=0

for deb in "$PKGDIR"/*.deb; do
    if extract_package "$deb"; then
        ((EXTRACTED++))
    else
        ((FAILED++))
    fi
done

echo ""
echo "=== Extraction Summary ==="
echo "Successfully extracted: $EXTRACTED"
echo "Failed: $FAILED"
echo ""

# Post-extraction cleanup and fixes
echo "=== Post-Extraction Fixes ==="

# 1. Create standard symlinks
echo "Creating standard symlinks..."

cd "$ROOTFS"

# Ensure /lib exists and link ld-linux-aarch64
if [[ -d lib/aarch64-linux-gnu ]]; then
    ln -sf aarch64-linux-gnu/ld-linux-aarch64.so.1 lib/ld-linux-aarch64.so.1 2>/dev/null || true
fi

# Create /lib64 symlink if needed (some apps expect it)
if [[ ! -e lib64 ]]; then
    ln -sf lib lib64
fi

# Create /usr/lib64 symlink if needed
if [[ ! -e usr/lib64 ]] && [[ -d usr/lib ]]; then
    ln -sf lib usr/lib64
fi

# 2. Fix broken symlinks
echo "Checking for broken symlinks..."
find "$ROOTFS" -type l ! -exec test -e {} \; -print 2>/dev/null | head -20

# 3. Create essential directories
echo "Creating essential directories..."
mkdir -p "$ROOTFS"/{dev,proc,sys,tmp,run,mnt,media,root,home}
mkdir -p "$ROOTFS"/var/{log,run,lock,tmp,cache,lib}
mkdir -p "$ROOTFS"/etc/{X11,openbox,default,init.d}

# 4. Set permissions
echo "Setting permissions..."
chmod 1777 "$ROOTFS/tmp" 2>/dev/null || true
chmod 1777 "$ROOTFS/var/tmp" 2>/dev/null || true

# 5. List library dependencies
echo ""
echo "=== Library Analysis ==="

# Count libraries
LIB_COUNT=$(find "$ROOTFS" -name "*.so*" -type f 2>/dev/null | wc -l)
echo "Total shared libraries: $LIB_COUNT"

# Check for common libraries
echo ""
echo "Critical libraries check:"
for lib in \
    "libc.so" \
    "ld-linux-aarch64.so" \
    "libpthread.so" \
    "libdl.so" \
    "libm.so" \
    "libX11.so" \
    "libGL.so" \
    "libgtk-3.so" \
    "libglib-2.0.so" \
    "libdbus-1.so" \
    "libasound.so"
do
    found=$(find "$ROOTFS" -name "${lib}*" -type f 2>/dev/null | head -1)
    if [[ -n "$found" ]]; then
        echo "  [OK] $lib -> $found"
    else
        echo "  [MISSING] $lib"
    fi
done

# 6. Create ldconfig cache
echo ""
echo "=== Creating Library Cache ==="

# Create ld.so.conf
cat > "$ROOTFS/etc/ld.so.conf" << 'EOF'
/lib
/lib/aarch64-linux-gnu
/usr/lib
/usr/lib/aarch64-linux-gnu
/usr/local/lib
EOF

# Run ldconfig if available (requires ARM64 or qemu)
if command -v qemu-aarch64-static &> /dev/null; then
    echo "Running ldconfig with qemu..."
    # Copy qemu for chroot
    mkdir -p "$ROOTFS/usr/bin"
    cp /usr/bin/qemu-aarch64-static "$ROOTFS/usr/bin/" 2>/dev/null || true

    # Try to run ldconfig
    chroot "$ROOTFS" /sbin/ldconfig 2>/dev/null || echo "  Note: ldconfig will run on target system"
else
    echo "Note: ldconfig will be run on target ARM64 system"
fi

echo ""
echo "=== Extraction Complete ==="
echo "Rootfs created at: $ROOTFS"
echo ""
echo "Rootfs size:"
du -sh "$ROOTFS"
echo ""
echo "Next steps:"
echo "1. Run build-core-module.sh to create squashfs"
echo "2. Or manually verify rootfs contents first"
