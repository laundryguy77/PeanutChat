#!/bin/bash
# ---------------------------------------------------------
# Create dd-able disk image for Porteus Kiosk ARM64 (RPi 4)
# Usage: sudo ./make_img.sh
# Output: ../kiosk-arm64.img (dd to SD card)
# ---------------------------------------------------------

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMG_FILE="${SCRIPT_DIR}/../kiosk-arm64.img"

# Cleanup variables (set after loop device created)
LOOP_DEV=""
MOUNT_BOOT=""
MOUNT_DATA=""

cleanup() {
    echo ""
    echo "Cleaning up..."
    # Unmount any mounted filesystems
    [ -n "$MOUNT_BOOT" ] && mountpoint -q "$MOUNT_BOOT" 2>/dev/null && umount "$MOUNT_BOOT"
    [ -n "$MOUNT_DATA" ] && mountpoint -q "$MOUNT_DATA" 2>/dev/null && umount "$MOUNT_DATA"
    # Remove mount points
    [ -n "$MOUNT_BOOT" ] && [ -d "$MOUNT_BOOT" ] && rmdir "$MOUNT_BOOT" 2>/dev/null
    [ -n "$MOUNT_DATA" ] && [ -d "$MOUNT_DATA" ] && rmdir "$MOUNT_DATA" 2>/dev/null
    # Detach loop device
    [ -n "$LOOP_DEV" ] && [ -e "$LOOP_DEV" ] && losetup -d "$LOOP_DEV" 2>/dev/null
    echo "Cleanup complete."
}

trap cleanup EXIT

# Calculate sizes
BOOT_SIZE_MB=64
XZM_SIZE_MB=$(du -sm "${SCRIPT_DIR}/xzm" | cut -f1)
DOCS_SIZE_MB=$(du -sm "${SCRIPT_DIR}/docs" | cut -f1)
DATA_SIZE_MB=$((XZM_SIZE_MB + DOCS_SIZE_MB + 32))  # +32MB buffer for ext4 overhead
STORAGE_SIZE_MB=64
TOTAL_SIZE_MB=$((BOOT_SIZE_MB + DATA_SIZE_MB + STORAGE_SIZE_MB + 4))  # +4MB for partition table

echo "=== Porteus Kiosk ARM64 - Disk Image Creator ==="
echo "Boot partition:    ${BOOT_SIZE_MB}MB"
echo "Data partition:    ${DATA_SIZE_MB}MB (xzm + docs)"
echo "Storage partition: ${STORAGE_SIZE_MB}MB"
echo "Total image size:  ${TOTAL_SIZE_MB}MB"
echo ""

# Check for root
if [ "$EUID" -ne 0 ]; then
    echo "This script requires root to create partitions and mount filesystems."
    echo "Run with: sudo ./make_img.sh"
    exit 1
fi

# Clean up any previous image
rm -f "$IMG_FILE"

# Create empty image file
echo "[1/7] Creating ${TOTAL_SIZE_MB}MB image file..."
dd if=/dev/zero of="$IMG_FILE" bs=1M count=$TOTAL_SIZE_MB status=progress

# Create partition table
echo ""
echo "[2/7] Creating partition table..."
sfdisk "$IMG_FILE" << PART
label: dos
unit: sectors

# Partition 1: FAT32 boot (type 0c = FAT32 LBA)
1 : size=${BOOT_SIZE_MB}M, type=c, bootable

# Partition 2: Linux data for xzm/docs (type 83 = Linux)
2 : size=${DATA_SIZE_MB}M, type=83

# Partition 4: Storage/persistence (type 83 = Linux)
4 : size=${STORAGE_SIZE_MB}M, type=83
PART

# Setup loop device with partition scanning
echo ""
echo "[3/7] Setting up loop device..."
LOOP_DEV=$(losetup -f --show -P "$IMG_FILE")
echo "Loop device: $LOOP_DEV"

# Wait for partition devices to appear (with timeout)
echo "Waiting for partition devices..."
for i in $(seq 1 10); do
    if [ -e "${LOOP_DEV}p1" ] && [ -e "${LOOP_DEV}p2" ] && [ -e "${LOOP_DEV}p4" ]; then
        echo "Partition devices ready."
        break
    fi
    if [ $i -eq 10 ]; then
        echo "ERROR: Partition devices did not appear after 10 seconds"
        exit 1
    fi
    sleep 1
done

# Format partitions
echo ""
echo "[4/7] Formatting partitions..."
mkfs.vfat -F 32 -n "BOOT" "${LOOP_DEV}p1"
mkfs.ext4 -L "Kiosk" -m 0 "${LOOP_DEV}p2"  # -m 0 = no reserved blocks (not needed for read-only data)
mkfs.ext4 -L "StorageBkp" "${LOOP_DEV}p4"

# Create mount points
MOUNT_BOOT="/tmp/kiosk-boot-$$"
MOUNT_DATA="/tmp/kiosk-data-$$"
mkdir -p "$MOUNT_BOOT" "$MOUNT_DATA"

# Mount and copy boot files
echo ""
echo "[5/7] Copying boot files to partition 1..."
mount "${LOOP_DEV}p1" "$MOUNT_BOOT"
cp -v "${SCRIPT_DIR}"/boot/kernel8.img "$MOUNT_BOOT/"
cp -v "${SCRIPT_DIR}"/boot/initrd.img "$MOUNT_BOOT/"
cp -v "${SCRIPT_DIR}"/boot/*.dtb "$MOUNT_BOOT/"
cp -v "${SCRIPT_DIR}"/boot/start4*.elf "$MOUNT_BOOT/"
cp -v "${SCRIPT_DIR}"/boot/fixup4*.dat "$MOUNT_BOOT/"
cp -v "${SCRIPT_DIR}"/boot/config.txt "$MOUNT_BOOT/"
cp -v "${SCRIPT_DIR}"/boot/cmdline.txt "$MOUNT_BOOT/"
cp -r "${SCRIPT_DIR}"/boot/overlays "$MOUNT_BOOT/"
sync
umount "$MOUNT_BOOT"

# Mount and copy data files (xzm, docs)
echo ""
echo "[6/7] Copying xzm and docs to partition 2..."
mount "${LOOP_DEV}p2" "$MOUNT_DATA"
cp -r "${SCRIPT_DIR}"/xzm "$MOUNT_DATA/"
cp -r "${SCRIPT_DIR}"/docs "$MOUNT_DATA/"
sync
umount "$MOUNT_DATA"

# Disable cleanup trap message on success (cleanup still runs)
trap - EXIT

# Cleanup manually for clean output
echo ""
echo "[7/7] Cleaning up..."
rmdir "$MOUNT_BOOT" "$MOUNT_DATA" 2>/dev/null || true
losetup -d "$LOOP_DEV" 2>/dev/null || true
sync  # Flush loop device writes to image file
LOOP_DEV=""  # Prevent trap from double-cleanup

# Show result
echo ""
echo "=== Image Created Successfully ==="
ls -lh "$IMG_FILE"
echo ""
echo "Partition layout:"
fdisk -l "$IMG_FILE"
echo ""
echo "To write to SD card:"
echo "  sudo dd if=$IMG_FILE of=/dev/sdX bs=4M status=progress conv=fsync"
echo "  sync"
