#!/bin/sh
#
# This file is executed by init(8) when the system is being
# initialized for one of the "multi user" run levels (i.e.
# levels 1 through 6).
# Author: T.Jokiel <http://porteus-kiosk.org>
# ARM64 Port

# Set hostname:
hostname kiosk

# Set default time zone:
#tz=
if [ "$tz" ]; then
    ln -sf /usr/share/zoneinfo/$tz /etc/localtime-copied-from
    cp -L /etc/localtime-copied-from /etc/localtime
    hwclock --utc -s
fi

# Start cron and logging daemon:
/usr/sbin/crond &
/usr/sbin/rsyslogd &

# Initialize networking:
sh /etc/rc.d/rc.inet1 &

# Start messagebus:
/usr/bin/dbus-uuidgen --ensure=/etc/machine-id
/usr/bin/dbus-daemon --system &

# Initialize loopback interface:
ifconfig lo 127.0.0.1 2>/dev/null
route add -net 127.0.0.0 netmask 255.0.0.0 lo 2>/dev/null

# Enable firewall:
/etc/rc.d/rc.FireWall

# Enable ACPI events (e.g. possibility of shutting down the kiosk by pressing a PC's power button):
/usr/sbin/acpid -n &

# Initialize swap partitions:
#for swpprt in `blkid | grep ' TYPE="swap"' | cut -d: -f1`; do swapon $swpprt; done

# Initialize swapfile:
#swapsize=1024
if [ "$swapsize" ]; then
    sh /opt/scripts/persistence
    # Make sure that persistent partition is mounted so we wont fill the RAM:
    if grep -q -w '/opt/storage xfs' /proc/mounts; then
	# Create swapfile if it does not exist or its size is different than configured:
	if [ -e /opt/storage/swapfile ]; then
	    sfsize="$((`du /opt/storage/swapfile | cut -d/ -f1`/1024))"
	    [ $sfsize = $swapsize ] || { dd < /dev/zero > /opt/storage/swapfile bs=1M count=$swapsize 2>/dev/null; mkswap /opt/storage/swapfile >/dev/null; }
	else
	    dd < /dev/zero > /opt/storage/swapfile bs=1M count=$swapsize 2>/dev/null; mkswap /opt/storage/swapfile >/dev/null
	fi
	# Recreate swap file if needed:
	swapon /opt/storage/swapfile || { dd < /dev/zero > /opt/storage/swapfile bs=1M count=$swapsize 2>/dev/null; mkswap /opt/storage/swapfile >/dev/null; swapon /opt/storage/swapfile; }
    fi
fi

# Initialize zRAM:
#zsize=33%
if [ "$zsize" ]; then
    modprobe zram; mem=$((`grep MemTotal /proc/meminfo | cut -d" " -f2- | sed s/kB//`/100)); size=`echo $zsize | sed 's/%//g'`
    echo $(($mem*1024*$size)) > /sys/block/zram0/disksize
    mkswap /dev/zram0 >/dev/null
    swapon -p 100 /dev/zram0
fi

# Unlink as it breaks our gtkdialog apps:
rm -f /etc/fonts/conf.d/10-hinting-slight.conf
