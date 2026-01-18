# TuxOS ARM64 Boot Configuration - Test Scenarios

## Overview

This document provides test cases for the unified `arm64-boot-config.sh` script and its autostart integration. The script handles both first-boot installation and subsequent configuration updates.

---

## Test Environment Setup

### Prerequisites
- Raspberry Pi 4 with SD card or USB storage
- Network connectivity to config server
- Access to module server (or local modules)
- Serial console or HDMI output for monitoring

### Key Files
| File | Purpose |
|------|---------|
| `/opt/scripts/arm64-boot-config.sh` | Main boot config script |
| `/etc/xdg/openbox/autostart` | Desktop session startup |
| `/opt/scripts/extras` | Device state persistence |
| `/opt/scripts/files/lcon` | Local config (known good) |
| `/tmp/config` | Wizard output (first boot) |
| `/tmp/boot-config.log` | Script debug log |

---

## Test Case 1: First Boot (Fresh Install)

### Description
System boots from live image for the first time. No local config exists. Wizard runs, user selects device type, system installs to target storage.

### Preconditions
```bash
# Verify first-run state
grep "first_run=yes" /opt/scripts/extras    # Should match
ls -la /opt/scripts/files/lcon               # Should NOT exist
ls -la /tmp/config                           # Should NOT exist
```

### Test Steps
1. Boot from live image (SD card or ISO)
2. Wait for X11/Openbox to start
3. Observe wizard-now dialog appears
4. Complete welcome (network config)
5. Complete wizard (device selection)
6. Observe notifications:
   - "Performing system reconfiguration..."
   - "Downloading additional components..."
   - "[XX%] Downloading XXX.xzm..."
   - "Burning ISO on /dev/XXX..."
   - "Reconfiguration complete. System will reboot."
7. System reboots automatically

### Expected Results
- `/tmp/config` created after wizard with:
  ```
  burn_dev=sda
  kiosk_config=http://cullerdigitalmedia.com/...
  ```
- Target device partitioned (256MB FAT32 boot + ext4 root)
- All modules downloaded/copied to root partition
- Boot files installed to boot partition
- System reboots into installed system

### Verification (After Reboot)
```bash
# Check we're booting from installed system
mount | grep "on / "                         # Should show ext4 partition
cat /opt/scripts/extras                       # Should NOT have first_run=yes
cat /opt/scripts/extras | grep boot_dev       # Should show partition
cat /opt/scripts/files/lcon                   # Should have config
ls /porteuskiosk/*.xzm                        # Should list modules
cat /docs/kiosk.sgn                           # Should show install timestamp
```

### Failure Indicators
- Script exits without reboot
- `/tmp/boot-config-failed` exists
- Error messages in `/tmp/boot-config.log`
- Device not partitioned
- Browser launches instead of reboot

---

## Test Case 2: Normal Boot (No Config Change)

### Description
System boots normally after installation. Remote config matches local config. Browser launches without reconfiguration.

### Preconditions
```bash
# Verify installed state
[ -f /opt/scripts/files/lcon ] && echo "OK: Local config exists"
grep -q "boot_dev=" /opt/scripts/extras && echo "OK: Boot device set"
! grep -q "first_run=yes" /opt/scripts/extras && echo "OK: Not first run"
```

### Test Steps
1. Boot installed system
2. Wait for network (up to 120s)
3. Observe: No reconfiguration notifications
4. Browser launches with configured homepage

### Expected Results
- Remote config downloaded to `/tmp/rcon`
- Filtered comparison shows no difference
- Script exits with code 0
- `/tmp/config_ok` created
- Browser launches promptly

### Verification
```bash
# Check log
grep "Configuration unchanged" /tmp/boot-config.log   # Should match
ls /tmp/config_ok                                      # Should exist
ls /tmp/boot-config-failed                             # Should NOT exist
```

### Performance Expectation
- Time from X11 start to browser: ~30-60s (depending on network)

---

## Test Case 3: Config Update (Remote Changed)

### Description
Remote config file has been modified since last boot. System detects change, downloads modules, updates root partition, reboots.

### Preconditions
```bash
# Verify installed state
[ -f /opt/scripts/files/lcon ] && echo "OK: Local config exists"
# MODIFY remote config on server (change homepage, add setting, etc.)
```

