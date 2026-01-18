# TuxOS ARM64 - Browser Flags Reference

## Overview

The `gui-app` script launches Chromium in kiosk mode for the ARM64 port. This document details all browser flags used and how remote config settings map to Chromium command-line options.

---

## Chromium Kiosk Flags

### Core Kiosk Flags (Always Applied)

| Flag | Purpose |
|------|---------|
| `--kiosk` | Fullscreen kiosk mode - no window decorations, no address bar |
| `--no-first-run` | Skip the first-run wizard/welcome screen |
| `--disable-infobars` | Disable info bars (password save, translation, etc.) |
| `--noerrdialogs` | Suppress error dialog popups |
| `--disable-session-crashed-bubble` | Don't show "Chrome didn't shut down correctly" bubble |
| `--disable-restore-session-state` | Don't restore previous browsing session |

### Stability Flags (Always Applied)

| Flag | Purpose |
|------|---------|
| `--disable-translate` | Disable page translation prompts |
| `--disable-features=TranslateUI` | Ensure translate UI is fully disabled |
| `--disable-component-update` | Prevent background component updates |
| `--check-for-update-interval=31536000` | Check for updates annually (effectively never) |
| `--disable-background-networking` | Prevent background network activity |
| `--disable-sync` | Disable Google account sync |
| `--disable-default-apps` | Don't install default apps |

### Pi4 Specific Flags

| Flag | Purpose |
|------|---------|
| `--use-gl=egl` | Use EGL for OpenGL (Pi4 GPU) |
| `--enable-features=VaapiVideoDecoder` | Enable hardware video decoding |
| `--disable-dev-shm-usage` | Don't use /dev/shm (limited on Pi) |
| `--memory-pressure-off` | Reduce aggressive memory pressure responses |

### GPU Fallback Flags (when `disable_gpu=yes`)

| Flag | Purpose |
|------|---------|
| `--disable-gpu` | Disable GPU hardware acceleration |
| `--disable-software-rasterizer` | Disable software GPU fallback |

---

## Config Settings to Flags Mapping

### Browser Display Settings

| Config Setting | Chromium Flag(s) | Notes |
|---------------|------------------|-------|
| `fullscreen=no` | `--start-maximized` (replaces `--kiosk`) | Window mode instead of true kiosk |
| `browser_zoom_level=150` | `--force-device-scale-factor=1.5` | Percentage converted to factor |
| `browser_zoom=125` | `--force-device-scale-factor=1.25` | Alias for browser_zoom_level |
| `disable_navigation=yes` | `--app=URL` | App mode removes all chrome |
| `disable_navigation_bar=yes` | `--app=URL` | Alias for disable_navigation |
| `disable_zoom_controls=yes` | `--disable-pinch` | Prevents pinch-to-zoom |
| `hide_mouse=yes` | `--cursor=none` | Hides mouse cursor |

### Security/Access Settings

| Config Setting | Chromium Flag(s) | Notes |
|---------------|------------------|-------|
| `enable_file_protocol=yes` | `--allow-file-access-from-files --disable-web-security` | Allow local file access |
| `allow_popup_windows=yes` | `--disable-popup-blocking` | Allow popups |
| `allow_media_devices=yes` | `--use-fake-ui-for-media-stream --enable-usermedia-screen-capturing` | Auto-allow webcam/mic |
| `incognito_mode=yes` | `--incognito` | Private browsing mode |
| `browser_user_agent=STRING` | `--user-agent="STRING"` | Custom user agent |

### Pi4 Hardware Settings

| Config Setting | Chromium Flag(s) | Notes |
|---------------|------------------|-------|
| `disable_gpu=yes` | `--disable-gpu --disable-software-rasterizer` | Use when GPU causes issues |

---

## Settings Not Handled by Flags

Some settings require additional mechanisms beyond command-line flags:

### Requires Chromium Policy File

These settings are managed via `/etc/chromium/policies/managed/policy.json`:

