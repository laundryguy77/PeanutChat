# TuxOS Kiosk UI Flow Specification

**Version:** 1.1
**Date:** 2026-01-14
**Purpose:** Complete specification of the GTKDialog UI flow for TuxOS Kiosk first-run setup

> **IMPORTANT DESIGN NOTE:** The network wait loop should ONLY execute on subsequent boots
> when a configuration already exists. On first run, there is no network configured yet,
> so waiting for network connectivity is pointless. The autostart script must check for
> first-run BEFORE attempting to wait for network.

---

## Table of Contents

1. [Overview](#1-overview)
2. [File Inventory](#2-file-inventory)
3. [Boot Sequence to UI](#3-boot-sequence-to-ui)
4. [Complete UI Flow Diagram](#4-complete-ui-flow-diagram)
5. [Phase 1: Autostart and Network Wait](#5-phase-1-autostart-and-network-wait)
6. [Phase 2: First-Run Script](#6-phase-2-first-run-script)
7. [Phase 3: Wizard-Now Prompt](#7-phase-3-wizard-now-prompt)
8. [Phase 4: Network Wizard (welcome)](#8-phase-4-network-wizard-welcome)
9. [Phase 5: TuxOS Authorization (wizard)](#9-phase-5-tuxos-authorization-wizard)
10. [Phase 6: Device Configuration Dialog](#10-phase-6-device-configuration-dialog)
11. [Remote Files Reference](#11-remote-files-reference)
12. [Configuration Output Format](#12-configuration-output-format)
13. [GTKDialog Function Library](#13-gtkdialog-function-library)

---

## 1. Overview

The TuxOS Kiosk setup process guides users through network configuration and device provisioning. The flow consists of multiple GTKDialog-based UI screens that collect configuration data and ultimately write a configuration file that determines the kiosk's behavior.

### High-Level Flow Summary

The autostart script must branch based on whether this is a first-run or subsequent boot:

```
BOOT → X11 Starts → Openbox → Autostart
                                   │
                                   ▼
                        ┌──────────────────┐
                        │  Check for lcon  │  Does /opt/scripts/files/lcon exist
                        │  config file     │  with kiosk_config= parameter?
                        └────────┬─────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 │                               │
                 ▼                               ▼
          [NO CONFIG]                     [CONFIG EXISTS]
          FIRST RUN                       SUBSEQUENT BOOT
                 │                               │
                 │                               ▼
                 │                    ┌──────────────────┐
                 │                    │  Apply network   │
                 │                    │  configuration   │
                 │                    └────────┬─────────┘
                 │                             │
                 │                             ▼
                 │                    ┌──────────────────┐
                 │                    │  Wait for Network│ (60s timeout)
                 │                    │  NOW MAKES SENSE │
                 │                    └────────┬─────────┘
                 │                             │
                 │                             ▼
                 │                    ┌──────────────────┐
                 │                    │  Launch Browser  │
                 │                    │  with homepage   │
                 │                    └──────────────────┘
                 │
                 ▼
      ┌──────────────────┐
      │    first-run     │ (orchestrator script)
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │   wizard-now     │ "Launch Network Wizard" button
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │    welcome       │ Network configuration wizard
      │  (8 pages)       │ Wired/Wireless/DHCP/Manual
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │  TEST NETWORK    │ Verify connectivity after config
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │     wizard       │ TuxOS Authorization Page
      │  (password)      │ Password: P@ss3264
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │     wizard       │ Device Configuration Dialog
      │  (drive select)  │ Device Type + Facility + Drive
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │  /tmp/config     │ Configuration file written
      └──────────────────┘
```

---

## 2. File Inventory

### Core Scripts (Execution Order)

| Order | File | Location | Purpose |
|-------|------|----------|---------|
| 1 | `autostart` | `/etc/xdg/openbox/autostart` | X11 session initialization, network wait, launches first-run |
| 2 | `first-run` | `/opt/scripts/first-run` | Orchestrates wizard flow, validates config |
| 3 | `wizard-now` | `/opt/scripts/wizard-now` | Initial prompt with "Launch Network Wizard" button |
| 4 | `welcome` | `/opt/scripts/welcome` | Network configuration wizard (8 GTKDialog pages) |
| 5 | `wizard` | `/opt/scripts/wizard` | TuxOS authorization + device configuration |

### Support Files

| File | Location | Purpose |
|------|----------|---------|
| `wizard-functions` | `/opt/scripts/files/wizard/wizard-functions` | GTKDialog helper functions library |
| `lcon.default` | `/opt/scripts/files/lcon.default` | Default configuration template |
| `keyboards.txt` | `/opt/scripts/files/wizard/keyboards.txt` | Keyboard layout options |
| `timezones.txt` | `/opt/scripts/files/wizard/timezones.txt` | Timezone options |

### Remote Files (Downloaded at Runtime)

| File | URL | Purpose |
|------|-----|---------|
| `key.txt` | `https://cullerdigitalmedia.com/files/key.txt` | Authorization password |
| `clients.txt` | `https://cullerdigitalmedia.com/files/clients.txt` | Client list (unused currently) |
| `dev.txt` | `https://cullerdigitalmedia.com/files/dev.txt` | Device type dropdown options |
| `fac.txt` | `https://cullerdigitalmedia.com/files/fac.txt` | Facility dropdown options |
| `num.txt` | `https://cullerdigitalmedia.com/files/num.txt` | Device number dropdown options |

### Temporary Files (Runtime)

| File | Purpose |
|------|---------|
| `/tmp/config` | Final wizard output, becomes `/opt/scripts/files/lcon` |
| `/tmp/report` | Network wizard summary report |
| `/tmp/knet/*` | Network wizard temporary files |
| `/tmp/kwiz.$$/*` | TuxOS wizard temporary files |
| `/tmp/launch-wizard` | Signal file: user clicked "Launch Network Wizard" |

---

## 3. Boot Sequence to UI

### 3.1 Kernel to X11

```
GPU Bootloader (start4.elf)
         │
         ▼
    kernel8.img (Linux 6.1.93 ARM64)
         │
         ▼
    initrd.img (initramfs)
         │
         ├── Mount AUFS union filesystem
         ├── Load XZM modules (000-kernel, 001-core, 003-settings)
         └── switch_root → /sbin/init
                │
                ▼
         /sbin/init (custom, busybox sh)
                │
                ├── Mount /proc, /sys, /dev
                ├── Run /etc/rc.d/rc.S (system init)
                └── Run /etc/rc.d/rc.4 (GUI init)
                        │
                        ▼
                   startx → X.Org (fbdev driver)
                        │
                        ▼
                   openbox-session
                        │
                        ▼
                   /etc/xdg/openbox/autostart
```

### 3.2 Autostart Initialization

**File:** `/etc/xdg/openbox/autostart`

> **CRITICAL:** The autostart script MUST check for first-run BEFORE waiting for network.
> On first boot, no network is configured yet, so waiting for connectivity is pointless.

The autostart script SHOULD perform these operations in order:

1. **Display Setup**
   - Set wallpaper with `feh`
   - Start D-Bus session
   - Start `dunst` notification daemon
   - Disable DPMS screen blanking

2. **First-Run Check** ← MUST HAPPEN BEFORE NETWORK WAIT
   ```bash
   LCON="/opt/scripts/files/lcon"

   # Check if system is configured
   if [ ! -f "$LCON" ] || ! grep -q "^kiosk_config=" "$LCON" 2>/dev/null; then
       # FIRST RUN - no config exists, skip network wait
       # Network hasn't been configured yet, so waiting is pointless
       log "First run detected - launching setup wizard"

       if [ -x /opt/scripts/first-run ]; then
           /opt/scripts/first-run
       fi

       # After wizard completes, config should exist
       # Exit or re-evaluate
       exit 0
   fi
   ```

3. **Network Wait** ← ONLY ON SUBSEQUENT BOOTS (config exists)
   - Apply network configuration (DHCP, WiFi, etc.)
   - Loop 30 times, ping `8.8.8.8`
   - 2 second delay between attempts
   - Total timeout: ~60 seconds
   - Logs "Network connected" on success
   - **This makes sense now because network IS configured**

4. **NTP Sync**
   - Background: `ntpdate -s pool.ntp.org`

5. **Launch Browser** (config exists, network should be up)
   - Read homepage from lcon
   - Launch chromium/firefox in kiosk mode

---

## 4. Complete UI Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AUTOSTART                                       │
│  /etc/xdg/openbox/autostart                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Set wallpaper, start dbus, dunst                                        │
│  2. CHECK IF FIRST RUN (does lcon with kiosk_config= exist?)                │
│     ├─► NO CONFIG: Call /opt/scripts/first-run, then exit                   │
│     └─► CONFIG EXISTS: Continue to step 3                                   │
│  3. WAIT FOR NETWORK (only if configured - makes sense now)                 │
│  4. Sync time via NTP                                                       │
│  5. Launch browser with configured homepage                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                            [FIRST RUN PATH]
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FIRST-RUN                                       │
│  /opt/scripts/first-run                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Verify this is truly first run (redundant check, but safe)              │
│  2. Clean up previous wizard temp files                                     │
│  3. Launch wizard-now prompt (30s timeout)                                  │
│  4. Wait for user to click "Launch" or timeout                              │
│  5. Launch welcome (network wizard) - CONFIGURE NETWORK FIRST               │
│  6. After network configured: Launch wizard (TuxOS authorization)           │
│  7. Validate wizard output                                                  │
│  8. Save config to /opt/scripts/files/lcon                                  │
│  9. Trigger update-config (optional)                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WIZARD-NOW                                      │
│  /opt/scripts/wizard-now                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Window: "Network Wizard" (400px wide)                                │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Title: "Network connection wizard"                                   │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Text: "Wait on connection or click on the launch button below       │  │
│  │         to start the network wizard immediately."                     │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  [  Launch network wizard  ]  ← Button                                │  │
│  │                                                                       │  │
│  │  ACTION: touch /tmp/launch-wizard                                     │
│  │          kill self                                                    │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │  User clicks "Launch network wizard"
                                      │  OR 30 second timeout
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WELCOME (Network Wizard)                        │
│  /opt/scripts/welcome                                                       │
│  8-Page GTKDialog Wizard (600×510 pixels)                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PAGE 0: CONNECTION TYPE CHOICE                                             │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Title: "Porteus Kiosk Wizard"                                        │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Text: "Welcome to the Porteus Kiosk setup wizard..."                 │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                   │  │
│  │  │   [icon]    │  │   [icon]    │  │   [icon]    │                   │  │
│  │  │   WIRED     │  │  WIRELESS   │  │   DIALUP    │                   │  │
│  │  │  160×160    │  │   160×160   │  │   160×160   │                   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                   │  │
│  │   "Select         "Select          "Select                            │  │
│  │    ethernet        wireless         dial-up                           │  │
│  │    connection"     connection"      connection"                       │  │
│  │                                                                       │  │
│  │  ACTIONS:                                                             │  │
│  │  • Wired:    echo "connection=wired" > $TMP/connection.tmp            │  │
│  │              Go to Page 2 (DHCP/Manual choice)                        │  │
│  │  • Wireless: echo "connection=wifi" > $TMP/connection.tmp             │  │
│  │              Start WiFi scan (get_essid &)                            │  │
│  │              Go to Page 2 (DHCP/Manual choice)                        │  │
│  │  • Dialup:   echo "connection=dialup" > $TMP/connection.tmp           │  │
│  │              Go to Page 1 (Dialup config)                             │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  PAGE 1: DIALUP CONFIGURATION                                               │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Title: "Modem Configuration"                                         │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Text: "Provide settings for your wired/mobile (2G/3G) dialup modem" │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Phone number:  [ *99#_________________ ]                             │  │
│  │  Username:      [ vodafone_____________ ]                             │  │
│  │  Password:      [ vodafone_____________ ]                             │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  OUTPUT: dialup_phone_number, dialup_username, dialup_password        │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  PAGE 2: DHCP OR MANUAL CHOICE                                              │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Title: "Network Configuration Type"                                  │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Text: "Choose DHCP if you would like your network configuration     │  │
│  │         to be automatically setup. Choose manual if you would like   │  │
│  │         to enter your network configuration manually."               │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │  ┌─────────────────────┐      ┌─────────────────────┐                │  │
│  │  │       [icon]        │      │       [icon]        │                │  │
│  │  │        DHCP         │      │       MANUAL        │                │  │
│  │  │      160×160        │      │       160×160       │                │  │
│  │  └─────────────────────┘      └─────────────────────┘                │  │
│  │  "Configure connection        "Configure connection                   │  │
│  │   using DHCP"                  manually"                              │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  [Dropdown: Wired authentication]                                     │  │
│  │     • No authentication (default)                                     │  │
│  │     • EAP over LAN (802.1x)                                          │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Username: [____________] (if 802.1x selected)                        │  │
│  │  Password: [____________] (if 802.1x selected)                        │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  ACTIONS:                                                             │  │
│  │  • DHCP + Wired:    echo "dhcp=yes" → Go to Page 5 (Proxy)           │  │
│  │  • DHCP + Wireless: echo "dhcp=yes" → Go to Page 4 (WiFi password)   │  │
│  │  • Manual:          Go to Page 3 (Manual IP config)                   │  │
│  │                                                                       │  │
│  │  OUTPUT: dhcp=yes, wired_authentication, eapol_username/password      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  PAGE 3: MANUAL IP CONFIGURATION                                            │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Title: "Manual Configuration"                                        │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Text: "Please enter your manual configuration options below."        │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Interface:    [▼ eth0 / wlan0 / etc  ]  (auto-detected dropdown)    │  │
│  │  IP Address:   [ 192.168.1.2__________ ]                              │  │
│  │  Network Mask: [ 255.255.255.0________ ]                              │  │
│  │  Gateway:      [ 192.168.1.1__________ ]                              │  │
│  │  DNS Server 1: [ 8.8.8.8______________ ]                              │  │
│  │  DNS Server 2: [ 208.67.222.222_______ ]                              │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  NEXT: If wired → Page 5 (Proxy)                                      │  │
│  │        If wireless → Page 4 (WiFi password)                           │  │
│  │                                                                       │  │
│  │  OUTPUT: network_interface, ip_address, netmask, default_gateway,     │  │
│  │          dns_server                                                   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  PAGE 4: WIRELESS CONNECTION DETAILS                                        │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Title: "Wireless Connection Details"                                 │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Text: "Wait for scan to finish and select an access point"           │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  SSID: [▼ NetworkName1 / NetworkName2 / ... ]  (scanned list)        │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  [▶ Enter hidden access point]  (expandable)                          │  │
│  │     Hidden SSID: [________________]                                   │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Encryption type: [▼ dropdown ]                                       │  │
│  │     • Open network (default)                                          │  │
│  │     • WEP                                                             │  │
│  │     • WPA/WPA2 Personal                                               │  │
│  │     • WPA/WPA2 Enterprise (PEAP)                                      │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Username:     [____________] (if PEAP selected)                      │  │
│  │  Password/Key: [____________] (if encryption selected)                │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  MAC address: XX:XX:XX:XX:XX:XX (display only)                        │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  NEXT: Go to Page 5 (Proxy)                                           │  │
│  │                                                                       │  │
│  │  OUTPUT: ssid_name, hidden_ssid_name, wifi_encryption,                │  │
│  │          wep_key/wpa_password/peap_password, peap_username            │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  PAGE 5: PROXY SETTINGS                                                     │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Title: "Proxy Settings"                                              │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  1. Click Next if you are not using proxy                             │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  2. Manual configuration                                              │  │
│  │     Format: ipaddress:port                                            │  │
│  │     Or: username:password@ipaddress:port                              │  │
│  │     [ guest:secret@192.168.1.20:3128_____ ]                           │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Proxy exceptions:  (○) No  (○) Yes                                   │  │
│  │  No proxy for: [ 127.0.0.1 domain.local ]  (if Yes)                   │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  3. Automatic configuration                                           │  │
│  │     PAC URL: [ http://domain.com/files/proxy.pac ]                    │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  NEXT: Go to Page 6 (Browser choice)                                  │  │
│  │                                                                       │  │
│  │  OUTPUT: proxy, proxy_exceptions, proxy_config                        │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  PAGE 6: BROWSER CHOICE                                                     │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Title: "Browser choice"                                              │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Text: "Select your preferred browser..."                             │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │  ┌─────────────────────┐      ┌─────────────────────┐                │  │
│  │  │       [icon]        │      │       [icon]        │                │  │
│  │  │      FIREFOX        │      │       CHROME        │                │  │
│  │  │      160×160        │      │       160×160       │                │  │
│  │  └─────────────────────┘      └─────────────────────┘                │  │
│  │  "Select Mozilla Firefox"    "Select Google Chrome"                   │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  ACTIONS:                                                             │  │
│  │  • Firefox: echo "browser=firefox" → Go to Page 7                     │  │
│  │  • Chrome:  Show EULA dialog first                                    │  │
│  │             echo "browser=chrome" → Go to Page 7                      │  │
│  │                                                                       │  │
│  │  OUTPUT: browser=firefox OR browser=chrome                            │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  PAGE 7: CONFIRMATION (Final Report)                                        │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Title: "Confirmation"                                                │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Text: "Please wait for the settings to appear below..."              │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │  YOUR FINAL REPORT:                                             │  │  │
│  │  │  connection=wifi                                                │  │  │
│  │  │  dhcp=yes                                                       │  │  │
│  │  │  ssid_name=MyNetwork                                            │  │  │
│  │  │  wifi_encryption=wpa                                            │  │  │
│  │  │  wpa_password=secret123                                         │  │  │
│  │  │  browser=firefox                                                │  │  │
│  │  │  ...                                                            │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  Text: "Please manually set the system time if you experience         │  │
│  │         connection troubles..."                                       │  │
│  │  Current date/time: 14 Jan 2026 15:30                                 │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │  NEXT: EXIT:finished → Network config written to /tmp/config          │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  BOTTOM BUTTONS (All Pages):                                                │
│  ═══════════════════════════════════════════════════════════════════════════│
│  [ Restart ]  [ Set keyboard layout ]  [ Virtual keyboard ]  [ Next ]      │
│       │               │                        │                  │         │
│       │               │                        │                  └─ Next   │
│       │               │                        │                     page   │
│       │               │                        └─ Toggle xvkbd              │
│       │               └─ /opt/scripts/set-kbd-layout                        │
│       └─ Reset wizard, go to Page 0                                         │
│                                                                             │
│  Additional buttons shown conditionally:                                    │
│  [ Set time ] - Page 7 only, /opt/scripts/set-system-clock                  │
│  [ Re-scan wifi ] - Page 4 only, re-run get_essid function                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │  Network config complete
                                      │  /tmp/config created with network settings
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WIZARD (TuxOS Authorization)                    │
│  /opt/scripts/wizard                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  INITIALIZATION:                                                            │
│  ═══════════════════════════════════════════════════════════════════════════│
│  1. Create temp directory: /tmp/kwiz.$$                                     │
│  2. Get PC ID: grep ^ID: /etc/version | cut -d" " -f2                       │
│  3. Create block device list for drive selection                            │
│  4. Download remote files:                                                  │
│     • curl cullerdigitalmedia.com/files/key.txt → $TMPDIR/drivekey.txt     │
│       (fallback: "P@ss3264")                                                │
│     • curl cullerdigitalmedia.com/files/clients.txt → /tmp/clients.txt     │
│       (fallback: "laundromat")                                              │
│                                                                             │
│  AUTHORIZATION PAGE (WIZARD_MAIN):                                          │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Window: "TuxOS Wizard" (580×480 pixels)                              │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │  Title: "TuxOS Wizard - Authorization Page"                           │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │  Text: "Please enter the password below to proceed with the          │  │
│  │         setup of this device."                                        │  │
│  │                                                                       │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │  Enter Password: [ 000000000_______________ ]                         │  │
│  │                                                                       │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │                    [  Install OS  ]                                   │  │
│  │                         │                                             │  │
│  │                         └─ Check password against key.txt             │  │
│  │                            If missing: show warning dialog            │  │
│  │                            If match: exit with "finished"             │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  PASSWORD VALIDATION LOOP:                                                  │
│  ═══════════════════════════════════════════════════════════════════════════│
│  while [ "$CID" != "$DRIVEKEY" ]; do                                        │
│      # Show WIZARD_MAIN dialog                                              │
│      # Read user input from $TMPDIR/configuration.id                        │
│      # Compare against $DRIVEKEY (contents of key.txt = "P@ss3264")         │
│      # If match: break loop and show device config dialog                   │
│      # If no match: loop continues, show dialog again                       │
│  done                                                                       │
│                                                                             │
│  EXPECTED PASSWORD: P@ss3264                                                │
│  SOURCE: https://cullerdigitalmedia.com/files/key.txt                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │  Password matches "P@ss3264"
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WIZARD (Device Configuration)                   │
│  /opt/scripts/wizard - DIALOG variable                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  INITIALIZATION (after password verified):                                  │
│  ═══════════════════════════════════════════════════════════════════════════│
│  Download dropdown data files:                                              │
│  • curl cullerdigitalmedia.com/files/num.txt → /tmp/num.txt                │
│  • curl cullerdigitalmedia.com/files/dev.txt → /tmp/dev.txt                │
│  • curl cullerdigitalmedia.com/files/fac.txt → /tmp/fac.txt                │
│                                                                             │
│  DEVICE CONFIGURATION DIALOG:                                               │
│  ═══════════════════════════════════════════════════════════════════════════│
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Window: "TuxOS Wizard" (580×500 pixels)                              │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │  Device Type:    [▼ dropdown from dev.txt ]                           │  │
│  │                     • Education                                       │  │
│  │                     • Kiosk                                           │  │
│  │                     • ActivityPro                                     │  │
│  │                     • Medcart                                         │  │
│  │                     • Treatment                                       │  │
│  │                     • NurseStation                                    │  │
│  │                     • Bedboard                                        │  │
│  │                     • Resident Room                                   │  │
│  │                     • Digital Signage                                 │  │
│  │                                                                       │  │
│  │  Facility:       [▼ dropdown from fac.txt ]                           │  │
│  │                     • (facility names loaded from server)             │  │
│  │                                                                       │  │
│  │  Device Number:  [▼ dropdown from num.txt ]                           │  │
│  │                     • 1, 2, 3, 4, 5, etc.                             │  │
│  │                                                                       │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │  Text: "Please choose the target device (must have at least          │  │
│  │         1 GB size) to which you will be installing the kiosk."       │  │
│  │                                                                       │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │  NAME          │ TYPE    │ MODEL                    │ SIZE     │  │  │
│  │  ├─────────────────────────────────────────────────────────────────┤  │  │
│  │  │  sda           │ disk    │ Samsung_SSD_860          │ 250G     │  │  │
│  │  │  sdb           │ disk    │ SanDisk_Ultra            │ 32G      │  │  │
│  │  │  mmcblk0       │ disk    │ SD_Card                  │ 16G      │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  │  (Table: selectable rows from lsblk output)                           │  │
│  │                                                                       │  │
│  │  ─────────────────────────────────────────────────────────────────────│  │
│  │                                                                       │  │
│  │                    [  Install OS  ]                                   │  │
│  │                         │                                             │  │
│  │                         └─ Write config and exit                      │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  CONFIG URL CONSTRUCTION:                                                   │
│  ═══════════════════════════════════════════════════════════════════════════│
│  Base URL: http://cullerdigitalmedia.com/                                   │
│                                                                             │
│  Device Type        │ URL Pattern                                           │
│  ──────────────────────────────────────────────────────────────────────────│
│  Education          │ {base}kc/{facility}_ed.txt                            │
│  Kiosk              │ {base}kc/{facility}/{facility}_ks{num}.txt            │
│  ActivityPro        │ {base}activitypro/{facility}.txt                      │
│  Medcart            │ {base}kc/{facility}/{facility}_mc{num}.txt            │
│  Treatment          │ {base}kc/{facility}/{facility}_tc{num}.txt            │
│  NurseStation       │ {base}kc/{facility}/{facility}_ns{num}.txt            │
│  Bedboard           │ {base}kc/{facility}/{facility}_stats.txt              │
│  Resident Room      │ {base}kc/{facility}/{facility}_rr{num}.txt            │
│  Digital Signage    │ {base}signage/{facility}/{facility}_ds{num}.txt       │
│                                                                             │
│  Example: Device=Kiosk, Facility=Sunrise, Number=3                          │
│  → http://cullerdigitalmedia.com/kc/sunrise/sunrise_ks3.txt                 │
│                                                                             │
│  OUTPUT TO /tmp/config:                                                     │
│  ═══════════════════════════════════════════════════════════════════════════│
│  burn_dev=sdb                    (selected drive)                           │
│  kiosk_config=http://cullerdigitalmedia.com/kc/sunrise/sunrise_ks3.txt      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │  Configuration complete
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CONFIGURATION OUTPUT                            │
│  /tmp/config → /opt/scripts/files/lcon                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FINAL CONFIG FILE CONTENTS (merged from welcome + wizard):                 │
│  ═══════════════════════════════════════════════════════════════════════════│
│                                                                             │
│  # Network settings (from welcome script):                                  │
│  connection=wifi                                                            │
│  dhcp=yes                                                                   │
│  ssid_name=MyNetwork                                                        │
│  wifi_encryption=wpa                                                        │
│  wpa_password=secretpassword                                                │
│  browser=firefox                                                            │
│                                                                             │
│  # Device settings (from wizard script):                                    │
│  burn_dev=sdb                                                               │
│  kiosk_config=http://cullerdigitalmedia.com/kc/sunrise/sunrise_ks3.txt      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Phase 1: Autostart and First-Run Detection

### File: `/etc/xdg/openbox/autostart`

### Purpose
Initialize the X11 session, detect first-run vs subsequent boot, and route accordingly.

> **DESIGN PRINCIPLE:** Check for first-run BEFORE waiting for network. On first boot,
> no network configuration exists, so waiting for connectivity is pointless and wastes
> 60 seconds. The network wizard must run first to configure connectivity.

### Correct Operation Order

```bash
#!/bin/bash
LCON="/opt/scripts/files/lcon"

# ==============================================================================
# 1. Display Setup (always runs)
# ==============================================================================
feh --bg-scale /usr/share/wallpapers/default.jpg &
eval $(dbus-launch --sh-syntax)
dunst &
xset -dpms; xset s off; xset s noblank

# ==============================================================================
# 2. FIRST-RUN CHECK - MUST HAPPEN BEFORE NETWORK WAIT
# ==============================================================================
if [ ! -f "$LCON" ] || ! grep -q "^kiosk_config=" "$LCON" 2>/dev/null; then
    # ┌─────────────────────────────────────────────────────────────────────┐
    # │ FIRST RUN - No configuration exists                                 │
    # │ Network is NOT configured yet, so don't wait for it!                │
    # │ Launch wizard sequence to configure network first                   │
    # └─────────────────────────────────────────────────────────────────────┘
    log "First run detected - no network config exists yet"
    log "Launching setup wizard (skipping pointless network wait)"

    if [ -x /opt/scripts/first-run ]; then
        /opt/scripts/first-run
    fi

    # Wizard handles everything, exit when done
    # (or loop back to check if config now exists)
    exit 0
fi

# ==============================================================================
# 3. SUBSEQUENT BOOT - Config exists, network SHOULD be configured
# ==============================================================================
log "Configuration found, applying network settings..."

# Apply network config (this actually enables DHCP/WiFi/etc)
# ... network configuration commands from lcon ...

# NOW wait for network - this makes sense because config exists
log "Waiting for network..."
for i in $(seq 1 30); do
    ping -c 1 8.8.8.8 > /dev/null 2>&1 && {
        log "Network connected"
        break
    }
    sleep 2
done

# ==============================================================================
# 4. NTP Sync (after network is up)
# ==============================================================================
ntpdate -s pool.ntp.org 2>/dev/null &

# ==============================================================================
# 5. Launch Browser (system is configured and network should be up)
# ==============================================================================
HOMEPAGE=$(grep "^homepage=" "$LCON" | cut -d= -f2-)
chromium --kiosk "$HOMEPAGE" &
```

### Key Design Points

| Scenario | Network Wait? | Reason |
|----------|---------------|--------|
| First boot (no lcon) | **NO** | Network not configured yet - waiting is pointless |
| Subsequent boot (lcon exists) | **YES** | Network IS configured, just needs to come up |

### Decision Flow

```
autostart begins
      │
      ▼
┌─────────────────────────┐
│ Does lcon exist with    │
│ kiosk_config= ?         │
└───────────┬─────────────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
   NO              YES
    │               │
    │               ├─► Apply network config
    │               ├─► Wait for network (60s)
    │               ├─► NTP sync
    │               └─► Launch browser
    │
    └─► Launch first-run
        └─► wizard-now
            └─► welcome (network config)
                └─► wizard (TuxOS auth)
                    └─► Save config
                        └─► Reboot or restart autostart
```

---

## 6. Phase 2: First-Run Script

### File: `/opt/scripts/first-run`

### Purpose
Orchestrate the complete wizard flow, validate configuration, and save results.

### Key Functions

| Function | Purpose |
|----------|---------|
| `is_first_run()` | Check if first run is needed (no config exists) |
| `launch_wizard()` | Launch wizard-now, then main wizard |
| `validate_config()` | Verify wizard output has required fields |
| `process_config()` | Clean and save config to lcon |
| `mark_complete()` | Create flag file to prevent re-run |
| `trigger_update_config()` | Optionally burn config to storage |

### Wizard Launch Sequence (Lines 90-167)

```bash
launch_wizard() {
    # 1. Clean up previous wizard temp files
    rm -f "$WIZARD_OUTPUT" 2>/dev/null
    rm -rf /tmp/kwiz.* 2>/dev/null
    rm -rf /tmp/knet 2>/dev/null

    # 2. Show wizard-now prompt (30 second timeout)
    if [ -x "$WIZARD_NOW_SCRIPT" ]; then
        "$WIZARD_NOW_SCRIPT" &
        local wizard_now_pid=$!

        # Wait for user to click or timeout
        local count=0
        while [ $count -lt 30 ]; do
            if [ -f "/tmp/launch-wizard" ]; then
                # User clicked button
                rm -f /tmp/launch-wizard
                kill $wizard_now_pid 2>/dev/null
                break
            fi
            sleep 1
            count=$((count + 1))
        done
    fi

    # 3. Launch main wizard
    if [ -x "$WIZARD_SCRIPT" ]; then
        "$WIZARD_SCRIPT"
    elif [ -x "$WELCOME_SCRIPT" ]; then
        # Fallback to network-only wizard
        "$WELCOME_SCRIPT"
    fi
}
```

### Required Config Fields

```bash
local required_fields="burn_dev kiosk_config"
```

---

## 7. Phase 3: Wizard-Now Prompt

### File: `/opt/scripts/wizard-now`

### Purpose
Display initial prompt allowing user to either wait for automatic network connection or manually launch the network wizard.

### GTKDialog Definition

```bash
export WizardNow='
<window decorated="true" title="Network Wizard" icon-name="kiosk"
        resizable="false" width-request="400">
<vbox margin="10">
    <text use-markup="true" yalign="1">
        <label>"<span weight='bold' size='x-large'>Network connection wizard</span>"</label>
    </text>
    <hseparator></hseparator>
    <text><label>""</label></text>
    <text yalign="0" xalign="0" wrap="true" width-request="350">
        <label>Wait on connection or click on the launch button below
               to start the network wizard immediately.</label>
    </text>
    <text><label>""</label></text>
    <hseparator></hseparator>
    <hbox>
        <button can-default="true" has-default="true" use-stock="true">
            <label>Launch network wizard</label>
            <input file icon="gtk-ok"></input>
            <action>touch /tmp/launch-wizard</action>
            <action>kill -9 `ps | grep -w WizardNow | ...`</action>
        </button>
    </hbox>
</vbox>
</window>
'
```

### UI Mockup

```
┌─────────────────────────────────────────────────┐
│  Network Wizard                            [─]  │
├─────────────────────────────────────────────────┤
│                                                 │
│  Network connection wizard                      │
│  ─────────────────────────────────────────────  │
│                                                 │
│  Wait on connection or click on the launch      │
│  button below to start the network wizard       │
│  immediately.                                   │
│                                                 │
│  ─────────────────────────────────────────────  │
│                                                 │
│       [ ✓ Launch network wizard ]               │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Behavior

| Action | Result |
|--------|--------|
| User clicks button | `touch /tmp/launch-wizard` then self-terminates |
| 30 second timeout | first-run kills process and proceeds |
| User closes window | Process exits, first-run proceeds |

---

## 8. Phase 4: Network Wizard (welcome)

### File: `/opt/scripts/welcome`

### Purpose
Configure network connection (wired, wireless, or dialup) through an 8-page GTKDialog wizard.

### Variables

```bash
export TMP=/tmp/knet           # Temporary working directory
export CONF=/tmp/config        # Output configuration file
export REPORT=/tmp/report      # Summary report
ICONS=/usr/share/pixmaps
WINWIDTH=600
WINHEIGHT=510
```

### Page Navigation

| Page | Name | Trigger |
|------|------|---------|
| 0 | Connection Type | Initial page |
| 1 | Dialup Config | Dialup button clicked |
| 2 | DHCP/Manual Choice | Wired or Wireless button clicked |
| 3 | Manual IP Config | Manual button clicked |
| 4 | Wireless Details | Wireless + (DHCP or after Manual) |
| 5 | Proxy Settings | After network config complete |
| 6 | Browser Choice | After proxy |
| 7 | Confirmation | After browser selection |

### Page 0: Connection Type Choice

**UI Elements:**
- Title: "Porteus Kiosk Wizard"
- Three 160×160 image buttons:
  - Wired (icon: `wired-160.png`)
  - Wireless (icon: `wifi-160.png`)
  - Dialup (icon: `dialup.png`)

**Actions:**

```bash
# Wired button:
echo "connection=wired" > $TMP/connection.tmp
echo 2 > $TMP/.knetPage  # Go to Page 2

# Wireless button:
echo "connection=wifi" > $TMP/connection.tmp
get_essid &              # Start WiFi scan in background
echo 2 > $TMP/.knetPage  # Go to Page 2

# Dialup button:
echo "connection=dialup" > $TMP/connection.tmp
echo 1 > $TMP/.knetPage  # Go to Page 1
```

### Page 1: Dialup Configuration

**UI Elements:**
- Title: "Modem Configuration"
- Input fields:
  - Phone number (default: `*99#`)
  - Username (default: `vodafone`)
  - Password (default: `vodafone`)

**Output Variables:**
```
dialup_phone_number=$pphone
dialup_username=$puser
dialup_password=$ppass
```

### Page 2: DHCP or Manual Choice

**UI Elements:**
- Title: "Network Configuration Type"
- Two 160×160 image buttons:
  - DHCP (icon: `internet-160.png`)
  - Manual (icon: `network-configuration-160.png`)
- Dropdown: Wired authentication type
  - No authentication (default)
  - EAP over LAN (802.1x)
- Conditional fields (if 802.1x selected):
  - Username
  - Password

**Actions:**

```bash
# DHCP button (wired):
echo "dhcp=yes" > $TMP/dhcp.tmp
echo 5 > $TMP/.knetPage  # Go to Page 5 (Proxy)

# DHCP button (wireless):
echo "dhcp=yes" > $TMP/dhcp.tmp
echo 4 > $TMP/.knetPage  # Go to Page 4 (WiFi details)

# Manual button:
get_device               # Populate interface dropdown
echo 3 > $TMP/.knetPage  # Go to Page 3 (Manual config)
```

**Output Variables:**
```
dhcp=yes
wired_authentication=eapol  (if 802.1x selected)
eapol_username=$a1
eapol_password=$a2
```

### Page 3: Manual IP Configuration

**UI Elements:**
- Title: "Manual Configuration"
- Dropdown: Network interface (auto-detected)
- Input fields:
  - IP Address (default: `192.168.1.2`)
  - Network Mask (default: `255.255.255.0`)
  - Gateway (default: `192.168.1.1`)
  - DNS Server 1 (default: `8.8.8.8`)
  - DNS Server 2 (default: `208.67.222.222`)

**Output Variables:**
```
network_interface=$device
ip_address=$ipaddress
netmask=$netmask
default_gateway=$gateway
dns_server=$dns1 $dns2
```

### Page 4: Wireless Connection Details

**UI Elements:**
- Title: "Wireless Connection Details"
- Text: "Wait for scan to finish and select an access point"
- Dropdown: SSID list (from WiFi scan, file-monitored)
- Expander: "Enter hidden access point"
  - Hidden SSID input field
- Dropdown: Encryption type
  - Open network (default)
  - WEP
  - WPA/WPA2 Personal
  - WPA/WPA2 Enterprise (PEAP)
- Conditional fields:
  - Username (PEAP only)
  - Password/Key (WEP/WPA/PEAP)
- Display: MAC address of WiFi card

**WiFi Scan Function:**
```bash
get_essid(){
    for nic in $(iwconfig 2>/dev/null | cut -d" " -f1 | sed '/^$/d' | sort); do
        ifconfig $nic up
        iwlist $nic scan | egrep 'ESSID|Quality' | ...
    done
}
```

**Output Variables:**
```
ssid_name="NetworkName"
hidden_ssid_name="HiddenNetwork"  (if hidden AP used)
wifi_encryption=wpa               (wep|wpa|eap-peap)
wep_key=$p1                       (if WEP)
wpa_password=$p1                  (if WPA)
peap_username=$p2                 (if PEAP)
peap_password=$p1                 (if PEAP)
```

### Page 5: Proxy Settings

**UI Elements:**
- Title: "Proxy Settings"
- Section 1: "Click Next if you are not using proxy"
- Section 2: Manual configuration
  - Input: Proxy address (format: `user:pass@ip:port`)
  - Radio buttons: Proxy exceptions (No/Yes)
  - Input: Exception list (if Yes)
- Section 3: Automatic configuration
  - Input: PAC URL

**Output Variables:**
```
proxy=guest:secret@192.168.1.20:3128
proxy_exceptions=127.0.0.1 domain.local
proxy_config=http://domain.com/proxy.pac
```

### Page 6: Browser Choice

**UI Elements:**
- Title: "Browser choice"
- Two 160×160 image buttons:
  - Firefox (icon: `firefox-160.png`)
  - Chrome (icon: `chrome-160.png`)

**Actions:**

```bash
# Firefox button:
echo "browser=firefox" > $TMP/xbrowser.tmp
get_report              # Compile final report
echo 7 > $TMP/.knetPage # Go to Page 7

# Chrome button:
gtk_list "Google Chrome EULA" ...  # Show license
echo "browser=chrome" > $TMP/xbrowser.tmp
get_report
echo 7 > $TMP/.knetPage
```

**Output Variables:**
```
browser=firefox  OR  browser=chrome
```

### Page 7: Confirmation

**UI Elements:**
- Title: "Confirmation"
- Text area: Final report (auto-refreshing from `/tmp/report`)
- Text: Current date/time
- Buttons:
  - Set time (conditional, calls `/opt/scripts/set-system-clock`)
  - Next → Exit wizard

**Report Generation:**
```bash
get_report(){
    for a in $(ls -rt $TMP/*.tmp); do
        cat $a >> $REPORT
    done
}
```

### Bottom Navigation Buttons

| Button | Visibility | Action |
|--------|------------|--------|
| Restart | Always | Reset to Page 0, clear all temp files |
| Set keyboard layout | Page 0 only | Launch `/opt/scripts/set-kbd-layout` |
| Virtual keyboard | Always | Toggle `xvkbd` |
| Set time | Page 7 only | Launch `/opt/scripts/set-system-clock` |
| Re-scan wifi | Page 4 only | Re-run `get_essid` |
| Next | Always | Advance to next page or exit |

### Final Output

When user clicks "Next" on Page 7:
```bash
# From line 636:
cp -a /tmp/report /tmp/config
```

The `/tmp/config` file now contains all network configuration settings.

---

## 9. Phase 5: TuxOS Authorization (wizard)

### File: `/opt/scripts/wizard`

### Purpose
Verify authorization via password and collect device-specific configuration.

### Initialization

```bash
# Variables
export PCID=$(grep ^ID: /etc/version | cut -d" " -f2)
export TMPDIR=/tmp/kwiz.$$

# Create temp directory
mkdir -p $TMPDIR

# Download authorization key
if curl cullerdigitalmedia.com/files/key.txt >> $TMPDIR/drivekey.txt; then
    continue
else
    echo P@ss3264 > $TMPDIR/drivekey.txt  # Fallback
fi

# Download client list
if curl cullerdigitalmedia.com/files/clients.txt >> "/tmp/clients.txt"; then
    continue
else
    echo laundromat >> /tmp/clients.txt  # Fallback
fi

DRIVEKEY=$(cat $TMPDIR/drivekey.txt)  # Expected: "P@ss3264"
```

### Authorization Dialog (WIZARD_MAIN)

```bash
WIZARD_MAIN='
<window title="TuxOS Wizard" icon-name="kiosk" resizable="false"
        width-request="580" height-request="480" decorated="true">
<vbox>
<vbox margin="10">
    <hseparator></hseparator>
    <text use-markup="true" yalign="1">
        <label>"<span weight='bold' size='x-large'>TuxOS Wizard - Authorization Page</span>"</label>
    </text>
    <hseparator></hseparator>

    <text><label>""</label></text>
    <text>
        <label>Please enter the password below to proceed with the setup of this device.</label>
    </text>
    <text><label>""</label></text>

    <hseparator></hseparator>

    <hbox>
        <text use-markup="true" yalign="1">
            <label>"<span weight='normal'>Enter Password:</span>"</label>
        </text>
        <entry sensitive="true">
            <variable>CID</variable>
            <default>000000000</default>
            <action signal="changed">echo $CID > '$TMPDIR'/configuration.id</action>
        </entry>
    </hbox>

    <text><label>""</label></text>

    <hbox>
        <button tooltip-text="Install TuxOS">
            <label>Install OS</label>
            <input file>/usr/share/icons/oxygen/16x16/devices/drive-harddisk.png</input>
            <action condition="command_is_true( [ ! -f '$TMPDIR'/configuration.id ] && echo true )">
                gtk_warning "Missing parameter" "You must provide configuration ID." 400
            </action>
            <action condition="command_is_true( [ ! -f '$TMPDIR'/configuration.id ] && echo true )"
                    function="break">break</action>
            <action function="exit">finished</action>
        </button>
    </hbox>
</vbox>
</vbox>
</window>'
```

### UI Mockup

```
┌─────────────────────────────────────────────────────────────┐
│  TuxOS Wizard                                          [─]  │
├─────────────────────────────────────────────────────────────┤
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│            TuxOS Wizard - Authorization Page                │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│                                                             │
│  Please enter the password below to proceed with the        │
│  setup of this device.                                      │
│                                                             │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Enter Password:  [ 000000000________________________ ]     │
│                                                             │
│                                                             │
│                                                             │
│                    [ 💾 Install OS ]                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Password Validation Loop

```bash
while ([ "$CID" != "$DRIVEKEY" ]); do
    # Clear previous attempt
    rm /tmp/CLIENT.txt
    touch "$TMPDIR"/CLIENT.txt
    echo "client" > /tmp/CLIENT.txt
    rm "$TMPDIR"/configuration.id
    touch "$TMPDIR"/configuration.id

    # Show authorization dialog
    echo "$WIZARD_MAIN" | sed '/^##/d' | \
        gtkdialog -i /opt/scripts/files/wizard/wizard-functions -s -c > $TMPDIR/output

    # Read user input
    CID=$(cat $TMPDIR/configuration.id)

    # If password matches, proceed to device config
    if ([ "$CID" = "$DRIVEKEY" ]); then
        # ... show device configuration dialog ...
    else
        echo "failed"
        # Loop continues, dialog shows again
    fi
done
```

### Expected Password
- **Value:** `P@ss3264`
- **Source:** `https://cullerdigitalmedia.com/files/key.txt`
- **Fallback:** Hardcoded in script if download fails

---

## 10. Phase 6: Device Configuration Dialog

### File: `/opt/scripts/wizard` (DIALOG variable)

### Purpose
After successful authorization, collect device type, facility, device number, and target drive.

### Remote File Downloads

```bash
# After password verified, download dropdown options:
touch /tmp/fac.txt
touch /tmp/dev.txt
touch /tmp/num.txt
curl cullerdigitalmedia.com/files/num.txt >> "/tmp/num.txt"
curl cullerdigitalmedia.com/files/dev.txt >> "/tmp/dev.txt"
curl cullerdigitalmedia.com/files/fac.txt >> "/tmp/fac.txt"
```

### Device Configuration Dialog

```bash
export DIALOG='
<window title="TuxOS Wizard" resizable="false"
        width-request="580" height-request="500" decorated="true">
<vbox>
    <hbox>
        <text><label>Device Type:</label></text>
        <comboboxentry>
            <label>Select Device Type:</label>
            <default>Device</default>
            <variable>DEVTYPE</variable>
            <input>cat /tmp/dev.txt</input>
            <sensitive>true</sensitive>
        </comboboxentry>
    </hbox>

    <hbox>
        <text><label>Facility</label></text>
        <comboboxentry>
            <label>Select Facility:</label>
            <default>Facility</default>
            <variable>FACNAM</variable>
            <input>cat /tmp/fac.txt</input>
            <sensitive>true</sensitive>
        </comboboxentry>
    </hbox>

    <hbox>
        <text><label>Device Number</label></text>
        <comboboxentry>
            <label>Select Device Number:</label>
            <default>#</default>
            <variable>DEVNUM</variable>
            <input>cat /tmp/num.txt</input>
            <sensitive>true</sensitive>
        </comboboxentry>
    </hbox>

    <hseparator></hseparator>

    <text xalign="0" width-request="540" wrap="true" use-markup="true">
        <label>"Please choose the target device (must have at least
               <span weight='bold' color='red'>1 GB</span> size) to which
               you will be installing the kiosk system."</label>
    </text>

    <hseparator></hseparator>

    <table>
        <variable>tblTarget</variable>
        <width>500</width>
        <label>"NAME               |TYPE           |MODEL                                              |SIZE"</label>
        <height>130</height>
        <input file>'$TMPDIR'/block.txt</input>
        <action>echo burn_dev=$tblTarget >> /tmp/config</action>
    </table>

    <button>
        <label>Install OS</label>
        <variable>butBurn</variable>
        <input file>/usr/share/icons/oxygen/16x16/devices/drive-harddisk.png</input>
        <action>echo "burn_dev=$tblTarget" >> /tmp/config</action>
        <action function="exit">finished</action>
    </button>
</vbox>
</window>
'
```

### UI Mockup

```
┌─────────────────────────────────────────────────────────────┐
│  TuxOS Wizard                                          [─]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Device Type:    [▼ Kiosk__________________________ ]       │
│                                                             │
│  Facility:       [▼ Sunrise________________________ ]       │
│                                                             │
│  Device Number:  [▼ 3______________________________ ]       │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Please choose the target device (must have at least        │
│  1 GB size) to which you will be installing the kiosk.      │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ NAME      │ TYPE   │ MODEL              │ SIZE      │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │ sda       │ disk   │ Samsung_SSD_860    │ 250G      │    │
│  │ sdb       │ disk   │ SanDisk_Ultra      │ 32G    ◄──│────│── Selected
│  │ mmcblk0   │ disk   │ SD_Card            │ 16G       │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│                    [ 💾 Install OS ]                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Block Device List Generation

```bash
# From line 35:
lsblk -o NAME,TYPE,MODEL,SIZE | \
    egrep -v 'NAME|loop|part|rom' | \
    tr -s ' ' | \
    sed -e 's/ /_/g' -e 's/_/|/1' -e 's/_/|/1' -e 's/\(.*\)_/\1|/' \
    > $TMPDIR/block.txt
```

**Example output (block.txt):**
```
sda|disk|Samsung_SSD_860_EVO|250G
sdb|disk|SanDisk_Ultra_Fit|32G
mmcblk0|disk|SD_Card|16G
```

### Config URL Construction Logic

```bash
BASEURL='http://cullerdigitalmedia.com/'

if [ $DEVTYPE = "Education" ]; then
    TMPCONFIG="$BASEURL""kc/"
    FINCONFIG=$TMPCONFIG$(echo $FACNAM | tr '[:upper:]' '[:lower:]')"_ed.txt"
fi

if [ "$DEVTYPE" = "Kiosk" ]; then
    TMPCONFIG="$BASEURL""kc/"
    TMPCONFIG=$TMPCONFIG$(echo $FACNAM | tr '[:upper:]' '[:lower:]')
    TMPCONFIG=$TMPCONFIG"/"
    TMPCONFIG=$TMPCONFIG$(echo $FACNAM | tr '[:upper:]' '[:lower:]')
    TMPCONFIG=$TMPCONFIG"_ks"
    FINCONFIG=$TMPCONFIG$DEVNUM".txt"
fi

if [ $DEVTYPE = "ActivityPro" ]; then
    TMPCONFIG="$BASEURL""activitypro/"
    FINCONFIG=$TMPCONFIG$(echo $FACNAM | tr '[:upper:]' '[:lower:]')".txt"
fi

if [ $DEVTYPE = "Medcart" ]; then
    TMPCONFIG="$BASEURL""kc/"
    TMPCONFIG=$TMPCONFIG$(echo $FACNAM | tr '[:upper:]' '[:lower:]')
    TMPCONFIG=$TMPCONFIG"/"
    TMPCONFIG=$TMPCONFIG$(echo $FACNAM | tr '[:upper:]' '[:lower:]')
    TMPCONFIG=$TMPCONFIG"_mc"
    FINCONFIG=$TMPCONFIG$DEVNUM".txt"
fi

if [ $DEVTYPE = "Treatment" ]; then
    TMPCONFIG="$BASEURL""kc/"
    TMPCONFIG=$TMPCONFIG$(echo $FACNAM | tr '[:upper:]' '[:lower:]')
    TMPCONFIG=$TMPCONFIG"/"
    TMPCONFIG=$TMPCONFIG$(echo $FACNAM | tr '[:upper:]' '[:lower:]')
    TMPCONFIG=$TMPCONFIG"_tc"
    FINCONFIG=$TMPCONFIG$DEVNUM".txt"
fi

if [ $DEVTYPE = "NurseStation" ]; then
    TMPCONFIG="$BASEURL""kc/"
    TMPCONFIG=$TMPCONFIG$(echo $FACNAM | tr '[:upper:]' '[:lower:]')
    TMPCONFIG=$TMPCONFIG"/"
    TMPCONFIG=$TMPCONFIG$(echo $FACNAM | tr '[:upper:]' '[:lower:]')
    TMPCONFIG=$TMPCONFIG"_ns"
    FINCONFIG=$TMPCONFIG$DEVNUM".txt"
fi

if [ $DEVTYPE = "Bedboard" ]; then
    TMPCONFIG="$BASEURL""kc/"
    TMPCONFIG=$TMPCONFIG$(echo $FACNAM | tr '[:upper:]' '[:lower:]')
    TMPCONFIG=$TMPCONFIG"/"
    TMPCONFIG=$TMPCONFIG$(echo $FACNAM | tr '[:upper:]' '[:lower:]')
    TMPCONFIG=$TMPCONFIG"_stats"
    FINCONFIG=$TMPCONFIG".txt"
fi

if [ "$DEVTYPE" = "Resident Room" ]; then
    TMPCONFIG="$BASEURL""kc/"
    TMPCONFIG=$TMPCONFIG$(echo $FACNAM | tr '[:upper:]' '[:lower:]')
    TMPCONFIG=$TMPCONFIG"/"
    TMPCONFIG=$TMPCONFIG$(echo $FACNAM | tr '[:upper:]' '[:lower:]')
    TMPCONFIG=$TMPCONFIG"_rr"
    FINCONFIG=$TMPCONFIG$DEVNUM".txt"
fi

if [ "$DEVTYPE" = "Digital Signage" ]; then
    TMPCONFIG="$BASEURL""signage/"
    TMPCONFIG=$TMPCONFIG$(echo $FACNAM | tr '[:upper:]' '[:lower:]')
    TMPCONFIG=$TMPCONFIG"/"
    TMPCONFIG=$TMPCONFIG$(echo $FACNAM | tr '[:upper:]' '[:lower:]')
    TMPCONFIG=$TMPCONFIG"_ds"
    FINCONFIG=$TMPCONFIG$DEVNUM".txt"
fi
```

### Final Output

```bash
# Write to /tmp/config:
echo burn_dev="$tblTarget" >> /tmp/config
echo kiosk_config="$FINCONFIG" >> /tmp/config
```

---

## 11. Remote Files Reference

### Authentication

| File | URL | Contents | Purpose |
|------|-----|----------|---------|
| `key.txt` | `https://cullerdigitalmedia.com/files/key.txt` | `P@ss3264` | Authorization password |

### Dropdown Options

| File | URL | Example Contents | Purpose |
|------|-----|------------------|---------|
| `dev.txt` | `https://cullerdigitalmedia.com/files/dev.txt` | `Education`<br>`Kiosk`<br>`ActivityPro`<br>`Medcart`<br>`Treatment`<br>`NurseStation`<br>`Bedboard`<br>`Resident Room`<br>`Digital Signage` | Device type dropdown |
| `fac.txt` | `https://cullerdigitalmedia.com/files/fac.txt` | `Sunrise`<br>`Oakwood`<br>`Meadowbrook`<br>`... (facility names)` | Facility dropdown |
| `num.txt` | `https://cullerdigitalmedia.com/files/num.txt` | `1`<br>`2`<br>`3`<br>`4`<br>`5`<br>`... (numbers)` | Device number dropdown |
| `clients.txt` | `https://cullerdigitalmedia.com/files/clients.txt` | `laundromat`<br>`... (client names)` | Client list (currently unused) |

### Generated Config URLs

| Device Type | URL Pattern | Example |
|-------------|-------------|---------|
| Education | `{base}kc/{facility}_ed.txt` | `http://cullerdigitalmedia.com/kc/sunrise_ed.txt` |
| Kiosk | `{base}kc/{facility}/{facility}_ks{num}.txt` | `http://cullerdigitalmedia.com/kc/sunrise/sunrise_ks3.txt` |
| ActivityPro | `{base}activitypro/{facility}.txt` | `http://cullerdigitalmedia.com/activitypro/sunrise.txt` |
| Medcart | `{base}kc/{facility}/{facility}_mc{num}.txt` | `http://cullerdigitalmedia.com/kc/sunrise/sunrise_mc2.txt` |
| Treatment | `{base}kc/{facility}/{facility}_tc{num}.txt` | `http://cullerdigitalmedia.com/kc/sunrise/sunrise_tc1.txt` |
| NurseStation | `{base}kc/{facility}/{facility}_ns{num}.txt` | `http://cullerdigitalmedia.com/kc/sunrise/sunrise_ns4.txt` |
| Bedboard | `{base}kc/{facility}/{facility}_stats.txt` | `http://cullerdigitalmedia.com/kc/sunrise/sunrise_stats.txt` |
| Resident Room | `{base}kc/{facility}/{facility}_rr{num}.txt` | `http://cullerdigitalmedia.com/kc/sunrise/sunrise_rr101.txt` |
| Digital Signage | `{base}signage/{facility}/{facility}_ds{num}.txt` | `http://cullerdigitalmedia.com/signage/sunrise/sunrise_ds1.txt` |

---

## 12. Configuration Output Format

### Final `/tmp/config` File

After completing both the network wizard (`welcome`) and device wizard (`wizard`), the `/tmp/config` file contains:

```ini
# ================================================================
# Network Configuration (from welcome script)
# ================================================================

# Connection type
connection=wifi                    # wired|wifi|dialup

# DHCP setting
dhcp=yes                          # yes = automatic, absent = manual

# Manual IP settings (if dhcp not set)
network_interface=wlan0
ip_address=192.168.1.100
netmask=255.255.255.0
default_gateway=192.168.1.1
dns_server=8.8.8.8 8.8.4.4

# Wireless settings (if connection=wifi)
ssid_name=MyNetwork
wifi_encryption=wpa               # wep|wpa|eap-peap
wpa_password=secretpassword
# OR
wep_key=0123456789
# OR (for enterprise)
peap_username=user@domain
peap_password=enterprisepass

# Hidden network (if used)
hidden_ssid_name=HiddenNetwork

# Wired 802.1x authentication (if used)
wired_authentication=eapol
eapol_username=networkuser
eapol_password=networkpass

# Dialup settings (if connection=dialup)
dialup_phone_number=*99#
dialup_username=vodafone
dialup_password=vodafone

# Proxy settings
proxy=user:pass@192.168.1.20:3128
proxy_exceptions=127.0.0.1 localhost
# OR
proxy_config=http://domain.com/proxy.pac

# Browser selection
browser=firefox                    # firefox|chrome

# ================================================================
# Device Configuration (from wizard script)
# ================================================================

# Target drive for OS installation
burn_dev=sdb

# Remote configuration URL
kiosk_config=http://cullerdigitalmedia.com/kc/sunrise/sunrise_ks3.txt
```

### Config File Locations

| Stage | File | Purpose |
|-------|------|---------|
| Wizard output | `/tmp/config` | Temporary, merged network + device config |
| Permanent storage | `/opt/scripts/files/lcon` | Saved by first-run script |
| Comparison copy | `/opt/scripts/files/lconc` | For daemon.sh change detection |

---

## 13. GTKDialog Function Library

### File: `/opt/scripts/files/wizard/wizard-functions`

This file provides reusable GTKDialog functions used by both `welcome` and `wizard` scripts.

### Key Functions

#### `gtk_yesno(message, width)`
Display a Yes/No confirmation dialog.

```bash
gtk_yesno "Are you sure you want to proceed?" 400
# Result stored in /tmp/gtk_yesno
```

#### `gtk_warning(title, message, width)`
Display a warning dialog.

```bash
gtk_warning "Missing parameter" "You must provide configuration ID." 400
```

#### `gtk_list(title, message, width, type, file)`
Display content from a file (used for EULA display).

```bash
gtk_list "Google Chrome EULA" "Click OK to accept." 660 EULA /opt/scripts/files/wizard/license-GoogleChrome.txt
```

#### `get_device()`
Populate device dropdown based on connection type.

```bash
get_device
# Writes wired interfaces OR wireless interfaces to $TMP/device
```

#### `get_essid()`
Scan for available WiFi networks.

```bash
get_essid
# Writes SSID list to $TMP/essid
```

#### `get_input(title, text, width, output_file, prefix, input_file)`
Generic user input dialog.

```bash
get_input "Hostname" "Enter the hostname:" 400 $TMPDIR/hostname.tmp "hostname" ""
```

#### `get_whitelist()` / `get_blacklist()`
Multi-line URL filter input dialogs.

#### `dlist()`
Generate block device list for drive selection.

```bash
dlist
# Writes to $TMPDIR/block.txt
```

---

## Summary: Complete Intended Flow

> **KEY INSIGHT:** The flow branches at autostart based on whether configuration exists.
> Network wait only makes sense on subsequent boots when network IS configured.

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. BOOT                                                         │
│    Power on → Kernel → Initramfs → AUFS mount → /sbin/init      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. X11 SESSION                                                  │
│    rc.4 → startx → openbox → autostart                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. AUTOSTART - Decision Point                                   │
│    • Set wallpaper, start dbus, dunst                           │
│    • CHECK: Does /opt/scripts/files/lcon exist with             │
│             kiosk_config= parameter?                            │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
       [NO CONFIG]                     [CONFIG EXISTS]
       FIRST RUN                       SUBSEQUENT BOOT
              │                               │
              │                               ▼
              │               ┌─────────────────────────────────────┐
              │               │ SUBSEQUENT BOOT PATH                │
              │               │ • Apply network config from lcon    │
              │               │ • Wait for network (60s) ← VALID    │
              │               │ • NTP sync                          │
              │               │ • Launch browser with homepage      │
              │               │ • daemon.sh polls for changes       │
              │               └─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. FIRST-RUN (only on first boot, NO network wait)              │
│    • Verify first run state                                     │
│    • Launch wizard-now prompt (30s)                             │
│    • Launch wizard sequence                                     │
│    • Validate and save config                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. WIZARD-NOW                                                   │
│    GTK Window: "Network connection wizard"                      │
│    Button: "Launch network wizard"                              │
│    → Creates /tmp/launch-wizard signal file                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. WELCOME (Network Wizard) - 8 Pages                           │
│    Page 0: Wired / Wireless / Dialup choice                     │
│    Page 1: Dialup config (phone, user, pass)                    │
│    Page 2: DHCP / Manual choice + 802.1x auth                   │
│    Page 3: Manual IP configuration                              │
│    Page 4: Wireless SSID + encryption + password                │
│    Page 5: Proxy settings                                       │
│    Page 6: Browser choice (Firefox / Chrome)                    │
│    Page 7: Confirmation report                                  │
│    → Writes network config to /tmp/config                       │
│    → NETWORK IS NOW CONFIGURED                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6a. TEST NETWORK CONNECTION                                     │
│    • Apply the network config just entered                      │
│    • Verify connectivity (needed for downloading key.txt)       │
│    • If no connection, allow user to retry network wizard       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. WIZARD (TuxOS Authorization)                                 │
│    Downloads: key.txt (password = "P@ss3264")                   │
│    GTK Window: "TuxOS Wizard - Authorization Page"              │
│    Input: Password entry                                        │
│    Button: "Install OS"                                         │
│    → Loops until password matches key.txt                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │  Password correct
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. WIZARD (Device Configuration)                                │
│    Downloads: dev.txt, fac.txt, num.txt                         │
│    GTK Window: "TuxOS Wizard"                                   │
│    Dropdowns: Device Type, Facility, Device Number              │
│    Table: Drive selection (from lsblk)                          │
│    Button: "Install OS"                                         │
│    → Constructs config URL                                      │
│    → Appends to /tmp/config:                                    │
│      burn_dev=sdb                                               │
│      kiosk_config=http://...                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 9. CONFIGURATION SAVED                                          │
│    /tmp/config → /opt/scripts/files/lcon                        │
│    first-run marks complete                                     │
│    Optionally triggers update-config (may reboot)               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 10. REBOOT / RESTART AUTOSTART                                  │
│    Now config exists → subsequent boot path                     │
│    Browser launches with configured homepage                    │
│    daemon.sh polls for config changes                           │
└─────────────────────────────────────────────────────────────────┘
```

### Why Network Wait Only On Subsequent Boots

| Scenario | Has Network Config? | Wait for Network? | Reason |
|----------|---------------------|-------------------|--------|
| First boot | NO | **NO** | Nothing to wait for - network not set up yet |
| After wizard completes | YES | YES | Config exists, just needs connection |
| Any subsequent boot | YES | YES | Config persisted, network configured |

The network wizard (`welcome`) is what CREATES the network configuration. It makes no
logical sense to wait for a network connection before running the wizard that configures it.

---

## Document History

- **2026-01-14 v1.0:** Initial version created from codebase analysis
- **2026-01-14 v1.1:** Critical design correction - network wait logic
  - **Issue identified:** Waiting for network on first boot is pointless because
    network hasn't been configured yet
  - **Correction:** Autostart must check for first-run BEFORE network wait loop
  - **Updated sections:** Overview, Section 3.2, Section 4, Section 5, Summary
  - **Key insight:** Network wizard (`welcome`) CREATES the network config, so it
    must run before any network connectivity can exist

- **Purpose:** Comprehensive specification for TuxOS Kiosk UI flow
- **Source Files Analyzed:**
  - `/etc/xdg/openbox/autostart` (193 lines)
  - `/opt/scripts/first-run` (345 lines)
  - `/opt/scripts/wizard-now` (27 lines)
  - `/opt/scripts/welcome` (642 lines)
  - `/opt/scripts/wizard` (300 lines)
  - `/opt/scripts/files/wizard/wizard-functions` (~1000+ lines)
