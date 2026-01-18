#!/bin/sh
# rc.S - System initialization for Porteus Kiosk ARM64
# NOTE: /dev, /proc, /sys do NOT exist yet when this runs!

echo "=== rc.S: Starting system initialization ==="

# Mount virtual filesystems FIRST (no redirects - /dev doesn't exist yet!)
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev

# Now /dev exists, create subdirs and mount pts/shm
mkdir -p /dev/pts /dev/shm
mount -t devpts devpts /dev/pts
mount -t tmpfs tmpfs /dev/shm -o mode=1777

# Create /tmp as tmpfs
mkdir -p /tmp
mount -t tmpfs tmpfs /tmp -o mode=1777

# Create /run for runtime data
mkdir -p /run
mount -t tmpfs tmpfs /run -o mode=755

# Create runtime directories for services
mkdir -p /run/dbus /run/lock /run/user /run/udev
mkdir -p /var/log /var/tmp
mkdir -p /tmp/.X11-unix
chmod 1777 /tmp/.X11-unix
ln -sf /run /var/run 2>/dev/null

# Now we can use /dev/null safely
exec >/dev/console 2>&1

# Set hostname
hostname kiosk

echo "=== rc.S: Starting udev ==="

# Start udev for device management
# Note: systemd-udevd is a symlink to udevadm, which detects how it was called
if [ -x /lib/systemd/systemd-udevd ]; then
    echo "  Starting systemd-udevd (via udevadm)..."
    /lib/systemd/systemd-udevd --daemon
    sleep 2
elif [ -x /sbin/udevd ]; then
    echo "  Starting udevd..."
    /sbin/udevd --daemon
    sleep 2
else
    echo "  WARNING: No udev daemon found!"
fi

# Trigger device discovery
echo "  Triggering device events..."
udevadm trigger --action=add
udevadm settle --timeout=10
echo "  udev setup complete"

# Verify udev is running (check for udevadm since that's the actual binary name)
if pidof udevadm >/dev/null 2>&1; then
    echo "  udev daemon: RUNNING (PID: $(pidof udevadm))"
else
    echo "  WARNING: udev daemon NOT running!"
    echo "  Checking /dev/input/:"
    ls -la /dev/input/ 2>/dev/null || echo "    /dev/input not available"
fi

echo "=== rc.S: Loading GPU kernel modules ==="

# Load kernel modules for RPi4 GPU with explicit error reporting
echo "  Loading drm..."
modprobe drm && echo "    drm: OK" || echo "    drm: FAILED"
echo "  Loading drm_kms_helper..."
modprobe drm_kms_helper && echo "    drm_kms_helper: OK" || echo "    drm_kms_helper: FAILED"
echo "  Loading vc4..."
modprobe vc4 && echo "    vc4: OK" || echo "    vc4: FAILED"
echo "  Loading v3d..."
modprobe v3d && echo "    v3d: OK" || echo "    v3d: FAILED"

# Re-trigger udev to create device nodes for newly loaded modules
echo "  Re-triggering udev for GPU devices..."
udevadm trigger --subsystem-match=drm --action=add
udevadm settle --timeout=5

# Create DRI device directory (fallback if udev doesn't)
mkdir -p /dev/dri
chmod 755 /dev/dri

# Wait and verify GPU device nodes
sleep 2
echo "  Checking /dev/dri/:"
ls -la /dev/dri/ 2>/dev/null || echo "    /dev/dri is empty or missing!"

# Show loaded modules
echo "  Loaded DRM modules:"
lsmod | grep -E "(drm|vc4|v3d)" || echo "    No DRM modules loaded!"

# Setup networking
echo "Setting up networking..."

# Wait for eth0 to appear (up to 10 seconds)
for i in 1 2 3 4 5 6 7 8 9 10; do
    if [ -e /sys/class/net/eth0 ]; then
        echo "  eth0 found"
        break
    fi
    echo "  Waiting for eth0... ($i)"
    sleep 1
done

# List available interfaces for debug
echo "  Available interfaces:"
ls /sys/class/net/

# Bring up eth0 explicitly
if [ -e /sys/class/net/eth0 ]; then
    ip link set eth0 up
    sleep 1

    # Run DHCP
    echo "  Starting DHCP on eth0..."
    if [ -x /usr/sbin/dhcpcd ]; then
        /usr/sbin/dhcpcd -b eth0 &
    elif [ -x /sbin/udhcpc ]; then
        /sbin/udhcpc -i eth0 -s /usr/share/udhcpc/default.script -b -q &
    else
        echo "  WARNING: No DHCP client found!"
    fi
else
    echo "  ERROR: eth0 not found!"
fi

# Rebuild library cache (important for finding libs)
ldconfig 2>/dev/null

echo "System initialization complete"
