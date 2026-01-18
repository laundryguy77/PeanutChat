# Porteus Kiosk Parameter Reference

Complete reference of remote config parameters supported by the ARM64 port. Based on official Porteus Kiosk parameters from https://porteus-kiosk.org/parameters.html

---

## Connection Settings (00-network.sh)

| Parameter | Description | Values |
|-----------|-------------|--------|
| `connection` | Connection type | wired, wifi, dialup |
| `dhcp` | Use DHCP | yes, no |
| `ip_address` | Static IP address | IP address |
| `network_interface` | Network interface | eth0, wlan0, etc. |
| `default_gateway` | Default gateway | IP address |
| `netmask` | Subnet mask | Netmask (e.g., 255.255.255.0) |
| `dns_server` | DNS servers | IP address(es) |
| `wired_authentication` | 802.1x EAP authentication | EAP-PEAP, EAP-TLS |
| `eapol_username` | EAP username | String |
| `eapol_password` | EAP password | String |
| `ssid_name` | WiFi network name | SSID string |
| `hidden_ssid_name` | Hidden WiFi network | SSID string |
| `wifi_encryption` | WiFi security type | WEP, WPA, EAP-PEAP |
| `wep_key` | WEP key | WEP key string |
| `wpa_password` | WPA/WPA2 password | Password string |
| `peap_username` | Enterprise WiFi username | String |
| `peap_password` | Enterprise WiFi password | String |
| `dialup_*` | Modem/dialup settings | Various |

---

## Proxy Settings (10-proxy.sh)

| Parameter | Description | Values |
|-----------|-------------|--------|
| `proxy_config` | Proxy auto-config URL | PAC file URL |
| `proxy` | Manual proxy server | host:port |
| `proxy_exceptions` | Proxy bypass list | Comma-separated domains |

---

## Browser Settings (20-browser.sh)

### Core Browser Parameters

| Parameter | Description | Values |
|-----------|-------------|--------|
| `browser` | Browser selection | firefox, chrome |
| `homepage` | Start URL(s) | URL or URL list |
| `homepage_append` | Append to homepage | mac, hostname |
| `homepage_check` | Verify homepage URL | yes, no |

### URL Filtering

| Parameter | Description | Values |
|-----------|-------------|--------|
| `whitelist` | Allowed URLs only | URL patterns |
| `blacklist` | Blocked URLs | URL patterns |

### Browser Behavior

| Parameter | Description | Values |
|-----------|-------------|--------|
| `disable_private_mode` | Disable incognito mode | yes, no |
| `password_manager` | Enable password saving | yes, no |
| `browser_language` | UI language | Language code |
| `search_engine` | Default search engine | google, duckduckgo, etc. |
| `managed_bookmarks` | Toolbar bookmarks | JSON bookmark data |
| `import_certificates` | SSL certificates URL | URL to certificate bundle |
| `allow_popup_windows` | Allow popup windows | yes, no |

### Display Controls

| Parameter | Description | Values |
|-----------|-------------|--------|
| `disable_zoom_controls` | Disable zoom | yes, no |
| `browser_zoom_level` | Default zoom level | Percentage |
| `browser_user_agent` | Custom user agent | UA string |
| `enable_file_protocol` | Allow file:// URLs | yes, no |
| `browser_preferences` | Custom browser prefs | Pref string |

### Navigation Bar

| Parameter | Description | Values |
|-----------|-------------|--------|
| `disable_address_bar` | Hide URL bar | yes, no |
| `autohide_navigation_bar` | Auto-hide toolbar | yes, no |
| `disable_navigation_bar` | Remove toolbar entirely | yes, no |
| `onscreen_buttons` | Virtual nav buttons | yes, no |
| `onscreen_buttons_position` | Button position | top, bottom, left, right |

### Automation

| Parameter | Description | Values |
|-----------|-------------|--------|
| `toggle_tabs` | Auto-switch tabs | Seconds interval |
| `refresh_webpage` | Auto-refresh page | Seconds interval |

