#!/bin/bash
#
# build-custom-packages.sh - Build packages not available in repositories
#
# These packages need to be compiled from source for ARM64:
# - gtkdialog (GTK dialog builder)
# - hsetroot (wallpaper setter)
# - fbv (framebuffer viewer)
#

set -e

BASEDIR="/home/culler/saas_dev/pk-port/arm64"
SRCDIR="$BASEDIR/build-source"
DESTDIR="$BASEDIR/custom-packages"
ROOTFS="$BASEDIR/rootfs"
LOGDIR="$BASEDIR/logs"

# Cross-compile settings (for building on x86_64 host)
CROSS_COMPILE="${CROSS_COMPILE:-aarch64-linux-gnu-}"
CC="${CROSS_COMPILE}gcc"
CXX="${CROSS_COMPILE}g++"
AR="${CROSS_COMPILE}ar"
STRIP="${CROSS_COMPILE}strip"

# Check if cross-compiler is available
check_cross_compiler() {
    if ! command -v ${CC} &> /dev/null; then
        echo "Cross-compiler not found: ${CC}"
        echo ""
        echo "Install with:"
        echo "  sudo apt-get install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu"
        echo ""
        echo "Or set CROSS_COMPILE= to build natively on ARM64"
        exit 1
    fi
    echo "Using cross-compiler: $CC"
}

# Create directories
mkdir -p "$SRCDIR"
mkdir -p "$DESTDIR"
mkdir -p "$LOGDIR"

echo "=== ARM64 Custom Package Builder ==="
echo "Source directory: $SRCDIR"
echo "Output directory: $DESTDIR"
echo ""

