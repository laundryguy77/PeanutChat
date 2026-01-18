#!/bin/bash
# =============================================================================
# Parameter Handler: 10-proxy.sh
# =============================================================================
# Handles: proxy_config, proxy, proxy_exceptions
#
# To add a new parameter:
#   1. Add parameter check below
#   2. Test: echo "param=value" >> /opt/scripts/files/lcon && /opt/scripts/apply-config
# =============================================================================

# Source config if not already sourced
[ -z "$CONFIG" ] && CONFIG="/opt/scripts/files/lcon"
[ -f "$CONFIG" ] && source "$CONFIG"

log() { echo "[$(basename "$0")] $*" >> "${LOG_FILE:-/tmp/apply-config.log}"; }

# ----- Parameter: proxy_config -----
# Description: URL to proxy auto-config (PAC) file
# Values: URL (e.g., http://proxy.example.com/proxy.pac)
if [ -n "$proxy_config" ]; then
    log "Proxy auto-config (PAC): $proxy_config"

    # Download PAC file for local use
    pac_file="/tmp/proxy.pac"
    if wget -q -O "$pac_file" "$proxy_config" 2>/dev/null; then
        log "Downloaded PAC file to: $pac_file"

        # Export for applications that support it
        export auto_proxy="$proxy_config"
    else
        log "WARNING: Failed to download PAC file"
    fi
fi

# ----- Parameter: proxy -----
# Description: Manual proxy server
# Values: [username:password@]host:port
if [ -n "$proxy" ]; then
    log "Proxy configured: $proxy"

    # Parse proxy string
    # Format: [user:pass@]host:port or just host:port
    if echo "$proxy" | grep -q '@'; then
        # Has authentication
        proxy_auth=$(echo "$proxy" | cut -d'@' -f1)
        proxy_host=$(echo "$proxy" | cut -d'@' -f2)
    else
        proxy_auth=""
        proxy_host="$proxy"
    fi

    # Extract host and port
    proxy_server=$(echo "$proxy_host" | cut -d':' -f1)
    proxy_port=$(echo "$proxy_host" | cut -d':' -f2)
    [ "$proxy_port" = "$proxy_server" ] && proxy_port="3128"  # Default proxy port

    # Build proxy URL
    if [ -n "$proxy_auth" ]; then
        proxy_url="http://${proxy_auth}@${proxy_server}:${proxy_port}"
    else
        proxy_url="http://${proxy_server}:${proxy_port}"
    fi

    # Export environment variables
    export http_proxy="$proxy_url"
    export https_proxy="$proxy_url"
    export HTTP_PROXY="$proxy_url"
    export HTTPS_PROXY="$proxy_url"

    # Write to profile for persistence
    proxy_profile="/etc/profile.d/proxy.sh"
    cat > "$proxy_profile" << EOF
# Proxy configuration from kiosk config
export http_proxy="$proxy_url"
export https_proxy="$proxy_url"
export HTTP_PROXY="$proxy_url"
export HTTPS_PROXY="$proxy_url"
EOF

    log "Proxy environment set: $proxy_server:$proxy_port"

    # Configure for specific applications

    # Chromium proxy
    CHROMIUM_FLAGS="/etc/chromium-flags.conf"
    if [ -f "$CHROMIUM_FLAGS" ] || touch "$CHROMIUM_FLAGS" 2>/dev/null; then
        # Remove existing proxy flags
        sed -i '/--proxy-server/d' "$CHROMIUM_FLAGS" 2>/dev/null
        # Add proxy flag
        echo "--proxy-server=$proxy_server:$proxy_port" >> "$CHROMIUM_FLAGS"
        log "Chromium proxy configured"
    fi

    # Firefox proxy (via prefs)
    FIREFOX_PREFS="/home/guest/.mozilla/firefox/default/user.js"
    if [ -d "$(dirname "$FIREFOX_PREFS")" ]; then
        cat >> "$FIREFOX_PREFS" << EOF
// Proxy configuration
user_pref("network.proxy.type", 1);
user_pref("network.proxy.http", "$proxy_server");
user_pref("network.proxy.http_port", $proxy_port);
user_pref("network.proxy.ssl", "$proxy_server");
user_pref("network.proxy.ssl_port", $proxy_port);
EOF
        log "Firefox proxy configured"
    fi
fi

# ----- Parameter: proxy_exceptions -----
# Description: Hosts/IPs that bypass proxy
# Values: Space or comma-separated list
if [ -n "$proxy_exceptions" ]; then
    log "Proxy exceptions: $proxy_exceptions"

    # Normalize separators to comma
    no_proxy=$(echo "$proxy_exceptions" | tr ' ' ',')

    # Export environment
    export no_proxy="$no_proxy"
    export NO_PROXY="$no_proxy"

    # Add to profile
    proxy_profile="/etc/profile.d/proxy.sh"
    if [ -f "$proxy_profile" ]; then
        cat >> "$proxy_profile" << EOF
export no_proxy="$no_proxy"
export NO_PROXY="$no_proxy"
EOF
    fi

    # Chromium bypass list
    CHROMIUM_FLAGS="/etc/chromium-flags.conf"
    if [ -f "$CHROMIUM_FLAGS" ]; then
        sed -i '/--proxy-bypass-list/d' "$CHROMIUM_FLAGS" 2>/dev/null
        echo "--proxy-bypass-list=$no_proxy" >> "$CHROMIUM_FLAGS"
    fi

    log "Proxy exceptions configured"
fi

log "Proxy handler completed"
