#!/bin/bash
# =============================================================================
# Parameter Handler: 00-network.sh
# =============================================================================
# Handles: connection, dhcp, ip_address, network_interface, default_gateway,
#          netmask, dns_server, wired_authentication, eapol_username,
#          eapol_password, ssid_name, hidden_ssid_name, wifi_encryption,
#          wep_key, wpa_password, peap_username, peap_password,
#          dialup_username, dialup_password, dialup_phone_number
#
# Note: Most network parameters are handled at boot by first-run/wizard.
#       This handler applies runtime changes when config is updated remotely.
#
# To add a new parameter:
#   1. Add parameter check below
#   2. Test: echo "param=value" >> /opt/scripts/files/lcon && /opt/scripts/apply-config
# =============================================================================

# Source config if not already sourced
[ -z "$CONFIG" ] && CONFIG="/opt/scripts/files/lcon"
[ -f "$CONFIG" ] && source "$CONFIG"

log() { echo "[$(basename "$0")] $*" >> "${LOG_FILE:-/tmp/apply-config.log}"; }

# ----- Parameter: connection -----
# Description: Connection type
# Values: wired, wifi, dialup
if [ -n "$connection" ]; then
    log "Connection type: $connection"
fi

# ----- Parameter: network_interface -----
# Description: Network adapter to use
# Values: eth0, wlan0, etc.
if [ -n "$network_interface" ]; then
    log "Network interface: $network_interface"
fi

# ----- Parameter: dhcp -----
# Description: Use DHCP for IP configuration
# Values: yes, no
if [ -n "$dhcp" ]; then
    log "DHCP: $dhcp"
fi

# ----- Parameter: ip_address -----
# Description: Static IP address
# Values: IP address (e.g., 192.168.1.100)
if [ -n "$ip_address" ] && [ "$dhcp" != "yes" ]; then
    log "Static IP configured: $ip_address"

    iface="${network_interface:-eth0}"

    # Apply static IP
    if command -v ip >/dev/null 2>&1; then
        # Build netmask in CIDR format
        cidr="24"  # Default /24
        if [ -n "$netmask" ]; then
            case "$netmask" in
                255.255.255.0)   cidr="24" ;;
                255.255.0.0)     cidr="16" ;;
                255.0.0.0)       cidr="8" ;;
                255.255.255.128) cidr="25" ;;
                255.255.255.192) cidr="26" ;;
                255.255.255.224) cidr="27" ;;
                255.255.255.240) cidr="28" ;;
            esac
        fi

        ip addr flush dev "$iface" 2>/dev/null
        ip addr add "$ip_address/$cidr" dev "$iface" 2>/dev/null
        ip link set "$iface" up 2>/dev/null
        log "Applied static IP: $ip_address/$cidr on $iface"
    fi
fi

# ----- Parameter: default_gateway -----
# Description: Default gateway/router
# Values: IP address
if [ -n "$default_gateway" ] && [ "$dhcp" != "yes" ]; then
    log "Setting default gateway: $default_gateway"

    if command -v ip >/dev/null 2>&1; then
        ip route del default 2>/dev/null
        ip route add default via "$default_gateway" 2>/dev/null
        log "Default gateway set: $default_gateway"
    fi
fi

# ----- Parameter: dns_server -----
# Description: DNS server(s)
# Values: Space-separated IP addresses
if [ -n "$dns_server" ] && [ "$dhcp" != "yes" ]; then
    log "Setting DNS servers: $dns_server"

    # Update resolv.conf
    > /etc/resolv.conf
    for dns in $dns_server; do
        echo "nameserver $dns" >> /etc/resolv.conf
    done
    log "DNS servers configured"
fi

# ----- WiFi Parameters -----
# These are typically applied at boot, but can be reconfigured

# ----- Parameter: ssid_name -----
# Description: WiFi network name
# Values: SSID string
if [ -n "$ssid_name" ] && [ "$connection" = "wifi" ]; then
    log "WiFi SSID: $ssid_name"
fi

# ----- Parameter: hidden_ssid_name -----
# Description: Hidden WiFi network name
# Values: SSID string
if [ -n "$hidden_ssid_name" ]; then
    log "Hidden WiFi SSID configured"
fi

# ----- Parameter: wifi_encryption -----
# Description: WiFi security type
# Values: open, wep, wpa, wpa2, eap-peap
if [ -n "$wifi_encryption" ]; then
    log "WiFi encryption: $wifi_encryption"
fi

# ----- Parameter: wep_key -----
# Description: WEP encryption key
# Values: WEP key string
if [ -n "$wep_key" ]; then
    log "WEP key configured"
fi

# ----- Parameter: wpa_password -----
# Description: WPA/WPA2 password
# Values: Password string
if [ -n "$wpa_password" ]; then
    log "WPA password configured"

    # If we need to reconnect to WiFi with new credentials
    if [ "$connection" = "wifi" ] && [ -n "$ssid_name" ]; then
        iface="${network_interface:-wlan0}"

        # Generate wpa_supplicant config
        wpa_conf="/tmp/wpa_supplicant.conf"
        cat > "$wpa_conf" << EOF
ctrl_interface=/var/run/wpa_supplicant
update_config=1

network={
    ssid="$ssid_name"
    psk="$wpa_password"
}
EOF

        # Restart wpa_supplicant if running
        if pidof wpa_supplicant >/dev/null 2>&1; then
            killall wpa_supplicant 2>/dev/null
            sleep 1
        fi

        wpa_supplicant -B -i "$iface" -c "$wpa_conf" 2>/dev/null && \
            log "WiFi reconnecting to $ssid_name"
    fi
fi

# ----- Parameter: peap_username / peap_password -----
# Description: Enterprise WiFi credentials
if [ -n "$peap_username" ] && [ -n "$peap_password" ]; then
    log "Enterprise WiFi credentials configured"
fi

# ----- 802.1x Wired Authentication -----

# ----- Parameter: wired_authentication -----
# Description: Enable 802.1x EAP for wired network
# Values: eapol, none
if [ "$wired_authentication" = "eapol" ]; then
    log "802.1x wired authentication enabled"

    if [ -n "$eapol_username" ] && [ -n "$eapol_password" ]; then
        iface="${network_interface:-eth0}"

        # Generate wpa_supplicant config for wired EAP
        wpa_conf="/tmp/wpa_supplicant_wired.conf"
        cat > "$wpa_conf" << EOF
ctrl_interface=/var/run/wpa_supplicant
ap_scan=0

network={
    key_mgmt=IEEE8021X
    eap=PEAP
    identity="$eapol_username"
    password="$eapol_password"
    phase2="auth=MSCHAPV2"
}
EOF

        wpa_supplicant -B -i "$iface" -c "$wpa_conf" -D wired 2>/dev/null && \
            log "802.1x authentication started on $iface"
    fi
fi

# ----- Dialup Parameters -----
# Note: Rarely used but included for completeness

if [ "$connection" = "dialup" ]; then
    log "Dialup connection configured"

    # ----- Parameter: dialup_phone_number -----
    if [ -n "$dialup_phone_number" ]; then
        log "Dialup phone: $dialup_phone_number"
    fi

    # ----- Parameter: dialup_username / dialup_password -----
    if [ -n "$dialup_username" ]; then
        log "Dialup credentials configured"
    fi
fi

log "Network handler completed"