### Input/Media

| Parameter | Description | Values |
|-----------|-------------|--------|
| `virtual_keyboard` | On-screen keyboard | yes, no |
| `allow_media_devices` | Webcam/mic access | yes, no |

---

## Display Settings (30-display.sh)

| Parameter | Description | Values |
|-----------|-------------|--------|
| `wallpaper` | Background image URL | URL to image |
| `screen_settings` | Resolution/position | xrandr settings |
| `screen_rotate` | Screen rotation | left, right, inverted, normal |

---

## Input Settings (40-input.sh)

### Keyboard

| Parameter | Description | Values |
|-----------|-------------|--------|
| `disable_input_devices` | Disable keyboard/mouse | keyboard, mouse, both |
| `primary_keyboard_layout` | Primary keyboard layout | Layout code (us, de, etc.) |
| `secondary_keyboard_layout` | Secondary layout | Layout code |
| `disable_numlock` | Disable numlock | yes, no |

### Mouse/Cursor

| Parameter | Description | Values |
|-----------|-------------|--------|
| `hide_mouse` | Hide mouse cursor | yes, no |
| `mouse_cursor_size` | Cursor size | Pixels |
| `mouse_speed` | Pointer acceleration | Speed value |
| `right_mouse_click` | Enable right-click | yes, no |

### Touchscreen

| Parameter | Description | Values |
|-----------|-------------|--------|
| `touchscreen_calibration` | Calibration data | Calibration string |

---

## Power/Idle Settings (50-power.sh)

### Screensaver

| Parameter | Description | Values |
|-----------|-------------|--------|
| `screensaver_idle` | Screensaver timeout | Seconds |
| `screensaver_archive` | Slideshow ZIP URL | URL |
| `screensaver_archive_update` | Refresh slideshow | yes, no |
| `slide_duration` | Time per slide | Seconds |
| `slide_random` | Randomize slides | yes, no |
| `screensaver_video` | Video screensaver URL | URL |
| `screensaver_webpage` | Webpage screensaver | URL |

### Power Management

| Parameter | Description | Values |
|-----------|-------------|--------|
| `dpms_idle` | Monitor off timeout | Seconds |
| `freeze_idle` | Freeze timeout | Seconds |
| `standby_idle` | Standby timeout | Seconds |
| `suspend_idle` | Suspend timeout | Seconds |
| `halt_idle` | Shutdown timeout | Seconds |

### Session Management

| Parameter | Description | Values |
|-----------|-------------|--------|
| `session_idle` | Session restart timeout | Seconds |
| `session_idle_action` | Idle action | lock, restart |
| `session_idle_forced` | Force restart | yes, no |

---

## Audio Settings (60-audio.sh)

| Parameter | Description | Values |
|-----------|-------------|--------|
| `default_sound_card` | Audio output device | Device name/number |
| `default_microphone` | Audio input device | Device name/number |
| `volume_level` | Volume percentage | 0-100 |

---

## Services (70-services.sh)

### SSH

| Parameter | Description | Values |
|-----------|-------------|--------|
| `additional_components` | Enable services | ssh, vnc, printing (comma-separated) |
| `root_password` | Root/admin password | Password string |
| `ssh_port` | SSH port number | Port (default: 22) |
| `ssh_localhost_only` | Restrict SSH to localhost | yes, no |

### VNC

| Parameter | Description | Values |
|-----------|-------------|--------|
| `vnc_password` | VNC password | Password string |
| `vnc_port` | VNC port number | Port (default: 5900) |
| `vnc_interactive` | Allow VNC control | yes, no |
| `vnc_query_user` | Prompt before VNC | yes, no |
| `vnc_localhost_only` | Restrict VNC to localhost | yes, no |

### Printing