# Build gtkdialog
build_gtkdialog() {
    echo "=== Building gtkdialog ==="

    cd "$SRCDIR"

    # Clone if not present
    if [[ ! -d "gtkdialog" ]]; then
        echo "Cloning gtkdialog..."
        git clone https://github.com/01micko/gtkdialog.git
    fi

    cd gtkdialog

    # Clean previous build
    make distclean 2>/dev/null || true

    # Configure for ARM64
    echo "Configuring gtkdialog..."
    ./autogen.sh 2>&1 | tee "$LOGDIR/gtkdialog-autogen.log"

    # For cross-compilation, need to set up pkg-config for target
    export PKG_CONFIG_PATH="$ROOTFS/usr/lib/aarch64-linux-gnu/pkgconfig:$ROOTFS/usr/share/pkgconfig"
    export PKG_CONFIG_SYSROOT_DIR="$ROOTFS"

    ./configure \
        --prefix=/usr \
        --sysconfdir=/etc \
        --host=aarch64-linux-gnu \
        --build=$(uname -m)-linux-gnu \
        CC="$CC" \
        CXX="$CXX" \
        2>&1 | tee "$LOGDIR/gtkdialog-configure.log"

    # Build
    echo "Building gtkdialog..."
    make -j$(nproc) 2>&1 | tee "$LOGDIR/gtkdialog-build.log"

    # Install to destination
    echo "Installing gtkdialog..."
    make DESTDIR="$DESTDIR/gtkdialog" install

    # Copy to rootfs
    cp -a "$DESTDIR/gtkdialog"/* "$ROOTFS"/ 2>/dev/null || true

    echo "gtkdialog built successfully"
}

# Build hsetroot
build_hsetroot() {
    echo "=== Building hsetroot ==="

    cd "$SRCDIR"

    # Clone if not present
    if [[ ! -d "hsetroot" ]]; then
        echo "Cloning hsetroot..."
        git clone https://github.com/himdel/hsetroot.git
    fi

    cd hsetroot

    # Clean previous build
    make clean 2>/dev/null || true

    # Build for ARM64
    echo "Building hsetroot..."
    make CC="$CC" 2>&1 | tee "$LOGDIR/hsetroot-build.log"

    # Install
    mkdir -p "$DESTDIR/hsetroot/usr/bin"
    cp hsetroot "$DESTDIR/hsetroot/usr/bin/"
    $STRIP "$DESTDIR/hsetroot/usr/bin/hsetroot" 2>/dev/null || true

    # Copy to rootfs
    cp -a "$DESTDIR/hsetroot"/* "$ROOTFS"/ 2>/dev/null || true

    echo "hsetroot built successfully"
}

# Build fbv
build_fbv() {
    echo "=== Building fbv ==="

    cd "$SRCDIR"

    # Download if not present
    if [[ ! -d "fbv-1.0b" ]]; then
        echo "Downloading fbv..."
        wget -q http://s-tech.elsat.net.pl/fbv/fbv-1.0b.tar.gz || {
            echo "Warning: Could not download fbv from original source"
            echo "Trying alternative..."
            # fbv is also available in some distro repos
            return 1
        }
        tar xzf fbv-1.0b.tar.gz
    fi

    cd fbv-1.0b

    # Clean previous build
    make clean 2>/dev/null || true

    # Configure
    echo "Configuring fbv..."
    ./configure --prefix=/usr 2>&1 | tee "$LOGDIR/fbv-configure.log"

    # Patch Makefile for cross-compilation
    sed -i "s|^CC=.*|CC=$CC|" Makefile

    # Build
    echo "Building fbv..."
    make 2>&1 | tee "$LOGDIR/fbv-build.log"

    # Install
    mkdir -p "$DESTDIR/fbv/usr/bin"
    cp fbv "$DESTDIR/fbv/usr/bin/"
    $STRIP "$DESTDIR/fbv/usr/bin/fbv" 2>/dev/null || true

    # Copy to rootfs
    cp -a "$DESTDIR/fbv"/* "$ROOTFS"/ 2>/dev/null || true

    echo "fbv built successfully"
}

# Build xvkbd (virtual keyboard)
build_xvkbd() {
    echo "=== Building xvkbd ==="

    cd "$SRCDIR"

    # Download if not present
    XVKBD_VERSION="4.1"
    if [[ ! -d "xvkbd-$XVKBD_VERSION" ]]; then
        echo "Downloading xvkbd..."
        wget -q "http://t-sato.in.coocan.jp/xvkbd/xvkbd-${XVKBD_VERSION}.tar.gz" || {
            echo "Warning: Could not download xvkbd"
            return 1
        }
        tar xzf "xvkbd-${XVKBD_VERSION}.tar.gz"
    fi

    cd "xvkbd-$XVKBD_VERSION"

    # Clean previous build
    make clean 2>/dev/null || true

    # Use xmkmf or manual Makefile
    if command -v xmkmf &> /dev/null; then
        xmkmf
    fi

    # Build
    echo "Building xvkbd..."
    make CC="$CC" CFLAGS="-O2" 2>&1 | tee "$LOGDIR/xvkbd-build.log" || {
        echo "Warning: xvkbd build failed"
        return 1
    }

    # Install
    mkdir -p "$DESTDIR/xvkbd/usr/bin"
    cp xvkbd "$DESTDIR/xvkbd/usr/bin/"
    $STRIP "$DESTDIR/xvkbd/usr/bin/xvkbd" 2>/dev/null || true

    # Copy to rootfs
    cp -a "$DESTDIR/xvkbd"/* "$ROOTFS"/ 2>/dev/null || true

    echo "xvkbd built successfully"
}

# Main menu
show_menu() {
    echo ""
    echo "Select packages to build:"
    echo "1) gtkdialog  - GTK dialog builder (required for kiosk dialogs)"
    echo "2) hsetroot   - Wallpaper setter"
    echo "3) fbv        - Framebuffer image viewer"
    echo "4) xvkbd      - Virtual keyboard"
    echo "5) all        - Build all packages"
    echo "6) exit"
    echo ""
}

# Main execution
check_cross_compiler

if [[ -n "$1" ]]; then
    case "$1" in
        1|gtkdialog) build_gtkdialog ;;
        2|hsetroot) build_hsetroot ;;
        3|fbv) build_fbv ;;
        4|xvkbd) build_xvkbd ;;
        5|all)
            build_gtkdialog
            build_hsetroot
            build_fbv
            build_xvkbd
            ;;
        *) echo "Unknown option: $1" ;;
    esac
else
    show_menu
    read -p "Choice: " choice
    case "$choice" in
        1) build_gtkdialog ;;
        2) build_hsetroot ;;
        3) build_fbv ;;
        4) build_xvkbd ;;
        5)
            build_gtkdialog
            build_hsetroot
            build_fbv
            build_xvkbd
            ;;
        6) exit 0 ;;
        *) echo "Unknown option" ;;
    esac
fi

echo ""
echo "=== Build Complete ==="
echo "Built packages in: $DESTDIR"
ls -la "$DESTDIR"