| Config Setting | Policy Key | Notes |
|---------------|------------|-------|
| `whitelist` | `URLAllowlist` | JSON array of allowed URLs |
| `blacklist` | `URLBlocklist` | JSON array of blocked URLs |
| `disable_private_mode=yes` | `IncognitoModeAvailability: 1` | 0=allowed, 1=disabled, 2=forced |
| `password_manager=yes` | `PasswordManagerEnabled: true` | Enable password saving |
| `managed_bookmarks` | `ManagedBookmarks` | JSON bookmark structure |
| `disable_context_menu=yes` | Custom CSS/JS injection | Not a direct policy |

### Requires External Handling

| Config Setting | How It's Handled |
|---------------|------------------|
| `refresh_webpage=SECONDS` | Page must include meta refresh, or use extension |
| `toggle_tabs=SECONDS` | Requires background script/extension |
| `virtual_keyboard=yes` | Starts `onboard` or `matchbox-keyboard` daemon |
| `session_password` | Uses `session-manager` script before browser launch |
| `screensaver_*` | Handled by power management scripts, not browser |

---

## Homepage Resolution

The homepage URL is resolved in this priority order:

1. **`/tmp/kiosk_url.env`** - Sourceable file with `KIOSK_URL="..."`
2. **`/opt/scripts/files/lcon`** - `homepage=URL` setting
3. **`/opt/scripts/extras`** - `homepage=URL` setting
4. **Default** - `about:blank`

### Example lcon Config
```ini
homepage=http://example.com/signage
browser_zoom=125
fullscreen=yes
disable_navigation=yes
```

### Resulting Chromium Command
```bash
chromium \
    --kiosk \
    --no-first-run \
    --disable-infobars \
    --noerrdialogs \
    --disable-session-crashed-bubble \
    --disable-restore-session-state \
    --disable-translate \
    --disable-features=TranslateUI \
    --disable-component-update \
    --check-for-update-interval=31536000 \
    --disable-background-networking \
    --disable-sync \
    --disable-default-apps \
    --use-gl=egl \
    --enable-features=VaapiVideoDecoder \
    --disable-dev-shm-usage \
    --memory-pressure-off \
    --force-device-scale-factor=1.25 \
    --app="http://example.com/signage"
```

---

## Pi4 Troubleshooting

### Browser Won't Start
1. Check `/tmp/gui-app.log` for errors
2. Try adding `disable_gpu=yes` to config
3. Ensure `/home/guest` is writable

### GPU Issues
```ini
# Add to config to disable GPU
disable_gpu=yes
```

### Memory Issues
The Pi4 has limited RAM. Consider:
- Using simpler web pages
- Adding swap (`zRAM` config option)
- Reducing browser_zoom_level

### Display Issues
Check that:
- X11 is running (`echo $DISPLAY` should show `:0`)
- Guest user exists and can access display
- Screen resolution is detected (`xrandr`)

---

## File Locations

| File | Purpose |
|------|---------|
| `/opt/scripts/gui-app` | Main browser launcher script |
| `/opt/scripts/files/lcon` | Local config (homepage, settings) |
| `/opt/scripts/extras` | Device state (boot_dev, config URL) |
| `/tmp/kiosk_url.env` | Optional override (KIOSK_URL) |
| `/tmp/gui-app.log` | gui-app runtime log |
| `/etc/chromium/policies/managed/policy.json` | Chromium policies |

---

## See Also

- [ARM64_PORT_REFERENCE.md](ARM64_PORT_REFERENCE.md) - Complete system reference
- [PARAM_REFERENCE.md](../docs/PARAM_REFERENCE.md) - All config parameters
- [SCRIPTS_REFERENCE.md](../docs/SCRIPTS_REFERENCE.md) - Boot script reference

---

## Document History

- **Created:** January 2026
- **Purpose:** Document gui-app browser flags and settings mapping
- **Author:** Joel (Cornerstone Holdings) with Claude AI assistance
