#!/bin/sh
# Simplified xinitrc for Porteus Kiosk ARM64
# Openbox is confirmed working - minimal diagnostics now

# Mark that we started
touch /mnt/logs/xinitrc_started 2>/dev/null || touch /tmp/xinitrc_started

# Log to persistent storage
exec >> /mnt/logs/xinitrc.log 2>&1
set -x

echo "=== xinitrc starting at $(date) ==="
echo "DISPLAY=$DISPLAY"

# Set library path
export LD_LIBRARY_PATH=/usr/lib/aarch64-linux-gnu:/lib/aarch64-linux-gnu:/usr/lib:/lib

# Run ldconfig
ldconfig

# Start D-Bus session
eval $(dbus-launch --sh-syntax)
export DBUS_SESSION_BUS_ADDRESS
echo "DBUS_SESSION_BUS_ADDRESS=$DBUS_SESSION_BUS_ADDRESS"

# Set background
xsetroot -solid "#404040"

# Start openbox in background
echo "=== Starting openbox ==="
/usr/bin/openbox &
OPENBOX_PID=$!
echo "openbox PID: $OPENBOX_PID"

sleep 2

# Verify openbox is running
if kill -0 $OPENBOX_PID 2>/dev/null; then
    echo "openbox is RUNNING"
else
    echo "ERROR: openbox died!"
    exit 1
fi

# Run autostart (this is where the magic happens)
echo "=== Calling autostart ==="
/etc/xdg/openbox/autostart

# Wait for openbox
wait $OPENBOX_PID
