#!/bin/bash
#
# setup-directories.sh - Initialize directory structure for ARM64 build
#

BASEDIR="/home/culler/saas_dev/pk-port/arm64"

echo "=== Setting up ARM64 Build Directory Structure ==="
echo ""

# Create all necessary directories
mkdir -p "$BASEDIR/packages/debs"
mkdir -p "$BASEDIR/packages/extracted"
mkdir -p "$BASEDIR/rootfs"
mkdir -p "$BASEDIR/build-source"
mkdir -p "$BASEDIR/output"
mkdir -p "$BASEDIR/config"
mkdir -p "$BASEDIR/logs"

echo "Created directories:"
echo "  $BASEDIR/packages/debs      - Downloaded .deb packages"
echo "  $BASEDIR/packages/extracted - Extracted package contents"
echo "  $BASEDIR/rootfs             - Assembled root filesystem"
echo "  $BASEDIR/build-source       - Source code for compilation"
echo "  $BASEDIR/output             - Final .xzm modules"
echo "  $BASEDIR/config             - Configuration files"
echo "  $BASEDIR/logs               - Build logs"
echo ""

# Make scripts executable
chmod +x "$BASEDIR/scripts"/*.sh 2>/dev/null || true

echo "Scripts made executable."
echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Run: ./download-packages.sh 2    (direct download method)"
echo "2. Run: ./extract-packages.sh"
echo "3. Run: ./build-core-module.sh"