### Setup: Modify Remote Config
```bash
# On config server, edit the device's config file
# Add or change a non-filtered setting, e.g.:
# homepage=http://new-url.example.com
# OR
# browser_zoom=110
```

### Test Steps
1. Modify remote config on server
2. Reboot the kiosk device
3. Wait for network
4. Observe notifications:
   - "Performing system reconfiguration..."
   - "Downloading additional components..."
   - "Burning ISO on /dev/XXX..."
   - "Reconfiguration complete. System will reboot."
5. System reboots automatically

### Expected Results
- Log shows "Configuration CHANGED - reconfiguration required"
- Modules downloaded/updated
- New config written to `/opt/scripts/files/lcon`
- System reboots

### Verification (After Reboot)
```bash
# Check new config applied
grep "homepage=" /opt/scripts/files/lcon   # Should show new value
cat /tmp/boot-config.log | tail -50        # Should show previous run
```

---

## Test Case 4: Filtered Settings Change (No Rebuild)

### Description
Remote config changes only include filtered settings (daemon_*, burn_dev, md5conf). These should NOT trigger a rebuild.

### Setup: Modify Only Filtered Settings
```bash
# On config server, edit config to change only:
daemon_check=10     # Was 5
daemon_force_reboot=no  # Was yes
```

### Test Steps
1. Modify only filtered settings on server
2. Reboot kiosk
3. Wait for boot config check

### Expected Results
- Log shows "Configuration unchanged"
- NO reconfiguration occurs
- Browser launches normally

### Verification
```bash
grep "Configuration unchanged" /tmp/boot-config.log   # Should match
```

---

## Test Case 5: Network Failure Handling

### Description
Network is unavailable during boot. Script should retry and eventually fail gracefully.

### Setup
```bash
# Disconnect network cable OR
# Block network at firewall/router
```

### Test Steps
1. Disconnect network
2. Boot kiosk
3. Observe behavior during 120s network wait
4. After timeout, observe script behavior

