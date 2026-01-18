#!/bin/bash
# ---------------------------------------------------------
# Script to create Porteus Kiosk ARM64 ISO.
# Adapted for Raspberry Pi 4 (no isolinux boot required).
# ---------------------------------------------------------

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_ISO="${SCRIPT_DIR}/../kiosk-arm64.iso"

echo "Creating Porteus Kiosk ARM64 ISO from files in: ${SCRIPT_DIR}"
echo "Output: ${OUTPUT_ISO}"
echo ""

# Check for xorriso
if ! command -v xorriso &> /dev/null; then
    echo "Error: xorriso is required but not installed."
    echo "Install with: sudo apt install xorriso"
    exit 1
fi

# Create data ISO (no bootable flags - RPi uses different boot mechanism)
# Volume label "Kiosk" is required by the init script for mounting
# Use graft-points to include only xzm/ and docs/ (not boot/, make_*.sh, etc.)
xorriso -as mkisofs \
    -o "${OUTPUT_ISO}" \
    -V "Kiosk" \
    -A "Porteus Kiosk ARM64" \
    -l -J -joliet-long -R -D \
    -graft-points \
    "xzm=${SCRIPT_DIR}/xzm" \
    "docs=${SCRIPT_DIR}/docs"

if [ $? -eq 0 ]; then
    echo ""
    echo "ISO created successfully: ${OUTPUT_ISO}"
    echo "Size: $(du -h "${OUTPUT_ISO}" | cut -f1)"
    echo ""
    echo "Note: This is a data ISO for Raspberry Pi 4."
    echo "To use:"
    echo "  1. Format SD card with FAT32 partition"
    echo "  2. Copy boot/ contents to SD card root"
    echo "  3. Copy xzm/ and docs/ to SD card"
    echo "  4. Or mount the ISO on a network share"
else
    echo "Error: Failed to create ISO."
    exit 1
fi
