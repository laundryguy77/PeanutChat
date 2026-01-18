#!/bin/bash
#
# download-packages.sh - Download ARM64 packages for 001-core.xzm
#
# This script downloads Debian ARM64 packages needed for the core module.
# Run from any machine with internet access.
#

set -e

BASEDIR="/home/culler/saas_dev/pk-port/arm64"
PKGDIR="$BASEDIR/packages/debs"
LISTDIR="$BASEDIR/packages"

# Create directories
mkdir -p "$PKGDIR"
mkdir -p "$LISTDIR"

# Debian ARM64 mirror
MIRROR="http://deb.debian.org/debian"
SUITE="bookworm"
ARCH="arm64"

echo "=== ARM64 Package Downloader for 001-core.xzm ==="
echo "Target directory: $PKGDIR"
echo ""

# Create package list file
cat > "$LISTDIR/packages-core.txt" << 'PKGLIST'
# Core System (CRITICAL)
libc6
libc-bin
libc-dev-bin
locales
busybox
kmod
udev
systemd-sysv
util-linux
libblkid1
libfdisk1
libmount1
libsmartcols1
libuuid1
dhcpcd5
iproute2
procps
libprocps8
coreutils
bash
dash
sed
grep
gawk
findutils
diffutils
tar

# Display System - X Server (CRITICAL)
xserver-xorg-core
xserver-xorg-input-evdev
xserver-xorg-input-libinput
xserver-xorg-video-fbdev
libxfont2
libpixman-1-0
libpciaccess0

# Mesa and DRI (CRITICAL)
libgl1-mesa-dri
libgl1-mesa-glx
libegl1-mesa
libegl-mesa0
libgbm1
libglapi-mesa
libglx-mesa0
libdrm2
libdrm-amdgpu1
libdrm-nouveau2
libdrm-radeon1
libdrm-common
mesa-va-drivers
libva2
libva-drm2
libva-x11-2
libvdpau1

# X11 Libraries (CRITICAL)
libx11-6
libx11-data
libx11-xcb1
libxext6
libxrender1
libxrandr2
libxinerama1
libxcursor1
libxcomposite1
libxdamage1
libxfixes3
libxi6
libxkbfile1
libxkbcommon0
libxkbcommon-x11-0
libxcb1
libxcb-render0
libxcb-shm0
libxcb-randr0
libxcb-xfixes0
libxcb-shape0
libxcb-sync1
libxcb-present0
libxcb-dri2-0
libxcb-dri3-0
libxcb-glx0
libxcb-xkb1
libxshmfence1
libxxf86vm1
libxmu6
libxpm4
libxt6
libxaw7
libxss1
libxtst6
libsm6
libice6

# X11 Utilities
x11-xserver-utils
x11-utils
x11-xkb-utils
xauth
xinit
xterm
xfonts-base
xfonts-encodings
xfonts-utils

# Window Manager - Openbox (CRITICAL)
openbox
libobrender32v5
libobt2v5
libimlib2

# GTK and GUI Libraries (CRITICAL)
libgtk2.0-0
libgtk2.0-common
libgtk-3-0
libgtk-3-common
libglib2.0-0
libglib2.0-data
libgdk-pixbuf-2.0-0
libgdk-pixbuf2.0-common
gdk-pixbuf-loaders
shared-mime-info
libcairo2
libcairo-gobject2
libpango-1.0-0
libpangocairo-1.0-0
libpangoft2-1.0-0
libatk1.0-0
libatk-bridge2.0-0
libatspi2.0-0
at-spi2-core

# Fonts (HIGH)
libfontconfig1
fontconfig-config
libfreetype6
libharfbuzz0b
fonts-dejavu-core
fonts-liberation
fontconfig

# Networking (HIGH)
curl
libcurl4
wget
libbpf1
libelf1
openssl
libssl3
ca-certificates
libnss3
libnss3-tools
libnspr4
iptables
libip4tc2
libip6tc2
libxtables12
rsync
ethtool
stunnel4
sshpass
openssh-client
libssh2-1
libgnutls30
libgssapi-krb5-2
libkrb5-3
libk5crypto3
libkrb5support0

# Audio (HIGH)
libasound2
libasound2-data
alsa-utils
libasound2-plugins
libpulse0
libpulse-mainloop-glib0

# D-Bus (CRITICAL)
dbus
dbus-daemon
libdbus-1-3
libdbus-glib-1-2
dbus-x11

# Desktop Utilities (MEDIUM)
tint2
dunst
libnotify4
notification-daemon
xcompmgr
conky-std
feh
libexif12
yad
mc
rsyslog
cron
acpid
ntpdate
logrotate

# Compression (HIGH)
squashfs-tools
xz-utils
liblzma5
gzip
bzip2
libbz2-1.0
unzip
cpio
zlib1g

# System Libraries (CRITICAL)
libexpat1
libffi8
libpcre2-8-0
libselinux1
libsepol2
libtinfo6
libncurses6
libncursesw6
libreadline8
liblz4-1
libzstd1
libudev1
libcap2
libcap2-bin
libseccomp2
libgcrypt20
libgpg-error0
libidn2-0
libunistring2
libpsl5
libnettle8
libhogweed6
libgmp10
libp11-kit0
libtasn1-6

# Additional Libraries
libjpeg62-turbo
libpng16-16
libtiff6
libwebp7
libxml2
liblcms2-2
libstartup-notification0
librsvg2-2
librsvg2-common
libutempter0
PKGLIST