### Expected Results
- Script retries download every 10s
- After NETWORK_TIMEOUT (120s), shows error
- `/tmp/boot-config-failed` created
- Error notification displayed
- System continues to boot (doesn't hang)

### Verification
```bash
cat /tmp/boot-config.log                    # Should show retry attempts
cat /tmp/boot-config-failed                 # Should show timeout error
```

---

## Test Case 6: Module Download Failure

### Description
Module server is unreachable or returns errors. Script should try local fallback, then fail if unavailable.

### Setup
```bash
# Modify MODULE_SERVER in script to invalid URL OR
# Block access to module server
```

### Test Steps
1. Make module server unreachable
2. Trigger config change (modify remote config)
3. Reboot kiosk

### Expected Results
- Script attempts download from MODULE_SERVER
- Falls back to local modules from `/mnt/live/memory/data/porteuskiosk/`
- If local modules exist: Installation proceeds
- If no local modules: Error exit with clear message

### Verification
```bash
grep "Server download failed" /tmp/boot-config.log    # Should show
grep "Copying.*from" /tmp/boot-config.log             # Should show fallback
# OR
grep "Failed to download required module" /tmp/boot-config.log  # If failed
```

---

## Test Case 7: Partition Type Handling

### Description
Script correctly handles different device naming conventions.

### Test Matrix

| Device Type | Base Device | Boot Partition | Root Partition |
|-------------|-------------|----------------|----------------|
| USB/SATA | sda | /dev/sda1 | /dev/sda2 |
| SD Card | mmcblk0 | /dev/mmcblk0p1 | /dev/mmcblk0p2 |
| NVMe | nvme0n1 | /dev/nvme0n1p1 | /dev/nvme0n1p2 |

### Test Steps (for each device type)
1. Boot from live image
2. Select target device in wizard
3. Verify correct partition naming in log

### Verification
```bash
# Check log shows correct partition handling
grep "Formatting boot partition" /tmp/boot-config.log
grep "Formatting root partition" /tmp/boot-config.log
# Partition names should match table above
```

---

## Test Case 8: Subsequent Boot Partition Detection

### Description
On subsequent boots (not first run), script correctly identifies the root partition from extras.

### Preconditions
```bash
cat /opt/scripts/extras | grep boot_dev
# Should show: boot_dev=/dev/sdX2 (or mmcblk0p2, etc.)
```

### Test Steps
1. Boot installed system
2. Trigger config change
3. Verify script uses correct partition (not base device)

### Expected Results
- Script reads `boot_dev` from extras
- Mounts existing partition (doesn't repartition)
- Updates modules in place

### Verification
```bash
grep "First boot: no" /tmp/boot-config.log
grep "Target device:" /tmp/boot-config.log   # Should show partition
```

---

## Test Case 9: Wizard Output Parsing

### Description
Script correctly parses wizard output for various URL patterns.

### Test Data
```bash
# Test various kiosk_config values
echo "burn_dev=sda" > /tmp/config
echo "kiosk_config=http://cullerdigitalmedia.com/signage/loom/loom_ds1.txt" >> /tmp/config

# OR
echo "kiosk_config=http://cullerdigitalmedia.com/kc/testfac/testfac_ks1.txt" >> /tmp/config
```

### Verification
```bash
# Run just the URL parsing:
. /opt/scripts/arm64-boot-config.sh <<< ""  # Source functions
get_config_url                               # Should return correct URL
```

---

## Test Case 10: POSIX Shell Compatibility

### Description
Script runs correctly under busybox ash (minimal POSIX shell).

### Test Steps
```bash
# Run with explicit busybox ash
busybox ash -x /opt/scripts/arm64-boot-config.sh 2>&1 | tee /tmp/ash-test.log

# Check for bashisms that would fail:
# - No [[ ]] (use [ ])
# - No (( )) for arithmetic (use $(( )))
# - No ${var//pattern/replace} (use sed)
# - No let (use $(( )))
# - No arrays
# - No local -a or local -i
```

### Verification
```bash
# If any syntax errors, they'll appear in trace output
grep -i "syntax error" /tmp/ash-test.log   # Should be empty
grep -i "not found" /tmp/ash-test.log      # Should be empty
```

---

## Debugging Commands

### View Logs
```bash
# Main boot config log
cat /tmp/boot-config.log

# Autostart log
cat /tmp/autostart.log

# System journal (if available)
journalctl -b | grep -i boot

# Kernel messages
dmesg | tail -100
```

### Check State Files
```bash
# Device state
cat /opt/scripts/extras

# Local config
cat /opt/scripts/files/lcon

# Filtered configs
cat /opt/scripts/files/lconc
cat /opt/scripts/files/rconc
diff /opt/scripts/files/lconc /opt/scripts/files/rconc
```

### Manual Script Testing
```bash
# Test config URL detection
CONFIG_URL=$(grep "^kiosk_config=" /tmp/config | cut -d= -f2-)
echo "URL: $CONFIG_URL"

# Test download
wget -q "$CONFIG_URL" -O /tmp/test-config
cat /tmp/test-config

# Test filtering
grep -v "^#" /tmp/test-config | grep -v "^$" | grep -v "^daemon_\|^burn_dev=\|^md5conf="
```

### Simulate First Boot
```bash
# WARNING: This will trigger installation!
rm -f /opt/scripts/files/lcon
rm -f /opt/scripts/extras
echo "burn_dev=sda" > /tmp/config
echo "kiosk_config=http://yourserver/test.txt" >> /tmp/config
# Then reboot or run: /opt/scripts/arm64-boot-config.sh
```

---

## Change Log Summary

### V5 Changes from V4
1. Removed `set -e` for safer error handling
2. Replaced `sed -i` with POSIX-compliant `tr` + `mv`
3. Added network retry with configurable timeout (120s default)
4. Unified partition separator logic via `get_partition_separator()`
5. Added failure marker file `/tmp/boot-config-failed`
6. Improved logging with cleaner output
7. Fixed variable naming to avoid conflicts (prefix with `_`)

### Autostart Integration Changes
1. Single call to `arm64-boot-config.sh` replaces both first-run and update-config
2. Proper handling of script exit codes
3. Graceful degradation if script fails
4. Maintains original x86 boot order
5. Removed debug xterm (production ready)
