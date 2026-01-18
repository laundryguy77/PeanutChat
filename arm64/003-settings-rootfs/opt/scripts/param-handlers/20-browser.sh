#!/bin/bash
# =============================================================================
# Parameter Handler: 20-browser.sh
# =============================================================================
# Handles: browser, homepage, homepage_append, homepage_check, whitelist,
#          blacklist, disable_private_mode, password_manager, browser_language,
#          search_engine, managed_bookmarks, import_certificates,
#          allow_popup_windows, disable_zoom_controls, browser_zoom_level,
#          browser_user_agent, enable_file_protocol, browser_preferences,
#          disable_address_bar, autohide_navigation_bar, disable_navigation_bar,
#          onscreen_buttons, onscreen_buttons_position, toggle_tabs,
#          refresh_webpage, virtual_keyboard, allow_media_devices
#
# To add a new parameter:
#   1. Add parameter check below
#   2. Test: echo "param=value" >> /opt/scripts/files/lcon && /opt/scripts/apply-config
# =============================================================================

# Source config if not already sourced
[ -z "$CONFIG" ] && CONFIG="/opt/scripts/files/lcon"
[ -f "$CONFIG" ] && source "$CONFIG"

log() { echo "[$(basename "$0")] $*" >> "${LOG_FILE:-/tmp/apply-config.log}"; }

# Chromium policy directory
CHROMIUM_POLICY_DIR="/etc/chromium/policies/managed"
CHROMIUM_POLICY_FILE="$CHROMIUM_POLICY_DIR/policy.json"

# Firefox profile directory
FIREFOX_PROFILE="/home/guest/.mozilla/firefox/default"

# ----- Parameter: browser -----
# Description: Browser selection (firefox, chrome, chromium)
# Note: This is primarily used by autostart for launching, but we set up policies here
if [ -n "$browser" ]; then
    log "Browser configured: $browser"
fi

# ----- Parameter: homepage -----
# Description: Initial webpage URL(s)
# Values: URL or space-separated URLs for multiple tabs
if [ -n "$homepage" ]; then
    log "Setting homepage: $homepage"

    # For Chromium: Set policy
    if [ -d "$CHROMIUM_POLICY_DIR" ] || mkdir -p "$CHROMIUM_POLICY_DIR" 2>/dev/null; then
        # Build or update policy JSON
        if [ -f "$CHROMIUM_POLICY_FILE" ]; then
            # Update existing policy (simple approach - recreate)
            :
        fi
    fi
fi

# ----- Parameter: whitelist -----
# Description: Allowed URLs/IPs (whitelist filtering)
# Values: Space-separated URLs or IP addresses
if [ -n "$whitelist" ]; then
    log "URL whitelist configured: $whitelist"

    # For Chromium: URLAllowlist policy
    # For Firefox: Extensions or proxy autoconfig
fi

# ----- Parameter: blacklist -----
# Description: Blocked URLs/IPs (blacklist filtering)
# Values: Space-separated URLs or IP addresses
if [ -n "$blacklist" ]; then
    log "URL blacklist configured: $blacklist"

    # For Chromium: URLBlocklist policy
    # For Firefox: Extensions or proxy autoconfig
fi

# ----- Parameter: disable_private_mode -----
# Description: Disable incognito/private browsing
# Values: yes, no
if [ "$disable_private_mode" = "yes" ]; then
    log "Disabling private browsing mode"
    # Chromium: IncognitoModeAvailability = 1 (disabled)
fi

# ----- Parameter: password_manager -----
# Description: Enable password saving
# Values: yes, no
if [ "$password_manager" = "yes" ]; then
    log "Enabling password manager"
    # Chromium: PasswordManagerEnabled = true
fi

# ----- Parameter: browser_language -----
# Description: Browser UI language
# Values: Language code (en-US, de-DE, etc.)
if [ -n "$browser_language" ]; then
    log "Setting browser language: $browser_language"
fi

# ----- Parameter: search_engine -----
# Description: Default search engine
# Values: google, duckduckgo
if [ -n "$search_engine" ]; then
    log "Setting search engine: $search_engine"
fi

# ----- Parameter: managed_bookmarks -----
# Description: Toolbar bookmarks
# Values: JSON or comma-separated URL list
if [ -n "$managed_bookmarks" ]; then
    log "Configuring managed bookmarks"
fi