echo "Package list created: $LISTDIR/packages-core.txt"
echo ""

# Function to download a package and its dependencies
download_package() {
    local pkg="$1"
    echo "  Downloading: $pkg"

    # Use apt-get download in a chroot or with apt configuration
    # For now, use direct URL construction from Packages file

    # This is a simplified approach - production would use apt properly
    apt-get download -o APT::Architecture=$ARCH \
        -o Dir::Etc::sourcelist=/dev/null \
        -o Dir::Etc::sourceparts=/dev/null \
        "$pkg:$ARCH" 2>/dev/null || true
}

# Create apt sources for ARM64
create_apt_config() {
    local aptdir="$BASEDIR/apt-arm64"
    mkdir -p "$aptdir/etc/apt/sources.list.d"
    mkdir -p "$aptdir/var/lib/apt/lists"
    mkdir -p "$aptdir/var/cache/apt/archives"

    cat > "$aptdir/etc/apt/sources.list" << EOF
deb [arch=arm64] http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware
deb [arch=arm64] http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware
deb [arch=arm64] http://deb.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
EOF

    echo "$aptdir"
}

# Method 1: Using apt with foreign architecture (if dpkg --add-architecture works)
download_with_apt() {
    echo "=== Method 1: Download using apt (requires root) ==="

    # Check if we can add arm64 architecture
    if command -v dpkg &> /dev/null; then
        echo "Adding arm64 architecture..."
        sudo dpkg --add-architecture arm64 || true
        sudo apt-get update || true

        cd "$PKGDIR"

        # Read packages and download
        while IFS= read -r pkg; do
            # Skip comments and empty lines
            [[ "$pkg" =~ ^#.*$ ]] && continue
            [[ -z "$pkg" ]] && continue

            echo "Downloading: $pkg"
            apt-get download "$pkg:arm64" 2>/dev/null || echo "  Warning: Could not download $pkg"
        done < "$LISTDIR/packages-core.txt"
    else
        echo "dpkg not available, skipping apt method"
    fi
}

# Method 2: Direct download from repository (no root needed)
download_direct() {
    echo "=== Method 2: Direct download from repository ==="

    local PACKAGES_URL="$MIRROR/dists/$SUITE/main/binary-$ARCH/Packages.xz"
    local PACKAGES_FILE="$LISTDIR/Packages"

    echo "Downloading package index..."
    wget -q -O "$PACKAGES_FILE.xz" "$PACKAGES_URL"
    xz -d -f "$PACKAGES_FILE.xz"

    echo "Package index downloaded: $PACKAGES_FILE"

    cd "$PKGDIR"

    # Read packages and find URLs
    while IFS= read -r pkg; do
        # Skip comments and empty lines
        [[ "$pkg" =~ ^#.*$ ]] && continue
        [[ -z "$pkg" ]] && continue

        # Find package in Packages file
        local filename=$(awk -v pkg="$pkg" '
            /^Package: / { current_pkg = $2 }
            /^Filename: / && current_pkg == pkg { print $2; exit }
        ' "$PACKAGES_FILE")

        if [[ -n "$filename" ]]; then
            local url="$MIRROR/$filename"
            local basename=$(basename "$filename")

            if [[ ! -f "$basename" ]]; then
                echo "Downloading: $pkg -> $basename"
                wget -q -c "$url" || echo "  Warning: Failed to download $pkg"
            else
                echo "Already have: $pkg"
            fi
        else
            echo "Warning: Package not found in index: $pkg"
        fi
    done < "$LISTDIR/packages-core.txt"
}

# Method 3: Using debootstrap (creates complete system)
download_with_debootstrap() {
    echo "=== Method 3: Using debootstrap (requires root) ==="

    local ROOTFS="$BASEDIR/rootfs-debootstrap"

    # Check for qemu-user-static
    if [[ ! -f /usr/bin/qemu-aarch64-static ]]; then
        echo "Installing qemu-user-static for ARM64 emulation..."
        sudo apt-get install -y qemu-user-static binfmt-support
    fi

    # Read include packages (first 20 critical ones)
    local INCLUDE_PKGS=$(grep -v '^#' "$LISTDIR/packages-core.txt" | grep -v '^$' | head -50 | tr '\n' ',')
    INCLUDE_PKGS=${INCLUDE_PKGS%,}  # Remove trailing comma

    echo "Creating ARM64 rootfs with debootstrap..."
    echo "Include packages: $INCLUDE_PKGS"

    sudo debootstrap --arch=arm64 --variant=minbase \
        --include="$INCLUDE_PKGS" \
        bookworm "$ROOTFS" \
        http://deb.debian.org/debian

    echo "Debootstrap complete: $ROOTFS"
}

# Main execution
echo "Select download method:"
echo "1) Using apt (requires root, adds arm64 architecture)"
echo "2) Direct download from repository (no root)"
echo "3) Using debootstrap (requires root, creates full rootfs)"
echo ""

# Default to method 2 (direct download) if no argument
METHOD="${1:-2}"

case "$METHOD" in
    1)
        download_with_apt
        ;;
    2)
        download_direct
        ;;
    3)
        download_with_debootstrap
        ;;
    *)
        echo "Invalid method. Use 1, 2, or 3"
        exit 1
        ;;
esac

echo ""
echo "=== Download Complete ==="
echo "Packages downloaded to: $PKGDIR"
echo ""
echo "Next step: Run extract-packages.sh to extract the packages"
