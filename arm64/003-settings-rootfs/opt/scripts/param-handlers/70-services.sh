#!/bin/bash
# =============================================================================
# Parameter Handler: 70-services.sh
# =============================================================================
# Handles: additional_components, root_password, ssh_port, ssh_localhost_only,
#          vnc_password, vnc_port, vnc_interactive, vnc_query_user,
#          vnc_localhost_only, printer_model, printer_connection, paper_size,
#          silent_printing, share_printer, printer_name
#
# To add a new parameter:
#   1. Add parameter check below
#   2. Test: echo "param=value" >> /opt/scripts/files/lcon && /opt/scripts/apply-config
# =============================================================================

# Source config if not already sourced
[ -z "$CONFIG" ] && CONFIG="/opt/scripts/files/lcon"
[ -f "$CONFIG" ] && source "$CONFIG"

log() { echo "[$(basename "$0")] $*" >> "${LOG_FILE:-/tmp/apply-config.log}"; }

# Ensure DISPLAY is set for VNC
export DISPLAY="${DISPLAY:-:0}"

# ----- Parameter: additional_components -----
# Description: Optional modules to enable (SSH, VNC, printing)
# Values: Comma-separated list (ssh, vnc, printing)
if [ -n "$additional_components" ]; then
    log "Additional components: $additional_components"
fi

# ----- Parameter: root_password -----
# Description: Root/admin password
# Values: Password string
if [ -n "$root_password" ]; then
    log "Setting root password"
    echo "root:$root_password" | chpasswd 2>/dev/null && \
        log "Root password updated"
fi

# ============================================================================
# SSH Configuration
# ============================================================================

# Check if SSH should be enabled (via additional_components or direct flag)
ssh_enabled=""
if echo "$additional_components" | grep -qi "ssh"; then
    ssh_enabled="yes"
fi

if [ "$ssh_enabled" = "yes" ]; then
    log "SSH service enabled"

    # ----- Parameter: ssh_port -----
    # Description: SSH listening port
    # Values: Port number (default 22)
    port="${ssh_port:-22}"

    # ----- Parameter: ssh_localhost_only -----
    # Description: Restrict SSH to localhost
    # Values: yes, no
    listen_addr="0.0.0.0"
    if [ "$ssh_localhost_only" = "yes" ]; then
        listen_addr="127.0.0.1"
        log "SSH restricted to localhost"
    fi

    # Configure sshd
    if [ -f /etc/ssh/sshd_config ]; then
        # Update port
        sed -i "s/^#*Port .*/Port $port/" /etc/ssh/sshd_config 2>/dev/null
        sed -i "s/^#*ListenAddress .*/ListenAddress $listen_addr/" /etc/ssh/sshd_config 2>/dev/null
    fi

    # Start SSH daemon if not running
    if ! pidof sshd >/dev/null 2>&1; then
        if [ -x /usr/sbin/sshd ]; then
            # Generate host keys if missing
            if [ ! -f /etc/ssh/ssh_host_rsa_key ]; then
                ssh-keygen -A 2>/dev/null
            fi
            /usr/sbin/sshd
            log "SSH daemon started on port $port"
        else
            log "WARNING: sshd not found"
        fi
    else
        log "SSH daemon already running"
    fi
fi

# ============================================================================
# VNC Configuration
# ============================================================================

# Check if VNC should be enabled
vnc_enabled=""
if echo "$additional_components" | grep -qi "vnc"; then
    vnc_enabled="yes"
fi

if [ "$vnc_enabled" = "yes" ]; then
    log "VNC service enabled"

    # ----- Parameter: vnc_port -----
    # Description: VNC listening port
    # Values: Port number (default 5900)
    port="${vnc_port:-5900}"

    # ----- Parameter: vnc_localhost_only -----
    # Description: Restrict VNC to localhost
    # Values: yes, no
    localhost_flag=""
    if [ "$vnc_localhost_only" = "yes" ]; then
        localhost_flag="-localhost"
        log "VNC restricted to localhost"
    fi

    # ----- Parameter: vnc_password -----
    # Description: VNC access password
    # Values: Password string
    passwd_flag=""
    if [ -n "$vnc_password" ]; then
        # Create password file
        mkdir -p /root/.vnc
        echo "$vnc_password" | vncpasswd -f > /root/.vnc/passwd 2>/dev/null
        chmod 600 /root/.vnc/passwd
        passwd_flag="-rfbauth /root/.vnc/passwd"
    else
        passwd_flag="-nopw"
    fi

    # ----- Parameter: vnc_interactive -----
    # Description: Allow remote control (not just view)
    # Values: yes, no
    viewonly_flag=""
    if [ "$vnc_interactive" != "yes" ]; then
        viewonly_flag="-viewonly"
    fi

    # ----- Parameter: vnc_query_user -----
    # Description: Prompt user before accepting connection
    # Values: yes, no
    accept_flag="-forever"
    if [ "$vnc_query_user" = "yes" ]; then
        accept_flag="-accept popup"
    fi

    # Start x11vnc if not running
    if ! pidof x11vnc >/dev/null 2>&1; then
        if command -v x11vnc >/dev/null 2>&1; then
            x11vnc -display :0 -rfbport "$port" $localhost_flag $passwd_flag $viewonly_flag $accept_flag -shared -bg 2>/dev/null
            log "VNC server started on port $port"
        else
            log "WARNING: x11vnc not found"
        fi
    else
        log "VNC server already running"
    fi
fi

# ============================================================================
# Printing Configuration
# ============================================================================

# Check if printing should be enabled
printing_enabled=""
if echo "$additional_components" | grep -qi "print"; then
    printing_enabled="yes"
fi

if [ "$printing_enabled" = "yes" ]; then
    log "Printing service enabled"

    # ----- Parameter: printer_name -----
    # Description: Printer name/identifier
    # Values: Name string
    name="${printer_name:-KioskPrinter}"

    # ----- Parameter: printer_model -----
    # Description: Printer driver/model
    # Values: Driver identifier (e.g., "HP LaserJet")
    if [ -n "$printer_model" ]; then
        log "Printer model: $printer_model"
    fi

    # ----- Parameter: printer_connection -----
    # Description: Printer connection type/URI
    # Values: usb://..., socket://..., lpd://...
    if [ -n "$printer_connection" ]; then
        log "Printer connection: $printer_connection"

        # Add printer via CUPS if available
        if command -v lpadmin >/dev/null 2>&1; then
            lpadmin -p "$name" -v "$printer_connection" -E 2>/dev/null && \
                log "Printer added: $name"
        fi
    fi

    # ----- Parameter: paper_size -----
    # Description: Default paper size
    # Values: Letter, A4, Legal, etc.
    if [ -n "$paper_size" ]; then
        log "Paper size: $paper_size"
    fi

    # ----- Parameter: silent_printing -----
    # Description: Disable print dialog
    # Values: yes, no
    if [ "$silent_printing" = "yes" ]; then
        log "Silent printing enabled"
    fi

    # ----- Parameter: share_printer -----
    # Description: Share printer on network
    # Values: yes, no
    if [ "$share_printer" = "yes" ]; then
        log "Printer sharing enabled"
        # Enable CUPS sharing
        if command -v cupsctl >/dev/null 2>&1; then
            cupsctl --share-printers 2>/dev/null
        fi
    fi
fi

log "Services handler completed"