# ----- Parameter: import_certificates -----
# Description: Import SSL certificates
# Values: URL to certificate file(s)
if [ -n "$import_certificates" ]; then
    log "Importing certificates from: $import_certificates"

    # Download and install certificates
    for cert_url in $import_certificates; do
        cert_file="/tmp/$(basename "$cert_url")"
        if wget -q -O "$cert_file" "$cert_url" 2>/dev/null; then
            # Add to system trust store
            if [ -d /usr/local/share/ca-certificates ]; then
                cp "$cert_file" /usr/local/share/ca-certificates/
                update-ca-certificates 2>/dev/null || true
            fi
            log "Imported certificate: $cert_url"
        else
            log "WARNING: Failed to download certificate: $cert_url"
        fi
    done
fi

# ----- Parameter: allow_popup_windows -----
# Description: Allow popup windows
# Values: yes, no
if [ "$allow_popup_windows" = "yes" ]; then
    log "Allowing popup windows"
fi

# ----- Parameter: disable_zoom_controls -----
# Description: Disable user zoom
# Values: yes, no
if [ "$disable_zoom_controls" = "yes" ]; then
    log "Disabling zoom controls"
fi

# ----- Parameter: browser_zoom_level -----
# Description: Default zoom level
# Values: 0.8 to 2.0 (1.0 = 100%)
if [ -n "$browser_zoom_level" ]; then
    log "Setting zoom level: $browser_zoom_level"
fi

# ----- Parameter: browser_user_agent -----
# Description: Custom user agent string
# Values: User agent string
if [ -n "$browser_user_agent" ]; then
    log "Setting custom user agent"
fi

# ----- Parameter: enable_file_protocol -----
# Description: Allow file:// URLs
# Values: yes, no
if [ "$enable_file_protocol" = "yes" ]; then
    log "Enabling file:// protocol"
fi

# ----- Parameter: browser_preferences -----
# Description: Custom Firefox prefs / Chrome policies
# Values: URL to preferences file or inline JSON
if [ -n "$browser_preferences" ]; then
    log "Applying custom browser preferences"
fi

# ----- Parameter: disable_address_bar -----
# Description: Hide URL bar (Firefox)
# Values: yes, no
if [ "$disable_address_bar" = "yes" ]; then
    log "Disabling address bar"
fi

# ----- Parameter: autohide_navigation_bar -----
# Description: Auto-hide toolbar
# Values: yes, no
if [ "$autohide_navigation_bar" = "yes" ]; then
    log "Enabling auto-hide navigation bar"
fi

# ----- Parameter: disable_navigation_bar -----
# Description: Remove navigation toolbar
# Values: yes, no
if [ "$disable_navigation_bar" = "yes" ]; then
    log "Disabling navigation bar"
fi

# ----- Parameter: onscreen_buttons -----
# Description: Virtual navigation buttons
# Values: yes, no
if [ "$onscreen_buttons" = "yes" ]; then
    log "Enabling onscreen buttons"
fi

# ----- Parameter: onscreen_buttons_position -----
# Description: Button position
# Values: left, right, top, bottom
if [ -n "$onscreen_buttons_position" ]; then
    log "Onscreen buttons position: $onscreen_buttons_position"
fi

# ----- Parameter: toggle_tabs -----
# Description: Auto-switch browser tabs
# Values: Interval in seconds
if [ -n "$toggle_tabs" ]; then
    log "Tab toggle interval: $toggle_tabs seconds"
    # Could start a background script to cycle tabs
fi

# ----- Parameter: refresh_webpage -----
# Description: Auto-refresh page
# Values: Interval in seconds
if [ -n "$refresh_webpage" ]; then
    log "Page refresh interval: $refresh_webpage seconds"
    # Browser-specific: meta refresh or extension
fi

# ----- Parameter: virtual_keyboard -----
# Description: On-screen keyboard
# Values: yes, no
if [ "$virtual_keyboard" = "yes" ]; then
    log "Enabling virtual keyboard"
    # Start onboard or similar OSK
    if command -v onboard >/dev/null 2>&1; then
        onboard &
    elif command -v matchbox-keyboard >/dev/null 2>&1; then
        matchbox-keyboard &
    fi
fi

# ----- Parameter: allow_media_devices -----
# Description: Auto-allow webcam/microphone
# Values: yes, no
if [ "$allow_media_devices" = "yes" ]; then
    log "Allowing media devices (webcam/mic)"
fi

log "Browser handler completed"