| Parameter | Description | Values |
|-----------|-------------|--------|
| `printer_model` | Printer driver/model | Model string |
| `printer_connection` | Printer connection | USB, network URI |
| `paper_size` | Paper format | A4, Letter, etc. |
| `silent_printing` | Skip print dialog | yes, no |
| `share_printer` | Share on network | yes, no |
| `printer_name` | Printer display name | String |

---

## System Settings (80-system.sh)

### Identity

| Parameter | Description | Values |
|-----------|-------------|--------|
| `hostname` | Computer hostname | String |
| `hostname_aliases` | /etc/hosts entries | host:ip pairs |

### Time

| Parameter | Description | Values |
|-----------|-------------|--------|
| `timezone` | Time zone | Timezone string (e.g., America/New_York) |
| `ntp_server` | NTP server | Server address |
| `rtc_wake` | RTC wake schedule | Cron-style schedule |

### Scheduled Actions

| Parameter | Description | Values |
|-----------|-------------|--------|
| `scheduled_action` | Scheduled commands | Command string |
| `automatic_updates` | Enable auto-updates | yes, no |
| `skip_updates` | Skip update days | Days to skip |

### Storage

| Parameter | Description | Values |
|-----------|-------------|--------|
| `persistence` | Persistent storage | Device or path |
| `swapfile` | Swap file | Size or path |
| `zRAM` | Compressed RAM swap | Size in MB |
| `removable_devices` | USB device support | yes, no |

### Network Security

| Parameter | Description | Values |
|-----------|-------------|--------|
| `disable_firewall` | Disable firewall | yes, no |
| `allow_icmp_protocol` | Allow ping | yes, no |
| `wake_on_lan` | Enable WoL | yes, no |

### Authentication

| Parameter | Description | Values |
|-----------|-------------|--------|
| `session_password` | Session login password | Password string |
| `shutdown_menu` | Show power menu | yes, no |

---

## Custom/Debug (90-custom.sh)

| Parameter | Description | Values |
|-----------|-------------|--------|
| `run_command` | Custom shell commands | Command string |
| `kernel_parameters` | Boot parameters | Parameter string |
| `gpu_driver` | GPU driver selection | Driver name |
| `debug` | Debug report generation | yes, no |
| `hardware_video_decode` | GPU video acceleration | yes, no |
| `watchdog` | Hardware watchdog | yes, no |

---

## Daemon Parameters (daemon.sh)

These special parameters are handled by the config daemon directly:

| Parameter | Description | Values |
|-----------|-------------|--------|
| `kiosk_config` | Remote config URL | URL |
| `daemon_check` | Poll interval | Minutes |
| `daemon_force_reboot` | Reboot on change | yes, no |
| `daemon_message` | Display notification | Message string |

---

## Handler Quick Reference

| Handler File | Parameters |
|--------------|------------|
| `00-network.sh` | connection, dhcp, ip_address, network_interface, gateway, dns, wifi, 802.1x |
| `10-proxy.sh` | proxy_config, proxy, proxy_exceptions |
| `20-browser.sh` | browser, homepage, whitelist, blacklist, zoom, user agent, certificates |
| `30-display.sh` | wallpaper, screen_settings, screen_rotate |
| `40-input.sh` | keyboard layout, hide_mouse, mouse_speed, touchscreen_calibration |
| `50-power.sh` | screensaver, dpms_idle, suspend_idle, halt_idle, session_idle |
| `60-audio.sh` | default_sound_card, default_microphone, volume_level |
| `70-services.sh` | SSH, VNC, printing configuration |
| `80-system.sh` | hostname, timezone, ntp_server, swapfile, zRAM, firewall, WoL |
| `90-custom.sh` | run_command, debug, gpu_driver, watchdog |

---

## See Also

- [PARAM_HANDLERS.md](PARAM_HANDLERS.md) - Handler architecture and how to add parameters
- [SCRIPTS_REFERENCE.md](SCRIPTS_REFERENCE.md) - Boot scripts and execution timeline
- Official documentation: https://porteus-kiosk.org/parameters.html
