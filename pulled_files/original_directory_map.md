# clean_iso Directory Map Report

**Generated:** $(date '+%Y-%m-%d %H:%M:%S')
**Source Directory:** /home/culler/saas_dev/pk-port/clean_iso/

---

## Overview

The `clean_iso` directory contains the original x86 TuxOS/Porteus Kiosk ISO structure. This is the reference x86 version (version 5.2.0) that the ARM64 port is based on.

### Top-Level Structure

\`\`\`
clean_iso/
├── boot/          - Bootloader and kernel files
├── docs/          - Documentation and licensing
├── xzm/           - SquashFS modules (.xzm files)
└── make_iso.sh    - ISO creation script
\`\`\`

---

## Module Summary

| Module | Size | Description |
|--------|------|-------------|
| 000-kernel.xzm | 51M | Linux kernel modules and firmware |
| 001-core.xzm | 64M | Core system binaries, libraries, X11, browsers |
| 003-settings.xzm | 1.2M | Init scripts, rc.d, kiosk scripts, configs |
| 004-wifi.xzm | 1.6M | WiFi/wireless networking support |
| 06-fonts.xzm | 34M | Font files (corefonts, dejavu, noto, etc.) |
| 08-ssh.xzm | 1.4M | OpenSSH client and server |
| 09-x11vnc.xzm | 620K | VNC server for remote access |
| firmware.xzm | 8.0M | Broadcom/BCM wireless firmware |
| NextWindow-5.10.25.xzm | 940K | NextWindow touchscreen driver |
| zz-settings.xzm | 12K | Override settings (daemon.sh, wizard scripts) |

---

## Boot Directory

\`\`\`
boot/
├── initrd.xz          - Initial ramdisk (XZ compressed)
├── vmlinuz            - Linux kernel 5.10.25-kiosk (x86_64)
├── isolinux/          - ISOLINUX bootloader
│   ├── isolinux.bin   - ISOLINUX binary
│   ├── isolinux.boot  - Boot sector
│   ├── isolinux.cfg   - ISOLINUX configuration
│   ├── grub.cfg       - GRUB configuration
│   └── efi/
│       └── efiboot.img - EFI boot image
├── pxelinux.0         - PXE boot loader
└── pxelinux.cfg/
    └── default        - PXE default configuration
\`\`\`

**Kernel Version:** 5.10.25-kiosk (x86_64, SMP PREEMPT)

---

## Docs Directory

\`\`\`
docs/
├── default.jpg    - Default background image
├── first_run      - First run marker file
├── GNU_GPL        - GPL license
├── kiosk.sgn      - Kiosk signature file
├── License.txt    - License information
└── version        - Version file (contains: 5.2.0)
\`\`\`

---

## Module Detailed Contents


### 000-kernel.xzm (Kernel Modules & Firmware)

Contains kernel modules for Linux 5.10.25-kiosk and firmware blobs for various hardware.

<details>
<summary>Click to expand full tree (3993 lines)</summary>

\`\`\`
/tmp/tmp.O7x0keuVBb/000-kernel
├── etc
│   └── modprobe.d
│       └── ath10k.conf
├── lib -> lib64/
├── lib64
│   ├── firmware
│   │   ├── 3com
│   │   │   └── typhoon.bin
│   │   ├── acenic
│   │   │   ├── tg1.bin
│   │   │   └── tg2.bin
│   │   ├── adaptec
│   │   │   ├── starfire_rx.bin
│   │   │   └── starfire_tx.bin
│   │   ├── agere_ap_fw.bin
│   │   ├── agere_sta_fw.bin
│   │   ├── amdgpu
│   │   │   ├── banks_k_2_smc.bin
│   │   │   ├── bonaire_ce.bin
│   │   │   ├── bonaire_k_smc.bin
│   │   │   ├── bonaire_mc.bin
│   │   │   ├── bonaire_me.bin
│   │   │   ├── bonaire_mec.bin
│   │   │   ├── bonaire_pfp.bin
│   │   │   ├── bonaire_rlc.bin
│   │   │   ├── bonaire_sdma1.bin
│   │   │   ├── bonaire_sdma.bin
│   │   │   ├── bonaire_smc.bin
│   │   │   ├── bonaire_uvd.bin
│   │   │   ├── bonaire_vce.bin
│   │   │   ├── carrizo_ce.bin
│   │   │   ├── carrizo_me.bin
│   │   │   ├── carrizo_mec2.bin
│   │   │   ├── carrizo_mec.bin
│   │   │   ├── carrizo_pfp.bin
│   │   │   ├── carrizo_rlc.bin
│   │   │   ├── carrizo_sdma1.bin
│   │   │   ├── carrizo_sdma.bin
│   │   │   ├── carrizo_uvd.bin
│   │   │   ├── carrizo_vce.bin
│   │   │   ├── fiji_ce.bin
│   │   │   ├── fiji_mc.bin
│   │   │   ├── fiji_me.bin
│   │   │   ├── fiji_mec2.bin
│   │   │   ├── fiji_mec.bin
│   │   │   ├── fiji_pfp.bin
│   │   │   ├── fiji_rlc.bin
│   │   │   ├── fiji_sdma1.bin
│   │   │   ├── fiji_sdma.bin
│   │   │   ├── fiji_smc.bin
│   │   │   ├── fiji_uvd.bin
│   │   │   ├── fiji_vce.bin
│   │   │   ├── hainan_ce.bin
│   │   │   ├── hainan_k_smc.bin
│   │   │   ├── hainan_mc.bin
│   │   │   ├── hainan_me.bin
│   │   │   ├── hainan_pfp.bin
│   │   │   ├── hainan_rlc.bin
│   │   │   ├── hainan_smc.bin
│   │   │   ├── hawaii_ce.bin
│   │   │   ├── hawaii_k_smc.bin
│   │   │   ├── hawaii_mc.bin
│   │   │   ├── hawaii_me.bin
│   │   │   ├── hawaii_mec.bin
│   │   │   ├── hawaii_pfp.bin
│   │   │   ├── hawaii_rlc.bin
│   │   │   ├── hawaii_sdma1.bin
│   │   │   ├── hawaii_sdma.bin
│   │   │   ├── hawaii_smc.bin
│   │   │   ├── hawaii_uvd.bin
│   │   │   ├── hawaii_vce.bin
│   │   │   ├── kabini_ce.bin
│   │   │   ├── kabini_me.bin
│   │   │   ├── kabini_mec.bin
│   │   │   ├── kabini_pfp.bin
│   │   │   ├── kabini_rlc.bin
│   │   │   ├── kabini_sdma1.bin
│   │   │   ├── kabini_sdma.bin
│   │   │   ├── kabini_uvd.bin
│   │   │   ├── kabini_vce.bin
│   │   │   ├── kaveri_ce.bin
│   │   │   ├── kaveri_me.bin
│   │   │   ├── kaveri_mec2.bin
│   │   │   ├── kaveri_mec.bin
│   │   │   ├── kaveri_pfp.bin
│   │   │   ├── kaveri_rlc.bin
│   │   │   ├── kaveri_sdma1.bin
│   │   │   ├── kaveri_sdma.bin
│   │   │   ├── kaveri_uvd.bin
│   │   │   ├── kaveri_vce.bin
│   │   │   ├── mullins_ce.bin
│   │   │   ├── mullins_me.bin
│   │   │   ├── mullins_mec.bin
│   │   │   ├── mullins_pfp.bin
│   │   │   ├── mullins_rlc.bin
│   │   │   ├── mullins_sdma1.bin
│   │   │   ├── mullins_sdma.bin
│   │   │   ├── mullins_uvd.bin
│   │   │   ├── mullins_vce.bin
│   │   │   ├── navi10_asd.bin
│   │   │   ├── navi10_ce.bin
│   │   │   ├── navi10_gpu_info.bin
│   │   │   ├── navi10_me.bin
│   │   │   ├── navi10_mec2.bin
│   │   │   ├── navi10_mec.bin
│   │   │   ├── navi10_pfp.bin
│   │   │   ├── navi10_rlc.bin
│   │   │   ├── navi10_sdma1.bin
│   │   │   ├── navi10_sdma.bin
│   │   │   ├── navi10_smc.bin
│   │   │   ├── navi10_sos.bin
│   │   │   ├── navi10_ta.bin
│   │   │   ├── navi10_vcn.bin
│   │   │   ├── navi12_asd.bin
│   │   │   ├── navi12_ce.bin
│   │   │   ├── navi12_dmcu.bin
│   │   │   ├── navi12_gpu_info.bin
│   │   │   ├── navi12_me.bin
│   │   │   ├── navi12_mec2.bin
│   │   │   ├── navi12_mec.bin
│   │   │   ├── navi12_pfp.bin
│   │   │   ├── navi12_rlc.bin
│   │   │   ├── navi12_sdma1.bin
│   │   │   ├── navi12_sdma.bin
│   │   │   ├── navi12_smc.bin
│   │   │   ├── navi12_sos.bin
│   │   │   ├── navi12_ta.bin
│   │   │   ├── navi12_vcn.bin
│   │   │   ├── navi14_asd.bin
│   │   │   ├── navi14_ce.bin
│   │   │   ├── navi14_ce_wks.bin
│   │   │   ├── navi14_gpu_info.bin
│   │   │   ├── navi14_me.bin
│   │   │   ├── navi14_mec2.bin
│   │   │   ├── navi14_mec2_wks.bin
│   │   │   ├── navi14_mec.bin
│   │   │   ├── navi14_mec_wks.bin
│   │   │   ├── navi14_me_wks.bin
│   │   │   ├── navi14_pfp.bin
│   │   │   ├── navi14_pfp_wks.bin
│   │   │   ├── navi14_rlc.bin
│   │   │   ├── navi14_sdma1.bin
│   │   │   ├── navi14_sdma.bin
│   │   │   ├── navi14_smc.bin
│   │   │   ├── navi14_sos.bin
│   │   │   ├── navi14_ta.bin
│   │   │   ├── navi14_vcn.bin
│   │   │   ├── oland_ce.bin
│   │   │   ├── oland_k_smc.bin
│   │   │   ├── oland_mc.bin
│   │   │   ├── oland_me.bin
│   │   │   ├── oland_pfp.bin
│   │   │   ├── oland_rlc.bin
│   │   │   ├── oland_smc.bin
│   │   │   ├── oland_uvd.bin
│   │   │   ├── picasso_asd.bin
│   │   │   ├── picasso_ce.bin
│   │   │   ├── picasso_gpu_info.bin
│   │   │   ├── picasso_me.bin
│   │   │   ├── picasso_mec2.bin
│   │   │   ├── picasso_mec.bin
│   │   │   ├── picasso_pfp.bin
│   │   │   ├── picasso_rlc_am4.bin
│   │   │   ├── picasso_rlc.bin
│   │   │   ├── picasso_sdma.bin
│   │   │   ├── picasso_ta.bin
│   │   │   ├── picasso_vcn.bin
│   │   │   ├── pitcairn_ce.bin
│   │   │   ├── pitcairn_k_smc.bin
│   │   │   ├── pitcairn_mc.bin
│   │   │   ├── pitcairn_me.bin
│   │   │   ├── pitcairn_pfp.bin
│   │   │   ├── pitcairn_rlc.bin
│   │   │   ├── pitcairn_smc.bin
│   │   │   ├── pitcairn_uvd.bin
│   │   │   ├── polaris10_ce_2.bin
│   │   │   ├── polaris10_ce.bin
│   │   │   ├── polaris10_k2_smc.bin
│   │   │   ├── polaris10_k_mc.bin
│   │   │   ├── polaris10_k_smc.bin
│   │   │   ├── polaris10_mc.bin
│   │   │   ├── polaris10_me_2.bin
│   │   │   ├── polaris10_me.bin
│   │   │   ├── polaris10_mec2_2.bin
│   │   │   ├── polaris10_mec_2.bin
│   │   │   ├── polaris10_mec2.bin
│   │   │   ├── polaris10_mec.bin
│   │   │   ├── polaris10_pfp_2.bin
│   │   │   ├── polaris10_pfp.bin
│   │   │   ├── polaris10_rlc.bin
│   │   │   ├── polaris10_sdma1.bin
│   │   │   ├── polaris10_sdma.bin
│   │   │   ├── polaris10_smc.bin
│   │   │   ├── polaris10_smc_sk.bin
│   │   │   ├── polaris10_uvd.bin
│   │   │   ├── polaris10_vce.bin
│   │   │   ├── polaris11_ce_2.bin
│   │   │   ├── polaris11_ce.bin
│   │   │   ├── polaris11_k2_smc.bin
│   │   │   ├── polaris11_k_mc.bin
│   │   │   ├── polaris11_k_smc.bin
│   │   │   ├── polaris11_mc.bin
│   │   │   ├── polaris11_me_2.bin
│   │   │   ├── polaris11_me.bin
│   │   │   ├── polaris11_mec2_2.bin
│   │   │   ├── polaris11_mec_2.bin
│   │   │   ├── polaris11_mec2.bin
│   │   │   ├── polaris11_mec.bin
│   │   │   ├── polaris11_pfp_2.bin
│   │   │   ├── polaris11_pfp.bin
│   │   │   ├── polaris11_rlc.bin
│   │   │   ├── polaris11_sdma1.bin
│   │   │   ├── polaris11_sdma.bin
│   │   │   ├── polaris11_smc.bin
│   │   │   ├── polaris11_smc_sk.bin
│   │   │   ├── polaris11_uvd.bin
│   │   │   ├── polaris11_vce.bin
│   │   │   ├── polaris12_ce_2.bin
│   │   │   ├── polaris12_ce.bin
│   │   │   ├── polaris12_k_mc.bin
│   │   │   ├── polaris12_k_smc.bin
│   │   │   ├── polaris12_mc.bin
│   │   │   ├── polaris12_me_2.bin
│   │   │   ├── polaris12_me.bin
│   │   │   ├── polaris12_mec2_2.bin
│   │   │   ├── polaris12_mec_2.bin
│   │   │   ├── polaris12_mec2.bin
│   │   │   ├── polaris12_mec.bin
│   │   │   ├── polaris12_pfp_2.bin
│   │   │   ├── polaris12_pfp.bin
│   │   │   ├── polaris12_rlc.bin
│   │   │   ├── polaris12_sdma1.bin
│   │   │   ├── polaris12_sdma.bin
│   │   │   ├── polaris12_smc.bin
│   │   │   ├── polaris12_uvd.bin
│   │   │   ├── polaris12_vce.bin
│   │   │   ├── raven2_asd.bin
│   │   │   ├── raven2_ce.bin
│   │   │   ├── raven2_gpu_info.bin
│   │   │   ├── raven2_me.bin
│   │   │   ├── raven2_mec2.bin
│   │   │   ├── raven2_mec.bin
│   │   │   ├── raven2_pfp.bin
│   │   │   ├── raven2_rlc.bin
│   │   │   ├── raven2_sdma.bin
│   │   │   ├── raven2_ta.bin
│   │   │   ├── raven2_vcn.bin
│   │   │   ├── raven_asd.bin
│   │   │   ├── raven_ce.bin
│   │   │   ├── raven_dmcu.bin
│   │   │   ├── raven_gpu_info.bin
│   │   │   ├── raven_kicker_rlc.bin
│   │   │   ├── raven_me.bin
│   │   │   ├── raven_mec2.bin
│   │   │   ├── raven_mec.bin
│   │   │   ├── raven_pfp.bin
│   │   │   ├── raven_rlc.bin
│   │   │   ├── raven_sdma.bin
│   │   │   ├── raven_ta.bin
│   │   │   ├── raven_vcn.bin
│   │   │   ├── renoir_asd.bin
│   │   │   ├── renoir_ce.bin
│   │   │   ├── renoir_dmcub.bin
│   │   │   ├── renoir_gpu_info.bin
│   │   │   ├── renoir_me.bin
│   │   │   ├── renoir_mec2.bin
│   │   │   ├── renoir_mec.bin
│   │   │   ├── renoir_pfp.bin
│   │   │   ├── renoir_rlc.bin
│   │   │   ├── renoir_sdma.bin
│   │   │   ├── renoir_ta.bin
│   │   │   ├── renoir_vcn.bin
│   │   │   ├── si58_mc.bin
│   │   │   ├── sienna_cichlid_ce.bin
│   │   │   ├── sienna_cichlid_dmcub.bin
│   │   │   ├── sienna_cichlid_me.bin
│   │   │   ├── sienna_cichlid_mec2.bin
│   │   │   ├── sienna_cichlid_mec.bin
│   │   │   ├── sienna_cichlid_pfp.bin
│   │   │   ├── sienna_cichlid_rlc.bin
│   │   │   ├── sienna_cichlid_sdma.bin
│   │   │   ├── sienna_cichlid_smc.bin
│   │   │   ├── sienna_cichlid_sos.bin
│   │   │   ├── sienna_cichlid_ta.bin
│   │   │   ├── sienna_cichlid_vcn.bin
│   │   │   ├── stoney_ce.bin
│   │   │   ├── stoney_me.bin
│   │   │   ├── stoney_mec.bin
│   │   │   ├── stoney_pfp.bin
│   │   │   ├── stoney_rlc.bin
│   │   │   ├── stoney_sdma.bin
│   │   │   ├── stoney_uvd.bin
│   │   │   ├── stoney_vce.bin
│   │   │   ├── tahiti_ce.bin
│   │   │   ├── tahiti_k_smc.bin
│   │   │   ├── tahiti_mc.bin
│   │   │   ├── tahiti_me.bin
│   │   │   ├── tahiti_pfp.bin
│   │   │   ├── tahiti_rlc.bin
│   │   │   ├── tahiti_smc.bin
│   │   │   ├── tahiti_uvd.bin
│   │   │   ├── tonga_ce.bin
│   │   │   ├── tonga_k_smc.bin
│   │   │   ├── tonga_mc.bin
│   │   │   ├── tonga_me.bin
│   │   │   ├── tonga_mec2.bin
│   │   │   ├── tonga_mec.bin
│   │   │   ├── tonga_pfp.bin
│   │   │   ├── tonga_rlc.bin
│   │   │   ├── tonga_sdma1.bin
│   │   │   ├── tonga_sdma.bin
│   │   │   ├── tonga_smc.bin
│   │   │   ├── tonga_uvd.bin
│   │   │   ├── tonga_vce.bin
│   │   │   ├── topaz_ce.bin
│   │   │   ├── topaz_k_smc.bin
│   │   │   ├── topaz_mc.bin
│   │   │   ├── topaz_me.bin
│   │   │   ├── topaz_mec2.bin
│   │   │   ├── topaz_mec.bin
│   │   │   ├── topaz_pfp.bin
│   │   │   ├── topaz_rlc.bin
│   │   │   ├── topaz_sdma1.bin
│   │   │   ├── topaz_sdma.bin
│   │   │   ├── topaz_smc.bin
│   │   │   ├── vega10_acg_smc.bin
│   │   │   ├── vega10_asd.bin
│   │   │   ├── vega10_ce.bin
│   │   │   ├── vega10_gpu_info.bin
│   │   │   ├── vega10_me.bin
│   │   │   ├── vega10_mec2.bin
│   │   │   ├── vega10_mec.bin
│   │   │   ├── vega10_pfp.bin
│   │   │   ├── vega10_rlc.bin
│   │   │   ├── vega10_sdma1.bin
│   │   │   ├── vega10_sdma.bin
│   │   │   ├── vega10_smc.bin
│   │   │   ├── vega10_sos.bin
│   │   │   ├── vega10_uvd.bin
│   │   │   ├── vega10_vce.bin
│   │   │   ├── vega12_asd.bin
│   │   │   ├── vega12_ce.bin
│   │   │   ├── vega12_gpu_info.bin
│   │   │   ├── vega12_me.bin
│   │   │   ├── vega12_mec2.bin
│   │   │   ├── vega12_mec.bin
│   │   │   ├── vega12_pfp.bin
│   │   │   ├── vega12_rlc.bin
│   │   │   ├── vega12_sdma1.bin
│   │   │   ├── vega12_sdma.bin
│   │   │   ├── vega12_smc.bin
│   │   │   ├── vega12_sos.bin
│   │   │   ├── vega12_uvd.bin
│   │   │   ├── vega12_vce.bin
│   │   │   ├── vega20_asd.bin
│   │   │   ├── vega20_ce.bin
│   │   │   ├── vega20_me.bin
│   │   │   ├── vega20_mec2.bin
│   │   │   ├── vega20_mec.bin
│   │   │   ├── vega20_pfp.bin
│   │   │   ├── vega20_rlc.bin
│   │   │   ├── vega20_sdma1.bin
│   │   │   ├── vega20_sdma.bin
│   │   │   ├── vega20_smc.bin
│   │   │   ├── vega20_sos.bin
│   │   │   ├── vega20_ta.bin
│   │   │   ├── vega20_uvd.bin
│   │   │   ├── vega20_vce.bin
│   │   │   ├── vegam_ce.bin
│   │   │   ├── vegam_me.bin
│   │   │   ├── vegam_mec2.bin
│   │   │   ├── vegam_mec.bin
│   │   │   ├── vegam_pfp.bin
│   │   │   ├── vegam_rlc.bin
│   │   │   ├── vegam_sdma1.bin
│   │   │   ├── vegam_sdma.bin
│   │   │   ├── vegam_smc.bin
│   │   │   ├── vegam_uvd.bin
│   │   │   ├── vegam_vce.bin
│   │   │   ├── verde_ce.bin
│   │   │   ├── verde_k_smc.bin
│   │   │   ├── verde_mc.bin
│   │   │   ├── verde_me.bin
│   │   │   ├── verde_pfp.bin
│   │   │   ├── verde_rlc.bin
│   │   │   ├── verde_smc.bin
│   │   │   └── verde_uvd.bin
│   │   ├── ar5523.bin
│   │   ├── ath10k
│   │   │   ├── QCA6174
│   │   │   │   ├── hw2.1
│   │   │   │   │   ├── board-2.bin
│   │   │   │   │   ├── board.bin
│   │   │   │   │   └── firmware-5.bin
│   │   │   │   └── hw3.0
│   │   │   │       ├── board-2.bin
│   │   │   │       ├── board.bin
│   │   │   │       ├── firmware-4.bin
│   │   │   │       └── firmware-6.bin
│   │   │   ├── QCA9377
│   │   │   │   └── hw1.0
│   │   │   │       ├── board-2.bin
│   │   │   │       ├── board.bin
│   │   │   │       ├── firmware-5.bin
│   │   │   │       └── firmware-6.bin
│   │   │   ├── QCA9887
│   │   │   │   └── hw1.0
│   │   │   │       ├── board.bin
│   │   │   │       └── firmware-5.bin
│   │   │   └── QCA988X
│   │   │       └── hw2.0
│   │   │           ├── board.bin
│   │   │           ├── firmware-4.bin
│   │   │           └── firmware-5.bin
│   │   ├── ath6k
│   │   │   ├── AR6003
│   │   │   │   ├── hw2.0
│   │   │   │   │   ├── athwlan.bin.z77
│   │   │   │   │   ├── bdata.SD31.bin
│   │   │   │   │   ├── bdata.SD32.bin
│   │   │   │   │   ├── bdata.WB31.bin
│   │   │   │   │   ├── data.patch.bin
│   │   │   │   │   └── otp.bin.z77
│   │   │   │   └── hw2.1.1
│   │   │   │       ├── athwlan.bin
│   │   │   │       ├── bdata.SD31.bin
│   │   │   │       ├── bdata.SD32.bin
│   │   │   │       ├── bdata.WB31.bin
│   │   │   │       ├── data.patch.bin
│   │   │   │       ├── endpointping.bin
│   │   │   │       ├── fw-2.bin
│   │   │   │       ├── fw-3.bin
│   │   │   │       └── otp.bin
│   │   │   └── AR6004
│   │   │       ├── hw1.2
│   │   │       │   ├── bdata.bin
│   │   │       │   └── fw-2.bin
│   │   │       └── hw1.3
│   │   │           ├── bdata.bin
│   │   │           └── fw-3.bin
│   │   ├── ath9k_htc
│   │   │   ├── htc_7010-1.4.0.fw
│   │   │   └── htc_9271-1.4.0.fw
│   │   ├── atmel
│   │   │   └── wilc1000_wifi_firmware-1.bin
│   │   ├── atmel_at76c502_3com.bin
│   │   ├── atmel_at76c502_3com-wpa.bin
│   │   ├── atmel_at76c502.bin
│   │   ├── atmel_at76c502d.bin
│   │   ├── atmel_at76c502d-wpa.bin
│   │   ├── atmel_at76c502e.bin
│   │   ├── atmel_at76c502e-wpa.bin
│   │   ├── atmel_at76c502-wpa.bin
│   │   ├── atmel_at76c503-i3861.bin
│   │   ├── atmel_at76c503-i3863.bin
│   │   ├── atmel_at76c503-rfmd-acc.bin
│   │   ├── atmel_at76c503-rfmd.bin
│   │   ├── atmel_at76c504_2958-wpa.bin
│   │   ├── atmel_at76c504a_2958-wpa.bin
│   │   ├── atmel_at76c504.bin
│   │   ├── atmel_at76c504-wpa.bin
│   │   ├── atmel_at76c505a-rfmd2958.bin
│   │   ├── atmel_at76c505-rfmd2958.bin
│   │   ├── atmel_at76c505-rfmd.bin
│   │   ├── atmel_at76c506.bin
│   │   ├── atmel_at76c506-wpa.bin
│   │   ├── b43
│   │   │   ├── a0g0bsinitvals5.fw
│   │   │   ├── a0g0bsinitvals9.fw
│   │   │   ├── a0g0initvals5.fw
│   │   │   ├── a0g0initvals9.fw
│   │   │   ├── a0g1bsinitvals13.fw
│   │   │   ├── a0g1bsinitvals5.fw
│   │   │   ├── a0g1bsinitvals9.fw
│   │   │   ├── a0g1initvals13.fw
│   │   │   ├── a0g1initvals5.fw
│   │   │   ├── a0g1initvals9.fw
│   │   │   ├── ac0bsinitvals40.fw
│   │   │   ├── ac0initvals40.fw
│   │   │   ├── ac1bsinitvals42.fw
│   │   │   ├── ac1initvals42.fw
│   │   │   ├── ac2bsinitvals41.fw
│   │   │   ├── ac2initvals41.fw
│   │   │   ├── ac3bsinitvals43.fw
│   │   │   ├── ac3initvals43.fw
│   │   │   ├── b0g0bsinitvals13.fw
│   │   │   ├── b0g0bsinitvals5.fw
│   │   │   ├── b0g0bsinitvals9.fw
│   │   │   ├── b0g0initvals13.fw
│   │   │   ├── b0g0initvals5.fw
│   │   │   ├── b0g0initvals9.fw
│   │   │   ├── ht0bsinitvals26.fw
│   │   │   ├── ht0bsinitvals29.fw
│   │   │   ├── ht0initvals26.fw
│   │   │   ├── ht0initvals29.fw
│   │   │   ├── lcn0bsinitvals24.fw
│   │   │   ├── lcn0bsinitvals25.fw
│   │   │   ├── lcn0bsinitvals26.fw
│   │   │   ├── lcn0initvals24.fw
│   │   │   ├── lcn0initvals25.fw
│   │   │   ├── lcn0initvals26.fw
│   │   │   ├── lcn1bsinitvals24.fw
│   │   │   ├── lcn1bsinitvals25.fw
│   │   │   ├── lcn1bsinitvals26.fw
│   │   │   ├── lcn1initvals24.fw
│   │   │   ├── lcn1initvals25.fw
│   │   │   ├── lcn1initvals26.fw
│   │   │   ├── lcn2bsinitvals24.fw
│   │   │   ├── lcn2bsinitvals25.fw
│   │   │   ├── lcn2bsinitvals26.fw
│   │   │   ├── lcn2initvals24.fw
│   │   │   ├── lcn2initvals25.fw
│   │   │   ├── lcn2initvals26.fw
│   │   │   ├── lcn400bsinitvals33.fw
│   │   │   ├── lcn400initvals33.fw
│   │   │   ├── lcn401bsinitvals33.fw
│   │   │   ├── lcn401initvals33.fw
│   │   │   ├── lcn402bsinitvals33.fw
│   │   │   ├── lcn402initvals33.fw
│   │   │   ├── lcn403bsinitvals33.fw
│   │   │   ├── lcn403initvals33.fw
│   │   │   ├── lcn404bsinitvals33.fw
│   │   │   ├── lcn404bsinitvals35.fw
│   │   │   ├── lcn404initvals33.fw
│   │   │   ├── lcn404initvals35.fw
│   │   │   ├── lcn405bsinitvals35.fw
│   │   │   ├── lcn405initvals35.fw
│   │   │   ├── lcn406bsinitvals37.fw
│   │   │   ├── lcn406initvals37.fw
│   │   │   ├── lcn407bsinitvals38.fw
│   │   │   ├── lcn407initvals38.fw
│   │   │   ├── lp0bsinitvals13.fw
│   │   │   ├── lp0bsinitvals14.fw
│   │   │   ├── lp0bsinitvals15.fw
│   │   │   ├── lp0bsinitvals16.fw
│   │   │   ├── lp0initvals13.fw
│   │   │   ├── lp0initvals14.fw
│   │   │   ├── lp0initvals15.fw
│   │   │   ├── lp0initvals16.fw
│   │   │   ├── lp1bsinitvals20.fw
│   │   │   ├── lp1bsinitvals22.fw
│   │   │   ├── lp1initvals20.fw
│   │   │   ├── lp1initvals22.fw
│   │   │   ├── lp2bsinitvals19.fw
│   │   │   ├── lp2initvals19.fw
│   │   │   ├── n0absinitvals11.fw
│   │   │   ├── n0bsinitvals11.fw
│   │   │   ├── n0bsinitvals16.fw
│   │   │   ├── n0bsinitvals17.fw
│   │   │   ├── n0bsinitvals22.fw
│   │   │   ├── n0bsinitvals24.fw
│   │   │   ├── n0bsinitvals25.fw
│   │   │   ├── n0initvals11.fw
│   │   │   ├── n0initvals16.fw
│   │   │   ├── n0initvals17.fw
│   │   │   ├── n0initvals22.fw
│   │   │   ├── n0initvals24.fw
│   │   │   ├── n0initvals25.fw
│   │   │   ├── n16bsinitvals30.fw
│   │   │   ├── n16initvals30.fw
│   │   │   ├── n18bsinitvals32.fw
│   │   │   ├── n18initvals32.fw
│   │   │   ├── n19bsinitvals34.fw
│   │   │   ├── n19initvals34.fw
│   │   │   ├── n1bsinitvals20.fw
│   │   │   ├── n1initvals20.fw
│   │   │   ├── n20bsinitvals36.fw
│   │   │   ├── n20initvals36.fw
│   │   │   ├── n2bsinitvals19.fw
│   │   │   ├── n2initvals19.fw
│   │   │   ├── pcm4.fw
│   │   │   ├── pcm5.fw
│   │   │   ├── sslpn0bsinitvals16.fw
│   │   │   ├── sslpn0initvals16.fw
│   │   │   ├── sslpn1bsinitvals20.fw
│   │   │   ├── sslpn1bsinitvals27.fw
│   │   │   ├── sslpn1initvals20.fw
│   │   │   ├── sslpn1initvals27.fw
│   │   │   ├── sslpn2bsinitvals19.fw
│   │   │   ├── sslpn2initvals19.fw
│   │   │   ├── sslpn3bsinitvals21.fw
│   │   │   ├── sslpn3initvals21.fw
│   │   │   ├── sslpn4bsinitvals22.fw
│   │   │   ├── sslpn4initvals22.fw
│   │   │   ├── ucode11.fw
│   │   │   ├── ucode13.fw
│   │   │   ├── ucode14.fw
│   │   │   ├── ucode15.fw
│   │   │   ├── ucode16_lp.fw
│   │   │   ├── ucode16_mimo.fw
│   │   │   ├── ucode16_sslpn.fw
│   │   │   ├── ucode16_sslpn_nobt.fw
│   │   │   ├── ucode17_mimo.fw
│   │   │   ├── ucode19_sslpn.fw
│   │   │   ├── ucode19_sslpn_nobt.fw
│   │   │   ├── ucode20_sslpn.fw
│   │   │   ├── ucode20_sslpn_nobt.fw
│   │   │   ├── ucode21_sslpn.fw
│   │   │   ├── ucode21_sslpn_nobt.fw
│   │   │   ├── ucode22_mimo.fw
│   │   │   ├── ucode22_sslpn.fw
│   │   │   ├── ucode24_lcn.fw
│   │   │   ├── ucode24_mimo.fw
│   │   │   ├── ucode25_lcn.fw
│   │   │   ├── ucode25_mimo.fw
│   │   │   ├── ucode26_mimo.fw
│   │   │   ├── ucode27_sslpn.fw
│   │   │   ├── ucode29_mimo.fw
│   │   │   ├── ucode30_mimo.fw
│   │   │   ├── ucode32_mimo.fw
│   │   │   ├── ucode33_lcn40.fw
│   │   │   ├── ucode34_mimo.fw
│   │   │   ├── ucode35_lcn40.fw
│   │   │   ├── ucode36_mimo.fw
│   │   │   ├── ucode37_lcn40.fw
│   │   │   ├── ucode38_lcn40.fw
│   │   │   ├── ucode40.fw
│   │   │   ├── ucode41.fw
│   │   │   ├── ucode42.fw
│   │   │   ├── ucode43.fw
│   │   │   ├── ucode5.fw
│   │   │   └── ucode9.fw
│   │   ├── b43legacy
│   │   │   ├── a0g0bsinitvals2.fw
│   │   │   ├── a0g0bsinitvals5.fw
│   │   │   ├── a0g0initvals2.fw
│   │   │   ├── a0g0initvals5.fw
│   │   │   ├── a0g1bsinitvals5.fw
│   │   │   ├── a0g1initvals5.fw
│   │   │   ├── b0g0bsinitvals2.fw
│   │   │   ├── b0g0bsinitvals5.fw
│   │   │   ├── b0g0initvals2.fw
│   │   │   ├── b0g0initvals5.fw
│   │   │   ├── pcm4.fw
│   │   │   ├── pcm5.fw
│   │   │   ├── ucode11.fw
│   │   │   ├── ucode2.fw
│   │   │   ├── ucode4.fw
│   │   │   └── ucode5.fw
│   │   ├── b43-open
│   │   │   ├── b0g0bsinitvals5.fw
│   │   │   ├── b0g0initvals5.fw
│   │   │   └── ucode5.fw
│   │   ├── bnx2
│   │   │   ├── bnx2-rv2p-06-6.0.15.fw
│   │   │   ├── bnx2-rv2p-09-6.0.17.fw
│   │   │   └── bnx2-rv2p-09ax-6.0.17.fw
│   │   ├── brcm
│   │   │   ├── bcm43xx-0.fw
│   │   │   ├── bcm43xx_hdr-0.fw
│   │   │   ├── brcmfmac43143.bin
│   │   │   ├── brcmfmac43236b.bin
│   │   │   ├── brcmfmac43242a.bin
│   │   │   ├── brcmfmac43569.bin
│   │   │   └── brcmfmac4373.bin
│   │   ├── carl9170-1.fw
│   │   ├── cpia2
│   │   │   └── stv0672_vp4.bin
│   │   ├── ctefx.bin
│   │   ├── e100
│   │   │   ├── d101m_ucode.bin
│   │   │   ├── d101s_ucode.bin
│   │   │   └── d102e_ucode.bin
│   │   ├── edgeport
│   │   │   ├── boot2.fw
│   │   │   ├── boot.fw
│   │   │   ├── down2.fw
│   │   │   ├── down3.bin
│   │   │   └── down.fw
│   │   ├── ess
│   │   │   ├── maestro3_assp_kernel.fw
│   │   │   └── maestro3_assp_minisrc.fw
│   │   ├── f2255usb.bin
│   │   ├── i915
│   │   │   ├── bxt_dmc_ver1_07.bin
│   │   │   ├── bxt_guc_33.0.0.bin
│   │   │   ├── bxt_huc_2.0.0.bin
│   │   │   ├── cml_guc_33.0.0.bin
│   │   │   ├── cml_huc_4.0.0.bin
│   │   │   ├── cnl_dmc_ver1_07.bin
│   │   │   ├── ehl_guc_33.0.4.bin
│   │   │   ├── ehl_huc_9.0.0.bin
│   │   │   ├── glk_dmc_ver1_04.bin
│   │   │   ├── glk_guc_33.0.0.bin
│   │   │   ├── glk_huc_4.0.0.bin
│   │   │   ├── icl_dmc_ver1_09.bin
│   │   │   ├── icl_guc_33.0.0.bin
│   │   │   ├── icl_huc_9.0.0.bin
│   │   │   ├── kbl_dmc_ver1_04.bin
│   │   │   ├── kbl_guc_33.0.0.bin
│   │   │   ├── kbl_huc_4.0.0.bin
│   │   │   ├── rkl_dmc_ver2_02.bin
│   │   │   ├── skl_dmc_ver1_27.bin
│   │   │   ├── skl_guc_33.0.0.bin
│   │   │   ├── skl_huc_2.0.0.bin
│   │   │   ├── tgl_dmc_ver2_08.bin
│   │   │   ├── tgl_guc_35.2.0.bin
│   │   │   └── tgl_huc_7.5.0.bin
│   │   ├── intel
│   │   │   ├── dsp_fw_bxtn_v3366.bin
│   │   │   ├── dsp_fw_cnl_v1858.bin
│   │   │   ├── dsp_fw_glk_v3366.bin
│   │   │   ├── dsp_fw_kbl_v3420.bin
│   │   │   ├── dsp_fw_release_v3402.bin
│   │   │   ├── fw_sst_0f28.bin
│   │   │   ├── fw_sst_0f28.bin-48kHz_i2s_master
│   │   │   ├── fw_sst_0f28_ssp0.bin
│   │   │   ├── fw_sst_22a8.bin
│   │   │   ├── IntcSST2.bin
│   │   │   ├── irci_irci_ecr-master_20161208_0213_20170112_1500.bin
│   │   │   ├── sof
│   │   │   │   ├── sof-apl.ri -> v1.5.1/intel-signed/sof-apl-v1.5.1.ri
│   │   │   │   ├── sof-bdw.ri -> v1.5.1/sof-bdw-v1.5.1.ri
│   │   │   │   ├── sof-byt.ri -> v1.5.1/sof-byt-v1.5.1.ri
│   │   │   │   ├── sof-cfl.ri -> v1.5.1/intel-signed/sof-cnl-v1.5.1.ri
│   │   │   │   ├── sof-cht.ri -> v1.5.1/sof-cht-v1.5.1.ri
│   │   │   │   ├── sof-cml.ri -> v1.5.1/intel-signed/sof-cnl-v1.5.1.ri
│   │   │   │   ├── sof-cnl.ri -> v1.5.1/intel-signed/sof-cnl-v1.5.1.ri
│   │   │   │   ├── sof-glk.ri -> v1.5.1/intel-signed/sof-apl-v1.5.1.ri
│   │   │   │   ├── sof-icl.ri -> v1.5.1/intel-signed/sof-icl-v1.5.1.ri
│   │   │   │   └── v1.5.1
│   │   │   │       ├── intel-signed
│   │   │   │       │   ├── sof-apl-v1.5.1.ri
│   │   │   │       │   ├── sof-cnl-v1.5.1.ri
│   │   │   │       │   └── sof-icl-v1.5.1.ri
│   │   │   │       ├── public-signed
│   │   │   │       │   ├── sof-apl-v1.5.1.ri
│   │   │   │       │   ├── sof-cnl-v1.5.1.ri
│   │   │   │       │   └── sof-icl-v1.5.1.ri
│   │   │   │       ├── sof-apl-v1.5.1.ldc
│   │   │   │       ├── sof-bdw-v1.5.1.ldc
│   │   │   │       ├── sof-bdw-v1.5.1.ri
│   │   │   │       ├── sof-byt-v1.5.1.ldc
│   │   │   │       ├── sof-byt-v1.5.1.ri
│   │   │   │       ├── sof-cht-v1.5.1.ldc
│   │   │   │       ├── sof-cht-v1.5.1.ri
│   │   │   │       ├── sof-cnl-v1.5.1.ldc
│   │   │   │       └── sof-icl-v1.5.1.ldc
│   │   │   ├── sof-tplg -> sof-tplg-v1.5.1
│   │   │   └── sof-tplg-v1.5.1
│   │   │       ├── sof-apl-asrc-pcm512x.tplg
│   │   │       ├── sof-apl-asrc-wm8804.tplg
│   │   │       ├── sof-apl-da7219.tplg
│   │   │       ├── sof-apl-demux-pcm512x.tplg
│   │   │       ├── sof-apl-dmic-2ch.tplg
│   │   │       ├── sof-apl-dmic-4ch.tplg
│   │   │       ├── sof-apl-dmic-a2ch-b2ch.tplg
│   │   │       ├── sof-apl-dmic-a2ch-b4ch.tplg
│   │   │       ├── sof-apl-dmic-a4ch-b2ch.tplg
│   │   │       ├── sof-apl-dmic-a96k-b16k.tplg
│   │   │       ├── sof-apl-eq-dmic.tplg
│   │   │       ├── sof-apl-eq-pcm512x.tplg
│   │   │       ├── sof-apl-keyword-detect.tplg
│   │   │       ├── sof-apl-nocodec.tplg
│   │   │       ├── sof-apl-pcm512x-master-44100.tplg
│   │   │       ├── sof-apl-pcm512x-master.tplg
│   │   │       ├── sof-apl-pcm512x-nohdmi.tplg
│   │   │       ├── sof-apl-pcm512x.tplg
│   │   │       ├── sof-apl-rt298.tplg
│   │   │       ├── sof-apl-src-50khz-pcm512x.tplg
│   │   │       ├── sof-apl-src-dmic.tplg
│   │   │       ├── sof-apl-src-pcm512x.tplg
│   │   │       ├── sof-apl-tdf8532.tplg
│   │   │       ├── sof-apl-wm8804.tplg
│   │   │       ├── sof-bdw-nocodec.tplg
│   │   │       ├── sof-bdw-rt286.tplg
│   │   │       ├── sof-bdw-rt5640.tplg
│   │   │       ├── sof-bdw-rt5677.tplg
│   │   │       ├── sof-byt-cx2072x-ssp0.tplg
│   │   │       ├── sof-byt-cx2072x.tplg
│   │   │       ├── sof-byt-da7213-ssp0.tplg
│   │   │       ├── sof-byt-da7213.tplg
│   │   │       ├── sof-byt-es8316-ssp0.tplg
│   │   │       ├── sof-byt-es8316.tplg
│   │   │       ├── sof-byt-nocodec.tplg
│   │   │       ├── sof-byt-rt5640-ssp0.tplg
│   │   │       ├── sof-byt-rt5640.tplg
│   │   │       ├── sof-byt-rt5645-ssp0.tplg
│   │   │       ├── sof-byt-rt5645.tplg
│   │   │       ├── sof-byt-rt5651-ssp0.tplg
│   │   │       ├── sof-byt-rt5651.tplg
│   │   │       ├── sof-byt-rt5670-ssp0.tplg
│   │   │       ├── sof-byt-rt5670.tplg
│   │   │       ├── sof-byt-rt5682-ssp0.tplg
│   │   │       ├── sof-byt-rt5682.tplg
│   │   │       ├── sof-cht-cx2072x.tplg
│   │   │       ├── sof-cht-da7213.tplg
│   │   │       ├── sof-cht-es8316.tplg
│   │   │       ├── sof-cht-max98090.tplg
│   │   │       ├── sof-cht-nocodec.tplg
│   │   │       ├── sof-cht-rt5640.tplg
│��  │   │       ├── sof-cht-rt5645.tplg
│   │   │       ├── sof-cht-rt5651.tplg
│   │   │       ├── sof-cht-rt5670.tplg
│   │   │       ├── sof-cht-rt5682.tplg
│   │   │       ├── sof-cht-src-50khz-pcm512x.tplg
│   │   │       ├── sof-cml-da7219-max98357a.tplg
│   │   │       ├── sof-cml-demux-rt5682-max98357a.tplg
│   │   │       ├── sof-cml-demux-rt5682.tplg
│   │   │       ├── sof-cml-eq-fir-loud-rt5682.tplg
│   │   │       ├── sof-cml-eq-fir-rt5682.tplg
│   │   │       ├── sof-cml-eq-iir-rt5682.tplg
│   │   │       ├── sof-cml-eq-rt1011-rt5682.tplg
│   │   │       ├── sof-cml-rt1011-rt5682.tplg
│   │   │       ├── sof-cml-rt5682-kwd.tplg
│   │   │       ├── sof-cml-rt5682-max98357a.tplg
│   │   │       ├── sof-cml-rt5682.tplg
│   │   │       ├── sof-cml-rt700.tplg
│   │   │       ├── sof-cml-rt711-rt1308-mono-rt715.tplg
│   │   │       ├── sof-cml-rt711-rt1308-rt715.tplg
│   │   │       ├── sof-cml-src-rt5682.tplg
│   │   │       ├── sof-cnl-nocodec.tplg
│   │   │       ├── sof-cnl-rt274.tplg
│   │   │       ├── sof-ehl-nocodec.tplg
│   │   │       ├── sof-ehl-rt5660-nohdmi.tplg
│   │   │       ├── sof-ehl-rt5660.tplg
│   │   │       ├── sof-glk-da7219-kwd.tplg
│   │   │       ├── sof-glk-da7219.tplg
│   │   │       ├── sof-glk-eq-da7219.tplg
│   │   │       ├── sof-glk-rt5682.tplg
│   │   │       ├── sof-hda-asrc-2ch.tplg
│   │   │       ├── sof-hda-generic-2ch-kwd.tplg
│   │   │       ├── sof-hda-generic-2ch.tplg
│   │   │       ├── sof-hda-generic-4ch-kwd.tplg
│   │   │       ├── sof-hda-generic-4ch.tplg
│   │   │       ├── sof-hda-generic-eq-2ch.tplg
│   │   │       ├── sof-hda-generic-eq-4ch.tplg
│   │   │       ├── sof-hda-generic-idisp-2ch.tplg
│   │   │       ├── sof-hda-generic-idisp-4ch.tplg
│   │   │       ├── sof-hda-generic-idisp.tplg
│   │   │       ├── sof-hda-generic.tplg
│   │   │       ├── sof-icl-dmic-4ch.tplg
│   │   │       ├── sof-icl-nocodec.tplg
│   │   │       ├── sof-icl-rt5682-kwd.tplg
│   │   │       ├── sof-icl-rt5682.tplg
│   │   │       ├── sof-icl-rt700.tplg
│   │   │       ├── sof-icl-rt711-rt1308-rt715-hdmi.tplg
│   │   │       ├── sof-icl-rt711-rt1308-rt715.tplg
│   │   │       ├── sof-imx8mp-wm8960.tplg
│   │   │       ├── sof-imx8qxp-cs42888.tplg
│   │   │       ├── sof-imx8qxp-nocodec-sai.tplg
│   │   │       ├── sof-imx8qxp-nocodec.tplg
│   │   │       ├── sof-imx8qxp-wm8960.tplg
│   │   │       ├── sof-jsl-da7219-mx98360a.tplg
│   │   │       ├── sof-jsl-da7219.tplg
│   │   │       ├── sof-tgl-max98357a-rt5682.tplg
│   │   │       ├── sof-tgl-max98373-rt5682.tplg
│   │   │       ├── sof-tgl-nocodec.tplg
│   │   │       ├── sof-tgl-rt5682.tplg
│   │   │       ├── sof-tgl-rt711-i2s-rt1308-2ch.tplg
│   │   │       ├── sof-tgl-rt711-i2s-rt1308-4ch.tplg
│   │   │       ├── sof-tgl-rt711-i2s-rt1308-nohdmi.tplg
│   │   │       ├── sof-tgl-rt711-rt1308.tplg
│   │   │       ├── sof-whl-demux-rt5682.tplg
│   │   │       ├── sof-whl-rt5682-kwd.tplg
│   │ �� │       └── sof-whl-rt5682.tplg
│   │   ├── ipw2100-1.3.fw
│   │   ├── ipw2100-1.3-i.fw
│   │   ├── ipw2200-bss.fw
│   │   ├── ipw2200-ibss.fw
│   │   ├── iwlwifi-1000-5.ucode
│   │   ├── iwlwifi-100-5.ucode
│   │   ├── iwlwifi-105-6.ucode
│   │   ├── iwlwifi-135-6.ucode
│   │   ├── iwlwifi-2000-6.ucode
│   │   ├── iwlwifi-2030-6.ucode
│   │   ├── iwlwifi-3160-17.ucode
│   │   ├── iwlwifi-3168-29.ucode
│   │   ├── iwlwifi-3945-2.ucode
│   │   ├── iwlwifi-4965-2.ucode
│   │   ├── iwlwifi-5000-5.ucode
│   │   ├── iwlwifi-5150-2.ucode
│   │   ├── iwlwifi-6000-4.ucode
│   │   ├── iwlwifi-6000g2a-6.ucode
│   │   ├── iwlwifi-6000g2b-6.ucode
│   │   ├── iwlwifi-6050-5.ucode
│   │   ├── iwlwifi-7260-17.ucode
│   │   ├── iwlwifi-7265-17.ucode
│   │   ├── iwlwifi-7265D-29.ucode
│   │   ├── iwlwifi-8000C-36.ucode
│   │   ├── iwlwifi-8265-36.ucode
│   │   ├── iwlwifi-9000-pu-b0-jf-b0-46.ucode
│   │   ├── iwlwifi-9260-th-b0-jf-b0-46.ucode
│   │   ├── iwlwifi-cc-a0-59.ucode
│   │   ├── iwlwifi-Qu-b0-hr-b0-59.ucode
│   │   ├── iwlwifi-Qu-b0-jf-b0-59.ucode
│   │   ├── iwlwifi-Qu-c0-hr-b0-59.ucode
│   │   ├── iwlwifi-Qu-c0-jf-b0-59.ucode
│   │   ├── iwlwifi-QuZ-a0-hr-b0-59.ucode
│   │   ├── iwlwifi-QuZ-a0-jf-b0-59.ucode
│   │   ├── iwlwifi-ty-a0-gf-a0-59.ucode
│   │   ├── kaweth
│   │   │   ├── new_code.bin
│   │   │   ├── new_code_fix.bin
│   │   │   ├── trigger_code.bin
│   │   │   └── trigger_code_fix.bin
│   │   ├── keyspan
│   │   │   ├── mpr.fw
│   │   │   ├── usa18x.fw
│   │   │   ├── usa19.fw
│   │   │   ├── usa19qi.fw
│   │   │   ├── usa19qw.fw
│   │   │   ├── usa19w.fw
│   │   │   ├── usa28.fw
│   │   │   ├── usa28xa.fw
│   │   │   ├── usa28xb.fw
│   │   │   ├── usa28x.fw
│   │   │   ├── usa49w.fw
│   │   │   └── usa49wlc.fw
│   │   ├── keyspan_pda
│   │   │   ├── keyspan_pda.fw
│   │   │   └── xircom_pgs.fw
│   │   ├── korg
│   │   │   └── k1212.dsp
│   │   ├── lbtf_usb.bin
│   │   ├── libertas
│   │   │   ├── gspi8686.bin -> gspi8686_v9.bin
│   │   │   ├── gspi8686_hlp.bin -> gspi8686_v9_helper.bin
│   │   │   ├── gspi8686_v9.bin
│   │   │   ├── gspi8686_v9_helper.bin
│   │   │   ├── gspi8688.bin
│   │   │   ├── gspi8688_helper.bin
│   │   │   ├── sd8385.bin
│   │   │   ├── sd8385_helper.bin
│   │   │   ├── sd8686_v8.bin
│   │   │   ├── sd8686_v8_helper.bin
│   │   │   ├── sd8686_v9.bin
│   │   │   ├── sd8686_v9_helper.bin
│   │   │   ├── sd8688.bin -> ../mrvl/sd8688.bin
│   │   │   ├── sd8688_helper.bin -> ../mrvl/sd8688_helper.bin
│   │   │   ├── usb8388.bin -> usb8388_v5.bin
│   │   │   ├── usb8388_v5.bin
│   │   │   ├── usb8388_v9.bin
│   │   │   └── usb8682.bin
│   │   ├── LICENCE.agere
│   │   ├── LICENCE.atheros_firmware
│   │   ├── LICENCE.broadcom_bcm43xx
│   │   ├── LICENCE.iwlwifi_firmware
│   │   ├── LICENCE.Marvell
���   │   ├── LICENCE.nvidia
│   │   ├── LICENCE.open-ath9k-htc-firmware
│   │   ├── LICENCE.ralink-firmware.txt
│   │   ├── LICENCE.rtlwifi_firmware.txt
│   │   ├── LICENSE.amdgpu
│   │   ├── LICENSE.amd-ucode
│   │   ├── LICENSE.atmel
│   │   ├── LICENSE.i915
│   │   ├── LICENSE.intel-ucode
│   │   ├── LICENSE.ipw2100-fw-1.3
│   │   ├── LICENSE.ipw2200-fw
│   │   ├── LICENSE.QualcommAtheros_ath10k
│   │   ├── LICENSE.radeon
│   │   ├── matrox
│   │   │   ├── g200_warp.fw
│   │   │   └── g400_warp.fw
│   │   ├── mediatek
│   │   │   ├── mt7610e.bin
│   │   │   ├── mt7610u.bin
│   │   │   ├── mt7615_cr4.bin
│   │   │   ├── mt7615_n9.bin
│   │   │   ├── mt7615_rom_patch.bin
│   │   │   ├── mt7650e.bin
│   │   │   ├── mt7662u.bin
│   │   │   ├── mt7662u_rom_patch.bin
│   │   │   ├── mt7663_n9_rebb.bin
│   │   │   ├── mt7663_n9_v3.bin
│   │   │   ├── mt7663pr2h.bin
│   │   │   ├── mt7663pr2h_rebb.bin
│   │   │   ├── mt7915_rom_patch.bin
│   │   │   ├── mt7915_wa.bin
│   │   │   └── mt7915_wm.bin
│   │   ├── moxa
│   │   │   ├── moxa-1110.fw
│   │   │   ├── moxa-1130.fw
│   │   │   ├── moxa-1131.fw
│   │   │   ├── moxa-1150.fw
│   │   │   └── moxa-1151.fw
│   │   ├── mrvl
│   │   │   ├── pcie8897_uapsta.bin
│   │   │   ├── sd8688.bin
│   │   │   ├── sd8688_helper.bin
│   │   │   ├── sd8897_uapsta.bin
│   │   │   └── usb8797_uapsta.bin
│   │   ├── mt7601u.bin
│   │   ├── mt7662.bin
│   │   ├── mt7662_rom_patch.bin
│   │   ├── mts_cdma.fw
│   │   ├── mts_edge.fw
│   │   ├── mts_gsm.fw
│   │   ├── mts_mt9234mu.fw
│   │   ├── mts_mt9234zba.fw
│   │   ├── mwl8k
│   │   │   ├── fmimage_8363.fw
│   │   │   ├── fmimage_8366_ap-3.fw
│   │   │   ├── fmimage_8366.fw
│   │   │   ├── fmimage_8687.fw
│   │   │   ├── helper_8363.fw
│   │   │   ├── helper_8366.fw
│   │   │   └── helper_8687.fw
│   │   ├── nvidia
│   │   │   ├── gk20a
│   │   │   │   ├── fecs_data.bin
│   │   │   │   ├── fecs_inst.bin
│   │   │   │   ├── gpccs_data.bin
│   │   │   │   ├── gpccs_inst.bin
│   │   │   │   ├── sw_bundle_init.bin
│   │   │   │   ├── sw_ctx.bin
│   │   │   │   ├── sw_method_init.bin
│   │   │   │   └── sw_nonctx.bin
│   │   │   ├── gm200
│   │   │   │   ├── acr
│   │   │   │   │   ├── bl.bin
│   │   │   │   │   ├── ucode_load.bin
│   │   │   │   │   └── ucode_unload.bin
│   │   │   │   └── gr
│   │   │   │       ├── fecs_bl.bin
│   │   │   │       ├── fecs_data.bin
│   │   │   │       ├── fecs_inst.bin
│   │   │   │       ├── fecs_sig.bin
│   │   │   │       ├── gpccs_bl.bin
│   │   │   │       ├── gpccs_data.bin
│   │   │   │       ├── gpccs_inst.bin
│   │   │   │       ├── gpccs_sig.bin
│   │   │   │       ├── sw_bundle_init.bin
│   │   │   │       ├── sw_ctx.bin
│   │   │   │       ├── sw_method_init.bin
│   │   │   │       └── sw_nonctx.bin
│   │   │   ├── gm204
│   │   │   │   └── gr
│   │   │   │       ├── fecs_data.bin
│   │   │   │       ├── fecs_sig.bin
│   │   │   │       ├── gpccs_data.bin
│   │   │   │       └── gpccs_sig.bin
│   │   │   ├── gm206
│   │   │   │   ├── acr
│   │   │   │   │   ├── ucode_load.bin
│   │   │   │   │   └── ucode_unload.bin
│   │   │   │   └── gr
│   │   │   │       ├── fecs_data.bin
│   │   │   │       ├── fecs_sig.bin
│   │   │   │       ├── gpccs_data.bin
│   │   │   │       └── gpccs_sig.bin
│   │   │   ├── gm20b
│   │   │   │   ├── acr
│   │   │   │   │   ├── bl.bin
│   │   │   │   │   └── ucode_load.bin
│   │   │   │   ├── gr
│   │   │   │   │   ├── fecs_bl.bin
│   │   │   │   │   ├── fecs_data.bin
│   │   │   │   │   ├── fecs_inst.bin
│   │   │   │   │   ├── fecs_sig.bin
│   │   │   │   │   ├── gpccs_data.bin
│   │   │   │   │   ├── gpccs_inst.bin
│   │   │   │   │   ├── sw_bundle_init.bin
│   │   │   │   │   ├── sw_ctx.bin
│   │   │   │   │   └── sw_nonctx.bin
│   │   │   │   └── pmu
│   │   │   │       ├── desc.bin
│   │   │   │       ├── image.bin
│   │   │   │       └── sig.bin
│   │   │   ├── gp100
│   │   │   │   ├── acr
│   │   │   │   │   ├── bl.bin
│   │   │   │   │   ├── ucode_load.bin
│   │   │   │   │   └── ucode_unload.bin
│   │   │   │   └── gr
│   │   │   │       ├── fecs_data.bin
│   │   │   │       ├── fecs_inst.bin
│   │   │   │       ├── fecs_sig.bin
│   │   │   │       ├── gpccs_data.bin
│   │   │   │       ├── gpccs_inst.bin
│   │   │   │       ├── gpccs_sig.bin
│   │   │   │       ├── sw_bundle_init.bin
│   │   │   │       ├── sw_ctx.bin
│   │   │   │       ├── sw_method_init.bin
│   │   │   │       └── sw_nonctx.bin
│   │   │   ├── gp102
│   │   │   │   ├── acr
│   │   │   │   │   ├── bl.bin
│   │   │   │   │   ├── ucode_load.bin
│   │   │   │   │   ├── ucode_unload.bin
│   │   │   │   │   └── unload_bl.bin
│   │   │   │   ├── gr
│   │   │   │   │   ├── fecs_data.bin
│   │   │   │   │   ├── fecs_inst.bin
│   │   │   │   │   ├── fecs_sig.bin
│   │   │   │   │   ├── gpccs_data.bin
│   │   │   │   │   ├── gpccs_inst.bin
│   │   │   │   │   ├── gpccs_sig.bin
│   │   │   │   │   ├── sw_bundle_init.bin
│   │   │   │   │   ├── sw_ctx.bin
│   │   │   │   │   ├── sw_method_init.bin
│   │   │   │   │   └── sw_nonctx.bin
│   ��   │   │   ├── nvdec
│   │   │   │   │   └── scrubber.bin
│   │   │   │   └── sec2
│   │   │   │       ├── desc-1.bin
│   │   │   │       ├── desc.bin
│   │   │   │       ├── image-1.bin
│   │   │   │       ├── image.bin
│   │   │   │       ├── sig-1.bin
│   │   │   │       └── sig.bin
│   │   │   ├── gp104
│   │   │   │   └── gr
│   │   │   │       ├── fecs_data.bin
│   │   │   │       ├── fecs_inst.bin
│   │   │   │       ├── fecs_sig.bin
│   │   │   │       ├── gpccs_data.bin
│   │   │   │       ├── gpccs_inst.bin
│   │   │   │       └── gpccs_sig.bin
│   │   │   ├── gp106
│   │   │   │   └── gr
│   │   │   │       ├── fecs_data.bin
│   │   │   │       ├── fecs_sig.bin
│   │   │   │       ├── gpccs_data.bin
│   │   │   │       └── gpccs_sig.bin
│   │   │   ├── gp107
│   │   │   │   └── gr
│   │   │   │       ├── fecs_bl.bin
│   │   │   │       ├── fecs_data.bin
│   │   │   │       ├── fecs_inst.bin
│   │   │   │       ├── fecs_sig.bin
│   │   │   │       ├── gpccs_bl.bin
│   │   │   │       ├── gpccs_data.bin
│   │   │   │       ├── gpccs_inst.bin
│   │   │   │       ├── gpccs_sig.bin
│   │   │   │       ├── sw_ctx.bin
│   │   │   │       └── sw_nonctx.bin
│   │   │   ├── gp108
│   │   │   │   └── gr
│   │   │   │       ├── fecs_bl.bin
│   │   │   │       ├── fecs_data.bin
│   │   │   │       ├── fecs_inst.bin
│   │   │   │       ├── fecs_sig.bin
│   │   │   │       ├── gpccs_bl.bin
│   │   │   │       ├── gpccs_data.bin
│   │   │   │       ├── gpccs_inst.bin
│   │   │   │       ├── gpccs_sig.bin
│   │   │   │       ├── sw_bundle_init.bin
│   │   │   │       ├── sw_ctx.bin
│   │   │   │       ├── sw_method_init.bin
│   │   │   │       └── sw_nonctx.bin
│   │   │   ├── gp10b
│   │   │   │   ├── acr
│   │   │   │   │   ├── bl.bin
│   │   │   │   │   └── ucode_load.bin
│   │   │   │   ├── gr
│   │   │   │   │   ├── fecs_bl.bin
│   │   │   │   │   ├── fecs_data.bin
│   │   │   │   │   ├── fecs_inst.bin
│   │   │   │   │   ├── fecs_sig.bin
│   │   │   │   │   ├── gpccs_bl.bin
│   │   │   │   │   ├── gpccs_data.bin
│   │   │   │   │   ├── gpccs_inst.bin
│   │   │   │   │   ├── gpccs_sig.bin
│   │   │   │   │   ├── sw_bundle_init.bin
│   │   │   │   │   ├── sw_ctx.bin
│   │   │   │   │   ├── sw_method_init.bin
│   │   │   │   │   └── sw_nonctx.bin
│   │   │   │   └── pmu
│   │   │   │       ├── desc.bin
│   │   │   │       ├── image.bin
│   │   │   │       └── sig.bin
│   │   │   ├── gv100
│   │   │   │   ├── acr
│   │   │   │��  │   ├── bl.bin
│   │   │   │   │   ├── ucode_load.bin
│   │   │   │   │   ├── ucode_unload.bin
│   │   │   │   │   └── unload_bl.bin
│   │   │   │   ├── gr
│   │   │   │   │   ├── fecs_bl.bin
│   │   │   │   │   ├── fecs_data.bin
│   │   │   │   │   ├── fecs_inst.bin
│   │   │   │   │   ├── fecs_sig.bin
│   │   │   │   │   ├── gpccs_bl.bin
│   │   │   │   │   ├── gpccs_data.bin
│   │   │   │   │   ├── gpccs_inst.bin
│   │   │   │   │   ├── gpccs_sig.bin
│   │   │   │   │   ├── sw_bundle_init.bin
│   │   │   │   │   ├── sw_ctx.bin
│   │   │   │   │   ├── sw_method_init.bin
│   │   │   │   │   └── sw_nonctx.bin
│   │   │   │   ├── nvdec
│   │   │   │   │   └── scrubber.bin
│   │   │   │   └── sec2
│   │   │   │       ├── desc.bin
│   │   │   │       ├── image.bin
│   │   │   │       └── sig.bin
│   │   │   ├── tu102
│   │   │   │   ├── acr
│   │   │   │   │   ├── bl.bin
│   │   │   │   │   ├── ucode_ahesasc.bin
│   │   │   │   │   ├── ucode_asb.bin
│   │   │   │   │   ├── ucode_unload.bin
│   │   │   │   │   └── unload_bl.bin
│   │   │   │   ├── gr
│   │   │   │   │   ├── fecs_bl.bin
│   │   │   │   │   ├── fecs_data.bin
│   │   │   │   │   ├── fecs_inst.bin
│   │   │   │   │   ├── fecs_sig.bin
│   │   │   │   │   ├── gpccs_bl.bin
│   │   │   │   │   ├── gpccs_data.bin
│   │   │   │   │   ├── gpccs_inst.bin
│   │   │   │   │   ├── gpccs_sig.bin
│   │   │   │   │   ├── sw_bundle_init.bin
│   │   │   │   │   ├── sw_ctx.bin
│   │   │   │   │   ├── sw_method_init.bin
│   │   │   │   │   ├── sw_nonctx.bin
│   │   │   │   │   └── sw_veid_bundle_init.bin
│   │   │   │   ├── nvdec
│   │   │   │   │   └── scrubber.bin
│   │   │   │   └── sec2
│   │   │   │       ├── desc.bin
│   │   │   │       ├── image.bin
│   │   │   │       └── sig.bin
│   │   │   ├── tu104
│   │   │   │   └── gr
│   │   │   │       ├── fecs_data.bin
│   │   │   │       ├── fecs_inst.bin
│   │   │   │       ├── fecs_sig.bin
│   │   │   │       ├── gpccs_data.bin
│   │   │   │       ├── gpccs_inst.bin
│   │   │   │       ├── gpccs_sig.bin
│   │   │   │       ├── sw_bundle_init.bin
│   │   │   │       ├── sw_ctx.bin
│   │   │   │       ├── sw_method_init.bin
│   │   │   │       ├── sw_nonctx.bin
│   │   │   │       └── sw_veid_bundle_init.bin
│   │   │   ├── tu106
│   │   │   │   └── gr
│   │   │   │       ├── fecs_data.bin
│   │   │   │       ├── fecs_inst.bin
│   │   │   │       ├── fecs_sig.bin
│   │   │   │       ├── gpccs_data.bin
│   │   │   │       ├── gpccs_inst.bin
│   │   │   │       ├── gpccs_sig.bin
│   │   │   │       ├── sw_bundle_init.bin
│   │   │   │       ├── sw_ctx.bin
│   │   │   │       ├── sw_method_init.bin
│   │   │   │       ├── sw_nonctx.bin
│   │   │   │       └── sw_veid_bundle_init.bin
│   │   │   ├── tu10x
│   │   │   │   └── typec
│   │   │   │       ├── ccg_boot.cyacd
│   │   │   │       ├── ccg_primary.cyacd
│   │   │   │       └── ccg_secondary.cyacd
│   │   │   ├── tu116
│   │   │   │   ├── acr
│   │   │   │   │   ├── bl.bin
│   │   │   │   │   ├── ucode_ahesasc.bin
│   │   │   │   │   ├── ucode_asb.bin
│   │   │   │   │   ├── ucode_unload.bin
│   │   │   │   │   └── unload_bl.bin
│   │   │   │   ├── gr
│   │   │   │   │   ├── fecs_bl.bin
│   │   │   │   │   ├── fecs_data.bin
│   │   │   │   │   ├── fecs_inst.bin
│   │   │   │   │   ├── fecs_sig.bin
│   │   │   │   │   ├── gpccs_bl.bin
│   │   │   │   │   ├── gpccs_data.bin
│   │   │   │   │   ├── gpccs_inst.bin
│   │   │   │   │   ├── gpccs_sig.bin
│   │   │   │   │   ├── sw_bundle_init.bin
│   │   │   │   │   ├── sw_ctx.bin
│   │   │   │   │   ├── sw_method_init.bin
│   │   │   │   │   ├── sw_nonctx.bin
│   │   │   │   │   └── sw_veid_bundle_init.bin
│   │   │   │   ├── nvdec
│   │   │   │   │   └── scrubber.bin
│   │   │   │   └── sec2
│   │   │   │       ├── desc.bin
│   │   │   │       ├── image.bin
│   │   │   │       └── sig.bin
│   │   │   └── tu117
│   │   │       └── gr
│   │   │           ├── fecs_data.bin
│   │   │           ├── fecs_inst.bin
│   │   │           ├── fecs_sig.bin
│   │   │           ├── gpccs_data.bin
│   │   │           ├── gpccs_inst.bin
│   │   │           ├── gpccs_sig.bin
│   │   │           ├── sw_bundle_init.bin
│   │   │           ├── sw_ctx.bin
│   │   │           ├── sw_method_init.bin
│   │   │           ├── sw_nonctx.bin
│   │   │           └── sw_veid_bundle_init.bin
│   │   ├── r128
│   │   │   └── r128_cce.bin
│   │   ├── radeon
│   │   │   ├── ARUBA_me.bin
│   │   │   ├── ARUBA_pfp.bin
│   │   │   ├── ARUBA_rlc.bin
│   │   │   ├── banks_k_2_smc.bin
│   │   │   ├── BARTS_mc.bin
│   │   │   ├── BARTS_me.bin
│   │   │   ├── BARTS_pfp.bin
│   │   │   ├── BARTS_smc.bin
│   │   │   ├── bonaire_ce.bin
│   │   │   ├── BONAIRE_ce.bin
│   │   │   ├── bonaire_k_smc.bin
│   │   │   ├── BONAIRE_mc2.bin
│   │   │   ├── bonaire_mc.bin
│   │   │   ├── BONAIRE_mc.bin
│   │   │   ├── bonaire_me.bin
│   │   │   ├── BONAIRE_me.bin
│   │   │   ├── bonaire_mec.bin
│   │   │   ├── BONAIRE_mec.bin
│   │   │   ├── bonaire_pfp.bin
│   │   │   ├── BONAIRE_pfp.bin
│   │   │   ├── bonaire_rlc.bin
│   │   │   ├── BONAIRE_rlc.bin
│   │   │   ├── bonaire_sdma1.bin
│   │   │   ├── bonaire_sdma.bin
│   │   │   ├── BONAIRE_sdma.bin
│   │   │   ├── bonaire_smc.bin
│   │   │   ├── BONAIRE_smc.bin
│   │   │   ├── bonaire_uvd.bin
│   │   │   ├── BONAIRE_uvd.bin
│   │   │   ├── bonaire_vce.bin
│   │   │   ├── BONAIRE_vce.bin
│   │   │   ├── BTC_rlc.bin
│   │   │   ├── CAICOS_mc.bin
│   │   │   ├── CAICOS_me.bin
│   │   │   ├── CAICOS_pfp.bin
│   │   │   ├── CAICOS_smc.bin
│   │   │   ├── CAYMAN_mc.bin
│   │   │   ├── CAYMAN_me.bin
│   │   │   ├── CAYMAN_pfp.bin
│   │   │   ├── CAYMAN_rlc.bin
│   │   │   ├── CAYMAN_smc.bin
│   │   │   ├── CEDAR_me.bin
│   │   │   ├── CEDAR_pfp.bin
│   │   │   ├── CEDAR_rlc.bin
│   │   │   ├── CEDAR_smc.bin
│   │   │   ├── CYPRESS_me.bin
│   │   │   ├── CYPRESS_pfp.bin
│   │   │   ├── CYPRESS_rlc.bin
│   │   │   ├── CYPRESS_smc.bin
│   │   │   ├── CYPRESS_uvd.bin
│   │   │   ├── hainan_ce.bin
│   │   │   ├── HAINAN_ce.bin
│   │   │   ├── hainan_k_smc.bin
│   │   │   ├── HAINAN_mc2.bin
│   │   │   ├── hainan_mc.bin
│   │   │   ├── HAINAN_mc.bin
│   │   │   ├── hainan_me.bin
│   │   │   ├── HAINAN_me.bin
│   │   │   ├── hainan_pfp.bin
│   │   │   ├── HAINAN_pfp.bin
│   │   │   ├── hainan_rlc.bin
│   │   │   ├── HAINAN_rlc.bin
│   │   │   ├── hainan_smc.bin
│   │   │   ├── HAINAN_smc.bin
│   │   │   ├── hawaii_ce.bin
│   │   │   ├── HAWAII_ce.bin
│   │   │   ├── hawaii_k_smc.bin
│   │   │   ├── HAWAII_mc2.bin
│   │   │   ├── hawaii_mc.bin
│   │   │   ├── HAWAII_mc.bin
│   │   │   ├── hawaii_me.bin
│   │   │   ├── HAWAII_me.bin
│   │   │   ├── hawaii_mec.bin
│   │   │   ├── HAWAII_mec.bin
│   │   │   ├── hawaii_pfp.bin
│   │   │   ├── HAWAII_pfp.bin
│   │   │   ├── hawaii_rlc.bin
│   │   │   ├── HAWAII_rlc.bin
│   │   │   ├── hawaii_sdma1.bin
│   │   │   ├── hawaii_sdma.bin
│   │   │   ├── HAWAII_sdma.bin
│   │   │   ├── hawaii_smc.bin
│   │   │   ├── HAWAII_smc.bin
│   │   │   ├── hawaii_uvd.bin
│   │   │   ├── hawaii_vce.bin
│   │   │   ├── JUNIPER_me.bin
│   │   │   ├── JUNIPER_pfp.bin
│   │   │   ├── JUNIPER_rlc.bin
│   │   │   ├── JUNIPER_smc.bin
│   │   │   ├── kabini_ce.bin
│   │   │   ├── KABINI_ce.bin
│   │   │   ├── kabini_me.bin
│   │   │   ├── KABINI_me.bin
│   │   │   ├── kabini_mec.bin
│   │   │   ├── KABINI_mec.bin
│   │   │   ├── kabini_pfp.bin
│   │   │   ├── KABINI_pfp.bin
│   │   │   ├── kabini_rlc.bin
│   │   │   ├── KABINI_rlc.bin
│   │   │   ├── kabini_sdma1.bin
│   │   │   ├── kabini_sdma.bin
│   │   │   ├── KABINI_sdma.bin
│   │   │   ├── kabini_uvd.bin
│   │   │   ├── kabini_vce.bin
│   │   │   ├── kaveri_ce.bin
│   │   │   ├── KAVERI_ce.bin
│   │   │   ├── kaveri_me.bin
│   │   │   ├── KAVERI_me.bin
│   │   │   ├── kaveri_mec2.bin
│   │   │   ├── kaveri_mec.bin
│   │   │   ├── KAVERI_mec.bin
│   │   │   ├── kaveri_pfp.bin
│   │   │   ├── KAVERI_pfp.bin
│   │   │   ├── kaveri_rlc.bin
│   │   │   ├── KAVERI_rlc.bin
│   │   │   ├── kaveri_sdma1.bin
│   │   │   ├── kaveri_sdma.bin
│   │   │   ├── KAVERI_sdma.bin
│   │   │   ├── kaveri_uvd.bin
│   │   │   ├── kaveri_vce.bin
│   │   │   ├── mullins_ce.bin
│   │   │   ├── MULLINS_ce.bin
│   │   │   ├── mullins_me.bin
│   │   │   ├── MULLINS_me.bin
│   │   │   ├── mullins_mec.bin
│   │   │   ├── MULLINS_mec.bin
│   │   │   ├── mullins_pfp.bin
│   │   │   ├── MULLINS_pfp.bin
│   │   │   ├── mullins_rlc.bin
│   │   │   ├── MULLINS_rlc.bin
│   │   │   ├── mullins_sdma1.bin
│   │   │   ├── mullins_sdma.bin
│   │   │   ├── MULLINS_sdma.bin
│   │   │   ├── mullins_uvd.bin
│   │   │   ├── mullins_vce.bin
│   │   │   ├── oland_ce.bin
│   │   │   ├── OLAND_ce.bin
│   │   │   ├── oland_k_smc.bin
│   │   │   ├── OLAND_mc2.bin
│   │   │   ├── oland_mc.bin
│   │   │   ├── OLAND_mc.bin
│   │   │   ├── oland_me.bin
│   │   │   ├── OLAND_me.bin
│   │   │   ├── oland_pfp.bin
│   │   │   ├── OLAND_pfp.bin
│   │   │   ├── oland_rlc.bin
│   │   │   ├── OLAND_rlc.bin
│   │   │   ├── oland_smc.bin
│   │   │   ├── OLAND_smc.bin
│   │   │   ├── PALM_me.bin
│   │   │   ├── PALM_pfp.bin
│   │   │   ├── pitcairn_ce.bin
│   │   │   ├── PITCAIRN_ce.bin
│   │   │   ├── pitcairn_k_smc.bin
│   │   │   ├── PITCAIRN_mc2.bin
│   │   │   ├── pitcairn_mc.bin
│   │   │   ├── PITCAIRN_mc.bin
│   │   │   ├── pitcairn_me.bin
│   │   │   ├── PITCAIRN_me.bin
│   │   │   ├── pitcairn_pfp.bin
│   │   │   ├── PITCAIRN_pfp.bin
│   │   │   ├── pitcairn_rlc.bin
│   │   │   ├── PITCAIRN_rlc.bin
│   │   │   ├── pitcairn_smc.bin
│   │   │   ├── PITCAIRN_smc.bin
│   │   │   ├── R100_cp.bin
│   │   │   ├── R200_cp.bin
│   │   │   ├── R300_cp.bin
│   │   │   ├── R420_cp.bin
│   │   │   ├── R520_cp.bin
│   │   │   ├── R600_me.bin
│   │   │   ├── R600_pfp.bin
│   │   │   ├── R600_rlc.bin
│   │   │   ├── R600_uvd.bin
│   │   │   ├── R700_rlc.bin
│   │   │   ├── REDWOOD_me.bin
│   │   │   ├── REDWOOD_pfp.bin
│   │   │   ├── REDWOOD_rlc.bin
│   │   │   ├── REDWOOD_smc.bin
│   │   │   ├── RS600_cp.bin
│   │   │   ├── RS690_cp.bin
│   │   │   ├── RS780_me.bin
│   │   │   ├── RS780_pfp.bin
│   │   │   ├── RS780_uvd.bin
│   │   │   ├── RV610_me.bin
│   │   │   ├── RV610_pfp.bin
│   │   │   ├── RV620_me.bin
│   │   │   ├── RV620_pfp.bin
│   │   │   ├── RV630_me.bin
│   │   │   ├── RV630_pfp.bin
│   │   │   ├── RV635_me.bin
│   │   │   ├── RV635_pfp.bin
│   │   │   ├── RV670_me.bin
│   │   │   ├── RV670_pfp.bin
│   │   │   ├── RV710_me.bin
│   │   │   ├── RV710_pfp.bin
│   │   │   ├── RV710_smc.bin
│   │   │   ├── RV710_uvd.bin
│   │   │   ├── RV730_me.bin
│   │   │   ├── RV730_pfp.bin
│   │   │   ├── RV730_smc.bin
│   │   │   ├── RV740_smc.bin
│   │   │   ├── RV770_me.bin
│   │   │   ├── RV770_pfp.bin
│   │   │   ├── RV770_smc.bin
│   │   │   ├── RV770_uvd.bin
│   │   │   ├── si58_mc.bin
│   │   │   ├── SUMO2_me.bin
│   │   │   ├── SUMO2_pfp.bin
│   │   │   ├── SUMO_me.bin
│   │   │   ├── SUMO_pfp.bin
│   │   │   ├── SUMO_rlc.bin
│   │   │   ├── SUMO_uvd.bin
│   │   │   ├── tahiti_ce.bin
│   │   │   ├── TAHITI_ce.bin
│   │   │   ├── tahiti_k_smc.bin
│   │   │   ├── TAHITI_mc2.bin
│   │   │   ├── tahiti_mc.bin
│   │   │   ├── TAHITI_mc.bin
│   │   │   ├── tahiti_me.bin
│   │   │   ├── TAHITI_me.bin
│   │   │   ├── tahiti_pfp.bin
│   │   │   ├── TAHITI_pfp.bin
│   │   │   ├── tahiti_rlc.bin
│   │   │   ├── TAHITI_rlc.bin
│   │   │   ├── tahiti_smc.bin
│   │   │   ├── TAHITI_smc.bin
│   │   │   ├── TAHITI_uvd.bin
│   │   │   ├── TAHITI_vce.bin
│   │   │   ├── TURKS_mc.bin
│   │   │   ├── TURKS_me.bin
│   │   │   ├── TURKS_pfp.bin
│   │   │   ├── TURKS_smc.bin
│   │   │   ├── verde_ce.bin
│   │   │   ├── VERDE_ce.bin
│   │   │   ├── verde_k_smc.bin
│   │   │   ├── VERDE_mc2.bin
│   │   │   ├── verde_mc.bin
│   │   │   ├── VERDE_mc.bin
│   │   │   ├── verde_me.bin
│   │   │   ├── VERDE_me.bin
│   │   │   ├── verde_pfp.bin
│   │   │   ├── VERDE_pfp.bin
│   │   │   ├── verde_rlc.bin
│   │   │   ├── VERDE_rlc.bin
│   │   │   ├── verde_smc.bin
│   │   │   └── VERDE_smc.bin
│   │   ├── rs9113_wlan_qspi.rps
│   │   ├── rt2561.bin
│   │   ├── rt2561s.bin
│   │   ├── rt2661.bin
│   │   ├── rt2860.bin
│   │   ├── rt2870.bin
│   │   ├── rt3070.bin -> rt2870.bin
│   │   ├── rt3071.bin
│   │   ├── rt3090.bin -> rt2860.bin
│   │   ├── rt3290.bin
│   │   ├── rt73.bin
│   │   ├── RTL8192E
│   │   │   ├── boot.img
│   │   │   ├── data.img
│   │   │   └── main.img
│   │   ├── RTL8192U
│   │   │   ├── boot.img
│   │   │   ├── data.img
│   │   │   └── main.img
│   │   ├── rtl_nic
│   │   │   ├── rtl8105e-1.fw
│   │   │   ├── rtl8106e-1.fw
│   │   │   ├── rtl8106e-2.fw
│   │   │   ├── rtl8107e-1.fw
│   │   │   ├── rtl8107e-2.fw
│   │   │   ├── rtl8125a-3.fw
│   │   │   ├── rtl8125b-1.fw
│   │   │   ├── rtl8125b-2.fw
│   │   │   ├── rtl8153a-2.fw
│   │   │   ├── rtl8153a-3.fw
│   │   │   ├── rtl8153a-4.fw
│   │   │   ├── rtl8153b-2.fw
│   │   │   ├── rtl8168d-1.fw
│   │   │   ├── rtl8168d-2.fw
│   │   │   ├── rtl8168e-1.fw
│   │   │   ├── rtl8168e-2.fw
│   │   │   ├── rtl8168e-3.fw
│   │   │   ├── rtl8168f-1.fw
│   │   │   ├── rtl8168f-2.fw
│   │   │   ├── rtl8168fp-3.fw
│   │   │   ├── rtl8168g-1.fw
│   │   │   ├── rtl8168g-2.fw
│   │   │   ├── rtl8168g-3.fw
│   │   │   ├── rtl8168h-1.fw
│   │   │   ├── rtl8168h-2.fw
│   │   │   ├── rtl8402-1.fw
│   │   │   ├── rtl8411-1.fw
│   │   │   └── rtl8411-2.fw
│   │   ├── rtlwifi
│   │   │   ├── rtl8188efw.bin
│   │   │   ├── rtl8188eufw.bin
│   │   │   ├── rtl8192cfw.bin
│   │   │   ├── rtl8192cfwU_B.bin
│   │   │   ├── rtl8192cfwU.bin
│   │   │   ├── rtl8192cufw_A.bin
│   │   │   ├── rtl8192cufw_B.bin
│   │   │   ├── rtl8192cufw.bin
│   │   │   ├── rtl8192cufw_TMSC.bin
│   │   │   ├── rtl8192defw.bin
│   │   │   ├── rtl8192eefw.bin
│   │   │   ├── rtl8192eu_ap_wowlan.bin
│   │   │   ├── rtl8192eu_nic.bin
│   │   │   ├── rtl8192eu_wowlan.bin
│   │   │   ├── rtl8192sefw.bin
│   │   │   ├── rtl8712u.bin
│   │   │   ├── rtl8723aufw_A.bin
│   │   │   ├── rtl8723aufw_B.bin
│   │   │   ├── rtl8723aufw_B_NoBT.bin
│   │   │   ├── rtl8723befw_36.bin
│   │   │   ├── rtl8723befw.bin
│   │   │   ├── rtl8723bs_ap_wowlan.bin
│   │   │   ├── rtl8723bs_bt.bin
│   │   │   ├── rtl8723bs_nic.bin
│   │   │   ├── rtl8723bs_wowlan.bin
│   │   │   ├── rtl8723bu_ap_wowlan.bin
│   │   │   ├── rtl8723bu_bt.bin
│   │   │   ├── rtl8723bu_nic.bin
│   │   │   ├── rtl8723bu_wowlan.bin
│   │   │   ├── rtl8723defw.bin
│   │   │   ├── rtl8723fw_B.bin
│   │   │   ├── rtl8723fw.bin
│   │   │   ├── rtl8812aefw.bin
│   │   │   ├── rtl8812aefw_wowlan.bin
│   │   │   ├── rtl8821aefw_29.bin
│   │   │   ├── rtl8821aefw.bin
│   │   │   ├── rtl8821aefw_wowlan.bin
│   │   │   └── rtl8822befw.bin
│   │   ├── rtw88
│   │   │   ├── rtw8723d_fw.bin
│   │   │   ├── rtw8821c_fw.bin
│   │   │   ├── rtw8822b_fw.bin
│   │   │   ├── rtw8822c_fw.bin
│   │   │   └── rtw8822c_wow_fw.bin
│   │   ├── sd8385.bin -> libertas/sd8385.bin
│   │   ├── sd8385_helper.bin -> libertas/sd8385_helper.bin
│   │   ├── sd8686.bin -> libertas/sd8686_v8.bin
│   │   ├── sd8686_helper.bin -> libertas/sd8686_v8_helper.bin
│   │   ├── sd8688.bin -> libertas/sd8688.bin
│   │   ├── sd8688_helper.bin -> libertas/sd8688_helper.bin
│   │   ├── slicoss
│   │   │   ├── gbdownload.sys
│   │   │   ├── gbrcvucode.sys
│   │   │   ├── oasisdownload.sys
│   │   │   └── oasisrcvucode.sys
│   │   ├── ti_3410.fw
│   │   ├── ti_5052.fw
│   │   ├── tigon
│   │   │   ├── tg3.bin
│   │   │   ├── tg3_tso5.bin
│   │   │   └── tg3_tso.bin
│   │   ├── usb8388.bin -> libertas/usb8388_v5.bin
│   │   ├── vicam
│   │   │   └── firmware.fw
│   │   ├── WHENCE
│   │   ├── whiteheat.fw
│   │   ├── whiteheat_loader.fw
│   │   ├── yamaha
│   │   │   ├── ds1_ctrl.fw
│   │   │   ├── ds1_dsp.fw
│   │   │   └── ds1e_ctrl.fw
│   │   ├── zd1201-ap.fw
│   │   ├── zd1201.fw
│   │   └── zd1211
│   │       ├── zd1211b_ub
│   │       ├── zd1211b_uphr
│   │       ├── zd1211b_ur
│   │       ├── zd1211_ub
│   │       ├── zd1211_uphr
│   │       └── zd1211_ur
│   └── modules
│       └── 5.10.25-kiosk
│           ├── kernel
│           │   ├── arch
│           │   │   └── x86
│           │   │       ├── crypto
│           │   │       │   ├── aesni-intel.ko
│           │   │       │   ├── glue_helper.ko
│           │   │       │   └── sha256-ssse3.ko
│           │   │       ├── events
│           │   │       │   ├── amd
│           │   │       │   │   └── power.ko
│           │   │       │   ├── intel
│           │   │       │   │   ├── intel-cstate.ko
│           │   │       │   │   └── intel-uncore.ko
│           │   │       │   └── rapl.ko
│           │   │       ├── kernel
│           │   │       │   ├── cpuid.ko
│           │   │       │   └── msr.ko
│           │   │       └── kvm
│           │   │           ├── kvm-amd.ko
│           │   │           ├── kvm-intel.ko
│           │   │           └── kvm.ko
│           │   ├── crypto
│           │   │   ├── af_alg.ko
│           │   │   ├── algif_aead.ko
│           │   │   ├── algif_hash.ko
│           │   │   ├── algif_rng.ko
│           │   │   ├── algif_skcipher.ko
│           │   │   ├── arc4.ko
│           │   │   ├── asymmetric_keys
│           │   │   │   └── pkcs8_key_parser.ko
│           │   │   ├── authencesn.ko
│           │   │   ├── authenc.ko
│           │   │   ├── cbc.ko
│           │   │   ├── ccm.ko
│           │   │   ├── chacha20poly1305.ko
│           │   │   ├── chacha_generic.ko
│           │   │   ├── cmac.ko
│           │   │   ├── cryptd.ko
│           │   │   ├── crypto_engine.ko
│           │   │   ├── crypto_simd.ko
│           │   │   ├── ctr.ko
│           │   │   ├── deflate.ko
│           │   │   ├── des_generic.ko
│           │   │   ├── drbg.ko
│           │   │   ├── ecb.ko
│           │   │   ├── essiv.ko
│           │   │   ├── gcm.ko
│           │   │   ├── gf128mul.ko
│           │   │   ├── ghash-generic.ko
│           │   │   ├── hmac.ko
│           │   │   ├── jitterentropy_rng.ko
│           │   │   ├── lz4hc.ko
│           │   │   ├── md4.ko
│           │   │   ├── md5.ko
│           │   │   ├── michael_mic.ko
│           │   │   ├── poly1305_generic.ko
│           │   │   ├── seqiv.ko
│           │   │   ├── sha1_generic.ko
│           │   │   ├── sha256_generic.ko
│           │   │   ├── sha3_generic.ko
│           │   │   ├── sha512_generic.ko
│           │   │   └── xts.ko
│           │   ├── drivers
│           │   │   ├── acpi
│           │   │   │   ├── acpi_pad.ko
│           │   │   │   ├── acpi_tad.ko
│           │   │   │   ├── dptf
│           │   │   │   │   ├── dptf_pch_fivr.ko
│           │   │   │   │   └── dptf_power.ko
│           │   │   │   ├── fan.ko
│           │   │   │   ├── nfit
│           │   │   │   │   └── nfit.ko
│           │   │   │   ├── sbshc.ko
│           │   │   │   ├── sbs.ko
│           │   │   │   ├── thermal.ko
│           │   │   │   └── video.ko
│           │   │   ├── base
│           │   │   │   └── regmap
│           │   │   │       ├── regmap-spi-avmm.ko
│           │   │   │       └── regmap-spi.ko
│           │   │   ├── bcma
│           │   │   │   └── bcma.ko
│           │   │   ├── block
│           │   │   │   └── zram
│           │   │   │       └── zram.ko
│           │   │   ├── bus
│           │   │   │   └── mhi
│           │   │   │       └── core
│           │   │   │           └── mhi.ko
│           │   │   ├── char
│           │   │   │   ├── agp
│           │   │   │   │   ├── amd64-agp.ko
│           │   │   │   │   ├── intel-agp.ko
│           │   │   │   │   ├── intel-gtt.ko
│           │   │   │   │   ├── sis-agp.ko
│           │   │   │   │   └── via-agp.ko
│           │   │   │   ├── hw_random
│           │   │   │   │   ├── amd-rng.ko
│           │   │   │   │   ├── ba431-rng.ko
│           │   │   │   │   ├── intel-rng.ko
│           │   │   │   │   ├── rng-core.ko
│           │   │   │   │   ├── timeriomem-rng.ko
│           │   │   │   │   ├── via-rng.ko
│           │   │   │   │   ├── virtio-rng.ko
│           │   │   │   │   └── xiphera-trng.ko
│           │   │   │   ├── lp.ko
│           │   │   │   ├── nvram.ko
│           │   │   │   └── ppdev.ko
│           │   │   ├── connector
│           │   │   │   └── cn.ko
│           │   │   ├── cpufreq
│           │   │   │   ├── acpi-cpufreq.ko
│           │   │   │   ├── amd_freq_sensitivity.ko
│           │   │   │   ├── cpufreq_conservative.ko
│           │   │   │   ├── cpufreq_powersave.ko
│           │   │   │   ├── cpufreq_userspace.ko
│           │   │   │   ├── pcc-cpufreq.ko
│           │   │   │   └── powernow-k8.ko
│           │   │   ├── crypto
│           │   │   │   ├── cavium
│           │   │   │   │   └── nitrox
│           │   │   │   │       └── n5pf.ko
│           │   │   │   ├── ccp
│           │   │   │   │   ├── ccp-crypto.ko
│           │   │   │   │   └── ccp.ko
│           │   │   │   ├── inside-secure
│           │   │   │   │   └── crypto_safexcel.ko
│           │   │   │   ├── padlock-aes.ko
│           │   │   │   ├── padlock-sha.ko
│           │   │   │   ├── qat
│           │   │   │   │   ├── qat_c3xxx
│           │   │   │   │   │   └── qat_c3xxx.ko
│           │   │   │   │   ├── qat_c3xxxvf
│           │   │   │   │   │   └── qat_c3xxxvf.ko
│           │   │   │   │   ├── qat_c62x
│           │   │   │   │   │   └── qat_c62x.ko
│           │   │   │   │   ├── qat_c62xvf
│           │   │   │   │   │   └── qat_c62xvf.ko
│           │   │   │   │   ├── qat_common
│           │   │   │   │   │   └── intel_qat.ko
│           │   │   │   │   ├── qat_dh895xcc
│           │   │   │   │   │   └── qat_dh895xcc.ko
│           │   │   │   │   └── qat_dh895xccvf
│           │   │   │   │       └── qat_dh895xccvf.ko
│           │   │   │   └── virtio
│           │   │   │       └── virtio_crypto.ko
│           │   │   ├── dca
│           │   │   │   └── dca.ko
│           │   │   ├── dma
│           │   │   │   ├── altera-msgdma.ko
│           │   │   │   ├── dw
│           │   │   │   │   └── dw_dmac_pci.ko
│           │   │   │   ├── hsu
│           │   │   │   │   └── hsu_dma.ko
│           │   │   │   ├── idma64.ko
│           │   │   │   ├── idxd
│           │   │   │   │   └── idxd.ko
│           │   │   │   ├── ioat
│           │   │   │   │   └── ioatdma.ko
│           │   │   │   └── virt-dma.ko
│           │   │   ├── extcon
│           │   │   │   ├── extcon-axp288.ko
│           │   │   │   ├── extcon-gpio.ko
│           │   │   │   ├── extcon-intel-cht-wc.ko
│           │   │   │   ├── extcon-intel-int3496.ko
│           │   │   │   ├── extcon-intel-mrfld.ko
│           │   │   │   ├── extcon-usbc-cros-ec.ko
│           │   │   │   └── extcon-usb-gpio.ko
│           │   │   ├── firmware
│           │   │   │   ├── dmi-sysfs.ko
│           │   │   │   └── efi
│           │   │   │       └── efivars.ko
│           │   │   ├── gpio
│           │   │   │   ├── gpio-104-dio-48e.ko
│           │   │   │   ├── gpio-104-idi-48.ko
│           │   │   │   ├── gpio-104-idio-16.ko
│           │   │   │   ├── gpio-adp5588.ko
│           │   │   │   ├── gpio-aggregator.ko
│           │   │   │   ├── gpio-amd8111.ko
│           │   │   │   ├── gpio-amd-fch.ko
│           │   │   │   ├── gpio-amdpt.ko
│           │   │   │   ├── gpio-bt8xx.ko
│           │   │   │   ├── gpio-crystalcove.ko
│           │   │   │   ├── gpio-dwapb.ko
│           │   │   │   ├── gpio-exar.ko
│           │   │   │   ├── gpio-f7188x.ko
│           ���   │   │   ├── gpio-generic.ko
│           │   │   │   ├── gpio-gpio-mm.ko
│           │   │   │   ├── gpio-ich.ko
│           │   │   │   ├── gpio-it87.ko
│           │   │   │   ├── gpio-max3191x.ko
│           │   │   │   ├── gpio-max7300.ko
│           │   │   │   ├── gpio-max7301.ko
│           │   │   │   ├── gpio-max730x.ko
│           │   │   │   ├── gpio-max732x.ko
│           │   │   │   ├── gpio-mb86s7x.ko
│           │   │   │   ├── gpio-mc33880.ko
│           │   │   │   ├── gpio-ml-ioh.ko
│           │   │   │   ├── gpio-pca953x.ko
│           │   │   │   ├── gpio-pca9570.ko
│           │   │   │   ├── gpio-pcf857x.ko
│           │   │   │   ├── gpio-pcie-idio-24.ko
│           │   │   │   ├── gpio-pci-idio-16.ko
│           │   │   │   ├── gpio-pisosr.ko
│           │   │   │   ├── gpio-rdc321x.ko
│           │   │   │   ├── gpio-sch311x.ko
│           │   │   │   ├── gpio-sch.ko
│           │   │   │   ├── gpio-tpic2810.ko
│           │   │   │   ├── gpio-vx855.ko
│           │   │   │   ├── gpio-wcove.ko
│           │   │   │   ├── gpio-winbond.ko
│           │   │   │   ├── gpio-ws16c48.ko
│           │   │   │   ├── gpio-xilinx.ko
│           │   │   │   └── gpio-xra1403.ko
│           │   │   ├── gpu
│           │   │   │   └── drm
│           │   │   │       ├── amd
│           │   │   │       │   └── amdgpu
│           │   │   │       │       └── amdgpu.ko
│           │   │   │       ├── ast
│           │   │   │       │   └── ast.ko
│           │   │   │       ├── bochs
│           │   │   │       │   └── bochs-drm.ko
│           │   │   │       ├── drm_ttm_helper.ko
│           │   │   │       ├── drm_vram_helper.ko
│           │   │   │       ├── gma500
│           │   │   │       │   └── gma500_gfx.ko
│           │   │   │       ├── i915
│           │   │   │       │   └── i915.ko
│           │   │   │       ├── mga
│           │   │   │       │   └── mga.ko
│           │   │   │       ├── mgag200
│           │   │   │       │   └── mgag200.ko
│           │   │   │       ├── nouveau
│           │   │   │       │   └── nouveau.ko
│           │   │   │       ├── qxl
│           │   │   │       │   └── qxl.ko
│           │   │   │       ├── r128
│           │   │   │       │   └── r128.ko
│           │   │   │       ├── radeon
│           │   │   │       │   └── radeon.ko
│           │   │   │       ├── savage
│           │   │   │       │   └── savage.ko
│           │   │   │       ├── scheduler
│           │   │   │       │   └── gpu-sched.ko
│           │   │   │       ├── sis
│           │   │   │       │   └── sis.ko
│           │   │   │       ├── tdfx
│           │   │   │       │   └── tdfx.ko
│           │   │   │       ├── tiny
│           │   │   │       │   └── cirrus.ko
│           │   │   │       ├── ttm
│           │   │   │       │   └── ttm.ko
│           │   │   │       ├── udl
│           │   │   │       │   └── udl.ko
│           │   │   │       ├── vboxvideo
│           │   │   │       │   └── vboxvideo.ko
│           │   │   │       ├── vgem
│           │   │   │       │   └── vgem.ko
│           │   │   │       ├── via
│           │   │   │       │   └── via.ko
│           │   │   │       ├── virtio
│           │   │   │       │   └── virtio-gpu.ko
│           │   │   │       ├── vkms
│           │   │   │       │   └── vkms.ko
│           │   │   │       ├── vmwgfx
│           │   │   │       │   └── vmwgfx.ko
│           │   │   │       └── xen
│           │   │   │           └── drm_xen_front.ko
│           │   │   ├── hid
│           │   │   │   ├── hid-a4tech.ko
│           │   │   │   ├── hid-accutouch.ko
│           │   │   │   ├── hid-alps.ko
│           │   │   │   ├── hid-asus.ko
│           │   │   │   ├── hid-cherry.ko
│           │   │   │   ├── hid-chicony.ko
│           │   │   │   ├── hid-corsair.ko
│           │   │   │   ├── hid-cougar.ko
│           │   │   │   ├── hid-cypress.ko
│           │   │   │   ├── hid-elan.ko
│           │   │   │   ├── hid-elo.ko
│           │   │   │   ├── hid-ezkey.ko
│           │   │   │   ├── hid-glorious.ko
│           │   │   │   ├── hid-google-hammer.ko
│           │   │   │   ├── hid-hyperv.ko
│           │   │   │   ├── hid-ite.ko
│           │   │   │   ├── hid-jabra.ko
│           │   │   │   ├── hid-kensington.ko
│           │   │   │   ├── hid-keytouch.ko
│           │   │   │   ├── hid-kye.ko
│           │   │   │   ├── hid-lenovo.ko
│           │   │   │   ├── hid-lg-g15.ko
│           │   │   │   ├── hid-logitech-dj.ko
│           │   │   │   ├── hid-logitech-hidpp.ko
│           │   │   │   ├── hid-logitech.ko
│           │   │   │   ├── hid-macally.ko
│           │   │   │   ├── hid-magicmouse.ko
│           │   │   │   ├── hid-maltron.ko
│           │   │   │   ├── hid-mcp2221.ko
│           │   │   │   ├── hid-microsoft.ko
│           │   │   │   ├── hid-monterey.ko
│           │   │   │   ├── hid-multitouch.ko
│           │   │   │   ├── hid-ntrig.ko
│           │   │   │   ├── hid-penmount.ko
│           │   │   │   ├── hid-primax.ko
│           │   │   │   ├── hid-redragon.ko
│           │   │   │   ├── hid-retrode.ko
│           │   │   │   ├── hid-rmi.ko
│           │   │   │   ├── hid-roccat-arvo.ko
│           │   │   │   ├── hid-roccat-common.ko
│           │   │   │   ├── hid-roccat-isku.ko
│           │   │   │   ├── hid-roccat.ko
│           │   │   │   ├── hid-roccat-kone.ko
│           │   │   │   ├── hid-roccat-koneplus.ko
│           │   │   │   ├── hid-roccat-konepure.ko
│           │   │   │   ├── hid-roccat-kovaplus.ko
│           │   │   │   ├── hid-roccat-lua.ko
│           │   │   │   ├── hid-roccat-pyra.ko
│           │   │   │   ├── hid-roccat-ryos.ko
│           │   │   │   ├── hid-roccat-savu.ko
│           │   │   │   ├── hid-saitek.ko
│           │   │   │   ├── hid-speedlink.ko
│           │   │   │   ├── hid-steam.ko
│           │   │   │   ├── hid-uclogic.ko
│           │   │   │   ├── hid-udraw-ps3.ko
│           │   │   │   ├── hid-viewsonic.ko
│           │   │   │   ├── hid-vivaldi.ko
│           │   │   │   ├── hid-waltop.ko
│           │   │   │   ├── i2c-hid
│           │   │   │   │   └── i2c-hid.ko
│           │   │   │   ├── intel-ish-hid
│           │   │   │   │   ├── intel-ish-ipc.ko
│           │   │   │   │   ├── intel-ishtp-hid.ko
│           │   │   │   │   ├── intel-ishtp.ko
│           │   │   │   │   └── intel-ishtp-loader.ko
│           │   │   │   ├── uhid.ko
│           │   │   │   └── wacom.ko
│           │   │   ├── hsi
│           │   │   │   ├── clients
│           │   │   │   │   └── hsi_char.ko
│           │   │   │   └── hsi.ko
│           │   │   ├── hv
│           │   │   │   ├── hv_balloon.ko
│           │   │   │   └── hv_utils.ko
│           │   │   ├── hwmon
│           │   │   │   ├── abituguru3.ko
│           │   │   │   ├── abituguru.ko
│           │   │   │   ├── acpi_power_meter.ko
│           │   │   │   ├── ad7314.ko
│           │   │   │   ├── ad7414.ko
│           │   │   │   ├── ad7418.ko
│           │   │   │   ├── adc128d818.ko
│           │   │   │   ├── adcxx.ko
│           │   │   │   ├── adm1021.ko
│           │   │   │   ├── adm1025.ko
│           │   │   │   ├── adm1026.ko
│           │   │   │   ├── adm1029.ko
│           │   │   │   ├── adm1031.ko
│           │   │   │   ├── adm1177.ko
│           │   │   │   ├── adm9240.ko
│           │   │   │   ├── ads7828.ko
│           │   │   │   ├── ads7871.ko
│           │   │   │   ├── adt7310.ko
│           │   │   │   ├── adt7410.ko
│           │   │   │   ├── adt7411.ko
│           │   │   │   ├── adt7462.ko
│           │   │   │   ├── adt7470.ko
│           │   │   │   ├── adt7475.ko
│           │   │   │   ├── adt7x10.ko
│           │   │   │   ├── amc6821.ko
│           │   │   │   ├── amd_energy.ko
│           │   │   │   ├── applesmc.ko
│           │   │   │   ├── as370-hwmon.ko
│           │   │   │   ├── asb100.ko
│           │   │   │   ├── asc7621.ko
│           │   │   │   ├── aspeed-pwm-tacho.ko
│           │   │   │   ├── asus_atk0110.ko
│           │   │   │   ├── atxp1.ko
│           │   │   │   ├── axi-fan-control.ko
│           │   │   │   ├── coretemp.ko
│           │   │   │   ├── corsair-cpro.ko
│           │   │   │   ├── dell-smm-hwmon.ko
│           │   │   │   ├── dme1737.ko
│           │   │   │   ├── drivetemp.ko
│           │   │   │   ├── ds1621.ko
│           │   │   │   ├── ds620.ko
│           │   │   │   ├── emc1403.ko
│           │   │   │   ├── emc2103.ko
│           │   │   │   ├── emc6w201.ko
│           │   │   │   ├── f71805f.ko
│           │   │   │   ├── f71882fg.ko
│           │   │   │   ├── f75375s.ko
│           │   │   │   ├── fam15h_power.ko
│           │   │   │   ├── fschmd.ko
│           │   │   │   ├── g760a.ko
│           │   │   │   ├── g762.ko
│           │   │   │   ├── gl518sm.ko
│           │   │   │   ├── gl520sm.ko
│           │   │   │   ├── hih6130.ko
│           │   │   │   ├── hwmon.ko
│           │   │   │   ├── hwmon-vid.ko
│           │   │   │   ├── i5500_temp.ko
│           │   │   │   ├── i5k_amb.ko
│           │   │   │   ├── iio_hwmon.ko
│           │   │   │   ├── ina209.ko
│           │   │   │   ├── ina2xx.ko
│           │   │   │   ├── ina3221.ko
│           │   │   │   ├── intel-m10-bmc-hwmon.ko
│           │   │   │   ├── it87.ko
│           │   │   │   ├── jc42.ko
│           │   │   │   ├── k10temp.ko
│           │   │   │   ├── k8temp.ko
│           │   │   │   ├── lineage-pem.ko
│           │   │   │   ├── lm63.ko
│           │   │   │   ├── lm70.ko
│           │   │   │   ├── lm73.ko
│           │   │   │   ├── lm75.ko
│           │   │   │   ├── lm77.ko
│           │   │   │   ├── lm78.ko
│           │   │   │   ├── lm80.ko
│           │   │   │   ├── lm83.ko
│           │   │   │   ├── lm85.ko
│           │   │   │   ├── lm87.ko
│           │   │   │   ├── lm90.ko
│           │   │   │   ├── lm92.ko
│           │   │   │   ├── lm93.ko
│           │   │   │   ├── lm95234.ko
│           │   │   │   ├── lm95241.ko
│           │   │   │   ├── lm95245.ko
│           │   │   │   ├── ltc2945.ko
│           │   │   │   ├── ltc2947-core.ko
│           │   │   │   ├── ltc2947-i2c.ko
│           │   │   │   ├── ltc2947-spi.ko
│           │   │   │   ├── ltc2990.ko
│           │   │   │   ├── ltc4151.ko
│           │   │   │   ├── ltc4215.ko
│           │   │   │   ├── ltc4222.ko
│           │   │   │   ├── ltc4245.ko
│           │   │   │   ├── ltc4260.ko
│           │   │   │   ├── ltc4261.ko
│           │   │   │   ├── max1111.ko
│           │   │   │   ├── max16065.ko
│           │   │   │   ├── max1619.ko
│           │   │   │   ├── max1668.ko
│           │   │   │   ├── max197.ko
│           │   │   │   ├── max31722.ko
│           │   │   │   ├── max31730.ko
│           │   │   │   ├── max31790.ko
│           │   │   │   ├── max6621.ko
│           │   │   │   ├── max6639.ko
│           │   │   │   ├── max6642.ko
│           │   │   │   ├── max6650.ko
│           │   │   │   ├── max6697.ko
│           │   │   │   ├── mcp3021.ko
│           │   │   │   ├── mr75203.ko
│           │   │   │   ├── nct6683.ko
│           │   │   │   ├── nct6775.ko
│           │   │   │   ├── nct7802.ko
│           │   │   │   ├── npcm750-pwm-fan.ko
│           │   │   │   ├── ntc_thermistor.ko
│           │   │   │   ├── pc87360.ko
│           │   │   │   ├── pc87427.ko
│           │   │   │   ├── pcf8591.ko
│           │   │   │   ├── pmbus
│           │   │   │   │   ├── adm1266.ko
│           │   │   │   │   ├── adm1275.ko
│           │   │   │   │   ├── bel-pfe.ko
│           │   │   │   │   ├── ibm-cffps.ko
│           │   │   │   │   ├── inspur-ipsps.ko
│           │   │   │   │   ├── ir35221.ko
│           │   │   │   │   ├── ir38064.ko
│           │   │   │   │   ├── irps5401.ko
│           │   │   │   │   ├── isl68137.ko
│           │   │   │   │   ├── lm25066.ko
│           │   │   │   │   ├── ltc2978.ko
│           │   │   │   │   ├── ltc3815.ko
│           │   │   │   │   ├── max16064.ko
│           │   │   │   │   ├── max16601.ko
│           │   │   │   │   ├── max20730.ko
│           │   │   │   │   ├── max20751.ko
│           │   │   │   │   ├── max31785.ko
│           │   │   │   │   ├── max34440.ko
│           │   │   │   │   ├── max8688.ko
│           │   │   │   │   ├── mp2975.ko
│           │   │   │   │   ├── pmbus_core.ko
│           │   │   │   │   ├── pmbus.ko
│           │   │   │   │   ├── pxe1610.ko
│           │   │   │   │   ├── tps40422.ko
│           │   │   │   │   ├── tps53679.ko
│           │   │   │   │   ├── ucd9000.ko
│           │   │   │   │   ├── ucd9200.ko
│           │   │   │   │   ├── xdpe12284.ko
│           │   │   │   │   └── zl6100.ko
│           │   │   │   ├── powr1220.ko
│           │   │   │   ├── sht15.ko
│           │   │   │   ├── sht21.ko
│           │   │   │   ├── sht3x.ko
│           │   │   │   ├── shtc1.ko
│           │   │   │   ├── sis5595.ko
│           │   │   │   ├── smm665.ko
│           │   │   │   ├── smsc47b397.ko
│           │   │   │   ├── smsc47m192.ko
│           │   │   │   ├── smsc47m1.ko
│           │   │   │   ├── stts751.ko
│           │   │   │   ├── tc654.ko
│           │   │   │   ├── tc74.ko
│           │   │   │   ├── thmc50.ko
│           │   │   │   ├── tmp102.ko
│           │   │   │   ├── tmp103.ko
│           │   │   │   ├── tmp108.ko
│           │   │   │   ├── tmp401.ko
│           │   │   │   ├── tmp421.ko
│           │   │   │   ├── tmp513.ko
│           │   │   │   ├── via686a.ko
│           │   │   │   ├── via-cputemp.ko
│           │   │   │   ├── vt1211.ko
│           │   │   │   ├── vt8231.ko
│           │   │   │   ├── w83627ehf.ko
│           │   │   │   ├── w83627hf.ko
│           │   │   │   ├── w83773g.ko
│           │   │   │   ├── w83781d.ko
│           │   │   │   ├── w83791d.ko
│           │   │   │   ├── w83792d.ko
│           │   │   │   ├── w83793.ko
│           │   │   │   ├── w83795.ko
│           │   │   │   ├── w83l785ts.ko
│           │   │   │   ├── w83l786ng.ko
│           │   │   │   └── xgene-hwmon.ko
│           │   │   ├── i2c
│           │   │   │   ├── algos
│           │   │   │   │   └── i2c-algo-pca.ko
│           │   │   │   ├── busses
│           │   │   │   │   ├── i2c-ali1535.ko
│           │   │   │   │   ├── i2c-ali1563.ko
│           │   │   │   │   ├── i2c-ali15x3.ko
│           │   │   │   │   ├── i2c-amd756.ko
│           │   │   │   │   ├── i2c-amd756-s4882.ko
│           │   │   │   │   ├── i2c-amd8111.ko
│           │   │   │   │   ├── i2c-amd-mp2-pci.ko
│           │   │   │   │   ├── i2c-amd-mp2-plat.ko
│           │   │   │   │   ├── i2c-cbus-gpio.ko
│           │   │   │   │   ├── i2c-cht-wc.ko
│           │   │   │   │   ├── i2c-cros-ec-tunnel.ko
│           │   │   │   │   ├── i2c-designware-pci.ko
│           │   │   │   │   ├── i2c-diolan-u2c.ko
│           │   │   │   │   ├── i2c-emev2.ko
│           │   │   │   │   ├── i2c-gpio.ko
│           │   │   │   │   ├── i2c-i801.ko
│           │   │   │   │   ├── i2c-isch.ko
│           │   │   │   │   ├── i2c-ismt.ko
│           │   │   │   │   ├── i2c-mlxcpld.ko
│           │   │   │   │   ├── i2c-nforce2.ko
│           │   │   │   │   ├── i2c-nforce2-s4985.ko
│           │   │   │   │   ├── i2c-nvidia-gpu.ko
│           │   │   │   │   ├── i2c-ocores.ko
│           │   │   │   │   ├── i2c-parport.ko
│           │   │   │   │   ├── i2c-pca-platform.ko
│           │   │   │   │   ├── i2c-piix4.ko
│           │   │   │   │   ├── i2c-robotfuzz-osif.ko
│           │   │   │   │   ├── i2c-scmi.ko
│           │   │   │   │   ├── i2c-simtec.ko
│           │   │   │   │   ├── i2c-sis5595.ko
│           │   │   │   │   ├── i2c-sis630.ko
│           │   │   │   │   ├── i2c-sis96x.ko
│           │   │   │   │   ├── i2c-taos-evm.ko
│           │   │   │   │   ├── i2c-tiny-usb.ko
│           │   │   │   │   ├── i2c-via.ko
│           │   │   │   │   ├── i2c-viapro.ko
│           │   │   │   │   └── i2c-xiic.ko
│           │   │   │   ├── i2c-dev.ko
│           │   │   │   ├── i2c-mux.ko
│           │   │   │   ├── i2c-smbus.ko
│           │   │   │   └── muxes
│           │   │   │       ├── i2c-mux-gpio.ko
│           │   │   │       ├── i2c-mux-ltc4306.ko
│           │   │   │       ├── i2c-mux-mlxcpld.ko
│           │   │   │       ├── i2c-mux-pca9541.ko
│           │   │   │       ├── i2c-mux-pca954x.ko
│           │   │   │       └── i2c-mux-reg.ko
│           │   │   ├── i3c
│           │   │   │   ├── i3c.ko
│           │   │   │   └── master
│           │   │   │       ├── dw-i3c-master.ko
│           │   │   │       └── i3c-master-cdns.ko
│           │   │   ├── iio
│           │   │   │   ├── accel
│           │   │   │   │   ├── adis16201.ko
│           │   │   │   │   ├── adis16209.ko
│           │   │   │   │   ├── adxl345_core.ko
│           │   │   │   │   ├── adxl345_i2c.ko
│           │   │   │   │   ├── adxl345_spi.ko
│           │   │   │   │   ├── adxl372_i2c.ko
│           │   │   │   │   ├── adxl372.ko
│           │   │   │   │   ├── adxl372_spi.ko
│           │   │   │   │   ├── bma180.ko
│           │   │   │   │   ├── bma220_spi.ko
│           │   │   │   │   ├── bma400_core.ko
│           │   │   │   │   ├── bma400_i2c.ko
│           │   │   │   │   ├── bma400_spi.ko
│           │   │   │   │   ├── bmc150-accel-core.ko
│           │   │   │   │   ├── bmc150-accel-i2c.ko
│           │   │   │   │   ├── bmc150-accel-spi.ko
│           │   │   │   │   ├── da280.ko
│           │   │   │   │   ├── da311.ko
│           │   │   │   │   ├── dmard09.ko
│           │   │   │   │   ├── dmard10.ko
│           │   │   │   │   ├── kxcjk-1013.ko
│           │   │   │   │   ├── kxsd9-i2c.ko
│           │   │   │   │   ├── kxsd9.ko
│           │   │   │   │   ├── kxsd9-spi.ko
│           │   │   │   │   ├── mc3230.ko
│           │   │   │   │   ├── mma7455_core.ko
│           │   │   │   │   ├── mma7455_i2c.ko
│           │   │   │   │   ├── mma7455_spi.ko
│           │   │   │   │   ├── mma7660.ko
│           │   │   │   │   ├── mma8452.ko
│           │   │   │   │   ├── mma9551_core.ko
│           │   │   │   │   ├── mma9551.ko
│           │   │   │   │   ├── mma9553.ko
│           │   │   │   │   ├── mxc4005.ko
│           │   │   │   │   ├── mxc6255.ko
│           │   │   │   │   ├── sca3000.ko
│           │   │   │   │   ├── st_accel_i2c.ko
│           │   │   │   │   ├── st_accel.ko
│           │   │   │   │   ├── st_accel_spi.ko
│           │   │   │   │   ├── stk8312.ko
│           │   │   │   │   └── stk8ba50.ko
│           │   │   │   ├── adc
│           │   │   │   │   ├── axp20x_adc.ko
│           │   │   │   │   ├── axp288_adc.ko
│           │   │   │   │   └── intel_mrfld_adc.ko
│           │   │   │   ├── buffer
│           │   │   │   │   ├── industrialio-buffer-cb.ko
│           │   │   │   │   ├── industrialio-triggered-buffer.ko
│           │   │   │   │   └── kfifo_buf.ko
│           │   │   │   ├── common
│           │   │   │   │   └── st_sensors
│           │   │   │   │       ├── st_sensors_i2c.ko
│           │   │   │   │       ├── st_sensors.ko
│           │   │   │   │       └── st_sensors_spi.ko
│           │   │   │   ├── imu
│           │   │   │   │   └── adis_lib.ko
│           │   │   │   └── industrialio.ko
│           │   │   ├── input
│           │   │   │   ├── ff-memless.ko
│           │   │   │   ├── input-leds.ko
│           │   │   │   ├── input-polldev.ko
│           │   │   │   ├── keyboard
│           │   │   │   │   ├── adc-keys.ko
│           │   │   │   │   ├── adp5588-keys.ko
│           │   │   │   │   ├── adp5589-keys.ko
│           │   │   │   │   ├── applespi.ko
│           │   │   │   │   ├── cros_ec_keyb.ko
│           │   │   │   │   ├── gpio_keys.ko
│           │   │   │   │   ├── gpio_keys_polled.ko
│           │   │   │   │   ├── lkkbd.ko
│           │   │   │   │   ├── lm8323.ko
│           │   │   │   │   ├── lm8333.ko
│           │   │   │   │   ├── matrix_keypad.ko
│           │   │   │   │   ├── max7359_keypad.ko
│           │   │   │   │   ├── mcs_touchkey.ko
│           │   │   │   │   ├── mpr121_touchkey.ko
│           │   │   │   │   ├── newtonkbd.ko
│           │   │   │   │   ├── opencores-kbd.ko
│           │   │   │   │   ├── qt1050.ko
│           │   │   │   │   ├── qt1070.ko
│           │   │   │   │   ├── qt2160.ko
│           │   │   │   │   ├── samsung-keypad.ko
│           │   │   │   │   ├── stowaway.ko
│           │   │   │   │   ├── sunkbd.ko
│           │   │   │   │   ├── tca6416-keypad.ko
│           │   │   │   │   ├── tca8418_keypad.ko
│           │   │   │   │   ├── tm2-touchkey.ko
│           │   │   │   │   └── xtkbd.ko
│           │   │   │   ├── matrix-keymap.ko
│           │   │   │   ├── misc
│           │   │   │   │   ├── apanel.ko
│           │   │   │   │   ├── atlas_btns.ko
│           │   │   │   │   ├── axp20x-pek.ko
│           │   │   │   │   ├── gpio-beeper.ko
│           │   │   │   │   ├── gpio_decoder.ko
│           │   │   │   │   ├── ideapad_slidebar.ko
│           │   │   │   │   ├── iqs269a.ko
│           │   │   │   │   ├��─ pwm-beeper.ko
│           │   │   │   │   ├── pwm-vibra.ko
│           │   │   │   │   ├── soc_button_array.ko
│           │   │   │   │   └── uinput.ko
│           │   │   │   ├── mouse
│           │   │   │   │   ├── appletouch.ko
│           │   │   │   │   ├── bcm5974.ko
│           │   │   │   │   ├── cyapatp.ko
│           │   │   │   │   ├── elan_i2c.ko
│           │   │   │   │   ├── gpio_mouse.ko
│           │   │   │   │   ├── psmouse.ko
│           │   │   │   │   ├── sermouse.ko
│           │   │   │   │   ├── synaptics_i2c.ko
│           │   │   │   │   ├── synaptics_usb.ko
│           │   │   │   │   └── vsxxxaa.ko
│           │   │   │   ├── rmi4
│           │   │   │   │   ├── rmi_core.ko
│           │   │   │   │   ├── rmi_i2c.ko
│           │   │   │   │   ├── rmi_smbus.ko
│           │   │   │   │   └── rmi_spi.ko
│           │   │   │   ├── serio
│           │   │   │   │   ├── pcips2.ko
│           │   │   │   │   ├── ps2-gpio.ko
│           │   │   │   │   ├── serport.ko
│           │   │   │   │   └── userio.ko
│           │   │   │   ├── sparse-keymap.ko
│           │   │   │   ├── tablet
│           │   │   │   │   ├── acecad.ko
│           │   │   │   │   ├── aiptek.ko
│           │   │   │   │   ├── gtco.ko
│           │   │   │   │   ├── hanwang.ko
│           │   │   │   │   ├── kbtab.ko
│           │   │   │   │   ├── pegasus_notetaker.ko
│           │   │   │   │   └── wacom_serial4.ko
│           │   │   │   └── touchscreen
│           │   │   │       ├── ad7877.ko
│           │   │   │       ├── ad7879-i2c.ko
│           │   │   │       ├── ad7879.ko
│           │   │   │       ├── ad7879-spi.ko
│           │   │   │       ├── ads7846.ko
│           │   │   │       ├── atmel_mxt_ts.ko
│           │   │   │       ├── auo-pixcir-ts.ko
│           │   │   │       ├── bu21013_ts.ko
│           │   │   │       ├── bu21029_ts.ko
│           │   │   │       ├── chipone_icn8505.ko
│           │   │   │       ├── cy8ctma140.ko
│           │   │   │       ├── cy8ctmg110_ts.ko
│           │   │   │       ├── cyttsp4_core.ko
│           │   │   │       ├── cyttsp4_i2c.ko
│           │   │   │       ├── cyttsp4_spi.ko
│           │   │   │       ├── cyttsp_core.ko
│           │   │   │       ├── cyttsp_i2c_common.ko
│           │   │   │       ├── cyttsp_i2c.ko
│           │   │   │       ├── cyttsp_spi.ko
│           │   │   │       ├── dynapro.ko
│           │   │   │       ├── edt-ft5x06.ko
│           │   │   │       ├── eeti_ts.ko
│           │   │   │       ├── egalax_ts_serial.ko
│           │   │   │       ├── ektf2127.ko
│           │   │   │       ├── elants_i2c.ko
│           │   │   │       ├── elo.ko
│           │   │   │       ├── exc3000.ko
│           │   │   │       ├── fujitsu_ts.ko
│           │   │   │       ├── goodix.ko
│           │   │   │       ├── gunze.ko
│           │   │   │       ├── hampshire.ko
│           │   │   │       ├── hideep.ko
│           │   │   │       ├── ili210x.ko
│           │   │   │       ├── inexio.ko
│           │   │   │       ├── iqs5xx.ko
│           │   │   │       ├── max11801_ts.ko
│           │   │   │       ├── mcs5000_ts.ko
│           │   │   │       ├── melfas_mip4.ko
│           │   │   │       ├── mk712.ko
│           │   │   │       ├── mms114.ko
│           │   │   │       ├── mtouch.ko
│           │   │   │       ├── penmount.ko
│           │   │   │       ├── pixcir_i2c_ts.ko
│           │   │   │       ├── raydium_i2c_ts.ko
│           │   │   │       ├── resistive-adc-touch.ko
│           │   │   │       ├── rohm_bu21023.ko
│           │   │   │       ├── s6sy761.ko
│           │   │   │       ├── silead.ko
│           │   │   │       ├── sis_i2c.ko
│           │   │   │       ├── st1232.ko
│           │   │   │       ├── stmfts.ko
│           │   │   │       ├── sur40.ko
│           │   │   │       ├── surface3_spi.ko
│           │   │   │       ├── sx8654.ko
│           │   │   │       ├── touchit213.ko
│           │   │   │       ├── touchright.ko
│           │   │   │       ├── touchwin.ko
│           │   │   │       ├── tps6507x-ts.ko
│           │   │   │       ├── tsc2004.ko
│           │   │   │       ├── tsc2005.ko
│           │   │   │       ├── tsc2007.ko
│           │   │   │       ├── tsc200x-core.ko
│           │   │   │       ├── tsc40.ko
│           │   │   │       ├── usbtouchscreen.ko
│           │   │   │       ├── wacom_i2c.ko
│           │   │   │       ├── wacom_w8001.ko
│           │   │   │       ├── wdt87xx_i2c.ko
│           │   │   │       ├── wm97xx-ts.ko
│           │   │   │       ├── zet6223.ko
│           │   │   │       ├── zforce_ts.ko
│           │   │   │       └── zinitix.ko
│           │   │   ├── iommu
│           │   │   │   └── amd
│           │   │   │       └── iommu_v2.ko
│           │   │   ├── leds
│           │   │   │   ├── led-class.ko
│           │   │   │   ├── leds-gpio.ko
│           │   │   │   ├── trigger
│           │   │   │   │   └── ledtrig-audio.ko
│           │   │   │   └── uleds.ko
│           │   │   ├── lightnvm
│           │   │   │   └── pblk.ko
│           │   │   ├── md
│           │   │   │   ├── dm-crypt.ko
│           │   │   │   ├── dm-mod.ko
│           │   │   │   └── dm-unstripe.ko
│           │   │   ├── media
│           │   │   │   ├── cec
│           │   │   │   │   ├── i2c
│           │   │   │   │   │   └── ch7322.ko
│           │   │   │   │   ├── platform
│           │   │   │   │   │   ├── cec-gpio
│           │   │   │   │   │   │   └── cec-gpio.ko
│           │   │   │   │   │   ├── cros-ec
│           │   │   │   │   │   │   └── cros-ec-cec.ko
│           │   │   │   │   │   └── seco
│           │   │   │   │   │       └── seco-cec.ko
│           │   │   │   │   └── usb
│           │   │   │   │       ├── pulse8
│           │   │   │   │       │   └── pulse8-cec.ko
│           │   │   │   │       └── rainshadow
│           │   │   │   │           └── rainshadow-cec.ko
│           │   │   │   ├── common
│           │   │   │   │   ├── tveeprom.ko
│           │   │   │   │   └── videobuf2
│           │   │   │   │       ├── videobuf2-common.ko
│           │   │   │   │       ├── videobuf2-dma-contig.ko
│           │   │   │   │       ├── videobuf2-dma-sg.ko
│           │   │   │   │       ├── videobuf2-memops.ko
│           │   │   │   │       ├── videobuf2-v4l2.ko
│           │   │   │   │       └── videobuf2-vmalloc.ko
│           │   │   │   ├── i2c
│           │   │   │   │   ├── msp3400.ko
│           │   │   │   │   ├── mt9v011.ko
│           │   │   │   │   ├── ov2640.ko
│           │   │   │   │   ├── ov7670.ko
│           │   │   │   │   ├── saa7115.ko
│           │   │   │   │   └── tvp5150.ko
│           │   │   │   ├── mc
│           │   │   │   │   └── mc.ko
│           │   │   │   ├── pci
│           │   │   │   │   ├── intel
│           │   │   │   │   │   └── ipu3
│           │   │   │   │   │       └── ipu3-cio2.ko
│           │   │   │   │   └── meye
│           │   │   │   │       └── meye.ko
│           │   │   │   ├── platform
│           │   │   │   │   ├── aspeed-video.ko
│           │   │   │   │   ├── cadence
│           │   │   │   │   │   ├── cdns-csi2rx.ko
│           │   │   │   │   │   └── cdns-csi2tx.ko
│           │   │   │   │   └── marvell-ccic
│           │   │   │   │       ├── cafe_ccic.ko
│           │   │   │   │       └── mcam-core.ko
│           │   │   │   ├── usb
│           │   │   │   │   ├── cpia2
│           │   │   │   │   │   └── cpia2.ko
│           │   │   │   │   ├── em28xx
│           │   │   │   │   │   ├── em28xx-alsa.ko
│           │   │   │   │   │   ├── em28xx.ko
│           │   │   │   │   │   └── em28xx-v4l.ko
│           │   │   │   │   ├── gspca
│           │   │   │   │   │   ├── gl860
│           │   │   │   │   │   │   └── gspca_gl860.ko
│           │   │   │   │   │   ├── gspca_benq.ko
│           │   │   │   │   │   ├── gspca_conex.ko
│           │   │   │   │   │   ├── gspca_cpia1.ko
│           │   │   │   │   │   ├── gspca_dtcs033.ko
│           │   │   │   │   │   ├── gspca_etoms.ko
│           │   │   │   │   │   ├── gspca_finepix.ko
│           │   │   │   │   │   ├── gspca_jeilinj.ko
│           │   │   │   │   │   ├── gspca_jl2005bcd.ko
│           │   │   │   │   │   ├── gspca_kinect.ko
│           │   │   │   │   │   ├── gspca_konica.ko
│           │   │   │   │   │   ├── gspca_main.ko
│           │   │   │   │   │   ├── gspca_mars.ko
│           │   │   │   │   │   ├── gspca_mr97310a.ko
│           │   │   │   │   │   ├── gspca_nw80x.ko
│           │   │   │   │   │   ├── gspca_ov519.ko
│           │   │   │   │   │   ├── gspca_ov534_9.ko
│           │   │   │   │   │   ├── gspca_ov534.ko
│           │   │   │   │   │   ├── gspca_pac207.ko
│           │   │   │   │   │   ├── gspca_pac7302.ko
│           │   │   │   │   │   ├── gspca_pac7311.ko
│           │   │   │   │   │   ├── gspca_se401.ko
│           │   │   │   │   │   ├── gspca_sn9c2028.ko
│           │   │   │   │   │   ├── gspca_sn9c20x.ko
│           │   │   │   │   │   ├── gspca_sonixb.ko
│           │   │   │   │   │   ├── gspca_sonixj.ko
│           │   │   │   │   │   ├── gspca_spca1528.ko
│           │   │   │   │   │   ├── gspca_spca500.ko
│           │   │   │   │   │   ├── gspca_spca501.ko
│           │   │   │   │   │   ├── gspca_spca505.ko
│           │   │   │   │   │   ├── gspca_spca506.ko
│           │   │   │   │   │   ├── gspca_spca508.ko
│           │   │   │   │   │   ├── gspca_spca561.ko
│           │   │   │   │   │   ├── gspca_sq905c.ko
│           │   │   │   │   │   ├── gspca_sq905.ko
│           │   │   │   │   │   ├── gspca_sq930x.ko
│           │   │   │   │   │   ├── gspca_stk014.ko
│           │   │   │   │   │   ├── gspca_stk1135.ko
│           │   │   │   │   │   ├── gspca_stv0680.ko
│           │   │   │   │   │   ├── gspca_sunplus.ko
│           │   │   │   │   │   ├── gspca_t613.ko
│           │   │   │   │   │   ├── gspca_topro.ko
│           │   │   │   │   │   ├── gspca_touptek.ko
│           │   │   │   │   │   ├── gspca_tv8532.ko
│           │   │   │   │   │   ├── gspca_vc032x.ko
│           │   │   │   │   │   ├── gspca_vicam.ko
│           │   │   │   │   │   ├── gspca_xirlink_cit.ko
│           │   │   │   │   │   ├── gspca_zc3xx.ko
│           │   │   │   │   │   ├── m5602
│           │   │   │   │   │   │   └── gspca_m5602.ko
│           │   │   │   │   │   └── stv06xx
│           │   │   │   │   │       └── gspca_stv06xx.ko
│           │   │   │   │   ├── pwc
│           │   │   │   │   │   └── pwc.ko
│           │   │   │   │   ├── s2255
│           │   │   │   │   │   └── s2255drv.ko
│           │   │   │   │   ├── stkwebcam
│           │   │   │   │   │   └── stkwebcam.ko
│           │   │   │   │   ├── usbtv
│           │   │   │   │   │   └── usbtv.ko
│           │   │   │   │   ├── uvc
│           │   │   │   │   │   └── uvcvideo.ko
│           │   │   │   │   └── zr364xx
│           │   │   │   │       └── zr364xx.ko
│           │   │   │   └── v4l2-core
│           │   │   │       ├── tuner.ko
│           │   │   │       ├── v4l2-dv-timings.ko
│           │   │   │       ├── v4l2-fwnode.ko
│           │   │   │       ├── videobuf-core.ko
│           │   │   │       ├── videobuf-vmalloc.ko
│           │   │   │       └── videodev.ko
│           │   │   ├── mfd
│           │   │   │   ├── axp20x-i2c.ko
│           │   │   │   ├── axp20x.ko
│           │   │   │   ├── cros_ec_dev.ko
│           │   │   │   ├── intel-lpss-acpi.ko
│           │   │   │   ├── intel-lpss.ko
│           │   │   │   ├── intel-lpss-pci.ko
│           │   │   │   ├── intel-m10-bmc.ko
│           │   │   │   ├── intel_pmc_bxt.ko
│           │   │   │   ├── intel_soc_pmic_bxtwc.ko
│           │   │   │   ├── intel_soc_pmic_chtdc_ti.ko
│           │   │   │   ├── intel_soc_pmic_mrfld.ko
│           │   │   │   ├── lpc_ich.ko
│           │   │   │   ├── lpc_sch.ko
│           │   │   │   ├── rdc321x-southbridge.ko
│           │   │   │   └── vx855.ko
│           │   │   ├── misc
│           │   │   │   ├── eeprom
│           │   │   │   │   └── eeprom_93cx6.ko
│           │   │   │   ├── lis3lv02d
│           │   │   │   │   └── lis3lv02d.ko
│           │   │   │   ├── mei
│           │   │   │   │   ├── hdcp
│           │   │   │   │   │   └── mei_hdcp.ko
│           │   │   │   │   ├── mei.ko
│           │   │   │   │   ├── mei-me.ko
│           │   │   │   │   └── mei-txe.ko
│           │   │   │   ├── pvpanic.ko
│           │   │   │   ├── vmw_balloon.ko
│           │   │   │   └── vmw_vmci
│           │   │   │       └── vmw_vmci.ko
│           │   │   ├── mmc
│           │   │   │   └── core
│           │   │   │       └── sdio_uart.ko
│           │   │   ├── mux
│           │   │   │   └── mux-core.ko
│           │   │   ├── net
│           │   │   │   ├── ethernet
│           │   │   │   │   ├── 3com
│           │   │   │   │   │   ├── 3c59x.ko
│           │   │   │   │   │   └── typhoon.ko
│           │   │   │   │   ├── 8390
│           │   │   │   │   │   ├── 8390.ko
│           │   │   │   │   │   └── ne2k-pci.ko
│           │   │   ���   │   ├── adaptec
│           │   │   │   │   │   └── starfire.ko
│           │   │   │   │   ├── agere
│           │   │   │   │   │   └── et131x.ko
│           │   │   │   │   ├── alacritech
│           │   │   │   │   │   └── slicoss.ko
│           │   │   │   │   ├── alteon
│           │   │   │   │   │   └── acenic.ko
│           │   │   │   │   ├── altera
│           │   │   │   │   │   └── altera_tse.ko
│           │   │   │   │   ├── amazon
│           │   │   │   │   │   └── ena
│           │   │   │   │   │       └── ena.ko
│           │   │   │   │   ├── amd
│           │   │   │   │   │   ├── amd8111e.ko
│           │   │   │   │   │   └── pcnet32.ko
│           │   │   │   │   ├── aquantia
│           │   │   │   │   │   └── atlantic
│           │   │   │   │   │       └── atlantic.ko
│           │   │   │   │   ├── atheros
│           │   │   │   │   │   ├── alx
│           │   │   │   │   │   │   └── alx.ko
│           │   │   │   │   │   ├── atl1c
│           │   │   │   │   │   │   └── atl1c.ko
│           │   │   │   │   │   ├── atl1e
│           │   │   │   │   │   │   └── atl1e.ko
│           │   │   │   │   │   └── atlx
│           │   │   │   │   │       ├── atl1.ko
│           │   │   │   │   │       └── atl2.ko
│           │   │   │   │   ├── aurora
│           │   │   │   │   │   └── nb8800.ko
│           │   │   │   │   ├── broadcom
│           │   │   │   │   │   ├── b44.ko
│           │   │   │   │   │   ├── bcmsysport.ko
│           │   │   │   │   │   ├── bnx2.ko
│           │   │   │   │   │   ├── cnic.ko
│           │   │   │   │   │   ├── genet
│           │   │   │   │   │   │   └── genet.ko
│           │   │   │   │   │   └── tg3.ko
│           │   │   │   │   ├── cadence
│           │   │   │   │   │   ├── macb.ko
│           │   │   │   │   │   └── macb_pci.ko
│           │   │   │   │   ├── cavium
│           │   │   │   │   │   ├── common
│           │   │   │   │   │   │   └── cavium_ptp.ko
│           │   │   │   │   │   ├── liquidio
│           │   │   │   │   │   │   ├── liquidio.ko
│           │   │   │   │   │   │   └── liquidio_vf.ko
│           │   │   │   │   │   └── thunder
│           │   │   │   │   │       ├── nicpf.ko
│           │   │   │   │   │       ├── nicvf.ko
│           │   │   │   │   │       ├── thunder_bgx.ko
│           │   │   │   │   │       └── thunder_xcv.ko
│           │   │   │   │   ├── dec
│           │   │   │   │   │   └── tulip
│           │   │   │   │   │       ├── de2104x.ko
│           │   │   │   │   │       ├── de4x5.ko
│           │   │   │   │   │       ├── dmfe.ko
│           │   │   │   │   │       ├── tulip.ko
│           │   │   │   │   │       ├── uli526x.ko
│           │   │   │   │   │       └── winbond-840.ko
│           │   │   │   │   ├── dlink
│           │   │   │   │   │   ├── dl2k.ko
│           │   │   │   │   │   └── sundance.ko
│           │   │   │   │   ├── dnet.ko
│           │   │   │   │   ├── ec_bhf.ko
│           │   │   │   │   ├── ethoc.ko
│           │   │   │   │   ├── fealnx.ko
│           │   │   │   │   ├── google
│           │   │   │   │   │   └── gve
│           │   │   │   │   │       └── gve.ko
│           │   │   │   │   ├── huawei
│           │   │   │   │   │   └── hinic
│           │   │   │   │   │       └── hinic.ko
│           │   │   │   │   ├── intel
│           │   │   │   │   │   ├── e1000
│           │   │   │   │   │   │   └── e1000.ko
│           │   │   │   │   │   ├── e1000e
│           │   │   │   │   │   │   └── e1000e.ko
│           │   │   │   │   │   ├── e100.ko
│           │   │   │   │   │   ├── i40e
│           │   │   │   │   │   │   └── i40e.ko
│           │   │   │   │   │   ├── ice
│           │   │   │   │   │   │   └── ice.ko
│           │   │   │   │   │   ├── igb
│           │   │   │   │   │   │   └── igb.ko
│           │   │   │   │   │   ├── igbvf
│           │   │   │   │   │   │   └── igbvf.ko
│           │   │   │   │   │   └── igc
│           │   │   │   │   │       └── igc.ko
│           │   │   │   │   ├── jme.ko
│           │   │   │   │   ├── marvell
│           │   │   │   │   │   ├── mvmdio.ko
│           │   │   │   │   │   ├── skge.ko
│           │   │   │   │   │   └── sky2.ko
│           │   │   │   │   ├── micrel
│           │   │   │   │   │   ├── ks8842.ko
│           │   │   │   │   │   ├── ks8851.ko
│           │   │   │   │   │   ├── ks8851_mll.ko
│           │   │   │   │   │   └── ksz884x.ko
│           │   │   │   │   ├── microchip
│           │   │   │   │   │   ├── enc28j60.ko
│           │   │   │   │   │   ├── encx24j600.ko
│           │   │   │   │   │   ├── encx24j600-regmap.ko
│           │   │   │   │   │   └── lan743x.ko
│           │   │   │   │   ├── natsemi
│           │   │   │   │   │   ├── natsemi.ko
│           │   │   │   │   │   └── ns83820.ko
│           │   │   │   │   ├── nvidia
│           │   │   │   │   │   └── forcedeth.ko
│           │   │   │   │   ���── packetengines
│           │   │   │   │   │   ├── hamachi.ko
│           │   │   │   │   │   └── yellowfin.ko
│           │   │   │   │   ├── pensando
│           │   │   │   │   │   └── ionic
│           │   │   │   │   │       └── ionic.ko
│           │   │   │   │   ├── qualcomm
│           │   │   │   │   │   └── emac
│           │   │   │   │   │       └── qcom-emac.ko
│           │   │   │   │   ├── rdc
│           │   │   │   │   │   └── r6040.ko
│           │   │   │   │   ├── realtek
│           │   │   │   │   │   ├── 8139cp.ko
│           │   │   │   │   │   ├── 8139too.ko
│           │   │   │   │   │   └── r8169.ko
│           │   │   │   │   ├── silan
│           │   │   │   │   │   └── sc92031.ko
│           │   │   │   │   ├── sis
│           │   │   │   │   │   ├── sis190.ko
│           │   │   │   │   │   └── sis900.ko
│           │   │   │   │   ├── smsc
│           │   │   │   │   │   ├── epic100.ko
│           │   │   │   │   │   ├── smsc911x.ko
│           │   │   │   │   │   └── smsc9420.ko
│           │   │   │   │   ├── stmicro
│           │   │   │   │   │   └── stmmac
│           │   │   │   │   │       ├── dwmac-generic.ko
│           │   │   │   │   │       ├── dwmac-intel.ko
│           │   │   │   │   │       ├── stmmac.ko
│           │   │   │   │   │       ├── stmmac-pci.ko
│           │   │   │   │   │       └── stmmac-platform.ko
│           │   │   │   │   ├── synopsys
│           │   │   │   │   │   └── dwc-xlgmac.ko
│           │   │   │   │   ├── ti
│           │   │   │   │   │   └── tlan.ko
│           │   │   │   │   ├── via
│           │   │   │   │   │   ├── via-rhine.ko
│           │   │   │   │   │   └── via-velocity.ko
│           │   │   │   │   └── xilinx
│           │   │   │   │       ├── ll_temac.ko
│           │   │   │   │       └── xilinx_emac.ko
│           │   │   │   ├── hyperv
│           │   │   │   │   └── hv_netvsc.ko
│           │   │   │   ├── mdio
│           │   │   │   │   ├── mdio-bcm-unimac.ko
│           │   │   │   │   ├── mdio-cavium.ko
│           │   │   │   │   ├── mdio-i2c.ko
│           │   │   │   │   └── mdio-thunder.ko
│           │   │   │   ├── mdio.ko
│           │   │   │   ├── mii.ko
│           │   │   │   ├── net_failover.ko
│           │   │   │   ├── pcs
│           │   │   │   │   └── pcs-xpcs.ko
│           │   │   │   ├── phy
│           │   │   │   │   ├── adin.ko
│           │   │   │   │   ├── amd.ko
│           │   │   │   │   ├── aquantia.ko
│           │   │   │   │   ├── at803x.ko
│ ��         │   │   │   │   ├── ax88796b.ko
│           │   │   │   │   ├── bcm54140.ko
│           │   │   │   │   ├── bcm7xxx.ko
│           │   │   │   │   ├── bcm84881.ko
│           │   │   │   │   ├── bcm87xx.ko
│           │   │   │   │   ├── cicada.ko
│           │   │   │   │   ├── davicom.ko
│           │   │   │   │   ├── dp83822.ko
│           │   │   │   │   ├── dp83848.ko
│           │   │   │   │   ├── dp83867.ko
│           │   │   │   │   ├── dp83869.ko
│           │   │   │   │   ├── dp83tc811.ko
│           │   │   │   │   ├── et1011c.ko
│           │   │   │   │   ├── fixed_phy.ko
│           │   │   │   │   ├── icplus.ko
│           │   │   │   │   ├── intel-xway.ko
│           │   │   │   │   ├── lxt.ko
│           │   │   │   │   ├── marvell.ko
│           │   │   │   │   ├── micrel.ko
│           │   │   │   │   ├── microchip.ko
│           │   │   │   │   ├── microchip_t1.ko
│           │   │   │   │   ├── mscc
│           │   │   │   │   │   └── mscc.ko
│           │   │   │   │   ├── national.ko
│           │   │   │   │   ├── nxp-tja11xx.ko
│           │   │   │   │   ├── phylink.ko
│           │   │   │   │   ├── qsemi.ko
│           │   │   │   │   ├── rockchip.ko
│           │   │   │   │   ├── sfp.ko
│           │   │   │   │   ├── smsc.ko
│           │   │   │   │   ├── ste10Xp.ko
│           │   │   │   │   ├── teranetics.ko
│           │   │   │   │   ├── uPD60620.ko
│           │   │   │   │   ├── vitesse.ko
│           │   │   │   │   └── xilinx_gmii2rgmii.ko
│           │   │   │   ├── ppp
│           │   │   │   │   ├── bsd_comp.ko
│           │   │   │   │   ├── ppp_async.ko
│           │   │   │   │   ├── ppp_deflate.ko
│           │   │   │   │   ├── ppp_generic.ko
│           │   │   │   │   ├── ppp_mppe.ko
│           │   │   │   │   ├── pppoe.ko
│           │   │   │   │   ├── pppox.ko
│           │   │   │   │   └── ppp_synctty.ko
│           │   │   │   ├── slip
│           │   │   │   │   └── slhc.ko
│           │   │   │   ├── thunderbolt-net.ko
│           │   │   │   ├── tun.ko
│           │   │   │   ├── usb
│           │   │   │   │   ├── aqc111.ko
│           │   │   │   │   ├── asix.ko
│           │   │   │   │   ├── ax88179_178a.ko
│           │   │   │   │   ├── catc.ko
│           │   │   │   │   ├── cdc_eem.ko
│           │   │   │   │   ├── cdc_ether.ko
│           │   │   │   │   ├── cdc_mbim.ko
│           │   │   │   │   ├── cdc_ncm.ko
│           │   │   │   │   ├── ch9200.ko
│           │   │   │   │   ├── cx82310_eth.ko
│           │   │   │   │   ├── dm9601.ko
│           │   │   │   │   ├── gl620a.ko
│           │   │   │   │   ├── hso.ko
│           │   │   │   │   ├── huawei_cdc_ncm.ko
│           │   │   │   │   ├── int51x1.ko
│           │   │   │   │   ├── ipheth.ko
│           │   │   │   │   ├── kalmia.ko
│           │   │   │   │   ├── kaweth.ko
│           │   │   │   │   ├── lan78xx.ko
│           │   │   │   │   ├── lg-vl600.ko
│           │   │   │   │   ├── mcs7830.ko
│           │   │   │   │   ├── net1080.ko
│           │   │   │   │   ├── pegasus.ko
│           │   │   │   │   ├── plusb.ko
│           │   │   │   │   ├── qmi_wwan.ko
│           │   │   │   │   ├── r8152.ko
│           │   │   │   │   ├── rndis_host.ko
│           │   │   │   │   ├── rtl8150.ko
│           │   │   │   │   ├── sierra_net.ko
│           │   │   │   │   ├── smsc75xx.ko
│           │   │   │   │   ├── smsc95xx.ko
│           │   │   │   │   ├── sr9700.ko
│           │   │   │   │   ├── sr9800.ko
│           │   │   │   │   ├── usbnet.ko
│           │   │   │   │   └── zaurus.ko
│           │   │   │   ├── virtio_net.ko
│           │   │   │   ├── vmxnet3
│           │   │   │   │   └── vmxnet3.ko
│           │   │   │   ├── wireless
│           │   │   │   │   ├── admtek
│           │   │   │   │   │   └── adm8211.ko
│           │   │   │   │   ├── ath
│           │   │   │   │   │   ├── ar5523
│           │   │   │   │   │   │   └── ar5523.ko
│           │   │   │   │   │   ├── ath10k
│           │   │   │   │   │   │   ├── ath10k_core.ko
│           │   │   │   │   │   │   ├── ath10k_pci.ko
│           │   │   │   │   │   │   ├── ath10k_sdio.ko
│           │   │   │   │   │   │   └── ath10k_usb.ko
│           │   │   │   │   │   ├── ath11k
│           │   │   │   │   │   │   ├── ath11k.ko
│           │   │   │   │   │   │   └── ath11k_pci.ko
│           │   │   │   │   │   ├── ath5k
│           │   │   │   │   │   │   └── ath5k.ko
│           │   │   │   │   │   ├── ath6kl
│           │   │   │   │   │   │   ├── ath6kl_core.ko
│           │   │   │   │   │   │   ├── ath6kl_sdio.ko
│           │   │   │   │   │   │   └── ath6kl_usb.ko
│           │   │   │   │   │   ├── ath9k
│           │   │   │   │   │   │   ├── ath9k_common.ko
│           │   │   │   │   │   │   ├── ath9k_htc.ko
│           │   │   │   │   │   │   ├── ath9k_hw.ko
│           │   │   │   │   │   │   ├── ath9k.ko
│           │   │   │   │   │   │   └── ath9k_pci_owl_loader.ko
│           │   │   │   │   │   ├── ath.ko
│           │   │   │   │   │   ├── carl9170
│           │   │   │   │   │   │   └── carl9170.ko
│           │   │   │   │   │   └── wcn36xx
│           │   │   │   │   │       └── wcn36xx.ko
│           │   │   │   │   ├── atmel
│           │   │   │   │   │   ├── at76c50x-usb.ko
│           │   │   │   │   │   ├── atmel.ko
│           │   │   │   │   │   └── atmel_pci.ko
│           │   │   │   │   ├── broadcom
│           │   │   │   │   │   ├── b43
│           │   │   │   │   │   │   └── b43.ko
│           │   │   │   │   │   ├── b43legacy
│           │   │   │   │   │   │   └── b43legacy.ko
│           │   │   │   │   │   └── brcm80211
│           │   │   │   │   │       ├── brcmfmac
│           │   │   │   │   │       │   └── brcmfmac.ko
│           │   │   │   │   │       ├── brcmsmac
│           │   │   │   │   │       │   └── brcmsmac.ko
│           │   │   │   │   │       └── brcmutil
│           │   │   │   │   │           └── brcmutil.ko
│           │   │   │   │   ├── cisco
│           │   │   │   │   │   └── airo.ko
│           │   │   │   │   ├── intel
│           │   │   │   │   │   ├── ipw2x00
│           │   │   │   │   │   │   ├── ipw2100.ko
│           │   │   │   │   │   │   ├── ipw2200.ko
│           │   │   │   │   │   │   └── libipw.ko
│           │   │   │   │   │   ├── iwlegacy
│           │   │   │   │   │   │   ├── iwl3945.ko
│           │   │   │   │   │   │   ├── iwl4965.ko
│           │   │   │   │   │   │   └── iwlegacy.ko
│           │   │   │   │   │   └── iwlwifi
│           │   │   │   │   │       ├── dvm
│           │   │   │   │   │       │   └── iwldvm.ko
│           │   │   │   │   │       ├── iwlwifi.ko
│           │   │   │   │   │       └── mvm
│           │   │   │   │   │           └── iwlmvm.ko
│           │   │   │   │   ├── intersil
│           │   │   │   │   │   ├── hostap
│           │   │   │   │   │   │   ├── hostap.ko
│           │   │   │   │   │   │   ├── hostap_pci.ko
│           │   │   │   │   │   │   └── hostap_plx.ko
│           │   │   │   │   │   ├── orinoco
│           │   │   │   │   │   │   ├── orinoco.ko
│           │   │   │   │   │   │   ├── orinoco_nortel.ko
│           │   │   │   │   │   │   ├── orinoco_plx.ko
│           │   │   │   │   │   │   ├── orinoco_tmd.ko
│           │   │   │   │   │   │   └── orinoco_usb.ko
│           │   │   │   │   │   └── p54
│           │   │   │   │   │       ├── p54common.ko
│           │   │   │   │   │       ├── p54pci.ko
│           │   │   │   │   │       ├── p54spi.ko
│           │   │   │   │   │       └── p54usb.ko
│           │   │   │   │   ├── marvell
│           │   │   │   │   │   ├── libertas
│           │   │   │   │   │   │   ├── libertas.ko
│           │   │   │   │   │   │   ├── libertas_sdio.ko
│           │   │   │   │   │   │   ├── libertas_spi.ko
│           │   │   │   │   │   │   └── usb8xxx.ko
│           │   │   │   │   │   ├── libertas_tf
│           │   │   │   │   │   │   ├── libertas_tf.ko
│           │   │   │   │   │   │   └── libertas_tf_usb.ko
│           │   │   │   │   │   ├── mwifiex
│           │   │   │   │   │   │   ├── mwifiex.ko
│           │   │   │   │   │   │   ├── mwifiex_pcie.ko
│           │   │   │   │   │   │   ├── mwifiex_sdio.ko
│           │   │   │   │   │   │   └── mwifiex_usb.ko
│           │   │   │   │   │   └── mwl8k.ko
│           │   │   │   │   ├── mediatek
│           │   │   │   │   │   ├── mt76
│           │   │   │   │   │   │   ├── mt7603
│           │   │   │   │   │   │   │   └── mt7603e.ko
│           │   │   │   │   │   │   ├── mt7615
│           │   │   │   │   │   │   │   ├── mt7615-common.ko
│           │   │   │   │   │   │   │   ├── mt7615e.ko
│           │   │   │   │   │   │   │   ├── mt7663s.ko
│           │   │   │   │   │   │   │   ├── mt7663u.ko
│           │   │   │   │   │   │   │   └── mt7663-usb-sdio-common.ko
│           │   │   │   │   │   │   ├── mt76.ko
│           │   │   │   │   │   │   ├── mt76-sdio.ko
│           │   │   │   │   │   │   ├── mt76-usb.ko
│           │   │   │   │   │   │   ├── mt76x0
│           │   │   │   │   │   │   │   ├── mt76x0-common.ko
│           │   │   │   │   │   │   │   ├── mt76x0e.ko
│           │   │   │   │   │   │   │   └── mt76x0u.ko
│           │   │   │   │   │   │   ├── mt76x02-lib.ko
│           │   │   │   │   │   │   ├── mt76x02-usb.ko
│           │   │   │   │   │   │   ├── mt76x2
│           │   │   │   │   │   │   │   ├── mt76x2-common.ko
│           │   │   │   │   │   │   │   ├── mt76x2e.ko
│           │   │   │   │   │   │   │   └── mt76x2u.ko
│           │   │   │   │   │   │   └── mt7915
│           │   │   │   │   │   │       └── mt7915e.ko
│           │   │   │   │   │   └── mt7601u
│           │   │   │   │   │       └── mt7601u.ko
│           │   │   │   │   ├── microchip
│           │   │   │   │   │   └── wilc1000
│           │   │   │   │   │       ├── wilc1000.ko
│           │   │   │   │   │       ├── wilc1000-sdio.ko
│           │   │   │   │   │       └── wilc1000-spi.ko
│           │   │   │   │   ├── quantenna
│           │   │   │   │   │   └── qtnfmac
│           │   │   │   │   │       ├── qtnfmac.ko
│           │   │   │   │   │       └── qtnfmac_pcie.ko
│           │   │   │   │   ├── ralink
│           │   │   │   │   │   └── rt2x00
│           │   │   │   │   │       ├── rt2400pci.ko
│           │   │   │   │   │       ├── rt2500pci.ko
│           │   │   │   │   │       ├── rt2500usb.ko
│           │   │   │   │   │       ├── rt2800lib.ko
│           │   │   │   │   │       ├── rt2800mmio.ko
│           │   │   │   │   │       ├── rt2800pci.ko
│           │   │   │   │   │       ├── rt2800usb.ko
│           │   │   │   │   │       ├── rt2x00lib.ko
│           │   │   │   │   │       ├── rt2x00mmio.ko
│           │   │   │   │   │       ├── rt2x00pci.ko
│           │   │   │   │   │       ├── rt2x00usb.ko
│           │   │   │   │   │       ├── rt61pci.ko
│           │   │   │   │   │       └── rt73usb.ko
│           │   │   │   │   ├── realtek
│           │   │   │   │   │   ├── rtl818x
│           │   │   │   │   │   │   ├── rtl8180
│           │   │   │   │   │   │   │   └── rtl818x_pci.ko
│           │   │   │   │   │   │   └── rtl8187
│           │   │   │   │   │   │       └── rtl8187.ko
│           │   │   │   │   │   ├── rtl8xxxu
│           │   │   │   │   │   │   └── rtl8xxxu.ko
│           │   │   │   │   │   ├── rtlwifi
│           │   │   │   │   │   │   ├── btcoexist
│           │   │   │   │   │   │   │   └── btcoexist.ko
│           │   │   │   │   │   │   ├── rtl8188ee
│           │   │   │   │   │   │   │   └── rtl8188ee.ko
│           │   │   │   │   │   │   ├── rtl8192c
│           │   │   │   │   │   │   │   └── rtl8192c-common.ko
│           │   │   │   │   │   │   ├── rtl8192ce
│           │   │   │   │   │   │   │   └── rtl8192ce.ko
│           │   │   │   │   │   │   ├── rtl8192cu
│           │   │   │   │   │   │   │   └── rtl8192cu.ko
│           │   │   │   │   │   │   ├── rtl8192de
│           │   │   │   │   │   │   │   └── rtl8192de.ko
│           │   │   │   │   │   │   ├── rtl8192ee
│           │   │   │   │   │   │   │   └── rtl8192ee.ko
│           │   │   │   │   │   │   ├── rtl8192se
│           │   │   │   │   │   │   │   └── rtl8192se.ko
│           │   │   │   │   │   │   ├── rtl8723ae
│           │   │   │   │   │   │   │   └── rtl8723ae.ko
│           │   │   │   │   │   │   ├── rtl8723be
│           │   │   │   │   │   │   │   └── rtl8723be.ko
│           │   │   │   │   │   ���   ├── rtl8723com
│           │   │   │   │   │   │   │   └── rtl8723-common.ko
│           │   │   │   │   │   │   ├── rtl8821ae
│           │   │   │   │   │   │   │   └── rtl8821ae.ko
│           │   │   │   │   │   │   ├── rtl_pci.ko
│           │   │   │   │   │   │   ├── rtl_usb.ko
│           │   │   │   │   │   │   └── rtlwifi.ko
│           │   │   │   │   │   └── rtw88
│           │   │   │   │   │       ├── rtw88_8723de.ko
│           │   │   │   │   │       ├── rtw88_8723d.ko
│           │   │   │   │   │       ├── rtw88_8821ce.ko
│           │   │   │   │   │       ├── rtw88_8821c.ko
│           │   │   │   │   │       ├── rtw88_8822be.ko
│           │   │   │   │   │       ├── rtw88_8822b.ko
│           │   │   │   │   │       ├── rtw88_8822ce.ko
│           │   │   │   │   │       ├── rtw88_8822c.ko
│           │   │   │   │   │       ├── rtw88_core.ko
│           │   │   │   │   │       └── rtw88_pci.ko
│           │   │   │   │   ├── rndis_wlan.ko
│           │   │   │   │   ├── rsi
│           │   │   │   │   │   ├── rsi_91x.ko
│           │   │   │   │   │   ├── rsi_sdio.ko
│           │   │   │   │   │   └── rsi_usb.ko
│           │   │   │   │   ├── st
│           │   │   │   │   │   └── cw1200
│           │   │   │   │   │       ├── cw1200_core.ko
│           │   │   │   │   │       ├── cw1200_wlan_sdio.ko
│           │   │   │   │   │       └── cw1200_wlan_spi.ko
│           │   │   │   │   ├── ti
│           │   │   │   │   │   ├── wl1251
│           │   │   │   │   │   │   ├── wl1251.ko
│           │   │   │   │   │   │   ├── wl1251_sdio.ko
│           │   │   │   │   │   │   └── wl1251_spi.ko
│           │   │   │   │   │   ├── wl12xx
│           │   │   │   │   │   │   └── wl12xx.ko
│           │   │   │   │   │   ├── wl18xx
│           │   │   │   │   │   │   └── wl18xx.ko
│           │   │   │   │   │   └── wlcore
│           │   │   │   │   │       ├── wlcore.ko
│           │   │   │   │   │       └── wlcore_sdio.ko
│           │   │   │   │   └── zydas
│           │   │   │   │       ├── zd1201.ko
│           │   │   │   │       └── zd1211rw
│           │   │   │   │           └── zd1211rw.ko
│           │   │   │   ├── xen-netback
│           │   │   │   │   └── xen-netback.ko
│           │   │   │   └── xen-netfront.ko
│           │   │   ├── nvdimm
│           │   │   │   ├── nd_blk.ko
│           │   │   │   ├── nd_btt.ko
│           │   │   │   ├── nd_pmem.ko
│           │   │   │   ├── nd_virtio.ko
│           │   │   │   └── virtio_pmem.ko
│           │   │   ├── nvmem
│           │   │   │   └── nvmem_qcom-spmi-sdam.ko
│           │   │   ├── parport
│           │   │   │   ├── parport.ko
│           │   │   │   ├── parport_pc.ko
│           │   │   │   └── parport_serial.ko
│           │   │   ├── pci
│           │   │   │   ├── controller
│           │   │   │   │   ├── pci-hyperv-intf.ko
│           │   │   │   │   ├── pci-hyperv.ko
│           │   │   │   │   └── vmd.ko
│           │   │   │   ├── hotplug
│           │   │   │   │   ├── acpiphp_ibm.ko
│           │   │   │   │   ├── cpcihp_generic.ko
│           │   │   │   │   └── cpcihp_zt5550.ko
│           │   │   │   ├── pci-pf-stub.ko
│           │   │   │   ├── pci-stub.ko
│           │   │   │   └── xen-pcifront.ko
│           │   │   ├── phy
│           │   │   │   ├── intel
│           │   │   │   │   └── phy-intel-lgm-emmc.ko
│           │   │   │   └── phy-lgm-usb.ko
│           │   │   ├── platform
│           │   │   │   ├── chrome
│           │   │   │   │   ├── chromeos_laptop.ko
│           │   │   │   │   ├── chromeos_pstore.ko
│           │   │   │   │   ├── chromeos_tbmc.ko
│           │   │   │   │   ├── cros_ec_chardev.ko
│           │   │   │   │   ├── cros_ec_i2c.ko
│           │   │   │   │   ├── cros_ec_ishtp.ko
│           │   │   │   │   ├── cros_ec.ko
│           │   │   │   │   ├── cros_ec_lightbar.ko
│           │   │   │   │   ├── cros_ec_lpcs.ko
│           │   │   │   │   ├── cros-ec-sensorhub.ko
│           │   │   │   │   ├── cros_ec_spi.ko
│           │   │   │   │   ├── cros_ec_sysfs.ko
│           │   │   │   │   ├── cros_ec_typec.ko
│           │   │   │   │   ├── cros_kbd_led_backlight.ko
│           │   │   │   │   ├── cros_usbpd_notify.ko
│           │   │   │   │   └── wilco_ec
│           │   │   │   │       ├── wilco_ec_events.ko
│           │   │   │   │       ├── wilco_ec.ko
│           │   │   │   │       └── wilco_ec_telem.ko
│           │   │   │   └── x86
│           │   │   │       ├── acerhdf.ko
│           │   │   │       ├── acer-wireless.ko
│           │   │   │       ├── acer-wmi.ko
│           │   │   │       ├── alienware-wmi.ko
│           │   │   │       ├── amilo-rfkill.ko
│           │   │   │       ├── apple-gmux.ko
│           │   │   │       ├── asus-laptop.ko
│           │   │   │       ├── asus-wireless.ko
│           │   │   │       ├── classmate-laptop.ko
│           │   │   │       ├── compal-laptop.ko
│           │   │   │       ├── dcdbas.ko
│           │   │   │       ├── dell-laptop.ko
│           │   │   │       ├── dell-rbtn.ko
│           │   │   │       ├── dell-smbios.ko
│           │   │   │       ├── dell-smo8800.ko
│           │   │   │       ├── dell-wmi-aio.ko
│           │   │   │       ├── dell-wmi-descriptor.ko
│           │   │   │       ├── dell-wmi.ko
│           │   │   │       ├── dell-wmi-led.ko
│           │   │   │       ├── fujitsu-laptop.ko
│           │   │   │       ├── fujitsu-tablet.ko
│           │   │   │       ├── gpd-pocket-fan.ko
│           │   │   │       ├── hdaps.ko
│           │   │   │       ├── hp_accel.ko
│           │   │   │       ├── hp-wireless.ko
│           │   │   │       ├── hp-wmi.ko
│           │   │   │       ├── huawei-wmi.ko
│           │   │   │       ├── i2c-multi-instantiate.ko
│           │   │   │       ├── ibm_rtl.ko
│           │   │   │       ├── ideapad-laptop.ko
│           │   │   │       ├── intel_atomisp2_led.ko
│           │   │   │       ├── intel_atomisp2_pm.ko
│           │   │   │       ├── intel_bxtwc_tmu.ko
│           │   │   │       ├── intel_chtdc_ti_pwrbtn.ko
│           │   │   │       ├── intel-hid.ko
│           │   │   │       ├── intel_int0002_vgpio.ko
│           │   │   │       ├── intel_ips.ko
│           │   │   │       ├── intel_menlow.ko
│           │   │   │       ├── intel_mid_powerbtn.ko
│           │   │   │       ├── intel_mid_thermal.ko
│           │   │   │       ├── intel_mrfld_pwrbtn.ko
│           │   │   │       ├── intel_oaktrail.ko
│           │   │   │       ├── intel_punit_ipc.ko
│           │   │   │       ├── intel-rst.ko
│           │   │   │       ├── intel_scu_ipcutil.ko
│           │   │   │       ├── intel_scu_pltdrv.ko
│           │   │   │       ├── intel-smartconnect.ko
│           │   │   │       ├── intel_speed_select_if
│           │   │   │       │   ├── isst_if_common.ko
│           │   │   │       │   ├── isst_if_mbox_msr.ko
│           │   │   │       │   ├── isst_if_mbox_pci.ko
│           │   │   │       │   └── isst_if_mmio.ko
│           │   │   │       ├── intel_telemetry_core.ko
│           │   │   │       ├── intel_telemetry_debugfs.ko
│           │   │   │       ├── intel_telemetry_pltdrv.ko
│           │   │   │       ├── intel-uncore-frequency.ko
│           │   │   │       ├── intel-vbtn.ko
│           │   │   │       ├── intel-wmi-sbl-fw-update.ko
│           │   │   │       ├── intel-wmi-thunderbolt.ko
│           │   │   │       ├── lg-laptop.ko
│           │   │   │       ├── mlx-platform.ko
│           │   │   │       ├── msi-laptop.ko
│           │   │   │       ├── msi-wmi.ko
│           │   │   │       ├── mxm-wmi.ko
│           │   │   │       ├── panasonic-laptop.ko
│           │   │   │       ├── pcengines-apuv2.ko
│           │   │   │       ├── peaq-wmi.ko
│           │   │   │       ├── samsung-laptop.ko
│           │   │   │       ├── samsung-q10.ko
│           │   │   │       ├── sony-laptop.ko
│           │   │   │       ├── surface3_button.ko
│           │   │   │       ├── surface3_power.ko
│           │   │   │       ├── surface3-wmi.ko
│           │   │   │       ├── surfacepro3_button.ko
│           │   │   │       ├── system76_acpi.ko
│           │   │   │       ├── thinkpad_acpi.ko
│           │   │   │       ├── topstar-laptop.ko
│           │   │   │       ├── toshiba_acpi.ko
│           │   │   │       ├── toshiba_bluetooth.ko
│           │   │   │       ├── toshiba_haps.ko
│           │   │   │       ├── toshiba-wmi.ko
│           │   │   │       ├── wmi.ko
│           │   │   │       └── xiaomi-wmi.ko
│           │   │   ├── power
│           │   │   │   └── supply
│           │   │   │       ├── axp20x_ac_power.ko
│           │   │   │       ├── axp20x_battery.ko
│           │   │   │       ├── axp20x_usb_power.ko
│           │   │   │       ├── axp288_charger.ko
│           │   │   │       ├── axp288_fuel_gauge.ko
│           │   │   │       ├── generic-adc-battery.ko
│           │   │   │       ├── gpio-charger.ko
│           │   │   │       └── wilco-charger.ko
│           │   │   ├── powercap
│           │   │   │   ├── intel_rapl_common.ko
│           │   │   │   └── intel_rapl_msr.ko
│           │   │   ├── pps
│           │   │   │   └── pps_core.ko
│           │   │   ├── ptp
│           │   │   │   ├── ptp.ko
│           │   │   │   ├── ptp_kvm.ko
│           │   │   │   └── ptp_vmw.ko
│           │   │   ├── pwm
│           │   │   │   ├── pwm-cros-ec.ko
│           │   │   │   ├── pwm-lpss.ko
│           │   │   │   ├── pwm-lpss-pci.ko
│           │   │   │   ├── pwm-lpss-platform.ko
│           │   │   │   └── pwm-pca9685.ko
│           │   │   ├── regulator
│           │   │   │   ├── axp20x-regulator.ko
│           │   │   │   ├── fixed.ko
│           │   │   │   ├── gpio-regulator.ko
│           │   │   │   └── pwm-regulator.ko
│           │   │   ├── rpmsg
│           │   │   │   ├── rpmsg_core.ko
│           │   │   │   └── virtio_rpmsg_bus.ko
│           │   │   ├── rtc
│           │   │   │   ├── rtc-cros-ec.ko
│           │   │   │   └── rtc-wilco-ec.ko
│           │   │   ├── scsi
│           │   │   │   └── sg.ko
│           │   │   ├── soc
│           │   │   │   └── qcom
│           │   │   │       └── qmi_helpers.ko
│           │   │   ├── soundwire
│           │   │   │   ├── soundwire-cadence.ko
│           │   │   │   ├── soundwire-generic-allocation.ko
│           │   │   │   └── soundwire-intel.ko
│           │   │   ├── spi
│           │   │   │   ├── spi-altera.ko
│           │   │   │   ├── spi-amd.ko
│           │   │   │   ├── spi-axi-spi-engine.ko
│           │   │   │   ├── spi-bitbang.ko
│           │   │   │   ├── spi-butterfly.ko
│           │   │   │   ├── spi-cadence.ko
│           │   │   │   ├── spidev.ko
│           │   │   │   ├── spi-dw.ko
│           │   │   │   ├── spi-dw-mmio.ko
│           │   │   │   ├── spi-dw-pci.ko
│           │   │   │   ├── spi-gpio.ko
│           │   │   │   ├── spi-lantiq-ssc.ko
│           │   │   │   ├── spi-lm70llp.ko
│           │   │   │   ├── spi-mux.ko
│           │   │   │   ├── spi-mxic.ko
│           │   │   │   ├── spi-nxp-fspi.ko
│           │   │   │   ├── spi-oc-tiny.ko
│           │   │   │   ├── spi-pxa2xx-pci.ko
│           │   │   │   ├── spi-pxa2xx-platform.ko
│           │   │   │   ├── spi-rockchip.ko
│           │   │   │   ├── spi-sc18is602.ko
│           │   │   │   ├── spi-slave-system-control.ko
│           │   │   │   ├── spi-slave-time.ko
│           │   │   │   ├── spi-tle62x0.ko
│           │   │   │   ├── spi-xcomm.ko
│           │   │   │   ├── spi-xilinx.ko
│           │   │   │   └── spi-zynqmp-gqspi.ko
│           │   │   ├── spmi
│           │   │   │   └── spmi.ko
│           │   │   ├── ssb
│           │   │   │   └── ssb.ko
│           │   │   ├── staging
│           │   │   │   ├── ks7010
│           │   │   │   │   └── ks7010.ko
│           │   │   │   ├── rtl8188eu
│           │   │   │   │   └── r8188eu.ko
│           │   │   │   ├── rtl8192e
│           │   │   │   │   ├── rtl8192e
│           │   │   │   │   │   └── r8192e_pci.ko
│           │   │   │   │   ├── rtllib_crypt_ccmp.ko
│           │   │   │   │   ├── rtllib_crypt_tkip.ko
│           │   │   │   │   ├── rtllib_crypt_wep.ko
│           │   │   │   │   └── rtllib.ko
│           │   │   │   ├── rtl8192u
│           │   │   │   │   └── r8192u_usb.ko
│           │   │   │   ├── rtl8712
│           │   │   │   │   └── r8712u.ko
│           │   │   │   ├── rtl8723bs
│           │   │   │   │   └── r8723bs.ko
│           │   │   │   ├── rts5208
│           │   │   │   │   └── rts5208.ko
│           │   │   │   ├── wfx
│           │   │   │   │   └── wfx.ko
│           │   │   │   └── wlan-ng
│           │   │   │       └── prism2_usb.ko
│           │   │   ├── thermal
│           │   │   │   ├── intel
│           │   │   │   │   ├── int340x_thermal
│           │   │   │   │   │   ├── acpi_thermal_rel.ko
│           │   │   │   │   │   ├── int3400_thermal.ko
│           │   │   │   │   │   ├── int3402_thermal.ko
│           │   │   │   │   │   ├── int3403_thermal.ko
│           │   │   │   │   │   ├── int3406_thermal.ko
│           │   │   │   │   │   ├── int340x_thermal_zone.ko
│           │   │   │   │   │   └── processor_thermal_device.ko
│           │   │   │   │   ├── intel_bxt_pmic_thermal.ko
│           │   │   │   │   ├── intel_pch_thermal.ko
│           │   │   │   │   ├── intel_powerclamp.ko
│           │   │   │   │   ├── intel_soc_dts_iosf.ko
│           │   │   │   │   ├── intel_soc_dts_thermal.ko
│           │   │   │   │   └── x86_pkg_temp_thermal.ko
│           │   │   │   └── thermal-generic-adc.ko
│           │   │   ├── tty
│           │   │   │   ├── serdev
│           │   │   │   │   └── serdev.ko
│           │   │   │   └── serial
│           │   │   │       ├── 8250
│           │   │   │       │   ├── 8250_base.ko
│           │   │   │       │   ├── 8250_dw.ko
│           │   │   │       │   ├── 8250_exar.ko
│           │   │   │       │   ├── 8250.ko
│           │   │   │       │   ├── 8250_lpss.ko
│           │   │   │       │   ├── 8250_mid.ko
│           │   │   │       │   └── 8250_pci.ko
│           │   │   │       ├── serial_core.ko
│           │   │   │       └── serial_mctrl_gpio.ko
│           │   │   ├── uio
│           │   │   │   ├── uio_cif.ko
│           │   │   │   ├── uio_dmem_genirq.ko
│           │   │   │   ├── uio_hv_generic.ko
│           │   │   │   ├── uio.ko
│           │   │   │   ├── uio_pci_generic.ko
│           │   │   │   └── uio_pdrv_genirq.ko
│           │   │   ├── usb
│           │   │   │   ├── class
│           │   │   │   │   ├── cdc-acm.ko
│           │   │   │   │   ├── cdc-wdm.ko
│           │   │   │   │   └── usblp.ko
│           │   │   │   ├── common
│           │   │   │   │   ├── usb-conn-gpio.ko
│           │   │   │   │   └── usb-otg-fsm.ko
│           │   │   │   ├── core
│           │   │   │   │   └── ledtrig-usbport.ko
│           │   │   │   ├── host
│           │   │   │   │   ├── bcma-hcd.ko
│           │   │   │   │   └── ssb-hcd.ko
│           │   │   │   ├── image
│           │   │   │   │   └── microtek.ko
│           │   │   │   ├── misc
│           │   │   │   │   ├── appledisplay.ko
│           │   │   │   │   ├── apple-mfi-fastcharge.ko
│           │   │   │   │   └── ezusb.ko
│           │   │   │   ├── mon
│           │   │   │   │   └── usbmon.ko
│           │   │   │   ├── roles
│           │   │   │   │   ├── intel-xhci-usb-role-switch.ko
│           │   │   │   │   └── roles.ko
│           │   │   │   ├── serial
│           │   │   │   │   ├── aircable.ko
│           │   │   │   │   ├── ark3116.ko
│           │   │   │   │   ├── belkin_sa.ko
│           │   │   │   │   ├── ch341.ko
│           │   │   │   │   ├── cp210x.ko
│           │   │   │   │   ├── cyberjack.ko
│           │   │   │   │   ├── cypress_m8.ko
│           │   │   │   │   ├── digi_acceleport.ko
│           │   │   │   │   ├── empeg.ko
│           │   │   │   │   ├── f81232.ko
│           │   │   │   │   ├── f81534.ko
│           │   │   │   │   ├── ftdi_sio.ko
│           │   │   │   │   ├── garmin_gps.ko
│           │   │   │   │   ├── io_edgeport.ko
│           │   │   │   │   ├── io_ti.ko
│           │   │   │   │   ├── ipaq.ko
│           │   │   │   │   ├── ipw.ko
│           │   │   │   │   ├── ir-usb.ko
│           │   │   │   │   ├── iuu_phoenix.ko
│           │   │   │   │   ├── keyspan.ko
│           │   │   │   │   ├── keyspan_pda.ko
│           │   │   │   │   ├── kl5kusb105.ko
│           │   │   │   │   ├── kobil_sct.ko
│           │   │   │   │   ├── mct_u232.ko
│           │   │   │   │   ├── metro-usb.ko
│           │   │   │   │   ├── mos7720.ko
│           │   │   │   │   ├── mos7840.ko
│           │   │   │   │   ├── mxuport.ko
│           │   │   │   │   ├── navman.ko
│           │   │   │   │   ├── omninet.ko
│           │   │   │   │   ├── opticon.ko
│           │   │   │   │   ├── option.ko
│           │   │   │   │   ├── oti6858.ko
│           │   │   │   │   ├── pl2303.ko
│           │   │   │   │   ├── qcaux.ko
│           │   │   │   │   ├── qcserial.ko
│           │   │   │   │   ├── quatech2.ko
│           │   │   │   │   ├── safe_serial.ko
│           │   │   │   │   ├── sierra.ko
│           │   │   │   │   ├── spcp8x5.ko
│           │   │   │   │   ├── ssu100.ko
│           │   │   │   │   ├── symbolserial.ko
│           │   │   │   │   ├── ti_usb_3410_5052.ko
│           │   │   │   │   ├── upd78f0730.ko
│           │   │   │   │   ├── usbserial.ko
│           │   │   │   │   ├── usb-serial-simple.ko
│           │   │   │   │   ├── usb_wwan.ko
│           │   │   │   │   ├── visor.ko
│           │   │   │   │   ├── whiteheat.ko
│           │   │   │   │   ├── wishbone-serial.ko
│           │   │   │   │   └── xsens_mt.ko
│           │   │   │   └── typec
│           │   │   │       ├── altmodes
│           │   │   │       │   ├── typec_displayport.ko
│           │   │   │       │   └── typec_nvidia.ko
│           │   │   │       ├── hd3ss3220.ko
│           │   │   │       ├── mux
│           │   │   │       │   ├── intel_pmc_mux.ko
│           │   │   │       │   └── pi3usb30532.ko
│           │   │   │       ├── stusb160x.ko
│           │   │   │       ├── tcpm
│           │   │   │       │   ├── fusb302.ko
│           │   │   │       │   ├── tcpci.ko
│           │   │   │       │   ├── tcpci_maxim.ko
│           │   │   │       │   ├── tcpci_rt1711h.ko
│           │   │   │       │   └── tcpm.ko
│           │   │   │       ├── tps6598x.ko
│           │   │   │       ├── typec.ko
│           │   │   │       └── ucsi
│           │   │   │           ├── typec_ucsi.ko
│           │   │   │           ├── ucsi_acpi.ko
│           │   │   │           └── ucsi_ccg.ko
│           │   │   ├── video
│           │   │   │   ├── backlight
│           │   │   │   │   └── apple_bl.ko
│           │   │   │   └── fbdev
│           │   │   │       └── uvesafb.ko
│           │   │   ├── virt
│           │   │   │   └── vboxguest
│           │   │   │       └── vboxguest.ko
│           │   │   ├── virtio
│           │   │   │   ├── virtio_balloon.ko
│           │   │   │   ├── virtio_dma_buf.ko
│           │   │   │   ├── virtio_input.ko
│           │   │   │   └── virtio_mmio.ko
│           │   │   └── xen
│           │   │       ├── pvcalls-front.ko
│           │   │       ├── xen-acpi-processor.ko
│           │   │       ├── xen-front-pgdir-shbuf.ko
│           │   │       ├── xenfs
│           │   │       │   └── xenfs.ko
│           │   │       ├── xen-gntalloc.ko
│           │   │       ├── xen-gntdev.ko
│           │   │       ├── xen-pciback
│           │   │       │   └── xen-pciback.ko
│           │   │       └── xen-privcmd.ko
│           │   ├── fs
│           │   │   ├── cachefiles
│           │   │   │   └── cachefiles.ko
│           │   │   ├── cifs
│           │   │   │   └── cifs.ko
│           │   │   ├── efivarfs
│           │   │   │   └── efivarfs.ko
│           │   │   ├── fscache
│           │   │   │   └── fscache.ko
│           │   │   ├── lockd
│           │   │   │   └── lockd.ko
│           │   │   ├── nfs
│           │   │   │   ├── blocklayout
│           │   │   │   │   └── blocklayoutdriver.ko
│           │   │   │   ├── filelayout
│           │   │   │   │   └── nfs_layout_nfsv41_files.ko
│           │   │   │   ├── flexfilelayout
│           │   │   │   │   └── nfs_layout_flexfiles.ko
│           │   │   │   ├── nfs.ko
│           │   │   │   ├── nfsv2.ko
│           │   │   │   ├── nfsv3.ko
│           │   │   │   └── nfsv4.ko
│           │   │   ├── nfs_common
│           │   │   │   ├── grace.ko
│           │   │   │   └── nfs_ssc.ko
│           │   │   └── vboxsf
│           │   │       └── vboxsf.ko
│           │   ├── lib
│           │   │   ├── crc16.ko
│           │   │   ├── crc4.ko
│           │   │   ├── crc8.ko
│           │   │   ├── crc-ccitt.ko
│           │   │   ├── crypto
│           │   │   │   ├── libarc4.ko
│           │   │   │   ├── libchacha.ko
│           │   │   │   ├── libdes.ko
│           │   │   │   └── libpoly1305.ko
│           │   │   ├── lz4
│           │   │   │   ├── lz4_decompress.ko
│           │   │   │   └── lz4hc_compress.ko
│           │   │   ├── math
│           │   │   │   └── cordic.ko
│           │   │   ├── ts_bm.ko
│           │   │   ├── ts_fsm.ko
│           │   │   └── ts_kmp.ko
│           │   ├── net
│           │   │   ├── core
│           │   │   │   └── failover.ko
│           │   │   ├── dns_resolver
│           │   │   │   └── dns_resolver.ko
│           │   │   ├── ipv4
│           │   │   │   └── netfilter
│           │   │   │       ├── iptable_filter.ko
│           │   │   │       ├── ip_tables.ko
│           │   │   │       ├── ipt_REJECT.ko
│           │   │   │       ├── ipt_SYNPROXY.ko
│           │   │   │       ├── nf_defrag_ipv4.ko
│           │   │   │       ├── nf_dup_ipv4.ko
│           │   │   │       ├── nf_log_arp.ko
│           │   │   │       ├── nf_log_ipv4.ko
│           │   │   │       ├── nf_reject_ipv4.ko
│           │   │   │       └── nf_socket_ipv4.ko
│           │   │   ├── mac80211
│           │   │   │   └── mac80211.ko
│           │   │   ├── netfilter
│           │   │   │   ├── nf_conncount.ko
│           │   │   │   ├── nf_conntrack_amanda.ko
│           │   │   │   ├── nf_conntrack_broadcast.ko
│           │   │   │   ├── nf_conntrack_ftp.ko
│           │   │   │   ├── nf_conntrack_h323.ko
│           │   │   │   ├── nf_conntrack_irc.ko
│           │   │   │   ├── nf_conntrack.ko
│           │   │   │   ├── nf_conntrack_netbios_ns.ko
│           │   │   │   ├── nf_conntrack_netlink.ko
│           │   │   │   ├── nf_conntrack_pptp.ko
│           │   │   │   ├── nf_conntrack_sane.ko
│           │   │   │   ├── nf_conntrack_sip.ko
│           │   │   │   ├── nf_conntrack_snmp.ko
│           │   │   │   ├── nf_conntrack_tftp.ko
│           │   │   │   ├── nf_log_common.ko
│           │   │   │   ├── nf_log_netdev.ko
│           │   │   │   ├── nfnetlink_acct.ko
│           │   │   │   ├── nfnetlink_cthelper.ko
│           │   │   │   ├── nfnetlink_cttimeout.ko
│           │   │   │   ├── nfnetlink.ko
│           │   │   │   ├── nfnetlink_log.ko
│           │   │   │   ├── nfnetlink_osf.ko
│           │   │   │   ├── nfnetlink_queue.ko
│           │   │   │   ├── nf_synproxy_core.ko
│           │   │   │   ├── x_tables.ko
│           │   │   │   ├── xt_addrtype.ko
│           │   │   │   ├── xt_bpf.ko
│           │   │   │   ├── xt_cgroup.ko
│           │   │   │   ├── xt_CLASSIFY.ko
│           │   │   │   ├── xt_cluster.ko
│           │   │   │   ├── xt_comment.ko
│           │   │   │   ├── xt_connbytes.ko
│           │   │   │   ├── xt_connlabel.ko
│           │   │   │   ├── xt_connlimit.ko
│           │   │   │   ├── xt_connmark.ko
│           │   │   │   ├── xt_CONNSECMARK.ko
│           │   │   │   ├── xt_conntrack.ko
│           │   │   │   ├── xt_cpu.ko
│           │   │   │   ├── xt_dccp.ko
│           │   │   │   ├── xt_devgroup.ko
│           │   │   │   ├── xt_dscp.ko
│           │   │   │   ├── xt_ecn.ko
│           │   │   │   ├── xt_esp.ko
│           │   │   │   ├── xt_hashlimit.ko
│           │   │   │   ├── xt_helper.ko
│           │   │   │   ├── xt_hl.ko
│           │   │   │   ├── xt_HMARK.ko
│           │   │   │   ├── xt_IDLETIMER.ko
│           │   │   │   ├── xt_ipcomp.ko
│           │   │   │   ├── xt_iprange.ko
│           │   │   │   ├── xt_l2tp.ko
│           │   │   │   ├── xt_LED.ko
│           │   │   │   ├── xt_length.ko
│           │   │   │   ├── xt_limit.ko
│           │   │   │   ├── xt_LOG.ko
│           │   │   │   ├── xt_mac.ko
│           │   │   │   ├── xt_mark.ko
│           │   │   │   ├── xt_multiport.ko
│           │   │   │   ├── xt_nfacct.ko
│           │   │   │   ├── xt_NFLOG.ko
│           │   │   │   ├── xt_NFQUEUE.ko
│           │   │   │   ├── xt_osf.ko
│           │   │   │   ├── xt_owner.ko
│           │   │   │   ├── xt_pkttype.ko
│           │   │   │   ├── xt_quota.ko
│           │   │   │   ├── xt_rateest.ko
│           │   │   │   ├── xt_RATEEST.ko
│           │   │   │   ├── xt_realm.ko
│           │   │   │   ├── xt_recent.ko
│           │   │   │   ├── xt_sctp.ko
│           │   │   │   ├── xt_SECMARK.ko
│           │   │   │   ├── xt_socket.ko
│           │   │   │   ├── xt_state.ko
│           │   │   │   ├── xt_statistic.ko
│           │   │   │   ├── xt_string.ko
│           │   │   │   ├── xt_tcpmss.ko
│           │   │   │   ├── xt_TCPMSS.ko
│           │   │   │   ├── xt_tcpudp.ko
│           │   │   │   ├── xt_TEE.ko
│           │   │   │   ├── xt_time.ko
│           │   │   │   └── xt_u32.ko
│           │   │   ├── qrtr
│           │   │   │   ├── ns.ko
│           │   │   │   ├── qrtr.ko
│           │   │   │   ├── qrtr-mhi.ko
│           │   │   │   ├── qrtr-smd.ko
│           │   │   │   └── qrtr-tun.ko
│           │   │   ├── rfkill
│           │   │   │   ├── rfkill-gpio.ko
│           │   │   │   └── rfkill.ko
│           │   │   ├── sunrpc
│           │   │   │   ├── auth_gss
│           │   │   │   │   └── auth_rpcgss.ko
│           │   │   │   └── sunrpc.ko
│           │   │   ├── vmw_vsock
│           │   │   │   ├── hv_sock.ko
│           │   │   │   ├── vmw_vsock_virtio_transport_common.ko
│           │   │   │   ├── vmw_vsock_virtio_transport.ko
│           │   │   │   ├── vmw_vsock_vmci_transport.ko
│           │   │   │   ├── vsock_diag.ko
│           │   │   │   ├── vsock.ko
│           │   │   │   └── vsock_loopback.ko
│           │   │   └── wireless
│           │   │       ├── cfg80211.ko
│           │   │       ├── lib80211_crypt_ccmp.ko
│           │   │       ├── lib80211_crypt_tkip.ko
│           │   │       ├── lib80211_crypt_wep.ko
│           │   │       └── lib80211.ko
│           │   ├── sound
│           │   │   ├── ac97_bus.ko
│           │   │   ├── core
│           │   │   │   ├── snd-compress.ko
│           │   │   │   ├── snd-hrtimer.ko
│           │   │   │   ├── snd-hwdep.ko
│           │   │   │   ├── snd-pcm-dmaengine.ko
│           │   │   │   ├── snd-pcm.ko
│           │   │   │   ├── snd-rawmidi.ko
│           │   │   │   └── snd-timer.ko
│           │   │   ├── drivers
│           │   │   │   ├── mpu401
│           │   │   │   │   └── snd-mpu401-uart.ko
│           │   │   │   ├── opl3
│           │   │   │   │   └── snd-opl3-lib.ko
│           │   │   │   └── vx
│           │   │   │       └── snd-vx-lib.ko
│           │   │   ├── hda
│           │   │   │   ├── ext
│           │   │   │   │   └── snd-hda-ext-core.ko
│           │   │   │   ├── snd-hda-core.ko
│           │   │   │   └── snd-intel-dspcfg.ko
│           │   │   ├── i2c
│           │   │   │   ├── other
│           │   │   │   │   ├── snd-ak4113.ko
│           │   │   │   │   ├── snd-ak4114.ko
│           │   │   │   │   ├── snd-ak4xxx-adda.ko
│           │   │   │   │   └── snd-pt2258.ko
│           │   │   │   ├── snd-cs8427.ko
│           │   │   │   └── snd-i2c.ko
│           │   │   ├── isa
│           │   │   │   └── sb
│           │   │   │       └── snd-sb-common.ko
│           │   │   ├── pci
│           │   │   │   ├── ac97
│           │   │   │   │   └── snd-ac97-codec.ko
│           │   │   │   ├── ali5451
│           │   │   │   │   └── snd-ali5451.ko
│           │   │   │   ├── asihpi
│           │   │   │   │   └── snd-asihpi.ko
│           │   │   │   ├── au88x0
│           │   │   │   │   ├── snd-au8810.ko
│           │   │   │   │   ├── snd-au8820.ko
│           │   │   │   │   └── snd-au8830.ko
│           │   │   │   ├── aw2
│           │   │   │   │   └── snd-aw2.ko
│           │   │   │   ├── ca0106
│           │   │   │   │   └── snd-ca0106.ko
│           │   │   │   ├── cs46xx
│           │   │   │   │   └── snd-cs46xx.ko
│           │   │   │   ├── ctxfi
│           │   │   │   │   └── snd-ctxfi.ko
│           │   │   │   ├── echoaudio
│           │   │   │   │   ├── snd-darla20.ko
│           │   │   │   │   ├── snd-darla24.ko
│           │   │   │   │   ├── snd-echo3g.ko
│           │   │   │   │   ├── snd-gina20.ko
│           │   │   │   │   ├── snd-gina24.ko
│           │   │   │   │   ├── snd-indigodj.ko
│           │   │   │   │   ├── snd-indigodjx.ko
│           │   │   │   │   ├── snd-indigoio.ko
│           │   │   │   │   ├── snd-indigoiox.ko
│           │   │   │   │   ├─��� snd-indigo.ko
│           │   │   │   │   ├── snd-layla20.ko
│           │   │   │   │   ├── snd-layla24.ko
│           │   │   │   │   ├── snd-mia.ko
│           │   │   │   │   └── snd-mona.ko
│           │   │   │   ├── emu10k1
│           │   │   │   │   ├── snd-emu10k1.ko
│           │   │   │   │   └── snd-emu10k1x.ko
│           │   │   │   ├── hda
│           │   │   │   │   ├── snd-hda-codec-analog.ko
│           │   │   │   │   ├── snd-hda-codec-ca0110.ko
│           │   │   │   │   ├── snd-hda-codec-ca0132.ko
│           │   │   │   │   ├── snd-hda-codec-cirrus.ko
│           │   │   │   │   ├── snd-hda-codec-cmedia.ko
│           │   │   │   │   ├── snd-hda-codec-conexant.ko
│           │   │   │   │   ├── snd-hda-codec-generic.ko
│           │   │   │   │   ├── snd-hda-codec-hdmi.ko
│           │   │   │   │   ├── snd-hda-codec-idt.ko
│           │   │   │   │   ├── snd-hda-codec.ko
│           │   │   │   │   ├── snd-hda-codec-realtek.ko
│           │   │   │   │   ├── snd-hda-codec-si3054.ko
│           │   │   │   │   ├── snd-hda-codec-via.ko
│           │   │   │   │   └── snd-hda-intel.ko
│           │   │   │   ├── ice1712
│           │   │   │   │   ├── snd-ice1712.ko
│           │   │   │   │   ├── snd-ice1724.ko
│           │   │   │   │   └── snd-ice17xx-ak4xxx.ko
│           │   │   │   ├── korg1212
│           │   │   │   │   └── snd-korg1212.ko
│           │   │   │   ├── lola
│           │   │   │   │   └── snd-lola.ko
│           │   │   │   ├── lx6464es
│           │   │   │   │   └── snd-lx6464es.ko
│           │   │   │   ├── mixart
│           │   │   │   │   └── snd-mixart.ko
│           │   │   │   ├── nm256
│           │   │   │   │   └── snd-nm256.ko
│           │   │   │   ├── oxygen
│           │   │   │   │   ├── snd-oxygen.ko
│           │   │   │   │   ├── snd-oxygen-lib.ko
│           │   │   │   │   └── snd-virtuoso.ko
│           │   │   │   ├── pcxhr
│           │   │   │   │   └── snd-pcxhr.ko
│           │   │   │   ├── riptide
│           │   │   │   │   └── snd-riptide.ko
│           │   │   │   ├── rme9652
│           │   │   │   │   ├── snd-hdsp.ko
│           │   │   │   │   ├── snd-hdspm.ko
│           │   │   │   │   └── snd-rme9652.ko
│           │   │   │   ├── snd-ad1889.ko
│           │   │   │   ├── snd-als300.ko
│           │   │   │   ├── snd-als4000.ko
│           │   │   │   ├── snd-atiixp.ko
│           │   │   │   ├── snd-atiixp-modem.ko
│           │   │   │   ├── snd-azt3328.ko
│           │   │   │   ├── snd-bt87x.ko
│           │   │   │   ├── snd-cmipci.ko
│           │   │   │   ├── snd-cs4281.ko
│           │   │   │   ├── snd-ens1370.ko
│           ���   │   │   ├── snd-ens1371.ko
│           │   │   │   ├── snd-es1938.ko
│           │   │   │   ├── snd-es1968.ko
│           │   │   │   ├── snd-fm801.ko
│           │   │   │   ├── snd-intel8x0.ko
│           │   │   │   ├── snd-intel8x0m.ko
│           │   │   │   ├── snd-maestro3.ko
│           │   │   │   ├── snd-rme32.ko
│           │   │   │   ├── snd-rme96.ko
│           │   │   │   ├── snd-sonicvibes.ko
│           │   │   │   ├── snd-via82xx.ko
│           │   │   │   ├── snd-via82xx-modem.ko
│           │   │   │   ├── trident
│           │   │   │   │   └── snd-trident.ko
│           │   │   │   ├── vx222
│           │   │   │   │   └── snd-vx222.ko
│           │   │   │   └── ymfpci
│           │   │   │       └── snd-ymfpci.ko
│           │   │   ├── soc
│           │   │   │   ├── amd
│           │   │   │   │   ├── acp_audio_dma.ko
│           │   │   │   │   ├── raven
│           │   │   │   │   │   ├── snd-acp3x-i2s.ko
│           │   │   │   │   │   ├── snd-acp3x-pcm-dma.ko
│           │   │   │   │   │   └── snd-pci-acp3x.ko
│           │   │   │   │   ├── renoir
│           │   │   │   │   │   ├── snd-acp3x-pdm-dma.ko
│           │   │   │   │   │   ├── snd-acp3x-rn.ko
│           │   │   │   │   │   └── snd-rn-pci-acp3x.ko
│           │   │   │   │   ├── snd-soc-acp-da7219mx98357-mach.ko
│           │   │   │   │   ├── snd-soc-acp-rt5645-mach.ko
│           │   │   │   │   └── snd-soc-acp-rt5682-mach.ko
│           │   │   │   ├── codecs
│           │   │   │   │   ├── snd-soc-ac97.ko
│           │   │   │   │   ├── snd-soc-adau7002.ko
│           │   │   │   │   ├── snd-soc-cros-ec-codec.ko
│           │   │   │   │   ├── snd-soc-cx2072x.ko
│           │   │   │   │   ├── snd-soc-da7213.ko
│           │   │   │   │   ├── snd-soc-da7219.ko
│           │   │   │   │   ├── snd-soc-dmic.ko
│           │   │   │   │   ├── snd-soc-es8316.ko
│           │   │   │   │   ├── snd-soc-hdac-hda.ko
│           │   │   │   │   ├── snd-soc-hdac-hdmi.ko
│           │   │   │   │   ├── snd-soc-max98090.ko
│           │   │   │   │   ├── snd-soc-max98357a.ko
│           │   │   │   │   ├── snd-soc-max98373-i2c.ko
│           │   │   │   │   ├── snd-soc-max98373.ko
│           │   │   │   │   ├── snd-soc-max98390.ko
│           │   │   │   │   ├── snd-soc-max98927.ko
│           │   │   │   │   ├── snd-soc-nau8824.ko
│           │   │   │   │   ├── snd-soc-nau8825.ko
│           │   │   │   │   ├── snd-soc-pcm512x-i2c.ko
│           │   │   │   │   ├── snd-soc-pcm512x.ko
│           │   │   │   │   ├── snd-soc-rl6231.ko
│           │   │   │   │   ├── snd-soc-rl6347a.ko
│           │   │   │   │   ├── snd-soc-rt1011.ko
│           │   │   │   │   ├── snd-soc-rt1015.ko
│           │   │   │   │   ├── snd-soc-rt286.ko
│           │   │   │   │   ├── snd-soc-rt298.ko
│           │   │   │   │   ├── snd-soc-rt5514.ko
│           │   │   │   │   ├── snd-soc-rt5514-spi.ko
│           │   │   │   │   ├── snd-soc-rt5640.ko
│           │   │   │   │   ├── snd-soc-rt5645.ko
│           │   │   │   │   ├── snd-soc-rt5651.ko
│           │   │   │   │   ├── snd-soc-rt5660.ko
│           │   │   │   │   ├── snd-soc-rt5663.ko
│           │   │   │   │   ├── snd-soc-rt5670.ko
│           │   │   │   │   ├── snd-soc-rt5677.ko
│           │   │   │   │   ├── snd-soc-rt5677-spi.ko
│           │   │   │   │   ├── snd-soc-rt5682-i2c.ko
│           │   │   │   │   ├── snd-soc-rt5682.ko
│           │   │   │   │   ├── snd-soc-ssm4567.ko
│           │   │   │   │   ├── snd-soc-ts3a227e.ko
│           │   │   │   │   ├── snd-soc-wm8804-i2c.ko
│           │   │   │   │   └── snd-soc-wm8804.ko
│           │   │   │   ├── dwc
│           │   │   │   │   └── designware_i2s.ko
│           │   │   │   ├── intel
│           │   │   │   │   ├── atom
│           │   │   │   │   │   ├── snd-soc-sst-atom-hifi2-platform.ko
│           │   │   │   │   │   └── sst
│           │   │   │   │   │       ├── snd-intel-sst-acpi.ko
│           │   │   │   │   │       ├── snd-intel-sst-core.ko
│           │   │   │   │   │       └── snd-intel-sst-pci.ko
│           │   │   │   │   ├── boards
│           │   │   │   │   │   ├── snd-skl_nau88l25_max98357a.ko
│           │   │   │   │   │   ├── snd-soc-cml_rt1011_rt5682.ko
│           │   │   │   │   │   ├── snd-soc-ehl-rt5660.ko
│           │   │   │   │   │   ├── snd-soc-kbl_da7219_max98357a.ko
│           │   │   │   │   │   ├── snd-soc-kbl_da7219_max98927.ko
│           │   │   │   │   │   ├── snd-soc-kbl_rt5660.ko
│           │   │   │   │   │   ├── snd-soc-kbl_rt5663_max98927.ko
│           │   │   │   │   │   ├── snd-soc-kbl_rt5663_rt5514_max98927.ko
│           │   │   │   │   │   ├── snd-soc-skl_hda_dsp.ko
│           │   │   │   │   │   ├── snd-soc-skl_nau88l25_ssm4567.ko
│           │   │   │   │   │   ├── snd-soc-skl_rt286.ko
│           │   │   │   │   │   ├── snd-soc-sof_da7219_max98373.ko
│           │   │   │   │   │   ├── snd-soc-sof_rt5682.ko
│           │   │   │   │   │   ├── snd-soc-sst-bdw-rt5650-mach.ko
│           │   │   │   │   │   ├── snd-soc-sst-bdw-rt5677-mach.ko
│           │   │   │   │   │   ├── snd-soc-sst-broadwell.ko
│           │   │   │   │   │   ├── snd-soc-sst-bxt-da7219_max98357a.ko
│           │   │   │   │   │   ├── snd-soc-sst-bxt-rt298.ko
│           │   │   │   │   │   ├── snd-soc-sst-byt-cht-cx2072x.ko
│           │   │   │   │   │   ├── snd-soc-sst-byt-cht-da7213.ko
│           │   │   │   │   │   ├── snd-soc-sst-byt-cht-es8316.ko
│           │   │   │   │   │   ├── snd-soc-sst-byt-cht-nocodec.ko
│           │   │   │   │   │   ├── snd-soc-sst-bytcr-rt5640.ko
│           │   │   │   │   │   ├── snd-soc-sst-bytcr-rt5651.ko
│           │   │   │   │   │   ├── snd-soc-sst-cht-bsw-max98090_ti.ko
│           │   │   │   │   │   ├── snd-soc-sst-cht-bsw-nau8824.ko
│           │   │   │   │   │   ├── snd-soc-sst-cht-bsw-rt5645.ko
│           │   │   │   │   │   ├── snd-soc-sst-cht-bsw-rt5672.ko
│           │   │   │   │   │   ├── snd-soc-sst-glk-rt5682_max98357a.ko
│           │   │   │   │   │   ├── snd-soc-sst-haswell.ko
│           │   │   │   │   │   ├── snd-soc-sst-sof-pcm512x.ko
│           │   │   │   │   │   └── snd-soc-sst-sof-wm8804.ko
│           │   │   │   │   ├── catpt
│           │   │   │   │   │   └── snd-soc-catpt.ko
│           │   │   │   │   ├── common
│           │   │   │   │   │   ├── snd-soc-acpi-intel-match.ko
│           │   │   │   │   │   ├── snd-soc-sst-dsp.ko
│           │   │   │   │   │   └── snd-soc-sst-ipc.ko
│           │   │   │   │   └── skylake
│           │   │   │   │       ├── snd-soc-skl.ko
│           │   │   │   │       └── snd-soc-skl-ssp-clk.ko
│           │   │   │   ├── snd-soc-acpi.ko
│           │   │   │   ├── snd-soc-core.ko
│           │   │   │   └── sof
│           │   │   │       ├── intel
│           │   │   │       │   ├── snd-sof-intel-byt.ko
│           │   │   │       │   ├── snd-sof-intel-hda-common.ko
│           │   │   │       │   ├── snd-sof-intel-hda.ko
│           │   │   │       │   └── snd-sof-intel-ipc.ko
│           │   │   │       ├── snd-sof-acpi.ko
│           │   │   │       ├── snd-sof.ko
│           │   │   │       ├── snd-sof-pci.ko
│           │   │   │       └── xtensa
│           │   │   │           └── snd-sof-xtensa-dsp.ko
│           │   │   ├── synth
│           │   │   │   └── snd-util-mem.ko
│           │   │   ├── usb
│           │   │   │   ├── 6fire
│           │   │   │   │   └── snd-usb-6fire.ko
│           │   │   │   ├── bcd2000
│           │   │   │   │   └── snd-bcd2000.ko
│           │   │   │   ├── caiaq
│           │   │   │   │   └── snd-usb-caiaq.ko
│           │   │   │   ├── hiface
│           │   │   │   │   └── snd-usb-hiface.ko
│           │   │   │   ├── line6
│           │   │   │   │   ├── snd-usb-line6.ko
│           │   │   │   │   ├── snd-usb-podhd.ko
│           │   │   │   │   ├── snd-usb-pod.ko
│           │   │   │   │   ├── snd-usb-toneport.ko
│           │   │   │   │   └── snd-usb-variax.ko
│           │   │   │   ├── misc
│           │   │   │   │   └── snd-ua101.ko
│           │   │   │   ├── snd-usb-audio.ko
│           │   │   │   ├── snd-usbmidi-lib.ko
│           │   │   │   └── usx2y
│           │   │   │       ├── snd-usb-us122l.ko
│           │   │   │       └── snd-usb-usx2y.ko
│           │   │   ├── x86
│           │   │   │   └── snd-hdmi-lpe-audio.ko
│           │   │   └── xen
│           │   │       └── snd_xen_front.ko
│           │   └── virt
│           │       └── lib
│           │           └── irqbypass.ko
│           ├── modules.alias
│           ├── modules.alias.bin
│           ├── modules.builtin
│           ├── modules.builtin.alias.bin
│           ├── modules.builtin.bin
│           ├── modules.builtin.modinfo
│           ├── modules.dep
│           ├── modules.dep.bin
│           ├── modules.devname
│           ├── modules.order
│           ├── modules.softdep
│           ├── modules.symbols
│           └── modules.symbols.bin
└── usr
    ├── lib -> lib64/
    └── lib64```
</details>

---

### 001-core.xzm (Core System)

Contains the main system binaries, libraries, X11, browsers (Chrome/Firefox), GTK, and all core userspace components.

<details>
<summary>Click to expand full tree (5512 lines)</summary>

\`\`\`
/tmp/tmp.O7x0keuVBb/001-core
├── bin
│   ├── date
│   ├── dd
│   ├── kmod
│   ├── login
│   ├── lsblk
│   ├── lsmod -> kmod
│   ├── modinfo -> kmod
│   ├── monr
│   └── udevadm
├── etc
│   ├── ca-certificates.conf
│   ├── cron.d
│   ├── cron.daily
│   │   └── logrotate
│   ├── cron.deny
│   ├── cron.hourly
│   ├── cron.monthly
│   ├── crontab
│   ├── cron.weekly
│   ├── dbus-1
│   │   ├── session.d
│   │   └── system.d
│   ├── fonts
│   │   ├── conf.avail
│   │   │   ├── 10-autohint.conf
│   │   │   ├── 10-hinting-full.conf
│   │   │   ├── 10-hinting-medium.conf
│   │   │   ├── 10-hinting-none.conf
│   │   │   ├── 10-hinting-slight.conf
│   │   │   ├── 10-no-sub-pixel.conf
│   │   │   ├── 10-scale-bitmap-fonts.conf
│   │   │   ├── 10-sub-pixel-bgr.conf
│   │   │   ├── 10-sub-pixel-rgb.conf
│   │   │   ├── 10-sub-pixel-vbgr.conf
│   │   │   ├── 10-sub-pixel-vrgb.conf
│   │   │   ├── 10-unhinted.conf
│   │   │   ├── 11-lcdfilter-default.conf
│   │   │   ├── 11-lcdfilter-legacy.conf
│   │   │   ├── 11-lcdfilter-light.conf
│   │   │   ├── 20-unhint-small-dejavu-sans.conf
│   │   │   ├── 20-unhint-small-dejavu-sans-mono.conf
│   │   │   ├── 20-unhint-small-dejavu-serif.conf
│   │   │   ├── 20-unhint-small-vera.conf
│   │   │   ├── 25-unhint-nonlatin.conf
│   │   │   ├── 30-metric-aliases.conf
│   │   │   ├── 40-nonlatin.conf
│   │   │   ├── 45-generic.conf
│   │   │   ├── 45-latin.conf
│   │   │   ├── 49-sansserif.conf
│   │   │   ├── 50-user.conf
│   │   │   ├── 51-local.conf
│   │   │   ├── 57-dejavu-sans.conf
│   │   │   ├── 57-dejavu-sans-mono.conf
│   │   │   ├── 57-dejavu-serif.conf
│   │   │   ├── 60-generic.conf
│   │   │   ├── 60-latin.conf
│   │   │   ├── 65-fonts-persian.conf
│   │   │   ├── 65-khmer.conf
│   │   │   ├── 65-nonlatin.conf
│   │   │   ├── 69-unifont.conf
│   │   │   ├── 70-no-bitmaps.conf
│   │   │   ├── 70-yes-bitmaps.conf
│   │   │   ├── 80-delicious.conf
│   │   │   └── 90-synthetic.conf
│   │   ├── conf.d
│   │   │   ├── 10-hinting-slight.conf -> ../conf.avail/10-hinting-slight.conf
│   │   │   ├── 10-scale-bitmap-fonts.conf -> ../conf.avail/10-scale-bitmap-fonts.conf
│   │   │   ├── 20-unhint-small-vera.conf -> ../conf.avail/20-unhint-small-vera.conf
│   │   │   ├── 30-metric-aliases.conf -> ../conf.avail/30-metric-aliases.conf
│   │   │   ├── 40-nonlatin.conf -> ../conf.avail/40-nonlatin.conf
│   │   │   ├── 45-generic.conf -> ../conf.avail/45-generic.conf
│   │   │   ├── 45-latin.conf -> ../conf.avail/45-latin.conf
│   │   │   ├── 49-sansserif.conf -> ../conf.avail/49-sansserif.conf
│   │   │   ├── 50-user.conf -> ../conf.avail/50-user.conf
│   │   │   ├── 51-local.conf -> ../conf.avail/51-local.conf
│   │   │   ├── 60-generic.conf -> ../conf.avail/60-generic.conf
│   │   │   ├── 60-latin.conf -> ../conf.avail/60-latin.conf
│   │   │   ├── 65-fonts-persian.conf -> ../conf.avail/65-fonts-persian.conf
│   │   │   ├── 65-nonlatin.conf -> ../conf.avail/65-nonlatin.conf
│   │   │   ├── 69-unifont.conf -> ../conf.avail/69-unifont.conf
│   │   │   ├── 80-delicious.conf -> ../conf.avail/80-delicious.conf
│   │   │   └── 90-synthetic.conf -> ../conf.avail/90-synthetic.conf
│   │   └── fonts.conf
│   ├── hosts
│   ├── login.defs
│   ├── logrotate.conf
│   ├── mc
│   │   ├── edit.indent.rc
│   │   ├── filehighlight.ini
│   │   ├── mc.default.keymap
│   │   ├── mcedit.menu
│   │   ├── mc.emacs.keymap
│   │   ├── mc.ext
│   │   ├── mc.keymap -> mc.default.keymap
│   │   ├── mc.menu
│   │   └── sfs.ini
│   ├── modprobe.d
│   │   ├── aliases.conf
│   │   ├── alsa.conf
│   │   └── i386.conf
│   ├── nsswitch.conf
│   ├── services
│   ├── ssl
│   │   ├── certs
│   │   │   ├── 02265526.0 -> Entrust_Root_Certification_Authority_-_G2.pem
│   │   │   ├── 03179a64.0 -> Staat_der_Nederlanden_EV_Root_CA.pem
│   │   │   ├── 062cdee6.0 -> GlobalSign_Root_CA_-_R3.pem
│   │   │   ├── 064e0aa9.0 -> QuoVadis_Root_CA_2_G3.pem
│   │   │   ├── 06dc52d5.0 -> SSL.com_EV_Root_Certification_Authority_RSA_R2.pem
│   │   │   ├── 080911ac.0 -> QuoVadis_Root_CA.pem
│   │   │   ├── 09789157.0 -> Starfield_Services_Root_Certificate_Authority_-_G2.pem
│   │   │   ├── 0a775a30.0 -> GTS_Root_R3.pem
│   │   │   ├── 0b1b94ef.0 -> CFCA_EV_ROOT.pem
│   │   │   ├── 0bf05006.0 -> SSL.com_Root_Certification_Authority_ECC.pem
│   │   │   ├── 0c4c9b6c.0 -> Global_Chambersign_Root_-_2008.pem
│   │   │   ├── 0f5dc4f3.0 -> UCA_Extended_Validation_Root.pem
│   │   │   ├── 0f6fa695.0 -> GDCA_TrustAUTH_R5_ROOT.pem
│   │   │   ├── 1001acf7.0 -> GTS_Root_R1.pem
│   │   │   ├── 106f3e4d.0 -> Entrust_Root_Certification_Authority_-_EC1.pem
│   │   │   ├── 128805a3.0 -> EE_Certification_Centre_Root_CA.pem
│   │   │   ├── 14bc7599.0 -> emSign_ECC_Root_CA_-_G3.pem
│   │   │   ├── 1636090b.0 -> Hellenic_Academic_and_Research_Institutions_RootCA_2011.pem
│   │   │   ├── 18856ac4.0 -> SecureSign_RootCA11.pem
│   │   │   ├── 1d3472b9.0 -> GlobalSign_ECC_Root_CA_-_R5.pem
│   │   │   ├── 1e08bfd1.0 -> IdenTrust_Public_Sector_Root_CA_1.pem
│   │   │   ├── 1e09d511.0 -> T-TeleSec_GlobalRoot_Class_2.pem
│   │   │   ├── 244b5494.0 -> DigiCert_High_Assurance_EV_Root_CA.pem
│   │   │   ├── 2923b3f9.0 -> emSign_Root_CA_-_G1.pem
│   │   │   ├── 2ae6433e.0 -> CA_Disig_Root_R2.pem
│   │   │   ├── 2b349938.0 -> AffirmTrust_Commercial.pem
│   │   │   ├── 2e5ac55d.0 -> DST_Root_CA_X3.pem
│   │   │   ├── 32888f65.0 -> Hellenic_Academic_and_Research_Institutions_RootCA_2015.pem
│   │   │   ├── 349f2832.0 -> EC-ACC.pem
│   │   │   ├── 3513523f.0 -> DigiCert_Global_Root_CA.pem
│   │   │   ├── 3bde41ac.0 -> Autoridad_de_Certificacion_Firmaprofesional_CIF_A62634068.pem
│   │   │   ├── 3e44d2f7.0 -> TrustCor_RootCert_CA-2.pem
│   │   │   ├── 3e45d192.0 -> Hongkong_Post_Root_CA_1.pem
│   │   │   ├── 40193066.0 -> Certum_Trusted_Network_CA_2.pem
│   │   │   ├── 4042bcee.0 -> ISRG_Root_X1.pem
│   │   │   ├── 40547a79.0 -> COMODO_Certification_Authority.pem
│   │   │   ├── 406c9bb1.0 -> emSign_Root_CA_-_C1.pem
│   │   │   ├── 4304c5e5.0 -> Network_Solutions_Certificate_Authority.pem
│   │   │   ├── 48bec511.0 -> Certum_Trusted_Network_CA.pem
│   │   │   ├── 4a6481c9.0 -> GlobalSign_Root_CA_-_R2.pem
│   │   │   ├── 4b718d9b.0 -> emSign_ECC_Root_CA_-_C3.pem
│   │   │   ├── 4bfab552.0 -> Starfield_Root_Certificate_Authority_-_G2.pem
│   │   │   ├── 4f316efb.0 -> SwissSign_Gold_CA_-_G2.pem
│   │   │   ├── 5273a94c.0 -> E-Tugra_Certification_Authority.pem
│   │   │   ├── 5443e9e3.0 -> T-TeleSec_GlobalRoot_Class_3.pem
│   │   │   ├── 54657681.0 -> Buypass_Class_2_Root_CA.pem
│   │   │   ├── 57bcb2da.0 -> SwissSign_Silver_CA_-_G2.pem
│   │   │   ├── 590d426f.0 -> CAcert_Inc._2.pem
│   │   │   ├── 5a4d6896.0 -> Staat_der_Nederlanden_Root_CA_-_G3.pem
│   │   │   ├── 5ad8a5d6.0 -> GlobalSign_Root_CA.pem
│   │   │   ├── 5c44d531.0 -> Staat_der_Nederlanden_Root_CA_-_G2.pem
│   │   │   ├── 5cd81ad7.0 -> TeliaSonera_Root_CA_v1.pem
│   │   │   ├── 5d3033c5.0 -> TrustCor_RootCert_CA-1.pem
│   │   │   ├── 5e98733a.0 -> Entrust_Root_Certification_Authority_-_G4.pem
│   │   │   ├── 5f15c80c.0 -> TWCA_Global_Root_CA.pem
│   │   │   ├── 607986c7.0 -> DigiCert_Global_Root_G2.pem
│   │   │   ├── 626dceaf.0 -> GTS_Root_R2.pem
│   │   │   ├── 6410666e.0 -> Taiwan_GRCA.pem
│   │   │   ├── 653b494a.0 -> Baltimore_CyberTrust_Root.pem
│   │   │   ├── 68dd7389.0 -> Hongkong_Post_Root_CA_3.pem
│   │   │   ├── 6b99d060.0 -> Entrust_Root_Certification_Authority.pem
│   │   │   ├── 6d41d539.0 -> Amazon_Root_CA_2.pem
│   │   │   ├── 6fa5da56.0 -> SSL.com_Root_Certification_Authority_RSA.pem
│   │   │   ├── 706f604c.0 -> XRamp_Global_CA_Root.pem
│   │   │   ├── 749e9e03.0 -> QuoVadis_Root_CA_1_G3.pem
│   │   │   ├── 75d1b2ed.0 -> DigiCert_Trusted_Root_G4.pem
│   │   │   ├── 76cb8f92.0 -> Cybertrust_Global_Root.pem
│   │   │   ├── 76faf6c0.0 -> QuoVadis_Root_CA_3.pem
│   │   │   ├── 7719f463.0 -> Hellenic_Academic_and_Research_Institutions_ECC_RootCA_2015.pem
│   │   │   ├── 773e07ad.0 -> OISTE_WISeKey_Global_Root_GC_CA.pem
│   │   │   ├── 7aaf71c0.0 -> TrustCor_ECA-1.pem
│   │   │   ├── 7f3d5d1d.0 -> DigiCert_Assured_ID_Root_G3.pem
│   │   │   ├── 8160b96c.0 -> Microsec_e-Szigno_Root_CA_2009.pem
│   │   │   ├── 8867006a.0 -> GeoTrust_Universal_CA_2.pem
│   │   │   ├── 8cb5ee0f.0 -> Amazon_Root_CA_3.pem
│   │   │   ├── 8d86cdd1.0 -> certSIGN_ROOT_CA.pem
│   │   │   ├── 930ac5d2.0 -> Actalis_Authentication_Root_CA.pem
│   │   │   ├── 93bc0acc.0 -> AffirmTrust_Networking.pem
│   │   │   ├── 988a38cb.0 -> NetLock_Arany_=Class_Gold=_Főtanúsítvány.pem
│   │   │   ├── 99d0fa06.0 -> cacert.org_root.pem
│   │   │   ├── 9c2e7d30.0 -> Sonera_Class_2_Root_CA.pem
│   │   │   ├── 9c8dfbd4.0 -> AffirmTrust_Premium_ECC.pem
│   │   │   ├── 9d04f354.0 -> DigiCert_Assured_ID_Root_G2.pem
│   │   │   ├── a3418fda.0 -> GTS_Root_R4.pem
│   │   │   ├── a94d09e5.0 -> ACCVRAIZ1.pem
│   │   │   ├── ACCVRAIZ1.pem -> ../../../usr/share/ca-certificates/mozilla/ACCVRAIZ1.crt
│   │   │   ├── AC_RAIZ_FNMT-RCM.pem -> ../../../usr/share/ca-certificates/mozilla/AC_RAIZ_FNMT-RCM.crt
│   │   │   ├── Actalis_Authentication_Root_CA.pem -> ../../../usr/share/ca-certificates/mozilla/Actalis_Authentication_Root_CA.crt
│   │   │   ├── aee5f10d.0 -> Entrust.net_Premium_2048_Secure_Server_CA.pem
│   │   │   ├── AffirmTrust_Commercial.pem -> ../../../usr/share/ca-certificates/mozilla/AffirmTrust_Commercial.crt
│   │   │   ├── AffirmTrust_Networking.pem -> ../../../usr/share/ca-certificates/mozilla/AffirmTrust_Networking.crt
│   │   │   ├── AffirmTrust_Premium_ECC.pem -> ../../../usr/share/ca-certificates/mozilla/AffirmTrust_Premium_ECC.crt
│   │   │   ├── AffirmTrust_Premium.pem -> ../../../usr/share/ca-certificates/mozilla/AffirmTrust_Premium.crt
│   │   │   ├── Amazon_Root_CA_1.pem -> ../../../usr/share/ca-certificates/mozilla/Amazon_Root_CA_1.crt
│   │   │   ├── Amazon_Root_CA_2.pem -> ../../../usr/share/ca-certificates/mozilla/Amazon_Root_CA_2.crt
│   │   │   ├── Amazon_Root_CA_3.pem -> ../../../usr/share/ca-certificates/mozilla/Amazon_Root_CA_3.crt
│   │   │   ├── Amazon_Root_CA_4.pem -> ../../../usr/share/ca-certificates/mozilla/Amazon_Root_CA_4.crt
│   │   │   ├── Atos_TrustedRoot_2011.pem -> ../../../usr/share/ca-certificates/mozilla/Atos_TrustedRoot_2011.crt
│   │   │   ├── Autoridad_de_Certificacion_Firmaprofesional_CIF_A62634068.pem -> ../../../usr/share/ca-certificates/mozilla/Autoridad_de_Certificacion_Firmaprofesional_CIF_A62634068.crt
│   │   │   ├── b0e59380.0 -> GlobalSign_ECC_Root_CA_-_R4.pem
│   │   │   ├── b1159c4c.0 -> DigiCert_Assured_ID_Root_CA.pem
│   │   │   ├── b1b8a7f3.0 -> OISTE_WISeKey_Global_Root_GA_CA.pem
│   │   │   ├── b66938e9.0 -> Secure_Global_CA.pem
│   │   │   ├── b727005e.0 -> AffirmTrust_Premium.pem
│   │   │   ├── b7a5b843.0 -> TWCA_Root_Certification_Authority.pem
│   │   │   ├── Baltimore_CyberTrust_Root.pem -> ../../../usr/share/ca-certificates/mozilla/Baltimore_CyberTrust_Root.crt
│   │   │   ├── Buypass_Class_2_Root_CA.pem -> ../../../usr/share/ca-certificates/mozilla/Buypass_Class_2_Root_CA.crt
│   │   │   ├── Buypass_Class_3_Root_CA.pem -> ../../../usr/share/ca-certificates/mozilla/Buypass_Class_3_Root_CA.crt
│   │   │   ├── c01eb047.0 -> UCA_Global_G2_Root.pem
│   │   │   ├── c0ff1f52.0 -> Verisign_Class_3_Public_Primary_Certification_Authority_-_G3.pem
│   │   │   ├── c28a8a30.0 -> D-TRUST_Root_Class_3_CA_2_2009.pem
│   │   │   ├── c47d9980.0 -> Chambers_of_Commerce_Root_-_2008.pem
│   │   │   ├── ca6e4ad9.0 -> ePKI_Root_Certification_Authority.pem
│   │   │   ├── ca-certificates.crt
│   │   │   ├── CAcert_Inc._2.pem -> ../../../usr/share/ca-certificates/mozilla/CAcert_Inc._2.crt
│   │   │   ├── cacert.org_root.pem -> ../../../usr/share/ca-certificates/cacert.org/cacert.org_root.crt
│   │   │   ├── CA_Disig_Root_R2.pem -> ../../../usr/share/ca-certificates/mozilla/CA_Disig_Root_R2.crt
│   │   │   ├── cbf06781.0 -> Go_Daddy_Root_Certificate_Authority_-_G2.pem
│   │   │   ├── cc450945.0 -> Izenpe.com.pem
│   │   │   ├── cd58d51e.0 -> Security_Communication_RootCA2.pem
│   │   │   ├── cd8c0d63.0 -> AC_RAIZ_FNMT-RCM.pem
│   │   │   ├── ce5e74ef.0 -> Amazon_Root_CA_1.pem
│   │   │   ├── Certigna.pem -> ../../../usr/share/ca-certificates/mozilla/Certigna.crt
│   │   │   ├── Certigna_Root_CA.pem -> ../../../usr/share/ca-certificates/mozilla/Certigna_Root_CA.crt
│   │   │   ├── certSIGN_ROOT_CA.pem -> ../../../usr/share/ca-certificates/mozilla/certSIGN_ROOT_CA.crt
│   │   │   ├── Certum_Trusted_Network_CA_2.pem -> ../../../usr/share/ca-certificates/mozilla/Certum_Trusted_Network_CA_2.crt
│   │   │��  ├── Certum_Trusted_Network_CA.pem -> ../../../usr/share/ca-certificates/mozilla/Certum_Trusted_Network_CA.crt
│   │   │   ├── CFCA_EV_ROOT.pem -> ../../../usr/share/ca-certificates/mozilla/CFCA_EV_ROOT.crt
│   │   │   ├── Chambers_of_Commerce_Root_-_2008.pem -> ../../../usr/share/ca-certificates/mozilla/Chambers_of_Commerce_Root_-_2008.crt
│   │   │   ├── Comodo_AAA_Services_root.pem -> ../../../usr/share/ca-certificates/mozilla/Comodo_AAA_Services_root.crt
│   │   │   ├── COMODO_Certification_Authority.pem -> ../../../usr/share/ca-certificates/mozilla/COMODO_Certification_Authority.crt
│   │   │   ├── COMODO_ECC_Certification_Authority.pem -> ../../../usr/share/ca-certificates/mozilla/COMODO_ECC_Certification_Authority.crt
│   │   │   ├── COMODO_RSA_Certification_Authority.pem -> ../../../usr/share/ca-certificates/mozilla/COMODO_RSA_Certification_Authority.crt
│   │   │   ├── Cybertrust_Global_Root.pem -> ../../../usr/share/ca-certificates/mozilla/Cybertrust_Global_Root.crt
│   │   │   ├── d4dae3dd.0 -> D-TRUST_Root_Class_3_CA_2_EV_2009.pem
│   │   │   ├── d6325660.0 -> COMODO_RSA_Certification_Authority.pem
│   │   │   ├── d7e8dc79.0 -> QuoVadis_Root_CA_2.pem
│   │   │   ├── d853d49e.0 -> Trustis_FPS_Root_CA.pem
│   │   │   ├── dc4d6a89.0 -> GlobalSign_Root_CA_-_R6.pem
│   │   │   ├── dd8e9d41.0 -> DigiCert_Global_Root_G3.pem
│   │   │   ├── de6d66f3.0 -> Amazon_Root_CA_4.pem
│   │   │   ├── def36a68.0 -> LuxTrust_Global_Root_2.pem
│   │   │   ├── DigiCert_Assured_ID_Root_CA.pem -> ../../../usr/share/ca-certificates/mozilla/DigiCert_Assured_ID_Root_CA.crt
│   │   │   ├── DigiCert_Assured_ID_Root_G2.pem -> ../../../usr/share/ca-certificates/mozilla/DigiCert_Assured_ID_Root_G2.crt
│   │   │   ├── DigiCert_Assured_ID_Root_G3.pem -> ../../../usr/share/ca-certificates/mozilla/DigiCert_Assured_ID_Root_G3.crt
│   │   │   ├── DigiCert_Global_Root_CA.pem -> ../../../usr/share/ca-certificates/mozilla/DigiCert_Global_Root_CA.crt
│   │   │   ├── DigiCert_Global_Root_G2.pem -> ../../../usr/share/ca-certificates/mozilla/DigiCert_Global_Root_G2.crt
│   │   │   ├── DigiCert_Global_Root_G3.pem -> ../../../usr/share/ca-certificates/mozilla/DigiCert_Global_Root_G3.crt
│   │   │   ├── DigiCert_High_Assurance_EV_Root_CA.pem -> ../../../usr/share/ca-certificates/mozilla/DigiCert_High_Assurance_EV_Root_CA.crt
│   │   │   ├── DigiCert_Trusted_Root_G4.pem -> ../../../usr/share/ca-certificates/mozilla/DigiCert_Trusted_Root_G4.crt
│   │   │   ├── DST_Root_CA_X3.pem -> ../../../usr/share/ca-certificates/mozilla/DST_Root_CA_X3.crt
│   │   │   ├── D-TRUST_Root_Class_3_CA_2_2009.pem -> ../../../usr/share/ca-certificates/mozilla/D-TRUST_Root_Class_3_CA_2_2009.crt
│   │   │   ├── D-TRUST_Root_Class_3_CA_2_EV_2009.pem -> ../../../usr/share/ca-certificates/mozilla/D-TRUST_Root_Class_3_CA_2_EV_2009.crt
│   │   │   ├── e113c810.0 -> Certigna.pem
│   │   │   ├── e18bfb83.0 -> QuoVadis_Root_CA_3_G3.pem
│   │   │   ├── e36a6752.0 -> Atos_TrustedRoot_2011.pem
│   │   │   ├── e73d606e.0 -> OISTE_WISeKey_Global_Root_GB_CA.pem
│   │   │   ├── e8de2f56.0 -> Buypass_Class_3_Root_CA.pem
│   │   │   ├── EC-ACC.pem -> ../../../usr/share/ca-certificates/mozilla/EC-ACC.crt
│   │   │   ├── ee64a828.0 -> Comodo_AAA_Services_root.pem
│   │   │   ├── EE_Certification_Centre_Root_CA.pem -> ../../../usr/share/ca-certificates/mozilla/EE_Certification_Centre_Root_CA.crt
│   │   │   ├── eed8c118.0 -> COMODO_ECC_Certification_Authority.pem
│   │   │   ├── ef954a4e.0 -> IdenTrust_Commercial_Root_CA_1.pem
│   │   │   ├── emSign_ECC_Root_CA_-_C3.pem -> ../../../usr/share/ca-certificates/mozilla/emSign_ECC_Root_CA_-_C3.crt
│   │   │   ├── emSign_ECC_Root_CA_-_G3.pem -> ../../../usr/share/ca-certificates/mozilla/emSign_ECC_Root_CA_-_G3.crt
│   │   │   ├── emSign_Root_CA_-_C1.pem -> ../../../usr/share/ca-certificates/mozilla/emSign_Root_CA_-_C1.crt
│   │   │   ├── emSign_Root_CA_-_G1.pem -> ../../../usr/share/ca-certificates/mozilla/emSign_Root_CA_-_G1.crt
│   │   │   ├── Entrust.net_Premium_2048_Secure_Server_CA.pem -> ../../../usr/share/ca-certificates/mozilla/Entrust.net_Premium_2048_Secure_Server_CA.crt
│   │   │   ├── Entrust_Root_Certification_Authority_-_EC1.pem -> ../../../usr/share/ca-certificates/mozilla/Entrust_Root_Certification_Authority_-_EC1.crt
│   │   │   ├── Entrust_Root_Certification_Authority_-_G2.pem -> ../../../usr/share/ca-certificates/mozilla/Entrust_Root_Certification_Authority_-_G2.crt
│   │   │   ├── Entrust_Root_Certification_Authority_-_G4.pem -> ../../../usr/share/ca-certificates/mozilla/Entrust_Root_Certification_Authority_-_G4.crt
│   │   │   ├── Entrust_Root_Certification_Authority.pem -> ../../../usr/share/ca-certificates/mozilla/Entrust_Root_Certification_Authority.crt
│   │   │   ├── ePKI_Root_Certification_Authority.pem -> ../../../usr/share/ca-certificates/mozilla/ePKI_Root_Certification_Authority.crt
│   │   │   ├── E-Tugra_Certification_Authority.pem -> ../../../usr/share/ca-certificates/mozilla/E-Tugra_Certification_Authority.crt
│   │   │   ├── f081611a.0 -> Go_Daddy_Class_2_CA.pem
│   │   │   ├── f0c70a8d.0 -> SSL.com_EV_Root_Certification_Authority_ECC.pem
│   │   │   ├── f30dd6ad.0 -> USERTrust_ECC_Certification_Authority.pem
│   │   │   ├── f3377b1b.0 -> Security_Communication_Root_CA.pem
│   │   │   ├── f387163d.0 -> Starfield_Class_2_CA.pem
│   │   │   ├── f39fc864.0 -> SecureTrust_CA.pem
│   │   │   ├── f51bb24c.0 -> Certigna_Root_CA.pem
│   │   │   ├── fc5a8f99.0 -> USERTrust_RSA_Certification_Authority.pem
│   │   │   ├── fe8a2cd8.0 -> SZAFIR_ROOT_CA2.pem
│   │   │   ├── ff34af3f.0 -> TUBITAK_Kamu_SM_SSL_Kok_Sertifikasi_-_Surum_1.pem
│   │   │   ├── GDCA_TrustAUTH_R5_ROOT.pem -> ../../../usr/share/ca-certificates/mozilla/GDCA_TrustAUTH_R5_ROOT.crt
│   │   │   ├── GeoTrust_Universal_CA_2.pem -> ../../../usr/share/ca-certificates/mozilla/GeoTrust_Universal_CA_2.crt
│   │   │   ├── Global_Chambersign_Root_-_2008.pem -> ../../../usr/share/ca-certificates/mozilla/Global_Chambersign_Root_-_2008.crt
│   │   │   ├── GlobalSign_ECC_Root_CA_-_R4.pem -> ../../../usr/share/ca-certificates/mozilla/GlobalSign_ECC_Root_CA_-_R4.crt
│   │   │   ├── GlobalSign_ECC_Root_CA_-_R5.pem -> ../../../usr/share/ca-certificates/mozilla/GlobalSign_ECC_Root_CA_-_R5.crt
│   │   │   ├── GlobalSign_Root_CA.pem -> ../../../usr/share/ca-certificates/mozilla/GlobalSign_Root_CA.crt
│   │   │   ├── GlobalSign_Root_CA_-_R2.pem -> ../../../usr/share/ca-certificates/mozilla/GlobalSign_Root_CA_-_R2.crt
│   │   │   ├── GlobalSign_Root_CA_-_R3.pem -> ../../../usr/share/ca-certificates/mozilla/GlobalSign_Root_CA_-_R3.crt
│   │   │   ├── GlobalSign_Root_CA_-_R6.pem -> ../../../usr/share/ca-certificates/mozilla/GlobalSign_Root_CA_-_R6.crt
│   │   │   ├── Go_Daddy_Class_2_CA.pem -> ../../../usr/share/ca-certificates/mozilla/Go_Daddy_Class_2_CA.crt
│   │   │   ├── Go_Daddy_Root_Certificate_Authority_-_G2.pem -> ../../../usr/share/ca-certificates/mozilla/Go_Daddy_Root_Certificate_Authority_-_G2.crt
│   │   │   ├── GTS_Root_R1.pem -> ../../../usr/share/ca-certificates/mozilla/GTS_Root_R1.crt
│   │   │   ├── GTS_Root_R2.pem -> ../../../usr/share/ca-certificates/mozilla/GTS_Root_R2.crt
│   │   │   ├── GTS_Root_R3.pem -> ../../../usr/share/ca-certificates/mozilla/GTS_Root_R3.crt
│   │   │   ├── GTS_Root_R4.pem -> ../../../usr/share/ca-certificates/mozilla/GTS_Root_R4.crt
│   │   │   ├── Hellenic_Academic_and_Research_Institutions_ECC_RootCA_2015.pem -> ../../../usr/share/ca-certificates/mozilla/Hellenic_Academic_and_Research_Institutions_ECC_RootCA_2015.crt
│   │   │   ├── Hellenic_Academic_and_Research_Institutions_RootCA_2011.pem -> ../../../usr/share/ca-certificates/mozilla/Hellenic_Academic_and_Research_Institutions_RootCA_2011.crt
│   │   │   ├── Hellenic_Academic_and_Research_Institutions_RootCA_2015.pem -> ../../../usr/share/ca-certificates/mozilla/Hellenic_Academic_and_Research_Institutions_RootCA_2015.crt
│   │   │   ├── Hongkong_Post_Root_CA_1.pem -> ../../../usr/share/ca-certificates/mozilla/Hongkong_Post_Root_CA_1.crt
│   │   │   ├── Hongkong_Post_Root_CA_3.pem -> ../../../usr/share/ca-certificates/mozilla/Hongkong_Post_Root_CA_3.crt
│   │   │   ├── IdenTrust_Commercial_Root_CA_1.pem -> ../../../usr/share/ca-certificates/mozilla/IdenTrust_Commercial_Root_CA_1.crt
│   │   │   ├── IdenTrust_Public_Sector_Root_CA_1.pem -> ../../../usr/share/ca-certificates/mozilla/IdenTrust_Public_Sector_Root_CA_1.crt
│   │   │   ├── ISRG_Root_X1.pem -> ../../../usr/share/ca-certificates/mozilla/ISRG_Root_X1.crt
│   │   │   ├── Izenpe.com.pem -> ../../../usr/share/ca-certificates/mozilla/Izenpe.com.crt
│   │   │   ├── LuxTrust_Global_Root_2.pem -> ../../../usr/share/ca-certificates/mozilla/LuxTrust_Global_Root_2.crt
│   │   │   ├── Microsec_e-Szigno_Root_CA_2009.pem -> ../../../usr/share/ca-certificates/mozilla/Microsec_e-Szigno_Root_CA_2009.crt
│   │   │   ├── NetLock_Arany_=Class_Gold=_Főtanúsítvány.pem -> ../../../usr/share/ca-certificates/mozilla/NetLock_Arany_=Class_Gold=_Főtanúsítvány.crt
│   │   │   ├── Network_Solutions_Certificate_Authority.pem -> ../../../usr/share/ca-certificates/mozilla/Network_Solutions_Certificate_Authority.crt
│   │   │   ├── OISTE_WISeKey_Global_Root_GA_CA.pem -> ../../../usr/share/ca-certificates/mozilla/OISTE_WISeKey_Global_Root_GA_CA.crt
│   │   │   ├── OISTE_WISeKey_Global_Root_GB_CA.pem -> ../../../usr/share/ca-certificates/mozilla/OISTE_WISeKey_Global_Root_GB_CA.crt
│   │   │   ├── OISTE_WISeKey_Global_Root_GC_CA.pem -> ../../../usr/share/ca-certificates/mozilla/OISTE_WISeKey_Global_Root_GC_CA.crt
│   │   │   ├── QuoVadis_Root_CA_1_G3.pem -> ../../../usr/share/ca-certificates/mozilla/QuoVadis_Root_CA_1_G3.crt
│   │   │   ├── QuoVadis_Root_CA_2_G3.pem -> ../../../usr/share/ca-certificates/mozilla/QuoVadis_Root_CA_2_G3.crt
│   │   │   ├── QuoVadis_Root_CA_2.pem -> ../../../usr/share/ca-certificates/mozilla/QuoVadis_Root_CA_2.crt
│   │   │   ├── QuoVadis_Root_CA_3_G3.pem -> ../../../usr/share/ca-certificates/mozilla/QuoVadis_Root_CA_3_G3.crt
│   │   │   ├── QuoVadis_Root_CA_3.pem -> ../../../usr/share/ca-certificates/mozilla/QuoVadis_Root_CA_3.crt
│   │   │   ├── QuoVadis_Root_CA.pem -> ../../../usr/share/ca-certificates/mozilla/QuoVadis_Root_CA.crt
│   │   │   ├── Secure_Global_CA.pem -> ../../../usr/share/ca-certificates/mozilla/Secure_Global_CA.crt
│   │   │   ├── SecureSign_RootCA11.pem -> ../../../usr/share/ca-certificates/mozilla/SecureSign_RootCA11.crt
│   │   │   ├── SecureTrust_CA.pem -> ../../../usr/share/ca-certificates/mozilla/SecureTrust_CA.crt
│��  │   │   ├── Security_Communication_RootCA2.pem -> ../../../usr/share/ca-certificates/mozilla/Security_Communication_RootCA2.crt
│   │   │   ├── Security_Communication_Root_CA.pem -> ../../../usr/share/ca-certificates/mozilla/Security_Communication_Root_CA.crt
│   │   │   ├── Sonera_Class_2_Root_CA.pem -> ../../../usr/share/ca-certificates/mozilla/Sonera_Class_2_Root_CA.crt
│   │   │   ├── SSL.com_EV_Root_Certification_Authority_ECC.pem -> ../../../usr/share/ca-certificates/mozilla/SSL.com_EV_Root_Certification_Authority_ECC.crt
│   │   │   ├── SSL.com_EV_Root_Certification_Authority_RSA_R2.pem -> ../../../usr/share/ca-certificates/mozilla/SSL.com_EV_Root_Certification_Authority_RSA_R2.crt
│   │   │   ├── SSL.com_Root_Certification_Authority_ECC.pem -> ../../../usr/share/ca-certificates/mozilla/SSL.com_Root_Certification_Authority_ECC.crt
│   │   │   ├── SSL.com_Root_Certification_Authority_RSA.pem -> ../../../usr/share/ca-certificates/mozilla/SSL.com_Root_Certification_Authority_RSA.crt
│   │   │   ├── Staat_der_Nederlanden_EV_Root_CA.pem -> ../../../usr/share/ca-certificates/mozilla/Staat_der_Nederlanden_EV_Root_CA.crt
│   │   │   ├── Staat_der_Nederlanden_Root_CA_-_G2.pem -> ../../../usr/share/ca-certificates/mozilla/Staat_der_Nederlanden_Root_CA_-_G2.crt
│   │   │   ├── Staat_der_Nederlanden_Root_CA_-_G3.pem -> ../../../usr/share/ca-certificates/mozilla/Staat_der_Nederlanden_Root_CA_-_G3.crt
│   │   │   ├── Starfield_Class_2_CA.pem -> ../../../usr/share/ca-certificates/mozilla/Starfield_Class_2_CA.crt
│   │   │   ├── Starfield_Root_Certificate_Authority_-_G2.pem -> ../../../usr/share/ca-certificates/mozilla/Starfield_Root_Certificate_Authority_-_G2.crt
│   │   │   ├── Starfield_Services_Root_Certificate_Authority_-_G2.pem -> ../../../usr/share/ca-certificates/mozilla/Starfield_Services_Root_Certificate_Authority_-_G2.crt
│   │   │   ├── SwissSign_Gold_CA_-_G2.pem -> ../../../usr/share/ca-certificates/mozilla/SwissSign_Gold_CA_-_G2.crt
│   │   │   ├── SwissSign_Silver_CA_-_G2.pem -> ../../../usr/share/ca-certificates/mozilla/SwissSign_Silver_CA_-_G2.crt
│   │   │   ├── SZAFIR_ROOT_CA2.pem -> ../../../usr/share/ca-certificates/mozilla/SZAFIR_ROOT_CA2.crt
│   │   │   ├── Taiwan_GRCA.pem -> ../../../usr/share/ca-certificates/mozilla/Taiwan_GRCA.crt
│   │   │   ├── TeliaSonera_Root_CA_v1.pem -> ../../../usr/share/ca-certificates/mozilla/TeliaSonera_Root_CA_v1.crt
│   │   │   ├── TrustCor_ECA-1.pem -> ../../../usr/share/ca-certificates/mozilla/TrustCor_ECA-1.crt
│   │   │   ├── TrustCor_RootCert_CA-1.pem -> ../../../usr/share/ca-certificates/mozilla/TrustCor_RootCert_CA-1.crt
│   │   │   ├── TrustCor_RootCert_CA-2.pem -> ../../../usr/share/ca-certificates/mozilla/TrustCor_RootCert_CA-2.crt
│   │   │   ├── Trustis_FPS_Root_CA.pem -> ../../../usr/share/ca-certificates/mozilla/Trustis_FPS_Root_CA.crt
│   │   │   ├── T-TeleSec_GlobalRoot_Class_2.pem -> ../../../usr/share/ca-certificates/mozilla/T-TeleSec_GlobalRoot_Class_2.crt
│   │   │   ├── T-TeleSec_GlobalRoot_Class_3.pem -> ../../../usr/share/ca-certificates/mozilla/T-TeleSec_GlobalRoot_Class_3.crt
│   │   │   ├── TUBITAK_Kamu_SM_SSL_Kok_Sertifikasi_-_Surum_1.pem -> ../../../usr/share/ca-certificates/mozilla/TUBITAK_Kamu_SM_SSL_Kok_Sertifikasi_-_Surum_1.crt
│   │   │   ├── TWCA_Global_Root_CA.pem -> ../../../usr/share/ca-certificates/mozilla/TWCA_Global_Root_CA.crt
│   │   │   ├── TWCA_Root_Certification_Authority.pem -> ../../../usr/share/ca-certificates/mozilla/TWCA_Root_Certification_Authority.crt
│   │   │   ├── UCA_Extended_Validation_Root.pem -> ../../../usr/share/ca-certificates/mozilla/UCA_Extended_Validation_Root.crt
│   │   │   ├── UCA_Global_G2_Root.pem -> ../../../usr/share/ca-certificates/mozilla/UCA_Global_G2_Root.crt
│   │   │   ├── USERTrust_ECC_Certification_Authority.pem -> ../../../usr/share/ca-certificates/mozilla/USERTrust_ECC_Certification_Authority.crt
│   │   │   ├── USERTrust_RSA_Certification_Authority.pem -> ../../../usr/share/ca-certificates/mozilla/USERTrust_RSA_Certification_Authority.crt
│   │   │   ├── Verisign_Class_3_Public_Primary_Certification_Authority_-_G3.pem -> ../../../usr/share/ca-certificates/mozilla/Verisign_Class_3_Public_Primary_Certification_Authority_-_G3.crt
│   │   │   └── XRamp_Global_CA_Root.pem -> ../../../usr/share/ca-certificates/mozilla/XRamp_Global_CA_Root.crt
│   │   └── openssl.cnf
│   ├── stunnel
│   │   └── stunnel.conf
│   ├── udev
│   │   └── udev.conf
│   ├── vdpau_wrapper.cfg
│   └── xdg
│       └── openbox
│           ├── environment
│           └── menu.xml
├── lib64
│   ├── dhcpcd
│   │   ├── dev
│   │   │   └── udev.so
│   │   ├── dhcpcd-hooks
│   │   │   ├── 01-test
│   │   │   ├── 20-resolv.conf
│   │   │   ├── 30-hostname
│   │   │   ├── 50-ntp.conf
│   │   │   └── 50-yp.conf
│   │   └── dhcpcd-run-hooks
│   ├── ld-2.32.so
│   ├── ld-linux-x86-64.so.2 -> ld-2.32.so
│   ├── ld-uClibc.so.0
│   ├── libanl-2.32.so
│   ├── libanl.so.1 -> libanl-2.32.so
│   ├── libattr.so.1 -> libattr.so.1.1.2448
│   ├── libattr.so.1.1.2448
│   ├── libblkid.so.1 -> libblkid.so.1.1.0
│   ├── libblkid.so.1.1.0
│   ├── libbz2.so.1 -> libbz2.so.1.0.6
│   ├── libbz2.so.1.0 -> libbz2.so.1.0.6
│   ├── libbz2.so.1.0.6
│   ├── libc-2.32.so
│   ├── libcap.so.2 -> libcap.so.2.43
│   ├── libcap.so.2.43
│   ├── libcom_err.so.2 -> libcom_err.so.2.1
│   ├── libcom_err.so.2.1
│   ├── libcrypt-2.32.so
│   ├── libcrypt.so.1 -> libcrypt-2.32.so
│   ├── libc.so.0
│   ├── libc.so.6 -> libc-2.32.so
│   ├── libdl-2.32.so
│   ├── libdl.so.2 -> libdl-2.32.so
│   ├── libext2fs.so.2 -> libext2fs.so.2.4
│   ├── libext2fs.so.2.4
│   ├── libfdisk.so.1 -> libfdisk.so.1.1.0
│   ├── libfdisk.so.1.1.0
│   ├── libip4tc.so.2 -> libip4tc.so.2.0.0
│   ├── libip4tc.so.2.0.0
│   ├── libkmod.so.2 -> libkmod.so.2.3.6
│   ├── libkmod.so.2.3.6
│   ├── libm-2.32.so
│   ├── libmnl.so.0 -> libmnl.so.0.2.0
│   ├── libmnl.so.0.2.0
│   ├── libmount.so.1 -> libmount.so.1.1.0
│   ├── libmount.so.1.1.0
│   ├── libm.so.6 -> libm-2.32.so
│   ├── libncurses.so.6 -> libncurses.so.6.2
│   ├── libncurses.so.6.2
│   ├── libnsl-2.32.so
│   ├── libnsl.so.1 -> libnsl-2.32.so
│   ├── libnss_dns-2.32.so
│   ├── libnss_dns.so.2 -> libnss_dns-2.32.so
│   ├── libnss_files-2.32.so
│   ├── libnss_files.so.2 -> libnss_files-2.32.so
│   ├── libpcre.so.1 -> libpcre.so.1.2.12
│   ├── libpcre.so.1.2.12
│   ├── libprocps.so.8 -> libprocps.so.8.0.2
│   ├── libprocps.so.8.0.2
│   ├── libpthread-2.32.so
│   ├── libpthread.so.0 -> libpthread-2.32.so
│   ├── libresolv-2.32.so
│   ├── libresolv.so.2 -> libresolv-2.32.so
│   ├── librt-2.32.so
│   ├── librt.so.1 -> librt-2.32.so
│   ├── libsmartcols.so.1 -> libsmartcols.so.1.1.0
│   ├── libsmartcols.so.1.1.0
│   ├── libtinfo.so.6 -> libtinfo.so.6.2
���   ├── libtinfo.so.6.2
│   ├── libudev.so.1 -> libudev.so.1.6.3
│   ├── libudev.so.1.6.3
│   ├── libusb-1.0.so.0 -> libusb-1.0.so.0.2.0
│   ├── libusb-1.0.so.0.2.0
│   ├── libutil-2.32.so
│   ├── libutil.so.1 -> libutil-2.32.so
│   ├── libuuid.so.1 -> libuuid.so.1.3.0
│   ├── libuuid.so.1.3.0
│   ├── libxtables.so.12 -> libxtables.so.12.3.0
│   ├── libxtables.so.12.3.0
│   ├── libz.so.1 -> libz.so.1.2.11
│   ├── libz.so.1.2.11
│   ├── modprobe.d
│   │   └── usb-load-ehci-first.conf
│   └── udev
│       ├── ata_id
│       ├── cdrom_id
│       ├── collect
│       ├── mtd_probe
│       ├── rules.d
│       │   ├── 40-gentoo.rules
│       │   ├── 50-udev-default.rules
│       │   ├── 60-block.rules
│       │   ├── 60-cdrom_id.rules
│       │   ├── 60-drm.rules
│       │   ├── 60-evdev.rules
│       │   ├── 60-input-id.rules
│       │   ├── 60-persistent-alsa.rules
│       │   ├── 60-persistent-input.rules
│       │   ├── 60-persistent-storage.rules
│       │   ├── 60-persistent-storage-tape.rules
│       │   ├── 60-persistent-v4l.rules
│       │   ├── 60-sensor.rules
│       │   ├── 60-serial.rules
│       │   ├── 64-btrfs.rules
│       │   ├── 65-libwacom.rules
│       │   ├── 70-joystick.rules
│       │   ├── 70-mouse.rules
│       │   ├── 70-touchpad.rules
│       │   ├── 75-net-description.rules
│       │   ├── 75-probe_mtd.rules
│       │   ├── 78-sound-card.rules
│       │   ├── 80-drivers.rules
│       │   ├── 80-net-name-slot.rules
│       │   └── wacom.rules
│       ├── scsi_id
│       └── v4l_id
├── sbin
│   ├── agetty
│   ├── depmod -> ../bin/kmod
│   ├── dhcpcd
│   ├── fdisk
│   ├── init
│   ├── insmod -> ../bin/kmod
│   ├── iptables -> xtables-legacy-multi
│   ├── iptables-legacy -> xtables-legacy-multi
│   ├── iptables-legacy-restore -> xtables-legacy-multi
│   ├── iptables-legacy-save -> xtables-legacy-multi
│   ├── iptables-restore -> xtables-legacy-multi
│   ├── iptables-save -> xtables-legacy-multi
│   ├── iptables-xml -> xtables-legacy-multi
│   ├── ldconfig
│   ├── mkfs.xfs
│   ├── modprobe -> ../bin/kmod
│   ├── rmmod -> ../bin/kmod
│   ├── udevadm -> //bin/udevadm
│   ├── udevd
│   ├── v86d
│   └── xtables-legacy-multi
└── usr
    ├── bin
    │   ├── alsamixer
    │   ├── alsaucm
    │   ├── amixer
    │   ├── aplay
    │   ├── apulse
    │   ├── arecord -> aplay
    │   ├── certutil
    │   ├── conky
    │   ├── c_rehash
    │   ├── crontab
    │   ├── curl
    │   ├── cvt
    │   ├── dbus-daemon
    │   ├── dbus-launch
    │   ├── dbus-send
    │   ├── dbus-uuidgen
    │   ├── dunst
    │   ├── dunstify
    │   ├── eglinfo
    │   ├── fbv
    │   ├── feh
    │   ├── free
    │   ├── fromdos
    │   ├── gio-launch-desktop
    │   ├── glxinfo
    │   ├── gsimplecal
    │   ├── gtf
    │   ├── gtkdialog
    │   ├── hhpc
    │   ├── hsetroot
    │   ├── hxselect
    │   ├── imlib2_grab
    │   ├── imlib2_view
    │   ├── iptables-xml -> /sbin/xtables-legacy-multi
    │   ���── isohybrid
    │   ├── logger
    │   ├── logrotate
    │   ├── mc
    │   ├── mcdiff -> mc
    │   ├── mcedit -> mc
    │   ├── mcookie
    │   ├── mcview -> mc
    │   ├── mkisofs
    │   ├── ntfs-3g
    │   ├── obxprop
    │   ├── openbox
    │   ├── openbox-session
    │   ├── openssl
    │   ├── pactester
    │   ├── ripples
    │   ├── rsync
    │   ├── sensors
    │   ├── setxkbmap
    │   ├── sshpass
    │   ├── stunnel
    │   ├── synclient
    │   ├── tiff2pdf
    │   ├── tint2
    │   ├── top
    │   ├── usb-devices
    │   ├── vainfo
    │   ├── vncpasswd
    │   ├── volumeicon
    │   ├── wget
    │   ├── wmctrl
    │   ├── X -> Xorg
    │   ├── xcompmgr
    │   ├── xdotool
    │   ├── xev
    │   ├── xinit
    │   ├── xinput
    │   ├── xinput_calibrator
    │   ├── xkbcomp
    │   ├── xlock
    │   ├── xmodmap
    │   ├── Xorg
    │   ├── xprintidle
    │   ├── xrandr
    │   ├── xset
    │   ├── xvkbd
    │   └── yad
    ├── lib64
    │   ├── apulse
    │   │   ├── libpulse-mainloop-glib.so -> libpulse-mainloop-glib.so.0
    │   │   ├── libpulse-mainloop-glib.so.0
    │   │   ├── libpulse-simple.so -> libpulse-simple.so.0
    │   │   ├── libpulse-simple.so.0
    │   │   ├── libpulse.so -> libpulse.so.0
    │   │   └── libpulse.so.0
    │   ├── dri
    │   │   ├── i915_dri.so
    │   │   ├── i965_dri.so
    │   │   ├── iris_dri.so
    │   │   ├── kms_swrast_dri.so
    │   │   ├── nouveau_dri.so
    │   │   ├── nouveau_vieux_dri.so
    │   │   ├── r200_dri.so
    │   │   ├── r300_dri.so
    │   │   ├── r600_dri.so
    │   │   ├── radeon_dri.so
    │   │   ├── radeonsi_dri.so
    │   │   ├── swrast_dri.so
    │   │   └── vmwgfx_dri.so
    │   ├── gconv
    │   │   ├── CP10007.so
    │   │   ├── CP1125.so
    │   │   ├── CP1250.so
    │   │   ├── CP1251.so
    │   │   ├── CP1252.so
    │   │   ├── CP1253.so
    │   │   ├── CP1254.so
    │   │   ├── CP1255.so
    │   │   ├── CP1256.so
    │   │   ├── CP1257.so
    │   │   ├── CP1258.so
    │   │   ├── CP737.so
    │   │   ├── CP770.so
    │   │   ├── CP771.so
    │   │   ├── CP772.so
    │   │   ├── CP773.so
    │   │   ├── CP774.so
    │   │   ├── CP775.so
    │   │   ├── CP932.so
    │   │   ├── gconv-modules
    │   │   ├── ISO8859-10.so
    │   │   ├── ISO8859-11.so
    │   │   ├── ISO8859-13.so
    │   │   ├── ISO8859-14.so
    │   │   ├── ISO8859-15.so
    │   │   ├── ISO8859-16.so
    │   │   ├── ISO8859-1.so
    │   │   ├── ISO8859-2.so
    │   │   ├── ISO8859-3.so
    │   │   ├── ISO8859-4.so
    │   │   ├── ISO8859-5.so
    │   │   ├── ISO8859-6.so
    │   │   ├── ISO8859-7.so
    │   │   ├── ISO8859-8.so
    │   │   ├── ISO8859-9E.so
    │   │   ├── ISO8859-9.so
    │   │   ├── UTF-16.so
    │   │   └── UTF-32.so
    │   ├── gdk-pixbuf-2.0
    │   │   └── 2.10.0
    │   │       ├── loaders
    │   │       │   ├── libpixbufloader-ani.so
    │   │       │   ├── libpixbufloader-bmp.so
    │   │       │   ├── libpixbufloader-gif.so
    │   │       │   ├── libpixbufloader-icns.so
    │   │       │   ├── libpixbufloader-ico.so
    │   │       │   ├── libpixbufloader-jpeg.so
    │   │       │   ├── libpixbufloader-pnm.so
    │   │       │   ├── libpixbufloader-qtif.so
    │   │       │   ├── libpixbufloader-svg.so
    │   │       │   ├── libpixbufloader-tga.so
    │   │       │   ├── libpixbufloader-tiff.so
    │   │       │   ├── libpixbufloader-xbm.so
    │   │       │   └── libpixbufloader-xpm.so
    │   │       └── loaders.cache
    │   ├── gtk-2.0
    │   │   └── 2.10.0
    │   │       ├── engines
    │   │       │   └── liboxygen-gtk.so
    │   │       └── printbackends
    │   │           └── libprintbackend-cups.so
    │   ├── gtk-3.0
    │   │   └── 3.0.0
    │   │       └── printbackends
    │   │           └── libprintbackend-cups.so
    │   ├── imlib2
    │   │   └── loaders
    │   │       ├── jpeg.so
    │   │       └── png.so
    │   ├── libasound.so -> libasound.so.2.0.0
    │   ├── libasound.so.2 -> libasound.so.2.0.0
    │   ├── libasound.so.2.0.0
    │   ├── libatk-1.0.so -> libatk-1.0.so.0
    │   ├── libatk-1.0.so.0 -> libatk-1.0.so.0.23609.1
    │   ├── libatk-1.0.so.0.23609.1
    │   ├── libatk-bridge-2.0.so -> libatk-bridge-2.0.so.0.0.0
    │   ├── libatk-bridge-2.0.so.0 -> libatk-bridge-2.0.so.0.0.0
    │   ├── libatk-bridge-2.0.so.0.0.0
    │   ├── libatomic.so -> libatomic.so.1.2.0
    │   ├── libatomic.so.1 -> libatomic.so.1.2.0
    │   ├── libatomic.so.1.2.0
    │   ├── libatspi.so -> libatspi.so.0.0.1
    │   ├── libatspi.so.0 -> libatspi.so.0.0.1
    │   ├── libatspi.so.0.0.1
    │   ├── libbsd.so -> libbsd.so.0.10.0
    │   ├── libbsd.so.0 -> libbsd.so.0.10.0
    │   ├── libbsd.so.0.10.0
    │   ├── libcairo-gobject.so -> libcairo-gobject.so.2.11600.0
    │   ├── libcairo-gobject.so.2 -> libcairo-gobject.so.2.11600.0
    │   ├── libcairo-gobject.so.2.11600.0
    │   ├── libcairo.so -> libcairo.so.2.11600.0
    │   ├── libcairo.so.2 -> libcairo.so.2.11600.0
    │   ├── libcairo.so.2.11600.0
    │   ├── libcrypto.so -> libcrypto.so.1.1
    │   ├── libcrypto.so.1.1
    │   ├── libcurl.so -> libcurl.so.4.7.0
    │   ├── libcurl.so.4 -> libcurl.so.4.7.0
    │   ├── libcurl.so.4.7.0
    │   ├── libdbus-1.so -> libdbus-1.so.3.19.13
    │   ├── libdbus-1.so.3 -> libdbus-1.so.3.19.13
    │   ├── libdbus-1.so.3.19.13
    │   ├── libdbus-glib-1.so -> libdbus-glib-1.so.2.3.4
    │   ├── libdbus-glib-1.so.2 -> libdbus-glib-1.so.2.3.4
    │   ├── libdbus-glib-1.so.2.3.4
    │   ├── libdrm_amdgpu.so -> libdrm_amdgpu.so.1.0.0
    │   ├── libdrm_amdgpu.so.1 -> libdrm_amdgpu.so.1.0.0
    │   ├── libdrm_amdgpu.so.1.0.0
    │   ├── libdrm_intel.so -> libdrm_intel.so.1.0.0
    │   ├── libdrm_intel.so.1 -> libdrm_intel.so.1.0.0
    │   ├── libdrm_intel.so.1.0.0
    │   ├── libdrm_nouveau.so -> libdrm_nouveau.so.2.0.0
    │   ├── libdrm_nouveau.so.2 -> libdrm_nouveau.so.2.0.0
    │   ├── libdrm_nouveau.so.2.0.0
    │   ├── libdrm_radeon.so -> libdrm_radeon.so.1.0.1
    │   ├── libdrm_radeon.so.1 -> libdrm_radeon.so.1.0.1
    │   ├── libdrm_radeon.so.1.0.1
    │   ├── libdrm.so -> libdrm.so.2.4.0
    │   ├── libdrm.so.2 -> libdrm.so.2.4.0
    │   ├── libdrm.so.2.4.0
    │   ├── libEGL_mesa.so -> libEGL_mesa.so.0
    │   ├── libEGL_mesa.so.0 -> libEGL_mesa.so.0.0.0
    │   ├── libEGL_mesa.so.0.0.0
    │   ├── libEGL.so -> libEGL.so.1
    │   ├── libEGL.so.1 -> libEGL.so.1.1.0
    │   ├── libEGL.so.1.1.0
    │   ├── libelf-0.182.so
    │   ├── libelf.so -> libelf.so.1
    │   ├── libelf.so.1 -> libelf-0.182.so
    │   ├── libepoxy.so -> libepoxy.so.0.0.0
    │   ├── libepoxy.so.0 -> libepoxy.so.0.0.0
    │   ├── libepoxy.so.0.0.0
    │   ├── libestr.so -> libestr.so.0.0.0
    │   ├── libestr.so.0 -> libestr.so.0.0.0
    │   ├── libestr.so.0.0.0
    │   ├── libevdev.so -> libevdev.so.2.3.0
    │   ├── libevdev.so.2 -> libevdev.so.2.3.0
    │   ├── libevdev.so.2.3.0
    │   ├── libexpat.so -> libexpat.so.1.6.12
    │   ├── libexpat.so.1 -> libexpat.so.1.6.12
    │   ├── libexpat.so.1.6.12
    │   ├── libfastjson.so -> libfastjson.so.4.2.0
    │   ├── libfastjson.so.4 -> libfastjson.so.4.2.0
    │   ├── libfastjson.so.4.2.0
    │   ├── libffi.so -> libffi.so.7.1.0
    │   ├── libffi.so.7 -> libffi.so.7.1.0
    │   ├── libffi.so.7.1.0
    │   ├── libfontconfig.so -> libfontconfig.so.1.12.0
    │   ├── libfontconfig.so.1 -> libfontconfig.so.1.12.0
    │   ├── libfontconfig.so.1.12.0
    │   ├── libfontenc.so -> libfontenc.so.1.0.0
    │   ├── libfontenc.so.1 -> libfontenc.so.1.0.0
    │   ├── libfontenc.so.1.0.0
    │   ├── libform.so -> libform.so.6
    │   ├── libform.so.6 -> libform.so.6.2
    │   ├── libform.so.6.2
    │   ├── libfreebl3.so
    │   ├── libfreeblpriv3.so
    │   ├── libfreetype.so -> libfreetype.so.6.17.4
    │   ├── libfreetype.so.6 -> libfreetype.so.6.17.4
    │   ├── libfreetype.so.6.17.4
    │   ├── libfribidi.so -> libfribidi.so.0.4.0
    │   ├── libfribidi.so.0 -> libfribidi.so.0.4.0
    │   ├── libfribidi.so.0.4.0
    │   ├── libfuse.so -> libfuse.so.2.9.9
    │   ├── libfuse.so.2 -> libfuse.so.2.9.9
    │   ├── libfuse.so.2.9.9
    │   ├── libgbm.so -> libgbm.so.1
    │   ├── libgbm.so.1 -> libgbm.so.1.0.0
    │   ├── libgbm.so.1.0.0
    │   ├── libgcc_s.so -> libgcc_s.so.1
    │   ├── libgcc_s.so.1
    │   ├── libgdk-3.so -> libgdk-3.so.0.2404.20
    │   ├── libgdk-3.so.0 -> libgdk-3.so.0.2404.20
    │   ├── libgdk-3.so.0.2404.20
    │   ├── libgdk_pixbuf-2.0.so -> libgdk_pixbuf-2.0.so.0
    │   ├── libgdk_pixbuf-2.0.so.0 -> libgdk_pixbuf-2.0.so.0.4200.2
    │   ├── libgdk_pixbuf-2.0.so.0.4200.2
    │   ├── libgdk-x11-2.0.so -> libgdk-x11-2.0.so.0.2400.32
    │   ├── libgdk-x11-2.0.so.0 -> libgdk-x11-2.0.so.0.2400.32
    │   ├── libgdk-x11-2.0.so.0.2400.32
    │   ├── libgio-2.0.so -> libgio-2.0.so.0
    │   ├── libgio-2.0.so.0 -> libgio-2.0.so.0.6600.7
    │   ├── libgio-2.0.so.0.6600.7
    │   ├── libglapi.so -> libglapi.so.0
    │   ├── libglapi.so.0 -> libglapi.so.0.0.0
    │   ├── libglapi.so.0.0.0
    │   ├── libGLdispatch.so -> libGLdispatch.so.0
    │   ├── libGLdispatch.so.0 -> libGLdispatch.so.0.0.0
    │   ├── libGLdispatch.so.0.0.0
    │   ├── libGLESv2.so -> libGLESv2.so.2
    │   ├── libGLESv2.so.2 -> libGLESv2.so.2.1.0
    │   ├── libGLESv2.so.2.1.0
    │   ├── libglib-2.0.so -> libglib-2.0.so.0
    │   ├── libglib-2.0.so.0 -> libglib-2.0.so.0.6600.7
    │   ├── libglib-2.0.so.0.6600.7
    │   ├── libGL.so -> libGL.so.1
    │   ├── libGL.so.1 -> libGL.so.1.7.0
    │   ├── libGL.so.1.7.0
    │   ├── libGLX_mesa.so -> libGLX_mesa.so.0
    │   ├── libGLX_mesa.so.0 -> libGLX_mesa.so.0.0.0
    │   ├── libGLX_mesa.so.0.0.0
    │   ├── libGLX.so -> libGLX.so.0
    │   ├── libGLX.so.0 -> libGLX.so.0.0.0
    │   ├── libGLX.so.0.0.0
    │   ├── libgmodule-2.0.so -> libgmodule-2.0.so.0
    │   ├── libgmodule-2.0.so.0 -> libgmodule-2.0.so.0.6600.7
    │   ├── libgmodule-2.0.so.0.6600.7
    │   ├── libgmp.so -> libgmp.so.10.4.1
    │   ├── libgmp.so.10 -> libgmp.so.10.4.1
    │   ├── libgmp.so.10.4.1
    │   ├── libgnutls.so -> libgnutls.so.30.28.1
    │   ├── libgnutls.so.30 -> libgnutls.so.30.28.1
    │   ├── libgnutls.so.30.28.1
    │   ├── libgobject-2.0.so -> libgobject-2.0.so.0
    │   ├── libgobject-2.0.so.0 -> libgobject-2.0.so.0.6600.7
    │   ├── libgobject-2.0.so.0.6600.7
    │   ├── libgthread-2.0.so -> libgthread-2.0.so.0
    │   ├── libgthread-2.0.so.0 -> libgthread-2.0.so.0.6600.7
    │   ├── libgthread-2.0.so.0.6600.7
    │   ├── libgtk-3.so -> libgtk-3.so.0.2404.20
    │   ├── libgtk-3.so.0 -> libgtk-3.so.0.2404.20
    │   ├── libgtk-3.so.0.2404.20
    │   ├── libgtk-x11-2.0.so -> libgtk-x11-2.0.so.0.2400.32
    │   ├── libgtk-x11-2.0.so.0 -> libgtk-x11-2.0.so.0.2400.32
    │   ├── libgtk-x11-2.0.so.0.2400.32
    │   ├── libgudev-1.0.so -> libgudev-1.0.so.0.3.0
    │   ├── libgudev-1.0.so.0 -> libgudev-1.0.so.0.3.0
    │   ├── libgudev-1.0.so.0.3.0
    │   ├── libharfbuzz.so -> libharfbuzz.so.0
    │   ├── libharfbuzz.so.0 -> libharfbuzz.so.0.20704.0
    │   ├── libharfbuzz.so.0.20704.0
    │   ├── libhogweed.so -> libhogweed.so.6.0
    │   ├── libhogweed.so.6 -> libhogweed.so.6.0
    │   ├── libhogweed.so.6.0
    │   ├── libICE.so -> libICE.so.6.3.0
    │   ├── libICE.so.6 -> libICE.so.6.3.0
    │   ├── libICE.so.6.3.0
    │   ├── libigdgmm.so -> libigdgmm.so.11
    │   ├── libigdgmm.so.11 -> libigdgmm.so.11.2.0
    │   ├── libigdgmm.so.11.2.0
    │   ├── libImlib2.so -> libImlib2.so.1.6.1
    │   ├── libImlib2.so.1 -> libImlib2.so.1.6.1
    │   ├── libImlib2.so.1.6.1
    │   ├── libinih.so -> libinih.so.0
    │   ├── libinih.so.0
    │   ├── libjpeg.so -> libjpeg.so.62
    │   ├── libjpeg.so.62 -> libjpeg.so.62.3.0
    │   ├── libjpeg.so.62.3.0
    │   ├── libkms.so -> libkms.so.1.0.0
    │   ├── libkms.so.1 -> libkms.so.1.0.0
    │   ├── libkms.so.1.0.0
    │   ├── libLLVM-11.0.1.so -> libLLVM-11.so
    │   ├── libLLVM-11.so
    │   ├── libLLVM.so -> libLLVM-11.so
    │   ├── libLTO.so -> libLTO.so.11
    │   ├── libLTO.so.11
    │   ├── liblua5.3.so -> liblua5.3.so.0.0.0
    │   ├── liblua5.3.so.0 -> liblua5.3.so.0.0.0
    │   ├── liblua5.3.so.0.0.0
    │   ├── libmenu.so -> libmenu.so.6
    │   ├── libmenu.so.6 -> libmenu.so.6.2
    │   ├── libmenu.so.6.2
    │   ├── libmtdev.so -> libmtdev.so.1.0.0
    │   ├── libmtdev.so.1 -> libmtdev.so.1.0.0
    │   ├── libmtdev.so.1.0.0
    │   ├── libnettle.so -> libnettle.so.8.0
    │   ├── libnettle.so.8 -> libnettle.so.8.0
    │   ├── libnettle.so.8.0
    │   ├── libnghttp2.so -> libnghttp2.so.14.20.0
    │   ├── libnghttp2.so.14 -> libnghttp2.so.14.20.0
    │   ├── libnghttp2.so.14.20.0
    │   ├── libnotify.so -> libnotify.so.4.0.0
    │   ├── libnotify.so.4 -> libnotify.so.4.0.0
    │   ├── libnotify.so.4.0.0
    │   ├── libnspr4.so
    │   ├── libnss3.so
    │   ├── libnssckbi.so
    │   ├── libnssdbm3.so
    │   ├── libnsssysinit.so
    │   ├── libnssutil3.so
    │   ├── libntfs-3g.so -> libntfs-3g.so.88.0.0
    │   ├── libntfs-3g.so.88 -> libntfs-3g.so.88.0.0
    │   ├── libntfs-3g.so.88.0.0
    │   ├── libobrender.so -> libobrender.so.32.0.0
    │   ├── libobrender.so.32 -> libobrender.so.32.0.0
    │   ├── libobrender.so.32.0.0
    │   ├── libobt.so -> libobt.so.2.0.2
    │   ├── libobt.so.2 -> libobt.so.2.0.2
    │   ├── libobt.so.2.0.2
    │   ├── libpacparser.so -> libpacparser.so.1
    │   ├── libpacparser.so.1
    │   ├── libpanel.so -> libpanel.so.6
    │   ├── libpanel.so.6 -> libpanel.so.6.2
    │   ├── libpanel.so.6.2
    │   ├── libpango-1.0.so -> libpango-1.0.so.0.4200.4
    │   ├── libpango-1.0.so.0 -> libpango-1.0.so.0.4200.4
    │   ├── libpango-1.0.so.0.4200.4
    │   ├── libpangocairo-1.0.so -> libpangocairo-1.0.so.0.4200.4
    │   ├── libpangocairo-1.0.so.0 -> libpangocairo-1.0.so.0.4200.4
    │   ├── libpangocairo-1.0.so.0.4200.4
    │   ├── libpangoft2-1.0.so -> libpangoft2-1.0.so.0.4200.4
    │   ├── libpangoft2-1.0.so.0 -> libpangoft2-1.0.so.0.4200.4
    │   ├── libpangoft2-1.0.so.0.4200.4
    │   ├── libpangoxft-1.0.so -> libpangoxft-1.0.so.0.4200.4
    │   ├── libpangoxft-1.0.so.0 -> libpangoxft-1.0.so.0.4200.4
    │   ├── libpangoxft-1.0.so.0.4200.4
    │   ├── libpciaccess.so -> libpciaccess.so.0.11.1
    │   ├── libpciaccess.so.0 -> libpciaccess.so.0.11.1
    │   ├── libpciaccess.so.0.11.1
    │   ├── libpci.so -> libpci.so.3
    │   ├── libpci.so.3 -> libpci.so.3.6.4
    │   ├── libpci.so.3.6.4
    │   ├── libpixman-1.so -> libpixman-1.so.0
    │   ├── libpixman-1.so.0 -> libpixman-1.so.0.40.0
    │   ├── libpixman-1.so.0.40.0
    │   ├── libplc4.so
    │   ├── libplds4.so
    │   ├── libpng16.so -> libpng16.so.16.37.0
    │   ├── libpng16.so.16 -> libpng16.so.16.37.0
    │   ├── libpng16.so.16.37.0
    │   ├── libpng.so -> libpng16.so
    │   ├── libpopt.so -> libpopt.so.0.0.1
    │   ├── libpopt.so.0 -> libpopt.so.0.0.1
    │   ├── libpopt.so.0.0.1
    │   ├── libRemarks.so -> libRemarks.so.11
    │   ├── libRemarks.so.11
    │   ├── librsvg-2.so -> librsvg-2.so.2.47.0
    │   ├── librsvg-2.so.2 -> librsvg-2.so.2.47.0
    │   ├── librsvg-2.so.2.47.0
    │   ├── libsensors.so -> libsensors.so.5
    │   ├── libsensors.so.5 -> libsensors.so.5.0.0
    │   ├── libsensors.so.5.0.0
    │   ├── libsmime3.so
    │   ├── libSM.so -> libSM.so.6.0.1
    │   ├── libSM.so.6 -> libSM.so.6.0.1
    │   ├── libSM.so.6.0.1
    │   ├── libsoftokn3.so
    │   ├── libsqlite3.so -> libsqlite3.so.0.8.6
    │   ├── libsqlite3.so.0 -> libsqlite3.so.0.8.6
    │   ├── libsqlite3.so.0.8.6
    │   ├── libssl3.so
    │   ├── libssl.so -> libssl.so.1.1
    │   ├── libssl.so.1.1
    │   ├── libstartup-notification-1.so -> libstartup-notification-1.so.0.0.0
    │   ├── libstartup-notification-1.so.0 -> libstartup-notification-1.so.0.0.0
    │   ├── libstartup-notification-1.so.0.0.0
    │   ├── libstdc++.so -> libstdc++.so.6.0.28
    │   ├── libstdc++.so.6 -> libstdc++.so.6.0.28
    │   ├── libstdc++.so.6.0.28
    │   ├── libtasn1.so -> libtasn1.so.6.6.0
    │   ├── libtasn1.so.6 -> libtasn1.so.6.6.0
    │   ├── libtasn1.so.6.6.0
    │   ├── libtcp-portmon.so
    │   ├── libtiff.so -> libtiff.so.5.6.0
    │   ├── libtiff.so.5 -> libtiff.so.5.6.0
    │   ├── libtiff.so.5.6.0
    │   ├── libunistring.so -> libunistring.so.2.1.0
    │   ├── libunistring.so.2 -> libunistring.so.2.1.0
    │   ├── libunistring.so.2.1.0
    │   ├── libva-drm.so -> libva-drm.so.2.1000.0
    │   ├── libva-drm.so.2 -> libva-drm.so.2.1000.0
    │   ├── libva-drm.so.2.1000.0
    │   ├── libva-glx.so -> libva-glx.so.2.1000.0
    │   ├── libva-glx.so.2 -> libva-glx.so.2.1000.0
    │   ├── libva-glx.so.2.1000.0
    │   ├── libva.so -> libva.so.2.1000.0
    │   ├── libva.so.2 -> libva.so.2.1000.0
    │   ├── libva.so.2.1000.0
    │   ├── libva-x11.so -> libva-x11.so.2.1000.0
    │   ├── libva-x11.so.2 -> libva-x11.so.2.1000.0
    │   ├── libva-x11.so.2.1000.0
    │   ├── libvdpau.so -> libvdpau.so.1.0.0
    │   ├── libvdpau.so.1 -> libvdpau.so.1.0.0
    │   ├── libvdpau.so.1.0.0
    │   ├── libvte.so -> libvte.so.9.2800.2
    │   ├── libvte.so.9 -> libvte.so.9.2800.2
    │   ├── libvte.so.9.2800.2
    │   ├── libwacom.so -> libwacom.so.2.6.1
    │   ├── libwacom.so.2 -> libwacom.so.2.6.1
    │   ├── libwacom.so.2.6.1
    │   ├── libwayland-client.so -> libwayland-client.so.0.3.0
    │   ├── libwayland-client.so.0 -> libwayland-client.so.0.3.0
    │   ├── libwayland-client.so.0.3.0
    │   ├── libwayland-cursor.so -> libwayland-cursor.so.0.0.0
    │   ├── libwayland-cursor.so.0 -> libwayland-cursor.so.0.0.0
    │   ├── libwayland-cursor.so.0.0.0
    │   ├── libwayland-egl.so -> libwayland-egl.so.1.0.0
    │   ├── libwayland-egl.so.1 -> libwayland-egl.so.1.0.0
    │   ├── libwayland-egl.so.1.0.0
    │   ├── libwayland-server.so -> libwayland-server.so.0.1.0
    │   ├── libwayland-server.so.0 -> libwayland-server.so.0.1.0
    │   ├── libwayland-server.so.0.1.0
    │   ├── libX11.so -> libX11.so.6.4.0
    │   ├── libX11.so.6 -> libX11.so.6.4.0
    │   ├── libX11.so.6.4.0
    │   ├── libX11-xcb.so -> libX11-xcb.so.1.0.0
    │   ├── libX11-xcb.so.1 -> libX11-xcb.so.1.0.0
    │   ├── libX11-xcb.so.1.0.0
    │   ├── libxatracker.so -> libxatracker.so.2
    │   ├── libxatracker.so.2 -> libxatracker.so.2.5.0
    │   ├── libxatracker.so.2.5.0
    │   ├── libXau.so -> libXau.so.6.0.0
    │   ├── libXau.so.6 -> libXau.so.6.0.0
    │   ├── libXau.so.6.0.0
    │   ├── libXaw3d.so -> libXaw3d.so.8.0.0
    │   ├── libXaw3d.so.8 -> libXaw3d.so.8.0.0
    │   ├── libXaw3d.so.8.0.0
    │   ├── libxcb-composite.so -> libxcb-composite.so.0.0.0
    │   ├── libxcb-composite.so.0 -> libxcb-composite.so.0.0.0
    │   ├── libxcb-composite.so.0.0.0
    │   ├── libxcb-cursor.so -> libxcb-cursor.so.0.0.0
    │   ├── libxcb-cursor.so.0 -> libxcb-cursor.so.0.0.0
    │   ├── libxcb-cursor.so.0.0.0
    │   ├── libxcb-damage.so -> libxcb-damage.so.0.0.0
    │   ├── libxcb-damage.so.0 -> libxcb-damage.so.0.0.0
    │   ├── libxcb-damage.so.0.0.0
    │   ├── libxcb-dpms.so -> libxcb-dpms.so.0.0.0
    │   ├── libxcb-dpms.so.0 -> libxcb-dpms.so.0.0.0
    │   ├── libxcb-dpms.so.0.0.0
    │   ├── libxcb-dri2.so -> libxcb-dri2.so.0.0.0
    │   ├── libxcb-dri2.so.0 -> libxcb-dri2.so.0.0.0
    │   ├── libxcb-dri2.so.0.0.0
    │   ├── libxcb-dri3.so -> libxcb-dri3.so.0.0.0
    │   ├── libxcb-dri3.so.0 -> libxcb-dri3.so.0.0.0
    │   ├── libxcb-dri3.so.0.0.0
    │   ├── libxcb-ewmh.so -> libxcb-ewmh.so.2.0.0
    │   ├── libxcb-ewmh.so.2 -> libxcb-ewmh.so.2.0.0
    │   ├── libxcb-ewmh.so.2.0.0
    │   ├── libxcb-glx.so -> libxcb-glx.so.0.0.0
    │   ├── libxcb-glx.so.0 -> libxcb-glx.so.0.0.0
    │   ├── libxcb-glx.so.0.0.0
    │   ├── libxcb-icccm.so -> libxcb-icccm.so.4.0.0
    │   ├── libxcb-icccm.so.4 -> libxcb-icccm.so.4.0.0
    │   ├── libxcb-icccm.so.4.0.0
    │   ├── libxcb-image.so -> libxcb-image.so.0.0.0
    │   ├── libxcb-image.so.0 -> libxcb-image.so.0.0.0
    │   ├── libxcb-image.so.0.0.0
    │   ├── libxcb-keysyms.so -> libxcb-keysyms.so.1.0.0
    │   ├── libxcb-keysyms.so.1 -> libxcb-keysyms.so.1.0.0
    │   ├── libxcb-keysyms.so.1.0.0
    │   ├── libxcb-present.so -> libxcb-present.so.0.0.0
    │   ├── libxcb-present.so.0 -> libxcb-present.so.0.0.0
    │   ├── libxcb-present.so.0.0.0
    │   ├── libxcb-randr.so -> libxcb-randr.so.0.1.0
    │   ├── libxcb-randr.so.0 -> libxcb-randr.so.0.1.0
    │   ├── libxcb-randr.so.0.1.0
    │   ├── libxcb-record.so -> libxcb-record.so.0.0.0
    │   ├── libxcb-record.so.0 -> libxcb-record.so.0.0.0
    │   ├── libxcb-record.so.0.0.0
    │   ├── libxcb-render.so -> libxcb-render.so.0.0.0
    │   ├── libxcb-render.so.0 -> libxcb-render.so.0.0.0
    │   ├── libxcb-render.so.0.0.0
    │   ├── libxcb-render-util.so -> libxcb-render-util.so.0.0.0
    │   ├── libxcb-render-util.so.0 -> libxcb-render-util.so.0.0.0
    │   ├── libxcb-render-util.so.0.0.0
    │   ├── libxcb-res.so -> libxcb-res.so.0.0.0
    │   ├── libxcb-res.so.0 -> libxcb-res.so.0.0.0
    │   ├── libxcb-res.so.0.0.0
    │   ├── libxcb-screensaver.so -> libxcb-screensaver.so.0.0.0
    │   ├── libxcb-screensaver.so.0 -> libxcb-screensaver.so.0.0.0
    │   ├── libxcb-screensaver.so.0.0.0
    │   ├── libxcb-shape.so -> libxcb-shape.so.0.0.0
    │   ├── libxcb-shape.so.0 -> libxcb-shape.so.0.0.0
    │   ├── libxcb-shape.so.0.0.0
    │   ├── libxcb-shm.so -> libxcb-shm.so.0.0.0
    │   ├── libxcb-shm.so.0 -> libxcb-shm.so.0.0.0
    │   ├── libxcb-shm.so.0.0.0
    │   ├── libxcb.so -> libxcb.so.1.1.0
    │   ├── libxcb.so.1 -> libxcb.so.1.1.0
    │   ├── libxcb.so.1.1.0
    │   ├── libxcb-sync.so -> libxcb-sync.so.1.0.0
    │   ├── libxcb-sync.so.1 -> libxcb-sync.so.1.0.0
    │   ├── libxcb-sync.so.1.0.0
    │   ├── libxcb-util.so -> libxcb-util.so.1.0.0
    │   ├── libxcb-util.so.1 -> libxcb-util.so.1.0.0
    │   ├── libxcb-util.so.1.0.0
    │   ├── libxcb-xf86dri.so -> libxcb-xf86dri.so.0.0.0
    │   ├── libxcb-xf86dri.so.0 -> libxcb-xf86dri.so.0.0.0
    │   ├── libxcb-xf86dri.so.0.0.0
    │   ├── libxcb-xfixes.so -> libxcb-xfixes.so.0.0.0
    │   ├── libxcb-xfixes.so.0 -> libxcb-xfixes.so.0.0.0
    │   ├── libxcb-xfixes.so.0.0.0
    │   ├── libxcb-xinerama.so -> libxcb-xinerama.so.0.0.0
    │   ├── libxcb-xinerama.so.0 -> libxcb-xinerama.so.0.0.0
    │   ├── libxcb-xinerama.so.0.0.0
    │   ├── libxcb-xinput.so -> libxcb-xinput.so.0.1.0
    │   ├── libxcb-xinput.so.0 -> libxcb-xinput.so.0.1.0
    │   ├── libxcb-xinput.so.0.1.0
    │   ├── libxcb-xkb.so -> libxcb-xkb.so.1.0.0
    │   ├── libxcb-xkb.so.1 -> libxcb-xkb.so.1.0.0
    │   ├── libxcb-xkb.so.1.0.0
    │   ├── libxcb-xtest.so -> libxcb-xtest.so.0.0.0
    │   ├── libxcb-xtest.so.0 -> libxcb-xtest.so.0.0.0
    │   ├── libxcb-xtest.so.0.0.0
    │   ├── libxcb-xvmc.so -> libxcb-xvmc.so.0.0.0
    │   ├── libxcb-xvmc.so.0 -> libxcb-xvmc.so.0.0.0
    │   ├── libxcb-xvmc.so.0.0.0
    │   ├── libxcb-xv.so -> libxcb-xv.so.0.0.0
    │   ├── libxcb-xv.so.0 -> libxcb-xv.so.0.0.0
    │   ├── libxcb-xv.so.0.0.0
    │   ├── libXcomposite.so -> libXcomposite.so.1.0.0
    │   ├── libXcomposite.so.1 -> libXcomposite.so.1.0.0
    │   ├── libXcomposite.so.1.0.0
    │   ├── libXcursor.so -> libXcursor.so.1.0.2
    │   ├── libXcursor.so.1 -> libXcursor.so.1.0.2
    │   ├── libXcursor.so.1.0.2
    │   ├── libXdamage.so -> libXdamage.so.1.1.0
    │   ├── libXdamage.so.1 -> libXdamage.so.1.1.0
    │   ├── libXdamage.so.1.1.0
    │   ├── libxdg-basedir.so -> libxdg-basedir.so.1.2.0
    │   ├── libxdg-basedir.so.1 -> libxdg-basedir.so.1.2.0
    │   ├── libxdg-basedir.so.1.2.0
    │   ├── libXdmcp.so -> libXdmcp.so.6.0.0
    │   ├── libXdmcp.so.6 -> libXdmcp.so.6.0.0
    │   ├── libXdmcp.so.6.0.0
    │   ├── libxdo.so -> libxdo.so.3
    │   ├── libxdo.so.3
    │   ├── libXext.so -> libXext.so.6.4.0
    │   ├── libXext.so.6 -> libXext.so.6.4.0
    │   ├── libXext.so.6.4.0
    │   ├── libXfixes.so -> libXfixes.so.3.1.0
    │   ├── libXfixes.so.3 -> libXfixes.so.3.1.0
    │   ├── libXfixes.so.3.1.0
    │   ├── libXfont2.so -> libXfont2.so.2.0.0
    │   ├── libXfont2.so.2 -> libXfont2.so.2.0.0
    │   ├── libXfont2.so.2.0.0
    │   ├── libXft.so -> libXft.so.2.3.3
    │   ├── libXft.so.2 -> libXft.so.2.3.3
    │   ├── libXft.so.2.3.3
    │   ├── libXinerama.so -> libXinerama.so.1.0.0
    │   ├── libXinerama.so.1 -> libXinerama.so.1.0.0
    │   ├── libXinerama.so.1.0.0
    │   ├── libXi.so -> libXi.so.6.1.0
    │   ├── libXi.so.6 -> libXi.so.6.1.0
    │   ├── libXi.so.6.1.0
    │   ├── libxkbcommon.so -> libxkbcommon.so.0.0.0
    │   ├── libxkbcommon.so.0 -> libxkbcommon.so.0.0.0
    │   ├── libxkbcommon.so.0.0.0
    │   ├── libxkbcommon-x11.so -> libxkbcommon-x11.so.0.0.0
    │   ├── libxkbcommon-x11.so.0 -> libxkbcommon-x11.so.0.0.0
    │   ├── libxkbcommon-x11.so.0.0.0
    │   ├── libxkbfile.so -> libxkbfile.so.1.0.2
    │   ├── libxkbfile.so.1 -> libxkbfile.so.1.0.2
    │   ├── libxkbfile.so.1.0.2
    │   ├── libxml2.so -> libxml2.so.2.9.10
    │   ├── libxml2.so.2 -> libxml2.so.2.9.10
    │   ├── libxml2.so.2.9.10
    │   ├── libXmu.so -> libXmu.so.6.2.0
    │   ├── libXmu.so.6 -> libXmu.so.6.2.0
    │   ├── libXmu.so.6.2.0
    │   ├── libXmuu.so -> libXmuu.so.1.0.0
    │   ├── libXmuu.so.1 -> libXmuu.so.1.0.0
    │   ├── libXmuu.so.1.0.0
    │   ├── libXpm.so -> libXpm.so.4.11.0
    │   ├── libXpm.so.4 -> libXpm.so.4.11.0
    │   ├── libXpm.so.4.11.0
    │   ├── libXrandr.so -> libXrandr.so.2.2.0
    │   ├── libXrandr.so.2 -> libXrandr.so.2.2.0
    │   ├── libXrandr.so.2.2.0
    │   ├── libXrender.so -> libXrender.so.1.3.0
    │   ├── libXrender.so.1 -> libXrender.so.1.3.0
    │   ├── libXrender.so.1.3.0
    │   ├── libxshmfence.so -> libxshmfence.so.1.0.0
    │   ├── libxshmfence.so.1 -> libxshmfence.so.1.0.0
    │   ├── libxshmfence.so.1.0.0
    │   ├── libxslt.so -> libxslt.so.1.1.34
    │   ├── libxslt.so.1 -> libxslt.so.1.1.34
    │   ├── libxslt.so.1.1.34
    │   ├── libXss.so -> libXss.so.1.0.0
    │   ├── libXss.so.1 -> libXss.so.1.0.0
    │   ├── libXss.so.1.0.0
    │   ├── libXt.so -> libXt.so.6.0.0
    │   ├── libXt.so.6 -> libXt.so.6.0.0
    │   ├── libXt.so.6.0.0
    │   ├── libXtst.so -> libXtst.so.6.1.0
    │   ├── libXtst.so.6 -> libXtst.so.6.1.0
    │   ├── libXtst.so.6.1.0
    │   ├── libXv.so -> libXv.so.1.0.0
    │   ├── libXv.so.1 -> libXv.so.1.0.0
    │   ├── libXv.so.1.0.0
    │   ├── libXxf86vm.so -> libXxf86vm.so.1.0.0
    │   ├── libXxf86vm.so.1 -> libXxf86vm.so.1.0.0
    │   ├── libXxf86vm.so.1.0.0
    │   ├── libzstd.so -> libzstd.so.1.4.5
    │   ├── libzstd.so.1 -> libzstd.so.1.4.5
    │   ├── libzstd.so.1.4.5
    │   ├── locale
    │   │   └── locale-archive
    │   ├── rsyslog
    │   │   ├── fmhash.so
    │   │   ├── imdiag.so
    │   │   ├── imfile.so
    │   │   ├── imklog.so
    │   │   ├── immark.so
    │   │   ├── impstats.so
    │   │   ├── imptcp.so
    │   │   ├── imtcp.so
    │   │   ├── imudp.so
    │   │   ├── imuxsock.so
    │   │   ├── lmnet.so
    │   │   ├── lmnetstrms.so
    │   │   ├── lmnsd_ptcp.so
    │   │   ├── lmregexp.so
    │   │   ├── lmtcpclt.so
    │   │   ├── lmtcpsrv.so
    │   │   ├── lmzlibw.so
    │   │   ├── mmanon.so
    │   │   ├── mmaudit.so
    │   │   ├── mmcount.so
    │   │   ├── mmexternal.so
    │   │   ├── mmfields.so
    │   │   ├── mmjsonparse.so
    │   │   ├── mmpstrucdata.so
    │   │   ├── mmrm1stspace.so
    │   │   ├── mmsequence.so
    │   │   ├── mmutf8fix.so
    │   │   ├── ommail.so
    │   │   ├── omprog.so
    │   │   ├── omruleset.so
    │   │   ├── omstdout.so
    │   │   ├── omtesting.so
    │   │   ├── omuxsock.so
    │   │   ├── pmaixforwardedfrom.so
    │   │   ├── pmciscoios.so
    │   │   ├── pmcisconames.so
    │   │   ├── pmlastmsg.so
    │   │   ├── pmnull.so
    │   │   ├── pmpanngfw.so
    │   │   └── pmsnare.so
    │   ├── va
    │   │   └── drivers
    │   │       ├── i965_drv_video.so
    │   │       ├── iHD_drv_video.so
    │   │       ├── nouveau_drv_video.so
    │   │       ├── r600_drv_video.so
    │   │       └── radeonsi_drv_video.so
    │   ├── vdpau
    │   │   ├── libvdpau_nouveau.so -> libvdpau_nouveau.so.1.0.0
    │   │   ├── libvdpau_nouveau.so.1 -> libvdpau_nouveau.so.1.0.0
    │   │   ├── libvdpau_nouveau.so.1.0 -> libvdpau_nouveau.so.1.0.0
    │   │   ├── libvdpau_nouveau.so.1.0.0
    │   │   ├── libvdpau_r300.so -> libvdpau_r300.so.1.0.0
    │   │   ├── libvdpau_r300.so.1 -> libvdpau_r300.so.1.0.0
    │   │   ├── libvdpau_r300.so.1.0 -> libvdpau_r300.so.1.0.0
    │   │   ├── libvdpau_r300.so.1.0.0
    │   │   ├── libvdpau_r600.so -> libvdpau_r600.so.1.0.0
    │   │   ├── libvdpau_r600.so.1 -> libvdpau_r600.so.1.0.0
    │   │   ├── libvdpau_r600.so.1.0 -> libvdpau_r600.so.1.0.0
    │   │   ├── libvdpau_r600.so.1.0.0
    │   │   ├── libvdpau_radeonsi.so -> libvdpau_radeonsi.so.1.0.0
    │   │   ├── libvdpau_radeonsi.so.1 -> libvdpau_radeonsi.so.1.0.0
    │   │   ├── libvdpau_radeonsi.so.1.0 -> libvdpau_radeonsi.so.1.0.0
    │   │   ├── libvdpau_radeonsi.so.1.0.0
    │   │   ├── libvdpau_trace.so -> libvdpau_trace.so.1.0.0
    │   │   ├── libvdpau_trace.so.1 -> libvdpau_trace.so.1.0.0
    │   │   └── libvdpau_trace.so.1.0.0
    │   ├── xorg
    │   │   ├── modules
    │   │   │   ├── drivers
    │   │   │   │   ├── amdgpu_drv.so
    │   │   │   │   ├── ast_drv.so
    │   │   │   │   ├── ati_drv.so
    │   │   │   │   ├── fbdev_drv.so
    │   │   │   │   ├── glint_drv.so
    │   │   │   │   ├── intel_drv.so
    │   │   │   │   ├── mga_drv.so
    │   │   │   │   ├── modesetting_drv.so
    │   │   │   │   ├── nouveau_drv.so
    │   │   │   │   ├── openchrome_drv.so
    │   │   │   │   ├── qxl_drv.so
    │   │   │   │   ├── r128_drv.so
    │   │   │   │   ├── radeon_drv.so
    │   │   │   │   ├── siliconmotion_drv.so
    │   │   │   │   ├── vboxvideo_drv.so
    │   │   │   │   ├── vesa_drv.so
    │   │   │   │   └── vmware_drv.so
    │   │   │   ├── extensions
    │   │   │   │   └── libglx.so
    │   │   │   ├── input
    │   │   │   │   ├── elographics_drv.so
    │   │   │   │   ├── evdev_drv.so
    │   │   │   │   ├── synaptics_drv.so
    │   │   │   │   └── wacom_drv.so
    │   │   │   ├── libexa.so
    │   │   │   ├── libfbdevhw.so
    │   │   │   ├── libfb.so
    │   │   │   ├── libglamoregl.so
    │   │   │   ├── libint10.so
    │   │   │   ├── libshadowfb.so
    │   │   │   ├── libshadow.so
    │   │   │   ├── libvbe.so
    │   │   │   ├── libvgahw.so
    │   │   │   └── libwfb.so
    │   │   └── protocol.txt
    │   └── xtables
    │       ├── libipt_ah.so
    │       ├── libipt_CLUSTERIP.so
    │       ├── libipt_DNAT.so
    │       ├── libipt_ECN.so
    │       ├── libipt_icmp.so
    │       ├── libipt_LOG.so
    │       ├── libipt_MASQUERADE.so
    │       ├── libipt_NETMAP.so
    │       ├── libipt_realm.so
    │       ├── libipt_REDIRECT.so
    │       ├── libipt_REJECT.so
    │       ├── libipt_SNAT.so
    │       ├── libipt_ttl.so
    │       ├── libipt_TTL.so
    │       ├── libipt_ULOG.so
    │       ├── libxt_addrtype.so
    │       ├── libxt_AUDIT.so
    │       ├── libxt_bpf.so
    │       ├── libxt_cgroup.so
    │       ├── libxt_CHECKSUM.so
    │       ├── libxt_CLASSIFY.so
    │       ├── libxt_cluster.so
    │       ├── libxt_comment.so
    │       ├── libxt_connbytes.so
    │       ├── libxt_connlimit.so
    │       ├── libxt_connmark.so
    │       ├── libxt_CONNMARK.so
    │       ├── libxt_CONNSECMARK.so
    │       ├── libxt_conntrack.so
    │       ├── libxt_cpu.so
    │       ├── libxt_CT.so
    │       ├── libxt_dccp.so
    │       ├── libxt_devgroup.so
    │       ├── libxt_dscp.so
    │       ├── libxt_DSCP.so
    │       ├── libxt_ecn.so
    │       ├── libxt_esp.so
    │       ├── libxt_hashlimit.so
    │       ├── libxt_helper.so
    │       ├── libxt_HMARK.so
    │       ├── libxt_IDLETIMER.so
    │       ├── libxt_ipcomp.so
    │       ├── libxt_iprange.so
    │       ├── libxt_ipvs.so
    │       ├── libxt_LED.so
    │       ├── libxt_length.so
    │       ├── libxt_limit.so
    │       ├── libxt_mac.so
    │       ├── libxt_mark.so
    │       ├── libxt_MARK.so
    │       ├── libxt_multiport.so
    │       ├── libxt_nfacct.so
    │       ├── libxt_NFLOG.so
    │       ├── libxt_NFQUEUE.so
    │       ├── libxt_NOTRACK.so -> libxt_CT.so
    │       ├── libxt_osf.so
    │       ├── libxt_owner.so
    │       ├── libxt_physdev.so
    │       ├── libxt_pkttype.so
    │       ├── libxt_policy.so
    │       ├── libxt_quota.so
    │       ├── libxt_rateest.so
    │       ├── libxt_RATEEST.so
    │       ├── libxt_recent.so
    │       ├── libxt_rpfilter.so
    │       ├── libxt_sctp.so
    │       ├── libxt_SECMARK.so
    │       ├── libxt_set.so
    │       ├── libxt_SET.so
    │       ├── libxt_socket.so
    │       ├── libxt_standard.so
    │       ├── libxt_state.so -> libxt_conntrack.so
    │       ├── libxt_statistic.so
    │       ├── libxt_string.so
    │       ├── libxt_SYNPROXY.so
    │       ├── libxt_tcpmss.so
    │       ├── libxt_TCPMSS.so
    │       ├── libxt_TCPOPTSTRIP.so
    │       ├── libxt_tcp.so
    │       ├── libxt_TEE.so
    │       ├── libxt_time.so
    │       ├── libxt_tos.so
    │       ├── libxt_TOS.so
    │       ├── libxt_TPROXY.so
    │       ├── libxt_TRACE.so
    │       ├── libxt_u32.so
    │       └── libxt_udp.so
    ├── libexec
    │   ├── mc
    │   │   ├── cons.saver
    │   │   ├── ext.d
    │   │   │   ├── archive.sh
    │   │   │   ├── doc.sh
    │   │   │   ├── image.sh
    │   │   │   ├── misc.sh
    │   │   │   ├── package.sh
    │   │   │   ├── sound.sh
    │   │   │   ├── text.sh
    │   │   │   ├── video.sh
    │   │   │   └── web.sh
    │   │   ├── extfs.d
    │   │   │   ├── a+
    │   │   │   ├── apt+
    │   │   │   ├── audio
    │   │   │   ├── bpp
    │   │   │   ├── changesetfs
    │   │   │   ├── deb
    │   │   │   ├── deba
    │   │   │   ├── debd
    │   │   │   ├── dpkg+
    │   │   │   ├── gitfs+
    │   │   │   ├── hp48+
    │   │   │   ├── iso9660
    │   │   │   ├── lslR
    │   │   │   ├── mailfs
    │   │   │   ├── patchfs
    │   │   │   ├── patchsetfs
    │   │   │   ├── README
    │   │   │   ├── README.extfs
    │   │   │   ├── rpm
    │   │   │   ├── rpms+
    │   │   │   ├── s3+
    │   │   │   ├── trpm
    │   │   │   ├── u7z
    │   │   │   ├── uace
    │   │   │   ├── ualz
    │   │   │   ├── uar
    │   │   │   ├── uarc
    │   │   │   ├── uarj
    │   │   │   ├── uc1541
    │   │   │   ├── ucab
    │   │   │   ├── uha
    │   │   │   ├── ulha
    │   │   │   ├── ulib
    │   │   │   ├── urar
    │   │   │   ├── uzip
    │   │   │   └── uzoo
    │   │   ├── fish
    │   │   │   ├── append
    │   │   │   ├── chmod
    │   │   │   ├── chown
    │   │   │   ├── fexists
    │   │   │   ├── get
    │   │   │   ├── hardlink
    │   │   │   ├── info
    │   │   │   ├── ln
    │   │   │   ├── ls
    │   │   │   ├── mkdir
    │   │   │   ├── mv
    │   │   │   ├── README.fish
    │   │   │   ├── rmdir
    │   │   │   ├── send
    │   │   │   ├── unlink
    │   │   │   └── utime
    │   │   ├── mc.csh
    │   │   ├── mc.sh
    │   │   ├── mc-wrapper.csh
    │   │   └── mc-wrapper.sh
    │   └── openbox-autostart
    ├── sbin
    │   ├── acpid
    │   ├── crond
    │   ├── ethtool
    │   ├── fatlabel
    │   ├── lspci
    │   ├── mkfs.fat
    │   ├── mtr
    │   ├── ntpdate
    │   ├── rsyslogd
    │   ├── run-crons
    │   ├── update-ca-certificates
    │   └── xfs_db
    └── share
        ├── alsa
        │   ├── alsa.conf
        │   ├── cards
        │   │   ├── AACI.conf
        │   │   ├── aliases.conf
        │   │   ├── ATIIXP.conf
        │   │   ├── ATIIXP-MODEM.conf
        │   │   ├── ATIIXP-SPDMA.conf
        │   │   ├── AU8810.conf
        │   │   ├── AU8820.conf
        │   │   ├── AU8830.conf
        │   │   ├── Audigy2.conf
        │   │   ├── Audigy.conf
        │   │   ├── Aureon51.conf
        │   │   ├── Aureon71.conf
        │   │   ├── CA0106.conf
        │   │   ├── CMI8338.conf
        │   │   ├── CMI8338-SWIEC.conf
        │   │   ├── CMI8738-MC6.conf
        │   │   ├── CMI8738-MC8.conf
        │   │   ├── CMI8788.conf
        │   │   ├── CS46xx.conf
        │   │   ├── Echo_Echo3G.conf
        │   │   ├── EMU10K1.conf
        │   │   ├── EMU10K1X.conf
        │   │   ├── ENS1370.conf
        │   │   ├── ENS1371.conf
        │   │   ├── ES1968.conf
        │   │   ├── FireWave.conf
        │   │   ├── FM801.conf
        │   │   ├── FWSpeakers.conf
        │   │   ├── GUS.conf
        │   │   ├── HDA-Intel.conf
        │   │   ├── HdmiLpeAudio.conf
        │   │   ├── ICE1712.conf
        │   │   ├── ICE1724.conf
        │   │   ├── ICH4.conf
        │   │   ├── ICH.conf
        │   │   ├── ICH-MODEM.conf
        │   │   ├── Loopback.conf
        │   │   ├── Maestro3.conf
        │   │   ├── NFORCE.conf
        │   │   ├── PC-Speaker.conf
        │   │   ├── pistachio-card.conf
        │   │   ├── PMac.conf
        │   │   ├── PMacToonie.conf
        │   │   ├── PS3.conf
        │   │   ├── RME9636.conf
        │   │   ├── RME9652.conf
        │   │   ├── SB-XFi.conf
        │   │   ├── SI7018.conf
        │   │   ├── TRID4DWAVENX.conf
        │   │   ├── USB-Audio.conf
        │   │   ├── vc4-hdmi.conf
        │   │   ├── VIA686A.conf
        │   │   ├── VIA8233A.conf
        │   │   ├── VIA8233.conf
        │   │   ├── VIA8237.conf
        │   │   ├── VX222.conf
        │   │   ├── VXPocket440.conf
        │   │   ├── VXPocket.conf
        │   │   └── YMF744.conf
        │   ├── init
        │   │   ├── 00main
        │   │   ├── ca0106
        │   │   ├── default
        │   │   ├── hda
        │   │   ├── help
        │   │   ├── info
        │   │   └── test
        │   ├── pcm
        │   │   ├── center_lfe.conf
        │   │   ├── default.conf
        │   │   ├── dmix.conf
        │   │   ├── dpl.conf
        │   │   ├── dsnoop.conf
        │   │   ├── front.conf
        │   │   ├── hdmi.conf
        │   │   ├── iec958.conf
        │   │   ├── modem.conf
        │   │   ├── rear.conf
        │   │   ├── side.conf
        │   │   ├── surround21.conf
        │   │   ├── surround40.conf
        │   │   ├── surround41.conf
        │   │   ├── surround50.conf
        │   │   ├── surround51.conf
        │   │   └── surround71.conf
        │   ├── speaker-test
        │   │   └── sample_map.csv
        │   ├── topology
        │   │   ├── broadwell
        │   │   │   └── broadwell.conf
        │   │   ├── bxtrt298
        │   │   │   └── bxt_i2s.conf
        │   │   ├── hda-dsp
        │   │   │   └── skl_hda_dsp_generic-tplg.conf
        │   │   └── sklrt286
        │   │       └── skl_i2s.conf
        │   ├── ucm
        │   │   └── README.md
        │   └── ucm2
        │       ├── broadwell-rt286
        │       │   ├── broadwell-rt286.conf
        │       │   └── HiFi.conf
        │       ├── broxton-rt298
        │       │   ├── broxton-rt298.conf
        │       │   ├── Hdmi.conf
        │       │   └── HiFi.conf
        │       ├── bytcht-cx2072x
        │       │   ├── bytcht-cx2072x.conf
        │       │   └── HiFi.conf
        │       ├── bytcht-es8316
        │       │   ├── bytcht-es8316.conf
        │       │   ├── HiFi-Components.conf
        │       │   ├── HiFi.conf
        │       │   └── HiFi-LongName.conf
        │       ├── bytcr-rt5640
        │       │   ├── bytcr-rt5640.conf
        │       │   ├── HiFi-Components.conf
        │       │   ├── HiFi.conf
        │       │   └── HiFi-LongName.conf
        │       ├── bytcr-rt5651
        │       │   ├── bytcr-rt5651.conf
        │       │   ├── HiFi-Components.conf
        │       │   ├── HiFi.conf
        │       │   └── HiFi-LongName.conf
        │       ├── cht-bsw-rt5672
        │       │   ├── cht-bsw-rt5672.conf
        │       │   ├── cht-bsw-rt5672-stereo-dmic2.conf
        │       │   ├── HiFi.conf
        │       │   ├── HiFi-stereo-dmic2.conf
        │       │   ├── LENOVO-20BN002QGE-ThinkPad8-20BN002QGE.conf -> cht-bsw-rt5672-stereo-dmic2.conf
        │       │   └── LENOVO-20BN002QGE-ThinkPad8.conf -> cht-bsw-rt5672-stereo-dmic2.conf
        │       ├── chtmax98090
        │       │   ├── chtmax98090.conf
        │       │   └── HiFi.conf
        │       ├── chtnau8824
        │       │   ├── chtnau8824.conf
        │       │   ├── chtnau8824-mono.conf
        │       │   ├── cube-i1_TF-Defaultstring-CherryTrailCR.conf -> chtnau8824-mono.conf
        │       │   ├── HiFi.conf
        │       │   ├── HiFi-mono.conf
        │       │   └── PIPO-W2S-Defaultstring-CherryTrailCR.conf -> chtnau8824-mono.conf
        │       ├── chtrt5645
        │       │   ├── ASUSTeKCOMPUTERINC.-T100HAN-1.0.conf -> chtrt5645-dmic1.conf
        │       │   ├── ASUSTeKCOMPUTERINC.-T100HAN-1.0-T100HAN.conf -> chtrt5645-dmic1.conf
        │       │   ├── chtrt5645.conf
        │       │   ├── chtrt5645-dmic1.conf
        │       │   ├── chtrt5645-dmic2.conf
        │       │   ├── chtrt5645-mono-speaker-analog-mic.conf
        │       │   ├── gpd-win-pocket-rt5645.conf -> chtrt5645-mono-speaker-analog-mic.conf
        │       │   ├── HiFi.conf
        │       │   ├── HiFi-dmic1.conf
        │       │   ├── HiFi-dmic2.conf
        │       │   ├── HiFi-mono-speaker-analog-mic.conf
        │       │   ├── LENOVO-80XF-LenovoMIIX320_10ICR-LNVNB161216.conf -> chtrt5645-dmic2.conf
        │       │   ├── MEDION-E1239TMD60568-0.1-Wingman.conf -> chtrt5645-dmic2.conf
        │       │   └── TECLAST-X80Pro-Defaultstring-CherryTrailCR.conf -> chtrt5645-mono-speaker-analog-mic.conf
        │       ├── chtrt5650
        │       │   ├── chtrt5650.conf
        │       │   └── HiFi.conf
        │       ├── codecs
        │       │   ├── cx2072x
        │       │   │   ├── DisableSeq.conf
        │       │   │   ├── EnableSeq.conf
        │       │   │   ├── HeadPhones.conf
        │       │   │   ├── HeadsetMic.conf
        │       │   │   ├── InternalMic.conf
        │       │   │   └── Speaker.conf
        │       │   ├── es8316
        │       │   │   ├── EnableSeq.conf
        │       │   │   ├── HeadPhones.conf
        │       │   │   ├── IN1-HeadsetMic.conf
        │       │   │   ├── IN1-InternalMic.conf
        │       │   │   ├── IN2-HeadsetMic.conf
        │       │   │   ├── IN2-InternalMic.conf
        │       │   │   ├── MonoSpeaker.conf
        │       │   │   └── Speaker.conf
        │       │   ├── max98090
        │       │   │   ├── EnableSeq.conf
        │       │   │   ├── Headphones.conf
        │       │   │   ├── HeadsetMic.conf
        │       │   │   ├── InternalMic.conf
        │       │   │   └── Speaker.conf
        │       │   ├── nau8824
        │       │   │   ├── EnableSeq.conf
        │       │   │   ├── HeadPhones.conf
        │       │   │   ├── HeadsetMic.conf
        │       │   │   ├── InternalMic.conf
        │       │   │   ├── MonoSpeaker.conf
        │       │   │   └── Speaker.conf
        │       │   ├── rt5640
        │       │   │   ├── DigitalMics.conf
        │       │   │   ├── EnableSeq.conf
        │       │   │   ├── HeadPhones.conf
        │       │   │   ├── HeadsetMic.conf
        │       │   │   ├── IN1-InternalMic.conf
        │       │   │   ├── IN3-InternalMic.conf
        │       │   │   ├── MonoSpeaker.conf
        │       │   │   └── Speaker.conf
        │       │   ├── rt5645
        │       │   │   ├── AnalogMic.conf
        │       │   │   ├── DigitalMicDisableSeq.conf
        │       │   │   ├── DigitalMicEnableSeq.conf
        │       │   │   ├── DisableSeq.conf
        │       │   │   ├── EnableSeq.conf
        │       │   │   ├── HeadphonesEnableSeq.conf
        │       │   │   ├── HSMicDisableSeq.conf
        │       │   │   ├── HSMicEnableSeq.conf
        │       │   │   └── SpeakerEnableSeq.conf
        │       │   ├── rt5651
        │       │   │   ├── DigitalMic.conf
        │       │   │   ├── EnableSeq.conf
        │       │   │   ├── HeadPhones.conf
        │       │   │   ├── HeadPhones-swapped.conf
        │       │   │   ├── IN12-InternalMic.conf
        │       │   │   ├── IN1-InternalMic.conf
        │       │   │   ├── IN2-HeadsetMic.conf
        │       │   │   ├── IN2-InternalMic.conf
        │       │   │   ├── IN3-HeadsetMic.conf
        │       │   │   ├── MonoSpeaker.conf
        │       │   │   └── Speaker.conf
        │       │   ├── rt5672
        │       │   │   ├── DMIC1.conf
        │       │   │   ├── DMIC2.conf
        │       │   │   ├── EnableSeq.conf
        │       │   │   ├── HeadPhones.conf
        │       │   │   ├── HeadsetMic.conf
        │       │   │   ├── MonoSpeaker.conf
        │       │   │   └── Speaker.conf
        │       │   ├── wcd934x
        │       │   │   ├── DefaultDisableSeq.conf
        │       │   │   ├── DefaultEnableSeq.conf
        │       │   │   ├── HeadphoneDisableSeq.conf
        │       │   │   ├── HeadphoneEnableSeq.conf
        │       │   │   ├── HeadphoneMicDisableSeq.conf
        │       │   │   ├── HeadphoneMicEnableSeq.conf
        │       │   │   ├── SpeakerDisableSeq.conf
        │       │   │   └── SpeakerEnableSeq.conf
        │       │   └── wsa881x
        │       │       ├── DefaultEnableSeq.conf
        │       │       ├── SpeakerDisableSeq.conf
        │       │       └── SpeakerEnableSeq.conf
        │       ├── DAISY-I2S
        │       │   ├── DAISY-I2S.conf
        │       │   └── HiFi.conf
        │       ├── DB410c
        │       │   ├── DB410c.conf
        │       │   ├── HDMI.conf
        │       │   └── HiFi.conf
        │       ├── DB820c
        │       │   ├── DB820c.conf
        │       │   ├── HDMI.conf
        │       │   └── HiFi.conf
        │       ├── DB845c
        │       │   ├── DB845c.conf
        │       │   ├── HDMI.conf
        │       │   └── HiFi.conf
        │       ├── GoogleNyan
        │       │   ├── GoogleNyan.conf
        │       │   └── HiFi.conf
        │       ├── hda-dsp
        │       │   ├── hda-dsp.conf
        │       │   ├── Hdmi1.conf
        │       │   ├── Hdmi2.conf
        │       │   └── HiFi.conf
        │       ├── HDA-Intel
        │       │   ├── HDAudio-DualCodecs.conf
        │       │   ├── HDAudio-Gigabyte-ALC1220DualCodecs.conf -> HDAudio-DualCodecs.conf
        │       │   ├── HDAudio-Lenovo-DualCodecs.conf -> HDAudio-DualCodecs.conf
        │       │   └── HiFi-dual.conf
        │       ├── kblrt5660
        │       │   ├── Hdmi1.conf
        │       │   ├── Hdmi2.conf
        │       │   ├── HiFi.conf
        │       │   └── kblrt5660.conf
        │       ├── PandaBoard
        │       │   ├── FMAnalog.conf
        │       │   ├���─ HiFi.conf
        │       │   ├── HiFiLP.conf
        │       │   ├── PandaBoard.conf
        │       │   ├── Record.conf
        │       │   ├── VoiceCall.conf
        │       │   └── Voice.conf
        │       ├── PandaBoardES
        │       │   ├── FMAnalog.conf
        │       │   ├── HiFi.conf
        │       │   ├── HiFiLP.conf
        │       │   ├── PandaBoardES.conf
        │       │   ├── Record.conf
        │       │   ├── VoiceCall.conf
        │       │   └── Voice.conf
        │       ├── PAZ00
        │       │   ├── HiFi.conf
        │       │   ├── PAZ00.conf
        │       │   └── Record.conf
        │       ├── platforms
        │       │   └── bytcr
        │       │       ├── PlatformDisableSeq.conf
        │       │       └── PlatformEnableSeq.conf
        │       ├── README.md
        │       ├── SDP4430
        │       │   ├── FMAnalog.conf
        │       │   ├── HiFi.conf
        │       │   ├── HiFiLP.conf
        │       │   ├── Record.conf
        │       │   ├── SDP4430.conf
        │       │   ├── VoiceCall.conf
        │       │   └── Voice.conf
        │       ├── skylake-rt286
        │       │   ├── Hdmi1.conf
        │       │   ├── Hdmi2.conf
        │       │   ├── HiFi.conf
        │       │   └── skylake-rt286.conf
        │       ├── SOF
        │       │   ├── HiFi.conf
        │       │   └── SOF.conf
        │       ├── sof-bdw-rt5677
        │       │   ├── HiFi.conf
        │       │   └── sof-bdw-rt5677.conf
        │       ├── sof-hda-dsp
        │       │   ├── HDA-Capture-value.conf
        │       │   ├── Hdmi.conf
        │       │   ├── HiFi.conf
        │       │   └── sof-hda-dsp.conf
        │       ├── tegraalc5632
        │       │   └── tegraalc5632.conf
        │       ├── ucm.conf
        │       ├── USB-Audio
        │       │   ├── Dell-WD15-Dock.conf
        │       │   ├── Dell-WD15-Dock-HiFi.conf
        │       │   ├── Realtek-ALC1220-VB-Desktop.conf
        │       │   └── Realtek-ALC1220-VB-Desktop-HiFi.conf
        │       └── VEYRON-I2S
        │           ├── HiFi.conf
        │           └── VEYRON-I2S.conf
        ├── ca-certificates
        │   ├── cacert.org
        │   │   └── cacert.org_root.crt
        │   └── mozilla
        │       ├── ACCVRAIZ1.crt
        │       ├── AC_RAIZ_FNMT-RCM.crt
        │       ├── Actalis_Authentication_Root_CA.crt
        │       ├── AffirmTrust_Commercial.crt
        │       ├── AffirmTrust_Networking.crt
        │       ├── AffirmTrust_Premium.crt
        │       ├── AffirmTrust_Premium_ECC.crt
        │       ├── Amazon_Root_CA_1.crt
        │       ├── Amazon_Root_CA_2.crt
        │       ├── Amazon_Root_CA_3.crt
        │       ├── Amazon_Root_CA_4.crt
        │       ├── Atos_TrustedRoot_2011.crt
        │       ├── Autoridad_de_Certificacion_Firmaprofesional_CIF_A62634068.crt
        │       ├── Baltimore_CyberTrust_Root.crt
        │       ├── Buypass_Class_2_Root_CA.crt
        │       ├── Buypass_Class_3_Root_CA.crt
        │       ├── CAcert_Inc._2.crt
        │       ├── CA_Disig_Root_R2.crt
        │       ├── Certigna.crt
        │       ├── Certigna_Root_CA.crt
        │       ├── certSIGN_ROOT_CA.crt
        │       ├── Certum_Trusted_Network_CA_2.crt
        │       ├── Certum_Trusted_Network_CA.crt
        │       ├── CFCA_EV_ROOT.crt
        │       ├── Chambers_of_Commerce_Root_-_2008.crt
        │       ├── Comodo_AAA_Services_root.crt
        │       ├── COMODO_Certification_Authority.crt
        │       ├── COMODO_ECC_Certification_Authority.crt
        │       ├── COMODO_RSA_Certification_Authority.crt
        │       ├── Cybertrust_Global_Root.crt
        │       ├── DigiCert_Assured_ID_Root_CA.crt
        │       ├── DigiCert_Assured_ID_Root_G2.crt
        │       ├── DigiCert_Assured_ID_Root_G3.crt
        │       ├── DigiCert_Global_Root_CA.crt
        │       ├── DigiCert_Global_Root_G2.crt
        │       ├── DigiCert_Global_Root_G3.crt
        │       ├── DigiCert_High_Assurance_EV_Root_CA.crt
        │       ├── DigiCert_Trusted_Root_G4.crt
        │       ├── DST_Root_CA_X3.crt
        │       ├── D-TRUST_Root_Class_3_CA_2_2009.crt
        │       ├── D-TRUST_Root_Class_3_CA_2_EV_2009.crt
        │       ├── EC-ACC.crt
        │       ├── EE_Certification_Centre_Root_CA.crt
        │       ├── emSign_ECC_Root_CA_-_C3.crt
        │       ├── emSign_ECC_Root_CA_-_G3.crt
        │       ├── emSign_Root_CA_-_C1.crt
        │       ├── emSign_Root_CA_-_G1.crt
        │       ├── Entrust.net_Premium_2048_Secure_Server_CA.crt
        │       ├── Entrust_Root_Certification_Authority.crt
        │       ├── Entrust_Root_Certification_Authority_-_EC1.crt
        │       ├── Entrust_Root_Certification_Authority_-_G2.crt
        │       ├── Entrust_Root_Certification_Authority_-_G4.crt
        │       ├── ePKI_Root_Certification_Authority.crt
        │       ├── E-Tugra_Certification_Authority.crt
        │       ├── GDCA_TrustAUTH_R5_ROOT.crt
        │       ├── GeoTrust_Universal_CA_2.crt
        │       ├── Global_Chambersign_Root_-_2008.crt
        │       ├── GlobalSign_ECC_Root_CA_-_R4.crt
        │       ├── GlobalSign_ECC_Root_CA_-_R5.crt
        │       ├── GlobalSign_Root_CA.crt
        │       ├── GlobalSign_Root_CA_-_R2.crt
        │       ├── GlobalSign_Root_CA_-_R3.crt
        │       ├── GlobalSign_Root_CA_-_R6.crt
        │       ├── Go_Daddy_Class_2_CA.crt
        │       ├── Go_Daddy_Root_Certificate_Authority_-_G2.crt
        │       ├── GTS_Root_R1.crt
        │       ├── GTS_Root_R2.crt
        │       ├── GTS_Root_R3.crt
        │       ├── GTS_Root_R4.crt
        │       ├── Hellenic_Academic_and_Research_Institutions_ECC_RootCA_2015.crt
        │       ├── Hellenic_Academic_and_Research_Institutions_RootCA_2011.crt
        │       ├── Hellenic_Academic_and_Research_Institutions_RootCA_2015.crt
        │       ├── Hongkong_Post_Root_CA_1.crt
        │       ├── Hongkong_Post_Root_CA_3.crt
        │       ├── IdenTrust_Commercial_Root_CA_1.crt
        │       ├── IdenTrust_Public_Sector_Root_CA_1.crt
        │       ├── ISRG_Root_X1.crt
        │       ├── Izenpe.com.crt
        │       ├── LuxTrust_Global_Root_2.crt
        │       ├── Microsec_e-Szigno_Root_CA_2009.crt
        │       ├── NetLock_Arany_=Class_Gold=_Főtanúsítvány.crt
        │       ├── Network_Solutions_Certificate_Authority.crt
        │       ├── OISTE_WISeKey_Global_Root_GA_CA.crt
        │       ├── OISTE_WISeKey_Global_Root_GB_CA.crt
        │       ├── OISTE_WISeKey_Global_Root_GC_CA.crt
        │       ├── QuoVadis_Root_CA_1_G3.crt
        │       ├── QuoVadis_Root_CA_2.crt
        │       ├── QuoVadis_Root_CA_2_G3.crt
        │       ├── QuoVadis_Root_CA_3.crt
        │       ├── QuoVadis_Root_CA_3_G3.crt
        │       ├── QuoVadis_Root_CA.crt
        │       ├── Secure_Global_CA.crt
        │       ├── SecureSign_RootCA11.crt
        │       ├── SecureTrust_CA.crt
        │       ├── Security_Communication_RootCA2.crt
        │       ├── Security_Communication_Root_CA.crt
        │       ├── Sonera_Class_2_Root_CA.crt
        │       ├── SSL.com_EV_Root_Certification_Authority_ECC.crt
        │       ├── SSL.com_EV_Root_Certification_Authority_RSA_R2.crt
        │       ├── SSL.com_Root_Certification_Authority_ECC.crt
        │       ├── SSL.com_Root_Certification_Authority_RSA.crt
        │       ├── Staat_der_Nederlanden_EV_Root_CA.crt
        │       ├── Staat_der_Nederlanden_Root_CA_-_G2.crt
        │       ├── Staat_der_Nederlanden_Root_CA_-_G3.crt
        │       ├── Starfield_Class_2_CA.crt
        │       ├── Starfield_Root_Certificate_Authority_-_G2.crt
        │       ├── Starfield_Services_Root_Certificate_Authority_-_G2.crt
        │       ├── SwissSign_Gold_CA_-_G2.crt
        │       ├── SwissSign_Silver_CA_-_G2.crt
        │       ├── SZAFIR_ROOT_CA2.crt
        │       ├── Taiwan_GRCA.crt
        │       ├── TeliaSonera_Root_CA_v1.crt
        │       ├── TrustCor_ECA-1.crt
        │       ├── TrustCor_RootCert_CA-1.crt
        │       ├── TrustCor_RootCert_CA-2.crt
        │       ├── Trustis_FPS_Root_CA.crt
        │       ├── T-TeleSec_GlobalRoot_Class_2.crt
        │       ├── T-TeleSec_GlobalRoot_Class_3.crt
        │       ├── TUBITAK_Kamu_SM_SSL_Kok_Sertifikasi_-_Surum_1.crt
        │       ├── TWCA_Global_Root_CA.crt
        │       ├── TWCA_Root_Certification_Authority.crt
        │       ├── UCA_Extended_Validation_Root.crt
        │       ├── UCA_Global_G2_Root.crt
        │       ├── USERTrust_ECC_Certification_Authority.crt
        │       ├── USERTrust_RSA_Certification_Authority.crt
        │       ├── Verisign_Class_3_Public_Primary_Certification_Authority_-_G3.crt
        │       └── XRamp_Global_CA_Root.crt
        ├── dbus-1
        │   ├── session.conf
        │   └── system.conf
        ├── dhcpcd
        │   └── hooks
        │       ├── 10-wpa_supplicant
        │       ├── 15-timezone
        │       └── 29-lookup-hostname
        ├── drirc.d
        │   └── 00-mesa-defaults.conf
        ├── fonts
        │   └── dejavu
        │       ├── DejaVuSans-Bold.ttf
        │       ├── DejaVuSans.ttf
        │       ├── DejaVuSerif-Bold.ttf
        │       └── DejaVuSerif.ttf
        ├── glvnd
        │   └── egl_vendor.d
        │       └── 50_mesa.json
        ├── icons
        │   ├── Adwaita
        │   │   ├── 16x16
        │   │   │   ├── actions
        │   │   │   │   ├── action-unavailable-symbolic.symbolic.png
        │   │   │   │   ├── address-book-new-symbolic.symbolic.png
        │   │   │   │   ├── application-exit-symbolic.symbolic.png
        │   │   │   │   ├── appointment-new-symbolic.symbolic.png
        │   │   │   │   ├── bookmark-new-symbolic.symbolic.png
        │   │   │   │   ├── call-start-symbolic.symbolic.png
        │   │   │   │   ├── call-stop-symbolic.symbolic.png
        ���   │   │   │   ├── camera-switch-symbolic.symbolic.png
        │   │   │   │   ├── chat-message-new-symbolic.symbolic.png
        │   │   │   │   ├── color-select-symbolic.symbolic.png
        │   │   │   │   ├── contact-new-symbolic.symbolic.png
        │   │   │   │   ├── document-edit-symbolic.symbolic.png
        │   │   │   │   ├── document-new-symbolic.symbolic.png
        │   │   │   │   ├── document-open-recent-symbolic.symbolic.png
        │   │   │   │   ├── document-open-symbolic.symbolic.png
        │   │   │   │   ├── document-page-setup-symbolic.symbolic.png
        │   │   │   │   ├── document-print-preview-symbolic.symbolic.png
        │   │   │   │   ├── document-print-symbolic.symbolic.png
        │   │   │   │   ├── document-properties-symbolic.symbolic.png
        │   │   │   │   ├── document-revert-symbolic-rtl.symbolic.png
        │   │   │   │   ├── document-revert-symbolic.symbolic.png
        │   │   │   │   ├── document-save-as-symbolic.symbolic.png
        │   │   │   │   ├── document-save-symbolic.symbolic.png
        │   │   │   │   ├── document-send-symbolic.symbolic.png
        │   │   │   │   ├── edit-clear-all-symbolic.symbolic.png
        │   │   │   │   ├── edit-clear-symbolic-rtl.symbolic.png
        │   │   │   │   ├── edit-clear-symbolic.symbolic.png
        │   │   │   │   ├── edit-copy-symbolic.symbolic.png
        │   │   │   │   ├── edit-cut-symbolic.symbolic.png
        │   │   │   │   ├── edit-delete-symbolic.symbolic.png
        │   │   │   │   ├── edit-find-replace-symbolic.symbolic.png
        │   │   │   │   ├── edit-find-symbolic.symbolic.png
        │   │   │   │   ├── edit-paste-symbolic.symbolic.png
        │   │   │   │   ├── edit-redo-symbolic-rtl.symbolic.png
        │   │   │   │   ├── edit-redo-symbolic.symbolic.png
        │   │   │   │   ├── edit-select-all-symbolic.symbolic.png
        │   │   │   │   ├── edit-select-symbolic.symbolic.png
        │   │   │   │   ├── edit-undo-symbolic-rtl.symbolic.png
        │   │   │   │   ├── edit-undo-symbolic.symbolic.png
        │   │   │   │   ├── error-correct-symbolic.symbolic.png
        │   │   │   │   ├── find-location-symbolic.symbolic.png
        │   │   │   │   ├── folder-new-symbolic.symbolic.png
        │   │   │   │   ├── font-select-symbolic.symbolic.png
        │   │   │   │   ├── format-indent-less-symbolic-rtl.symbolic.png
        │   │   │   │   ├── format-indent-less-symbolic.symbolic.png
        │   │   │   │   ├── format-indent-more-symbolic-rtl.symbolic.png
        │   │   │   │   ├── format-indent-more-symbolic.symbolic.png
        │   │   │   │   ├── format-justify-center-symbolic.symbolic.png
        │   │   │   │   ├── format-justify-fill-symbolic.symbolic.png
        │   │   │   │   ├── format-justify-left-symbolic.symbolic.png
        │   │   │   │   ├── format-justify-right-symbolic.symbolic.png
        │   │   │   │   ├── format-text-bold-symbolic.symbolic.png
        │   │   │   │   ├── format-text-direction-symbolic-rtl.symbolic.png
        │   │   │   │   ├── format-text-direction-symbolic.symbolic.png
        │   │   │   │   ├── format-text-italic-symbolic.symbolic.png
        │   │   │   │   ├── format-text-strikethrough-symbolic.symbolic.png
        │   │   │   │   ├── format-text-underline-symbolic.symbolic.png
        │   │   │   │   ├── go-bottom-symbolic.symbolic.png
        │   │   │   │   ├── go-down-symbolic.symbolic.png
        │   │   │   │   ├── go-first-symbolic-rtl.symbolic.png
        │   │   │   │   ├── go-first-symbolic.symbolic.png
        │   │   │   │   ├── go-home-symbolic.symbolic.png
        │   │   │   │   ├── go-jump-symbolic-rtl.symbolic.png
        │   │   │   │   ├── go-jump-symbolic.symbolic.png
        │   │   │   │   ├── go-last-symbolic-rtl.symbolic.png
        │   │   │   │   ├── go-last-symbolic.symbolic.png
        │   │   │   │   ├── go-next-symbolic-rtl.symbolic.png
        │   │   │   │   ├── go-next-symbolic.symbolic.png
        │   │   │   │   ├── go-previous-symbolic-rtl.symbolic.png
        │   │   │   │   ├── go-previous-symbolic.symbolic.png
        │   │   │   │   ├── go-top-symbolic.symbolic.png
        │   │   │   │   ├── go-up-symbolic.symbolic.png
        │   │   │   │   ├── help-about-symbolic.symbolic.png
        │   │   │   │   ├── insert-image-symbolic.symbolic.png
        │   │   │   │   ├── insert-link-symbolic.symbolic.png
        │   │   │   │   ├── insert-object-symbolic.symbolic.png
        │   │   │   │   ├── insert-text-symbolic.symbolic.png
        │   │   │   │   ├── list-add-symbolic.symbolic.png
        │   │   │   │   ├── list-remove-all-symbolic.symbolic.png
        │   │   │   │   ├── list-remove-symbolic.symbolic.png
        │   │   │   │   ├── mail-forward-symbolic.symbolic.png
        │   │   │   │   ├── mail-mark-important-symbolic.symbolic.png
        │   │   │   │   ├── mail-mark-junk-symbolic.symbolic.png
        │   │   │   │   ├── mail-mark-notjunk-symbolic.symbolic.png
        │   │   │   │   ├── mail-message-new-symbolic.symbolic.png
        │   │   │   │   ├── mail-reply-all-symbolic.symbolic.png
        │   │   │   │   ├── mail-reply-sender-symbolic.symbolic.png
        │   │   │   │   ├── mail-send-receive-symbolic.symbolic.png
        │   │   │   │   ├── mail-send-symbolic.symbolic.png
        │   │   │   │   ├── mark-location-symbolic.symbolic.png
        │   │   │   │   ├── media-eject-symbolic.symbolic.png
        │   │   │   │   ├── media-playback-pause-symbolic.symbolic.png
        │   │   │   │   ├── media-playback-start-symbolic.symbolic.png
        │   │   │   │   ├── media-playback-stop-symbolic.symbolic.png
        │   │   │   │   ├── media-record-symbolic.symbolic.png
        │   │   │   │   ├── media-seek-backward-symbolic.symbolic.png
        │   │   │   │   ├── media-seek-forward-symbolic.symbolic.png
        │   │   │   │   ├── media-skip-backward-symbolic.symbolic.png
        │   │   │   │   ├── media-skip-forward-symbolic.symbolic.png
        │   │   │   │   ├── media-view-subtitles-symbolic.symbolic.png
        │   │   │   │   ├── object-flip-horizontal-symbolic.symbolic.png
        │   │   │   │   ├── object-flip-vertical-symbolic.symbolic.png
        │   │   │   │   ├── object-rotate-left-symbolic.symbolic.png
        │   │   │   │   ├── object-rotate-right-symbolic.symbolic.png
        │   │   │   │   ├── object-select-symbolic.symbolic.png
        │   │   │   │   ├── open-menu-symbolic.symbolic.png
        │   │   │   │   ├── process-stop-symbolic.symbolic.png
        │   │   │   │   ├── send-to-symbolic.symbolic.png
        │   │   │   │   ├── sidebar-hide-symbolic.symbolic.png
        │   │   │   │   ├── sidebar-show-symbolic.symbolic.png
        │   │   │   │   ├── star-new-symbolic.symbolic.png
        │   │   │   │   ├── system-log-out-symbolic.symbolic.png
        │   │   │   │   ├── system-reboot-symbolic.symbolic.png
        │   │   │   │   ├── system-run-symbolic.symbolic.png
        │   │   │   │   ├── system-search-symbolic.symbolic.png
        │   │   │   │   ├── system-shutdown-symbolic.symbolic.png
        │   │   │   │   ├── system-switch-user-symbolic.symbolic.png
        │   │   │   │   ├── tab-new-symbolic.symbolic.png
        │   │   │   │   ├── tools-check-spelling-symbolic.symbolic.png
        │   │   │   │   ├── value-decrease-symbolic.symbolic.png
        │   │   │   │   ├── value-increase-symbolic.symbolic.png
        │   │   │   │   ├── view-app-grid-symbolic.symbolic.png
        │   │   │   │   ├── view-conceal-symbolic.symbolic.png
        │   │   │   │   ├── view-continuous-symbolic.symbolic.png
        │   │   │   │   ├── view-dual-symbolic.symbolic.png
        │   │   │   │   ├── view-fullscreen-symbolic.symbolic.png
        │   │   │   │   ├── view-grid-symbolic.symbolic.png
        │   │   │   │   ├── view-list-bullet-symbolic.symbolic.png
        │   │   │   │   ├── view-list-ordered-symbolic.symbolic.png
        │   │   │   │   ├── view-list-symbolic.symbolic.png
        │   │   │   │   ├── view-mirror-symbolic.symbolic.png
        │   │   │   │   ├── view-more-horizontal-symbolic.symbolic.png
        │   │   │   │   ├── view-more-symbolic.symbolic.png
        │   │   │   │   ├── view-paged-symbolic.symbolic.png
        │   │   │   │   ├── view-pin-symbolic.symbolic.png
        │   │   │   │   ├── view-refresh-symbolic.symbolic.png
        │   │   │   │   ├── view-restore-symbolic.symbolic.png
        │   │   │   │   ├── view-reveal-symbolic.symbolic.png
        │   │   │   │   ├── view-sort-ascending-symbolic.symbolic.png
        │   │   │   │   ├── view-sort-descending-symbolic.symbolic.png
        │   │   │   │   ├── zoom-fit-best-symbolic.symbolic.png
        │   │   │   │   ├── zoom-in-symbolic.symbolic.png
        │   │   │   │   ├── zoom-original-symbolic.symbolic.png
        │   │   │   │   └── zoom-out-symbolic.symbolic.png
        │   │   │   ├── apps
        │   │   │   │   ├── accessories-calculator-symbolic.symbolic.png
        │   │   │   │   ├── accessories-character-map-symbolic.symbolic.png
        │   │   │   │   ├── accessories-dictionary-symbolic.symbolic.png
        │   │   │   │   ├── accessories-text-editor-symbolic.symbolic.png
        │   │   │   │   ├── applets-screenshooter-symbolic.symbolic.png
        │   │   │   │   ├── gnome-power-manager-symbolic.symbolic.png
        │   │   │   │   ├── goa-panel-symbolic.symbolic.png
        │   │   │   │   ├── help-browser-symbolic.symbolic.png
        │   │   │   │   ├── help-contents-symbolic.symbolic.png
        │   │   │   │   ├── help-faq-symbolic.symbolic.png
        │   │   │   │   ├── multimedia-volume-control-symbolic.symbolic.png
        │   │   │   │   ├── preferences-color-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-accessibility-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-apps-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-display-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-font-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-keyboard-shortcuts-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-keyboard-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-locale-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-remote-desktop-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-screensaver-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-wallpaper-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-details-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-devices-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-network-proxy-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-network-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-notifications-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-parental-controls-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-privacy-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-search-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-sharing-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-time-symbolic.symbolic.png
        │   │   │   │   ├── system-file-manager-symbolic.symbolic.png
        │   │   │   │   ├── system-software-install-symbolic.symbolic.png
        │   │   │   │   ├── system-users-symbolic.symbolic.png
        │   │   │   │   ├── text-editor-symbolic.symbolic.png
        │   │   │   │   ├── user-info-symbolic.symbolic.png
        │   │   │   │   ├── utilities-terminal-symbolic.symbolic.png
        │   │   │   │   └── web-browser-symbolic.symbolic.png
        │   │   │   ├── categories
        │   │   │   │   ├── applications-engineering-symbolic.symbolic.png
        │   │   │   │   ├── applications-games-symbolic.symbolic.png
        │   │   │   │   ├── applications-graphics-symbolic.symbolic.png
        │   │   │   │   ├── applications-multimedia-symbolic.symbolic.png
        │   │   │   │   ├── applications-science-symbolic.symbolic.png
        │   │   │   │   ├── applications-system-symbolic.symbolic.png
        │   │   │   │   ├── applications-utilities-symbolic.symbolic.png
        │   │   │   │   ├── emoji-activities-symbolic.symbolic.png
        │   │   │   │   ├── emoji-body-symbolic.symbolic.png
        │   │   │   │   ├── emoji-flags-symbolic.symbolic.png
        │   │   │   │   ├── emoji-food-symbolic.symbolic.png
        │   │   │   │   ├── emoji-nature-symbolic.symbolic.png
        │   │   │   │   ├── emoji-objects-symbolic.symbolic.png
        │   │   │   │   ├── emoji-people-symbolic.symbolic.png
        │   │   │   │   ├── emoji-recent-symbolic.symbolic.png
        │   │   │   │   ├── emoji-symbols-symbolic.symbolic.png
        │   │   │   │   ├── emoji-travel-symbolic.symbolic.png
        │   │   │   │   ├── preferences-other-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-symbolic.symbolic.png
        │   │   │   │   └── system-help-symbolic.symbolic.png
        │   │   │   ├── devices
        │   │   │   │   ├── ac-adapter-symbolic.symbolic.png
        │   │   │   │   ├── audio-card-symbolic.symbolic.png
        │   │   │   │   ├── audio-headphones.png
        │   │   │   │   ├── audio-headphones-symbolic.symbolic.png
        │   │   │   │   ├── audio-headset.png
        │   │   │   │   ├── audio-headset-symbolic.symbolic.png
        │   │   │   │   ├── audio-input-microphone-symbolic.symbolic.png
        │   │   │   │   ├── audio-speakers-symbolic.symbolic.png
        │   │   │   │   ├── auth-fingerprint-symbolic.symbolic.png
        │   │   │   │   ├── auth-sim-symbolic.symbolic.png
        │   │   │   │   ├── auth-smartcard-symbolic.symbolic.png
        │   │   │   │   ├── battery-symbolic.symbolic.png
        │   │   │   │   ├── bluetooth-symbolic.symbolic.png
        │   │   │   │   ├── camera-photo-symbolic.symbolic.png
        │   │   │   │   ├── camera-video-symbolic.symbolic.png
        │   │   │   │   ├── camera-web-symbolic.symbolic.png
        │   │   │   │   ├── colorimeter-colorhug-symbolic.symbolic.png
        │   │   │   │   ├── computer-apple-ipad-symbolic.symbolic.png
        │   │   │   │   ├── computer.png
        │   │   │   │   ├── computer-symbolic.symbolic.png
        │   │   │   │   ├── display-projector-symbolic.symbolic.png
        │   │   │   │   ├── drive-harddisk-ieee1394-symbolic.symbolic.png
        │   │   │   │   ├── drive-harddisk.png
        │   │   │   │   ├── drive-harddisk-solidstate-symbolic.symbolic.png
        │   │   │   │   ├── drive-harddisk-symbolic.symbolic.png
        │   │   │   │   ├── drive-harddisk-system-symbolic.symbolic.png
        │   │   │   │   ├── drive-harddisk-usb-symbolic.symbolic.png
        │   │   │   │   ├── drive-multidisk-symbolic.symbolic.png
        │   │   │   │   ├── drive-optical-symbolic.symbolic.png
        │   │   │   │   ├── drive-removable-media.png
        │   │   │   │   ├── drive-removable-media-symbolic.symbolic.png
        │   │   │   │   ├── input-dialpad-symbolic.symbolic.png
        │   │   │   │   ├── input-gaming.png
        │   │   │   │   ├── input-gaming-symbolic.symbolic.png
        │   │   │   │   ├── input-keyboard-symbolic.symbolic.png
        │   │   │   │   ├── input-mouse-symbolic.symbolic.png
        │   │   │   │   ├── input-tablet-symbolic.symbolic.png
        │   │   │   │   ├── input-touchpad-symbolic.symbolic.png
        │   │   │   │   ├── media-flash-symbolic.symbolic.png
        │   │   │   │   ├── media-floppy-symbolic.symbolic.png
        │   │   │   │   ├── media-optical-bd-symbolic.symbolic.png
        │   │   │   │   ├── media-optical-cd-audio-symbolic.symbolic.png
        │   │   │   │   ├── media-optical-dvd-symbolic.symbolic.png
        │   │   │   │   ├── media-optical.png
        │   │   │   │   ├── media-optical-symbolic.symbolic.png
        │   │   │   │   ├── media-removable.png
        │   │   │   │   ├── media-removable-symbolic.symbolic.png
        │   │   │   │   ├── media-tape-symbolic.symbolic.png
        │   │   │   │   ├── media-zip-symbolic.symbolic.png
        │   │   │   │   ├── modem-symbolic.symbolic.png
        │   │   │   │   ├── multimedia-player-apple-ipod-touch-symbolic.symbolic.png
        │   │   │   │   ├── multimedia-player-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-symbolic.symbolic.png
        │   │   │   │   ├── network-wired-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-symbolic.symbolic.png
        │   │   │   │   ├── pda-symbolic.symbolic.png
        │   │   │   │   ├── phone-apple-iphone-symbolic.symbolic.png
        │   │   │   │   ├── phone-old-symbolic.symbolic.png
        │   │   │   │   ├── phone-symbolic.symbolic.png
        │   │   │   │   ├── printer-network.png
        │   │   │   │   ├── printer-network-symbolic.symbolic.png
        │   │   │   │   ├── printer.png
        │   │   │   │   ├── printer-symbolic.symbolic.png
        │   │   │   │   ├── scanner-symbolic.symbolic.png
        │   │   │   │   ├── thunderbolt-symbolic.symbolic.png
        │   │   │   │   ├── tv-symbolic.symbolic.png
        │   │   │   │   ├── uninterruptible-power-supply-symbolic.symbolic.png
        │   │   │   │   ├── video-display-symbolic.symbolic.png
        │   │   │   │   ├── video-joined-displays-symbolic.symbolic.png
        │   │   │   │   └── video-single-display-symbolic.symbolic.png
        │   │   │   ├── emblems
        │   │   │   │   ├── emblem-default-symbolic.symbolic.png
        │   │   │   │   ├── emblem-documents-symbolic.symbolic.png
        │   │   │   │   ├── emblem-favorite-symbolic.symbolic.png
        │   │   │   │   ├── emblem-important-symbolic.symbolic.png
        │   │   │   │   ├── emblem-music-symbolic.symbolic.png
        │   │   │   │   ├── emblem-ok-symbolic.symbolic.png
        │   │   │   │   ├── emblem-photos-symbolic.symbolic.png
        │   │   │   │   ├── emblem-readonly.png
        │   │   │   │   ├── emblem-shared.png
        │   │   │   │   ├── emblem-shared-symbolic.symbolic.png
        │   │   │   │   ├── emblem-symbolic-link.png
        │   │   │   │   ├── emblem-synchronizing.png
        │   │   │   │   ├── emblem-synchronizing-symbolic.symbolic.png
        │   │   │   │   ├── emblem-system-symbolic.symbolic.png
        │   │   │   │   ├── emblem-unreadable.png
        │   │   │   │   └── emblem-videos-symbolic.symbolic.png
        │   │   │   ├── emotes
        │   │   │   │   ├── emote-love-symbolic.symbolic.png
        │   │   │   │   ├── face-angel-symbolic.symbolic.png
        │   │   │   │   ├── face-angry-symbolic.symbolic.png
        │   │   │   │   ├── face-confused-symbolic.symbolic.png
        │   │   │   │   ├── face-cool-symbolic.symbolic.png
        │   │   │   │   ├── face-crying-symbolic.symbolic.png
        │   │   │   │   ├── face-devilish-symbolic.symbolic.png
        │   │   │   │   ├── face-embarrassed-symbolic.symbolic.png
        │   │   │   │   ├── face-glasses-symbolic.symbolic.png
        │   │   │   │   ├── face-kiss-symbolic.symbolic.png
        │   │   │   │   ├── face-laugh-symbolic.symbolic.png
        │   │   │   │   ├── face-monkey-symbolic.symbolic.png
        │   │   │   │   ├── face-plain-symbolic.symbolic.png
        │   │   │   │   ├── face-raspberry-symbolic.symbolic.png
        │   │   │   │   ├── face-sad-symbolic.symbolic.png
        │   │   │   │   ├── face-shutmouth-symbolic.symbolic.png
        │   │   │   │   ├── face-sick-symbolic.symbolic.png
        │   │   │   │   ├── face-smile-big-symbolic.symbolic.png
        │   │   │   │   ├── face-smile-symbolic.symbolic.png
        │   │   │   │   ├── face-smirk-symbolic.symbolic.png
        │   │   │   │   ├── face-surprise-symbolic.symbolic.png
        │   │   │   │   ├── face-tired-symbolic.symbolic.png
        │   │   │   │   ├── face-uncertain-symbolic.symbolic.png
        │   │   │   │   ├── face-wink-symbolic.symbolic.png
        │   │   │   │   ├── face-worried-symbolic.symbolic.png
        │   │   │   │   └── face-yawn-symbolic.symbolic.png
        │   │   │   ├── legacy
        │   │   │   │   ├── ac-adapter.png
        │   │   │   │   ├── accessories-calculator.png
        │   │   │   │   ├── accessories-character-map.png
        │   │   │   │   ├── accessories-dictionary.png
        │   │   │   │   ├── accessories-text-editor.png
        │   │   │   │   ├── address-book-new.png
        │   │   │   │   ├── applets-screenshooter.png
        │   │   │   │   ├── application-exit.png
        │   │   │   │   ├── applications-accessories.png
        │   │   │   │   ├── applications-development.png
        │   │   │   │   ├── applications-engineering.png
        │   │   │   │   ├── applications-games.png
        │   │   │   │   ├── applications-graphics.png
        │   │   │   │   ├── applications-internet.png
        │   │   │   │   ├── applications-office.png
        │   │   │   │   ├── applications-other.png
        │   │   │   │   ├── applications-science.png
        │   │   │   │   ├── applications-system.png
        │   │   │   │   ├── applications-utilities.png
        │   │   │   │   ├── appointment-missed.png
        │   │   │   │   ├── appointment-new.png
        │   │   │   │   ├── appointment-soon.png
        │   │   │   │   ├── audio-card.png
        │   │   │   │   ├── audio-speakers.png
        │   │   │   │   ├── audio-volume-high.png
        │   │   │   │   ├── audio-volume-low.png
        │   │   │   │   ├── audio-volume-medium.png
        │   │   │   │   ├── audio-volume-muted.png
        │   │   │   │   ├── battery-caution-charging.png
        │   │   │   │   ├── battery-caution-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-caution.png
        │   │   │   │   ├── battery-caution-symbolic.symbolic.png
        │   │   │   │   ├── battery-empty-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-empty.png
        │   │   │   │   ├── battery-empty-symbolic.symbolic.png
        │   │   │   │   ├── battery-full-charged.png
        │   │   │   │   ├── battery-full-charged-symbolic.symbolic.png
        │   │   │   │   ├── battery-full-charging.png
        │   │   │   │   ├── battery-full-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-full.png
        │   │   │   │   ├── battery-full-symbolic.symbolic.png
        │   │   │   │   ├── battery-good-charging.png
        │   │   │   │   ├── battery-good-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-good.png
        │   │   │   │   ├── battery-good-symbolic.symbolic.png
        │   │   │   │   ├── battery-low-charging.png
        │   │   │   │   ├── battery-low-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-low.png
        │   │   │   │   ├── battery-low-symbolic.symbolic.png
        │   │   │   │   ├── battery-missing.png
        │   │   │   │   ├── battery.png
        │   │   │   │   ├── bookmark-new.png
        │   │   │   │   ├── call-start.png
        │   │   │   │   ├── call-stop.png
        │   │   │   │   ├── camera-photo.png
        │   │   │   │   ├── camera-video.png
        │   │   │   │   ├── camera-web.png
        │   │   │   │   ├── changes-allow.png
        │   │   │   │   ├── changes-prevent.png
        │   │   │   │   ├── computer-fail.png
        │   │   │   │   ├── computer.png
        │   │   │   │   ├── contact-new.png
        │   │   │   │   ├── dialog-error.png
        │   │   │   │   ├── dialog-information.png
        │   │   │   │   ├── dialog-password.png
        │   │   │   │   ├── dialog-question.png
        │   │   │   │   ├── dialog-warning.png
        │   │   │   │   ├── document-new.png
        │   │   │   │   ├── document-open.png
        │   │   │   │   ├── document-open-recent.png
        │   │   │   │   ├── document-page-setup.png
        │   │   │   │   ├── document-print.png
        │   │   │   │   ├── document-print-preview.png
        │   │   │   │   ├── document-properties.png
        │   │   │   │   ├── document-revert.png
        │   │   │   │   ├── document-revert-rtl.png
        │   │   │   │   ├── document-save-as.png
        │   │   │   │   ├── document-save.png
        │   │   │   │   ├── document-send.png
        │   │   │   │   ├── drive-multidisk.png
        │   │   │   │   ├── drive-optical.png
        │   │   │   │   ├── ebook-reader.png
        │   │   │   │   ├── edit-clear-all.png
        │   │   │   │   ├── edit-clear.png
        │   │   │   │   ├── edit-clear-rtl.png
        │   │   │   │   ├── edit-copy.png
        │   │   │   │   ├── edit-cut.png
        │   │   │   │   ├── edit-delete.png
        │   │   │   │   ├── edit-find.png
        │   │   │   │   ├── edit-find-replace.png
        │   │   │   │   ├── edit-paste.png
        │   │   │   │   ├── edit-redo.png
        │   │   │   │   ├── edit-redo-rtl.png
        │   │   │   │   ├── edit-select-all.png
        │   │   │   │   ├── edit-undo.png
        │   │   │   │   ├── edit-undo-rtl.png
        │   │   │   │   ├── emblem-default.png
        │   │   │   │   ├── emblem-documents.png
        │   │   │   │   ├── emblem-downloads.png
        │   │   │   │   ├── emblem-favorite.png
        │   │   │   │   ├── emblem-generic.png
        │   │   │   │   ├── emblem-important.png
        │   │   │   │   ├── emblem-mail.png
        │   │   │   │   ├── emblem-new.png
        │   │   │   │   ├── emblem-package.png
        │   │   │   │   ├── emblem-photos.png
        │   │   │   │   ├── emblem-system.png
        │   │   │   │   ├── emblem-urgent.png
        │   │   │   │   ├── emblem-web.png
        │   │   │   │   ├── emote-love.png
        │   │   │   │   ├── face-angel.png
        │   │   │   │   ├── face-angry.png
        │   │   │   │   ├── face-cool.png
        │   │   │   │   ├── face-crying.png
        │   │   │   │   ├── face-devilish.png
        │   │   │   │   ├── face-embarrassed.png
        │   │   │   │   ├── face-glasses.png
        │   │   │   │   ├── face-kiss.png
        │   │   │   │   ├── face-laugh.png
        │   │   │   │   ├── face-monkey.png
        │   │   │   │   ├── face-plain.png
        │   │   │   │   ├── face-raspberry.png
        │   │   │   │   ├── face-sad.png
        │   │   │   │   ├── face-sick.png
        │   │   │   │   ├── face-smile-big.png
        │   │   │   │   ├── face-smile.png
        │   │   │   │   ├── face-smirk.png
        │   │   │   │   ├── face-surprise.png
        │   │   │   │   ├── face-tired.png
        │   │   │   │   ├── face-uncertain.png
        │   │   │   │   ├── face-wink.png
        │   │   │   │   ├── face-worried.png
        │   │   │   │   ├── folder-new.png
        │   │   │   │   ├── folder-visiting.png
        │   │   │   │   ├── format-indent-less.png
        │   │   │   │   ├── format-indent-less-rtl.png
        │   │   │   │   ├── format-indent-more.png
        │   │   │   │   ├── format-indent-more-rtl.png
        │   │   │   │   ├── format-justify-center.png
        │   │   │   │   ├── format-justify-fill.png
        │   │   │   │   ├── format-justify-left.png
        │   │   │   │   ├── format-justify-right.png
        │   │   │   │   ├── format-text-bold.png
        │   │   │   │   ├── format-text-direction-ltr.png
        │   │   │   │   ├── format-text-direction-rtl.png
        │   │   │   │   ├── format-text-italic.png
        │   │   │   │   ├── format-text-strikethrough.png
        │   │   │   │   ├── format-text-underline.png
        │   │   │   │   ├── go-bottom.png
        │   │   │   │   ├── go-down.png
        │   │   │   │   ├── go-first.png
        │   │   │   │   ├── go-first-rtl.png
        │   │   │   │   ├── go-home.png
        │   │   │   │   ├── go-jump.png
        │   │   │   │   ├── go-last.png
        │   │   │   │   ├── go-last-rtl.png
        │   │   │   │   ├── go-next.png
        │   │   │   │   ├── go-next-rtl.png
        │   │   │   │   ├── go-previous.png
        │   │   │   │   ├── go-previous-rtl.png
        │   │   │   │   ├── go-top.png
        │   │   │   │   ├── go-up.png
        │   │   │   │   ├── help-about.png
        │   │   │   │   ├── help-browser.png
        │   │   │   │   ├── help-contents.png
        │   │   │   │   ├── help-faq.png
        │   │   │   │   ├── image-missing.png
        │   │   │   │   ├── input-dialpad.png
        │   │   │   │   ├── input-gaming.png
        │   │   │   │   ├── input-keyboard.png
        │   │   │   │   ├── input-mouse.png
        │   │   │   │   ├── input-tablet.png
        │   │   │   │   ├── input-touchpad.png
        │   │   │   │   ├── insert-image.png
        │   │   │   │   ├── insert-link.png
        │   │   │   │   ├── insert-object.png
        │   │   │   │   ├── insert-text.png
        │   │   │   │   ├── list-add.png
        │   │   │   │   ├── list-remove.png
        │   │   │   │   ├── mail-attachment.png
        │   │   │   │   ├── mail-forward.png
        │   │   │   │   ├── mail-mark-important.png
        │   │   │   │   ├── mail-mark-junk.png
        │   │   │   │   ├── mail-mark-notjunk.png
        │   │   │   │   ├── mail-mark-read.png
        │   │   │   │   ├── mail-mark-unread.png
        │   │   │   │   ├── mail-message-new.png
        │   │   │   │   ├── mail-read.png
        │   │   │   │   ├── mail-replied.png
        │   │   │   │   ├── mail-reply-all.png
        │   │   │   │   ├── mail-reply-sender.png
        │   │   │   │   ├── mail-send.png
        │   │   │   │   ├── mail-send-receive.png
        │   │   │   │   ├── mail-signed.png
        │   │   │   │   ├── mail-signed-verified.png
        │   │   │   │   ├── mail-unread.png
        │   │   │   │   ├── mark-location.png
        │   │   │   │   ├── media-eject.png
        │   │   │   │   ├── media-flash.png
        │   │   │   │   ├── media-floppy.png
        │   │   │   │   ├── media-playback-pause.png
        │   │   │   │   ├── media-playback-start.png
        │   │   │   │   ├── media-playback-stop.png
        │   │   │   │   ├── media-playlist-repeat.png
        │   │   │   │   ├── media-playlist-shuffle.png
        │   │   │   │   ├── media-record.png
        │   │   │   │   ├── media-seek-backward.png
        │   │   │   │   ├── media-seek-forward.png
        │   │   │   │   ├── media-skip-backward.png
        │   │   │   │   ├── media-skip-forward.png
        │   │   │   │   ├── media-tape.png
        │   │   │   │   ├── microphone-sensitivity-high.png
        │   │   │   │   ├── microphone-sensitivity-low.png
        │   │   │   │   ├── microphone-sensitivity-medium.png
        │   │   │   │   ├── microphone-sensitivity-muted.png
        │   │   │   │   ├── modem.png
        │   │   │   │   ├── multimedia-player.png
        │   │   │   │   ├── multimedia-volume-control.png
        │   │   │   │   ├── network-cellular-connected.png
        │   │   │   │   ├── network-error.png
        │   │   │   │   ├── network-idle.png
        │   │   │   │   ├── network-offline.png
        │   │   │   │   ├── network-receive.png
        │   │   │   │   ├── network-transmit.png
        │   │   │   │   ├── network-transmit-receive.png
        │   │   │   │   ├── network-vpn.png
        │   │   │   │   ├── network-wired-disconnected.png
        │   │   │   │   ├── network-wired.png
        │   │   │   │   ├── network-wireless-encrypted.png
        │   │   │   │   ├── network-wireless.png
        │   │   │   │   ├── non-starred.png
        │   │   │   │   ├── object-flip-horizontal.png
        │   │   │   │   ├── object-flip-vertical.png
        │   │   │   │   ├── object-rotate-left.png
        │   │   │   │   ├── object-rotate-right.png
        │   │   │   │   ├── pda.png
        │   │   │   │   ├── phone.png
        │   │   │   │   ├── preferences-desktop-accessibility.png
        │   │   │   │   ├── preferences-desktop-display.png
        │   │   │   │   ├── preferences-desktop-font.png
        │   │   │   │   ├── preferences-desktop-keyboard.png
        │   │   │   │   ├── preferences-desktop-keyboard-shortcuts.png
        │   │   │   │   ├── preferences-desktop-locale.png
        │   │   │   │   ├── preferences-desktop-peripherals.png
        │   │   │   │   ├── preferences-desktop-personal.png
        │   │   │   │   ├── preferences-desktop.png
        │   │   │   │   ├── preferences-desktop-remote-desktop.png
        │   │   │   │   ├── preferences-desktop-screensaver.png
        │   │   │   │   ├── preferences-desktop-theme.png
        │   │   │   │   ├── preferences-desktop-wallpaper.png
        │   │   │   │   ├── preferences-other.png
        │   │   │   │   ├── preferences-system-network.png
        │   │   │   │   ├── preferences-system-notifications.png
        │   │   │   │   ├── preferences-system.png
        │   │   │   │   ├── preferences-system-privacy.png
        │   │   │   │   ├── preferences-system-search.png
        │   │   │   │   ├── preferences-system-sharing.png
        │   │   │   │   ├── preferences-system-windows.png
        │   │   │   │   ├── printer-error.png
        │   │   │   │   ├── printer-printing.png
        │   │   │   │   ├── process-stop.png
        │   │   │   │   ├── scanner.png
        │   │   │   │   ├── security-high.png
        │   │   │   │   ├── security-low.png
        │   │   │   │   ├── security-medium.png
        │   │   │   │   ├── semi-starred.png
        │   │   │   │   ├── semi-starred-rtl.png
        │   │   │   │   ├── software-update-available.png
        │   │   │   │   ├── software-update-urgent.png
        │   │   │   │   ├── starred.png
        │   │   │   │   ├── system-file-manager.png
        │   │   │   │   ├── system-help.png
        │   │   │   │   ├── system-lock-screen.png
        │   │   │   │   ├── system-log-out.png
        │   │   │   │   ├── system-run.png
        │   │   │   │   ├── system-search.png
        │   │   │   │   ├── system-shutdown.png
        │   │   │   │   ├── system-software-install.png
        │   │   │   │   ├── system-software-update.png
        │   │   │   │   ├── system-users.png
        │   │   │   │   ├── tab-new.png
        │   │   │   │   ├── task-due.png
        │   │   │   │   ├── task-past-due.png
        │   │   │   │   ├── tools-check-spelling.png
        │   │   │   │   ├── trophy-bronze.png
        │   │   │   │   ├── trophy-gold.png
        │   │   │   │   ├── trophy-silver.png
        │   │   │   │   ├── uninterruptible-power-supply.png
        │   │   │   │   ├── user-available.png
        │   │   │   │   ├── user-away.png
        │   │   │   │   ├── user-busy.png
        │   │   │   │   ├── user-idle.png
        │   │   │   │   ├── user-info.png
        │   │   │   │   ├── user-invisible.png
        │   │   │   │   ├── user-offline.png
        │   │   │   │   ├── utilities-terminal.png
        │   │   │   │   ├── video-display.png
        │   │   │   │   ├── view-fullscreen.png
        │   │   │   │   ├── view-refresh.png
        │   │   │   │   ├── view-restore.png
        │   │   │   │   ├── view-sort-ascending.png
        │   │   │   │   ├── view-sort-descending.png
        │   │   │   │   ├── web-browser.png
        │   │   │   │   ├── window-close.png
        │   │   │   │   ├── window-new.png
        │   │   │   │   ├── zoom-fit-best.png
        │   │   │   │   ├── zoom-in.png
        │   │   │   │   ├── zoom-original.png
        │   │   │   │   └── zoom-out.png
        │   │   │   ├── mimetypes
        │   │   │   │   ├── application-certificate.png
        │   │   │   │   ├── application-certificate-symbolic.symbolic.png
        │   │   │   │   ├── application-rss+xml-symbolic.symbolic.png
        │   │   │   │   ├── application-x-addon.png
        │   │   │   │   ├── application-x-addon-symbolic.symbolic.png
        │   │   │   │   ├── application-x-appliance-symbolic.symbolic.png
        │   │   │   │   ├── application-x-executable.png
        │   │   │   │   ├── application-x-executable-symbolic.symbolic.png
        │   │   │   │   ├── application-x-firmware.png
        │   │   │   │   ├── application-x-firmware-symbolic.symbolic.png
        │   │   │   │   ├── application-x-generic.png
        │   │   │   │   ├── application-x-sharedlib.png
        │   │   │   │   ├── audio-x-generic.png
        │   │   │   │   ├── audio-x-generic-symbolic.symbolic.png
        │   │   │   │   ├── font-x-generic.png
        │   │   │   │   ├── font-x-generic-symbolic.symbolic.png
        │   │   │   │   ├── image-x-generic.png
        │   │   │   │   ├── image-x-generic-symbolic.symbolic.png
        │   │   │   │   ├── inode-directory.png
        │   │   │   │   ├── inode-directory-symbolic.symbolic.png
        │   │   │   │   ├── package-x-generic.png
        │   │   │   │   ├── package-x-generic-symbolic.symbolic.png
        │   │   │   │   ├── text-html.png
        │   │   │   │   ├── text-x-generic.png
        │   │   │   │   ├── text-x-generic-symbolic.symbolic.png
        │   │   │   │   ├── text-x-generic-template.png
        │   │   │   │   ├── text-x-preview.png
        │   │   │   │   ├── text-x-script.png
        │   │   │   │   ├── video-x-generic.png
        │   │   │   │   ├── video-x-generic-symbolic.symbolic.png
        │   │   │   │   ├── x-office-address-book.png
        │   │   │   │   ├── x-office-address-book-symbolic.symbolic.png
        │   │   │   │   ├── x-office-calendar.png
        │   │   │   │   ├── x-office-calendar-symbolic.symbolic.png
        │   │   │   │   ├── x-office-document.png
        │   │   │   │   ├── x-office-document-symbolic.symbolic.png
        │   │   │   │   ├── x-office-document-template.png
        │   │   │   │   ├── x-office-drawing.png
        │   │   │   │   ├── x-office-drawing-symbolic.symbolic.png
        │   │   │   │   ├── x-office-drawing-template.png
        │   │   │   │   ├── x-office-presentation.png
        │   │   │   │   ├── x-office-presentation-symbolic.symbolic.png
        │   │   │   │   ├── x-office-presentation-template.png
        │   │   │   │   ├── x-office-spreadsheet.png
        │   │   │   │   ├── x-office-spreadsheet-symbolic.symbolic.png
        │   │   │   │   ├── x-office-spreadsheet-template.png
        │   │   │   │   └── x-package-repository.png
        │   │   │   ├── places
        │   │   │   │   ├── folder-documents.png
        │   │   │   │   ├── folder-documents-symbolic.symbolic.png
        │   │   │   │   ├── folder-download.png
        ���   │   │   │   ├── folder-download-symbolic.symbolic.png
        │   │   │   │   ├── folder-drag-accept.png
        │   │   │   │   ├── folder-music.png
        │   │   │   │   ├── folder-music-symbolic.symbolic.png
        │   │   │   │   ├── folder-open.png
        │   │   │   │   ├── folder-pictures.png
        │   │   │   │   ├── folder-pictures-symbolic.symbolic.png
        │   │   │   │   ├── folder.png
        │   │   │   │   ├── folder-publicshare.png
        │   │   │   │   ├── folder-publicshare-symbolic.symbolic.png
        │   │   │   │   ├── folder-remote.png
        │   │   │   │   ├── folder-remote-symbolic.symbolic.png
        │   │   │   │   ├── folder-saved-search.png
        │   │   │   │   ├── folder-saved-search-symbolic.symbolic.png
        │   │   │   │   ├── folder-symbolic.symbolic.png
        │   │   │   │   ├── folder-templates.png
        │   │   │   │   ├── folder-templates-symbolic.symbolic.png
        │   │   │   │   ├── folder-videos.png
        │   │   │   │   ├── folder-videos-symbolic.symbolic.png
        │   │   │   │   ├── network-server.png
        │   │   │   │   ├── network-server-symbolic.symbolic.png
        │   │   │   │   ├── network-workgroup.png
        │   │   │   │   ├── network-workgroup-symbolic.symbolic.png
        │   │   │   │   ├── start-here.png
        │   │   │   │   ├── start-here-symbolic.symbolic.png
        │   │   │   │   ├── user-bookmarks.png
        │   │   │   │   ├── user-bookmarks-symbolic.symbolic.png
        │   │   │   │   ├── user-desktop.png
        │   │   │   │   ├── user-desktop-symbolic.symbolic.png
        │   │   │   │   ├── user-home.png
        │   │   │   │   ├── user-home-symbolic.symbolic.png
        │   │   │   │   ├── user-trash.png
        │   │   │   │   └── user-trash-symbolic.symbolic.png
        │   │   │   ├── status
        │   │   │   │   ├── airplane-mode-symbolic.symbolic.png
        │   │   │   │   ├── alarm-symbolic.symbolic.png
        │   │   │   │   ├── appointment-missed-symbolic.symbolic.png
        │   │   │   │   ├── appointment-soon-symbolic.symbolic.png
        │   │   │   │   ├── audio-volume-high-symbolic.symbolic.png
        │   │   │   │   ├── audio-volume-low-symbolic.symbolic.png
        │   │   │   │   ├── audio-volume-medium-symbolic.symbolic.png
        │   │   │   │   ├── audio-volume-muted-symbolic.symbolic.png
        │   │   │   │   ├── audio-volume-overamplified-symbolic.symbolic.png
        │   │   │   │   ├── auth-sim-locked-symbolic.symbolic.png
        │   │   │   │   ├── auth-sim-missing-symbolic.symbolic.png
        │   │   │   │   ├── avatar-default.png
        │   │   │   │   ├── avatar-default-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-0-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-0-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-100-charged-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-100-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-10-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-10-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-20-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-20-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-30-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-30-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-40-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-40-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-50-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-50-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-60-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-60-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-70-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-70-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-80-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-80-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-90-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-90-symbolic.symbolic.png
        │   │   │   │   ├── battery-missing-symbolic.symbolic.png
        │   │   │   │   ├── bluetooth-active-symbolic.symbolic.png
        │   │   │   │   ├── bluetooth-disabled-symbolic.symbolic.png
        │   │   │   │   ├── bluetooth-hardware-disabled-symbolic.symbolic.png
        │   │   │   │   ├── call-incoming-symbolic.symbolic.png
        │   │   │   │   ├── call-missed-symbolic.symbolic.png
        │   │   │   │   ├── call-outgoing-symbolic.symbolic.png
        │   │   │   │   ├── camera-disabled-symbolic.symbolic.png
        │   │   │   │   ├── camera-hardware-disabled-symbolic.symbolic.png
        │   │   │   │   ├── changes-allow-symbolic.symbolic.png
        │   │   │   │   ├── changes-prevent-symbolic.symbolic.png
        │   │   │   │   ├── channel-insecure-symbolic.symbolic.png
        │   │   │   │   ├── channel-secure-symbolic.symbolic.png
        │   │   │   │   ├── computer-fail-symbolic.symbolic.png
        │   │   │   │   ├── contact-new-symbolic.symbolic.png
        │   │   │   │   ├── content-loading-symbolic.symbolic.png
        │   │   │   │   ├── daytime-sunrise-symbolic.symbolic.png
        │   │   │   │   ├── daytime-sunset-symbolic.symbolic.png
        │   │   │   │   ├── dialog-error-symbolic.symbolic.png
        │   │   │   │   ├── dialog-information-symbolic.symbolic.png
        │   │   │   │   ├── dialog-password-symbolic.symbolic.png
        │   │   │   │   ├── dialog-question-symbolic.symbolic.png
        │   │   │   │   ├── dialog-warning-symbolic.symbolic.png
        │   │   │   │   ├── display-brightness-symbolic.symbolic.png
        │   │   │   │   ├── folder-drag-accept-symbolic.symbolic.png
        │   │   │   │   ├── folder-open-symbolic.symbolic.png
        │   │   │   │   ├── folder-visiting-symbolic.symbolic.png
        │   │   │ �� │   ├── image-loading.png
        │   │   │   │   ├── image-loading-symbolic.symbolic.png
        │   │   │   │   ├── image-missing.png
        │   │   │   │   ├── keyboard-brightness-symbolic.symbolic.png
        │   │   │   │   ├── location-services-active-symbolic.symbolic.png
        │   │   │   │   ├── location-services-disabled-symbolic.symbolic.png
        │   │   │   │   ├── mail-attachment-symbolic.symbolic.png
        │   │   │   │   ├── mail-read-symbolic.symbolic.png
        │   │   │   │   ├── mail-replied-symbolic.symbolic.png
        │   │   │   │   ├── mail-unread-symbolic.symbolic.png
        │   │   │   │   ├── media-playlist-consecutive-symbolic.symbolic.png
        │   │   │   │   ├── media-playlist-repeat-song-symbolic.symbolic.png
        │   │   │   │   ├── media-playlist-repeat-symbolic.symbolic.png
        │   │   │   │   ├── media-playlist-shuffle-symbolic.symbolic.png
        │   │   │   │   ├── microphone-disabled-symbolic.symbolic.png
        │   │   │   │   ├── microphone-hardware-disabled-symbolic.symbolic.png
        │   │   │   │   ├── microphone-sensitivity-high-symbolic.symbolic.png
        │   │   │   │   ├── microphone-sensitivity-low-symbolic.symbolic.png
        │   │   │   │   ├── microphone-sensitivity-medium-symbolic.symbolic.png
        │   │   │   │   ├── microphone-sensitivity-muted-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-2g-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-3g-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-4g-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-acquiring-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-connected-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-disabled-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-edge-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-gprs-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-hardware-disabled-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-hspa-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-no-route-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-offline-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-signal-excellent-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-signal-good-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-signal-none-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-signal-ok-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-signal-weak-symbolic.symbolic.png
        │   │   │   │   ├── network-error-symbolic.symbolic.png
        │   │   │   │   ├── network-idle-symbolic.symbolic.png
        │   │   │   │   ├── network-no-route-symbolic.symbolic.png
        │   │   │   │   ├── network-offline-symbolic.symbolic.png
        │   │   │   │   ├── network-receive-symbolic.symbolic.png
        │   │   │   │   ├── network-transmit-receive-symbolic.symbolic.png
        │   │   │   │   ├── network-transmit-symbolic.symbolic.png
        ���   │   │   │   ├── network-vpn-acquiring-symbolic.symbolic.png
        │   │   │   │   ├── network-vpn-no-route-symbolic.symbolic.png
        │   │   │   │   ├── network-vpn-symbolic.symbolic.png
        │   │   │   │   ├── network-wired-acquiring-symbolic.symbolic.png
        │   │   │   │   ├── network-wired-disconnected-symbolic.symbolic.png
        │   │   │   │   ├── network-wired-no-route-symbolic.symbolic.png
        │   │   │   │   ├── network-wired-offline-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-acquiring-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-connected-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-disabled-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-encrypted-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-hardware-disabled-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-hotspot-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-no-route-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-offline-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-signal-excellent-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-signal-good-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-signal-none-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-signal-ok-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-signal-weak-symbolic.symbolic.png
        │   │   │   │   ├── night-light-symbolic.symbolic.png
        │   │   │   │   ├── non-starred-symbolic.symbolic.png
        │   │   │   │   ├── notifications-disabled-symbolic.symbolic.png
        │   │   │   │   ├── orientation-landscape-inverse-symbolic.symbolic.png
        │   │   │   │   ├── orientation-landscape-symbolic.symbolic.png
        │   │   │   │   ├── orientation-portrait-left-symbolic.symbolic.png
        │   │   │   │   ├── orientation-portrait-right-symbolic.symbolic.png
        │   │   │   │   ├── printer-error-symbolic.symbolic.png
        │   │   │   │   ├── printer-printing-symbolic.symbolic.png
        │   │   │   │   ├── printer-warning-symbolic.symbolic.png
        │   │   │   │   ├── rotation-allowed-symbolic.symbolic.png
        │   │   │   │   ├── rotation-locked-symbolic.symbolic.png
        │   │   │   │   ├── screen-shared-symbolic.symbolic.png
        │   │   │   │   ├── security-high-symbolic.symbolic.png
        │   │   │   │   ├── security-low-symbolic.symbolic.png
        │   │   │   │   ├── security-medium-symbolic.symbolic.png
        │   │   │   │   ├── semi-starred-symbolic-rtl.symbolic.png
        │   │   │   │   ├── semi-starred-symbolic.symbolic.png
        │   │   │   │   ├── software-update-available-symbolic.symbolic.png
        │   │   │   │   ├── software-update-urgent-symbolic.symbolic.png
        │   │   │   │   ├── starred-symbolic.symbolic.png
        │   │   │   │   ├── system-lock-screen-symbolic.symbolic.png
        │   │   │   │   ├── task-due-symbolic.symbolic.png
        │   │   │   │   ├── task-past-due-symbolic.symbolic.png
        │   │   │   │   ├── thunderbolt-acquiring-symbolic.symbolic.png
        │   │   │   │   ├── touch-disabled-symbolic.symbolic.png
        │   │   │   │   ├── touchpad-disabled-symbolic.symbolic.png
        │   │   │   │   ├── user-available-symbolic.symbolic.png
        │   │   │   │   ├── user-away-symbolic.symbolic.png
        │   │   │   │   ├── user-busy-symbolic.symbolic.png
        │   │   │   │   ├── user-idle-symbolic.symbolic.png
        │   │   │   │   ├── user-invisible-symbolic.symbolic.png
        │   │   │   │   ├── user-not-tracked-symbolic.symbolic.png
        │   │   │   │   ├── user-offline-symbolic.symbolic.png
        │   │   │   │   ├── user-status-pending-symbolic.symbolic.png
        │   │   │   │   ├── user-trash-full.png
        │   │   │   │   ├── user-trash-full-symbolic.symbolic.png
        │   │   │   │   ├── view-wrapped-symbolic-rtl.symbolic.png
        │   │   │   │   ├── view-wrapped-symbolic.symbolic.png
        │   │   │   │   ├── weather-clear-night-symbolic.symbolic.png
        │   │   │   │   ├── weather-clear-symbolic.symbolic.png
        │   │   │   │   ├── weather-few-clouds-night-symbolic.symbolic.png
        │   │   │   │   ├── weather-few-clouds-symbolic.symbolic.png
        │   │   │   │   ├── weather-fog-symbolic.symbolic.png
        │   │   │   │   ├── weather-overcast-symbolic.symbolic.png
        │   │   │   │   ├── weather-severe-alert-symbolic.symbolic.png
        │   │   │   │   ├── weather-showers-scattered-symbolic.symbolic.png
        │   │   │   │   ├── weather-showers-symbolic.symbolic.png
        │   │   │   │   ├── weather-snow-symbolic.symbolic.png
        │   │   │   │   ├── weather-storm-symbolic.symbolic.png
        │   │   │   │   ├── weather-tornado-symbolic.symbolic.png
        │   │   │   │   └── weather-windy-symbolic.symbolic.png
        │   │   │   └── ui
        │   │   │       ├── checkbox-checked-symbolic.symbolic.png
        │   │   │       ├── checkbox-mixed-symbolic.symbolic.png
        │   │   │       ├── checkbox-symbolic.symbolic.png
        │   │   │       ├── focus-legacy-systray-symbolic.symbolic.png
        │   │   │       ├── focus-top-bar-symbolic.symbolic.png
        │   │   │       ├── focus-windows-symbolic.symbolic.png
        │   │   │       ├── list-drag-handle-symbolic.symbolic.png
        │   │   │       ├── pan-down-symbolic.symbolic.png
        │   │   │       ├── pan-end-symbolic-rtl.symbolic.png
        │   │   │       ├── pan-end-symbolic.symbolic.png
        │   │   │       ├── pan-start-symbolic-rtl.symbolic.png
        │   │   │       ├── pan-start-symbolic.symbolic.png
        │   │   │       ├── pan-up-symbolic.symbolic.png
        │   │   │       ├── radio-checked-symbolic.symbolic.png
        │   │   │       ├── radio-mixed-symbolic.symbolic.png
        │   │   │       ├── radio-symbolic.symbolic.png
        │   │   │       ├── selection-end-symbolic-rtl.symbolic.png
        │   │   │       ├── selection-end-symbolic.symbolic.png
        │   │   │       ├── selection-start-symbolic-rtl.symbolic.png
        │   │   │       ├── selection-start-symbolic.symbolic.png
        │   │   │       ├── tab-new-symbolic.symbolic.png
        │   │   │       ├── window-close-symbolic.symbolic.png
        │   │   │       ├── window-maximize-symbolic.symbolic.png
        │   │   │       ├── window-minimize-symbolic.symbolic.png
        │   │   │       ├── window-new-symbolic.symbolic.png
        │   │   │       └── window-restore-symbolic.symbolic.png
        │   │   ├── 24x24
        │   │   │   ├── actions
        │   │   │   │   ├── action-unavailable-symbolic.symbolic.png
        │   │   │   │   ├── address-book-new-symbolic.symbolic.png
        │   │   │   │   ├── application-exit-symbolic.symbolic.png
        │   │   │   │   ├── appointment-new-symbolic.symbolic.png
        │   │   │   │   ├── bookmark-new-symbolic.symbolic.png
        │   │   │   │   ├── call-start-symbolic.symbolic.png
        │   │   │   │   ├── call-stop-symbolic.symbolic.png
        │   │   │   │   ├── camera-switch-symbolic.symbolic.png
        │   │   │   │   ├── chat-message-new-symbolic.symbolic.png
        │   │   │   │   ├── color-select-symbolic.symbolic.png
        │   │   │   │   ├── contact-new-symbolic.symbolic.png
        │   │   │   │   ├── document-edit-symbolic.symbolic.png
        │   │   │   │   ├── document-new-symbolic.symbolic.png
        │   │   │   │   ├── document-open-recent-symbolic.symbolic.png
        │   │   │   │   ├── document-open-symbolic.symbolic.png
        │   │   │   │   ├── document-page-setup-symbolic.symbolic.png
        │   │   │   │   ├── document-print-preview-symbolic.symbolic.png
        │   │   │   │   ├── document-print-symbolic.symbolic.png
        │   │   │   │   ├── document-properties-symbolic.symbolic.png
        │   │   │   │   ├── document-revert-symbolic-rtl.symbolic.png
        │   │   │   │   ├── document-revert-symbolic.symbolic.png
        │   │   │   │   ├── document-save-as-symbolic.symbolic.png
        │   │   │   │   ├── document-save-symbolic.symbolic.png
        │   │   │   │   ├── document-send-symbolic.symbolic.png
        │   │   │   │   ├── edit-clear-all-symbolic.symbolic.png
        │   │   │   │   ├── edit-clear-symbolic-rtl.symbolic.png
        │   │   │   │   ├── edit-clear-symbolic.symbolic.png
        │   │   │   │   ├── edit-copy-symbolic.symbolic.png
        │   │   │   │   ├── edit-cut-symbolic.symbolic.png
        │   │   │   │   ├── edit-delete-symbolic.symbolic.png
        │   │   │   │   ├── edit-find-replace-symbolic.symbolic.png
        │   │   │   │   ├── edit-find-symbolic.symbolic.png
        │   │   │   │   ├── edit-paste-symbolic.symbolic.png
        │   │   │   │   ├── edit-redo-symbolic-rtl.symbolic.png
        │   │   │   │   ├── edit-redo-symbolic.symbolic.png
        │   │   │   │   ├── edit-select-all-symbolic.symbolic.png
        │   │   │   │   ├── edit-select-symbolic.symbolic.png
        │   │   │   │   ├── edit-undo-symbolic-rtl.symbolic.png
        │   │   │   │   ├── edit-undo-symbolic.symbolic.png
        │   │   │   │   ├── error-correct-symbolic.symbolic.png
        │   │   │   │   ├── find-location-symbolic.symbolic.png
        │   │   │   │   ├── folder-new-symbolic.symbolic.png
        │   │   │   │   ├── font-select-symbolic.symbolic.png
        │   │   │   │   ├── format-indent-less-symbolic-rtl.symbolic.png
        │   │   │   │   ├── format-indent-less-symbolic.symbolic.png
        │   │   │   │   ├── format-indent-more-symbolic-rtl.symbolic.png
        │   │   │   │   ├── format-indent-more-symbolic.symbolic.png
        │   │   │   │   ├── format-justify-center-symbolic.symbolic.png
        │   │   │   │   ├── format-justify-fill-symbolic.symbolic.png
        │   │   │   │   ├── format-justify-left-symbolic.symbolic.png
        │   │   │   │   ├── format-justify-right-symbolic.symbolic.png
        │   │   │   │   ├── format-text-bold-symbolic.symbolic.png
        │   │   │   │   ├── format-text-direction-symbolic-rtl.symbolic.png
        │   │   │   │   ├── format-text-direction-symbolic.symbolic.png
        │   │   │   │   ├── format-text-italic-symbolic.symbolic.png
        │   │   │   │   ├── format-text-strikethrough-symbolic.symbolic.png
        │   │   │   │   ├── format-text-underline-symbolic.symbolic.png
        │   │   │   │   ├── go-bottom-symbolic.symbolic.png
        │   │   │   │   ├── go-down-symbolic.symbolic.png
        │   │   │   │   ├── go-first-symbolic-rtl.symbolic.png
        │   │   │   │   ├── go-first-symbolic.symbolic.png
        │   │   │   │   ├── go-home-symbolic.symbolic.png
        │   │   │   │   ├── go-jump-symbolic-rtl.symbolic.png
        │   │   │   │   ├── go-jump-symbolic.symbolic.png
        │   │   │   │   ├── go-last-symbolic-rtl.symbolic.png
        │   │   │   │   ├── go-last-symbolic.symbolic.png
        │   │   │   │   ├── go-next-symbolic-rtl.symbolic.png
        │   │   │   │   ├── go-next-symbolic.symbolic.png
        │   │   │   │   ├── go-previous-symbolic-rtl.symbolic.png
        │   │   │   │   ├── go-previous-symbolic.symbolic.png
        │   │   │   │   ├── go-top-symbolic.symbolic.png
        │   │   │   │   ├── go-up-symbolic.symbolic.png
        │   │   │   │   ├── help-about-symbolic.symbolic.png
        │   │   │   │   ├── insert-image-symbolic.symbolic.png
        │   │   │   │   ├── insert-link-symbolic.symbolic.png
        │   │   │   │   ├── insert-object-symbolic.symbolic.png
        │   │   │   │   ├── insert-text-symbolic.symbolic.png
        │   │   │   │   ├── list-add-symbolic.symbolic.png
        │   │   │   │   ├── list-remove-all-symbolic.symbolic.png
        │   │   │   │   ├── list-remove-symbolic.symbolic.png
        │   │   │   │   ├── mail-forward-symbolic.symbolic.png
        │   │   │   │   ├── mail-mark-important-symbolic.symbolic.png
        │   │   │   │   ├── mail-mark-junk-symbolic.symbolic.png
        │   │   │   │   ├── mail-mark-notjunk-symbolic.symbolic.png
        │   │   │   │   ├── mail-message-new-symbolic.symbolic.png
        │   │   │   │   ├── mail-reply-all-symbolic.symbolic.png
        │   │   │   │   ├── mail-reply-sender-symbolic.symbolic.png
        │   │   │   │   ├���─ mail-send-receive-symbolic.symbolic.png
        │   │   │   │   ├── mail-send-symbolic.symbolic.png
        │   │   │   │   ├── mark-location-symbolic.symbolic.png
        │   │   │   │   ├── media-eject-symbolic.symbolic.png
        │   │   │   │   ├── media-playback-pause-symbolic.symbolic.png
        │   │   │   │   ├── media-playback-start-symbolic.symbolic.png
        │   │   │   │   ├── media-playback-stop-symbolic.symbolic.png
        │   │   │   │   ├── media-record-symbolic.symbolic.png
        │   │   │   │   ├── media-seek-backward-symbolic.symbolic.png
        │   │   │   │   ├── media-seek-forward-symbolic.symbolic.png
        │   │   │   │   ├── media-skip-backward-symbolic.symbolic.png
        │   │   │   │   ├── media-skip-forward-symbolic.symbolic.png
        │   │   │   │   ├── media-view-subtitles-symbolic.symbolic.png
        │   │   │   │   ├── object-flip-horizontal-symbolic.symbolic.png
        │   │   │   │   ├── object-flip-vertical-symbolic.symbolic.png
        │   │   │   │   ├── object-rotate-left-symbolic.symbolic.png
        │   │   │   │   ├── object-rotate-right-symbolic.symbolic.png
        │   │   │   │   ├── object-select-symbolic.symbolic.png
        │   │   │   │   ├── open-menu-symbolic.symbolic.png
        │   │   │   │   ├── process-stop-symbolic.symbolic.png
        │   │   │   │   ├── send-to-symbolic.symbolic.png
        │   │   │   │   ├── sidebar-hide-symbolic.symbolic.png
        │   │   │   │   ├── sidebar-show-symbolic.symbolic.png
        │   │   │   │   ├── star-new-symbolic.symbolic.png
        │   │   │   │   ├── system-log-out-symbolic.symbolic.png
        │   │   │   │   ├── system-reboot-symbolic.symbolic.png
        │   │   │   │   ├── system-run-symbolic.symbolic.png
        │   │   │   │   ├── system-search-symbolic.symbolic.png
        │   │   │   │   ├── system-shutdown-symbolic.symbolic.png
        │   │   │   │   ├── system-switch-user-symbolic.symbolic.png
        │   │   │   │   ├── tab-new-symbolic.symbolic.png
        │   │   │   │   ├── tools-check-spelling-symbolic.symbolic.png
        │   │   │   │   ├── value-decrease-symbolic.symbolic.png
        │   │   │   │   ├── value-increase-symbolic.symbolic.png
        │   │   │   │   ├── view-app-grid-symbolic.symbolic.png
        │   │   │   │   ├── view-conceal-symbolic.symbolic.png
        │   │   │   │   ├── view-continuous-symbolic.symbolic.png
        │   │   │   │   ├── view-dual-symbolic.symbolic.png
        │   │   │   │   ├── view-fullscreen-symbolic.symbolic.png
        │   │   │   │   ├── view-grid-symbolic.symbolic.png
        │   │   │   │   ├── view-list-bullet-symbolic.symbolic.png
        │   │   │   │   ├── view-list-ordered-symbolic.symbolic.png
        │   │   │   │   ├── view-list-symbolic.symbolic.png
        │   │   │   │   ├── view-mirror-symbolic.symbolic.png
        │   │   │   │   ├── view-more-horizontal-symbolic.symbolic.png
        │   │   │   │   ├── view-more-symbolic.symbolic.png
        │   │   │   │   ├── view-paged-symbolic.symbolic.png
        │   │   │   │   ├── view-pin-symbolic.symbolic.png
        │   │   │   │   ├── view-refresh-symbolic.symbolic.png
        │   │   │   │   ├── view-restore-symbolic.symbolic.png
        │   │   │   │   ├── view-reveal-symbolic.symbolic.png
        │   │   │   │   ├── view-sort-ascending-symbolic.symbolic.png
        │   │   │   │   ├── view-sort-descending-symbolic.symbolic.png
        │   │   │   │   ├── zoom-fit-best-symbolic.symbolic.png
        │   │   │   │   ├── zoom-in-symbolic.symbolic.png
        │   │   │   │   ├── zoom-original-symbolic.symbolic.png
        │   │   │   │   └── zoom-out-symbolic.symbolic.png
        │   │   │   ├── apps
        │   │   │   │   ├── accessories-calculator-symbolic.symbolic.png
        │   │   │   │   ├── accessories-character-map-symbolic.symbolic.png
        │   │   │   │   ├── accessories-dictionary-symbolic.symbolic.png
        │   │   │   │   ├── accessories-text-editor-symbolic.symbolic.png
        │   │   │   │   ├── applets-screenshooter-symbolic.symbolic.png
        │   │   │   │   ├── gnome-power-manager-symbolic.symbolic.png
        │   │   │   │   ├── goa-panel-symbolic.symbolic.png
        │   │   │   │   ├── help-browser-symbolic.symbolic.png
        │   │   │   │   ├── help-contents-symbolic.symbolic.png
        │   │   │   │   ├── help-faq-symbolic.symbolic.png
        │   │   │   │   ├── multimedia-volume-control-symbolic.symbolic.png
        │   │   │   │   ├── preferences-color-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-accessibility-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-apps-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-display-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-font-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-keyboard-shortcuts-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-keyboard-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-locale-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-remote-desktop-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-screensaver-symbolic.symbolic.png
        │   │   │   │   ├── preferences-desktop-wallpaper-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-details-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-devices-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-network-proxy-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-network-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-notifications-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-parental-controls-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-privacy-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-search-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-sharing-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-time-symbolic.symbolic.png
        │   │   │   │   ├── system-file-manager-symbolic.symbolic.png
        │   │   │   │   ├── system-software-install-symbolic.symbolic.png
        │   │   │   │   ├── system-users-symbolic.symbolic.png
        │   │   │   │   ├── text-editor-symbolic.symbolic.png
        │   │   │   │   ├── user-info-symbolic.symbolic.png
        │   │   │   │   ├── utilities-terminal-symbolic.symbolic.png
        │   │   │   │   └── web-browser-symbolic.symbolic.png
        │   │   │   ├── categories
        │   │   │   │   ├── applications-engineering-symbolic.symbolic.png
        │   │   │   │   ├── applications-games-symbolic.symbolic.png
        │   │   │   │   ├── applications-graphics-symbolic.symbolic.png
        │   │   │   │   ├── applications-multimedia-symbolic.symbolic.png
        │   │   │   │   ├── applications-science-symbolic.symbolic.png
        │   │   │   │   ├── applications-system-symbolic.symbolic.png
        │   │   │   │   ├── applications-utilities-symbolic.symbolic.png
        │   │   │   │   ├── emoji-activities-symbolic.symbolic.png
        │   │   │   │   ├── emoji-body-symbolic.symbolic.png
        │   │   │   │   ├── emoji-flags-symbolic.symbolic.png
        │   │   │   │   ├── emoji-food-symbolic.symbolic.png
        │   │   │   │   ├── emoji-nature-symbolic.symbolic.png
        │   │   │   │   ├── emoji-objects-symbolic.symbolic.png
        │   │   │   │   ├── emoji-people-symbolic.symbolic.png
        │   │   │   │   ├── emoji-recent-symbolic.symbolic.png
        │   │   │   │   ├── emoji-symbols-symbolic.symbolic.png
        │   │   │   │   ├── emoji-travel-symbolic.symbolic.png
        │   │   │   │   ├── preferences-other-symbolic.symbolic.png
        │   │   │   │   ├── preferences-system-symbolic.symbolic.png
        │   │   │   │   └── system-help-symbolic.symbolic.png
        │   │   │   ├── devices
        │   │   │   │   ├── ac-adapter-symbolic.symbolic.png
        │   │   │   │   ├── audio-card-symbolic.symbolic.png
        │   │   │   │   ├── audio-headphones.png
        │   │   │   │   ├── audio-headphones-symbolic.symbolic.png
        │   │   │   │   ├── audio-headset.png
        │   │   │   │   ├── audio-headset-symbolic.symbolic.png
        │   │   │   │   ├── audio-input-microphone-symbolic.symbolic.png
        │   │   │   │   ├── audio-speakers-symbolic.symbolic.png
        │   │   │   │   ├── auth-fingerprint-symbolic.symbolic.png
        │   │   │   │   ├── auth-sim-symbolic.symbolic.png
        │   │   │   │   ├── auth-smartcard-symbolic.symbolic.png
        │   │   │   │   ├── battery-symbolic.symbolic.png
        │   │   │   │   ├── bluetooth-symbolic.symbolic.png
        │   │   │   │   ├── camera-photo-symbolic.symbolic.png
        │   │   │   │   ├── camera-video-symbolic.symbolic.png
        │   │   │   │   ├── camera-web-symbolic.symbolic.png
        │   │   │   │   ├── colorimeter-colorhug-symbolic.symbolic.png
        │   │   │   │   ├── computer-apple-ipad-symbolic.symbolic.png
        │   │   │   │   ├── computer.png
        │   │   │   │   ├── computer-symbolic.symbolic.png
        │   │   │   │   ├── display-projector-symbolic.symbolic.png
        │   │   │   │   ├── drive-harddisk-ieee1394-symbolic.symbolic.png
        │   │   │   │   ├── drive-harddisk.png
        │   │   │   │   ├── drive-harddisk-solidstate-symbolic.symbolic.png
        │   │   │   │   ├── drive-harddisk-symbolic.symbolic.png
        │   │   │   │   ├── drive-harddisk-system-symbolic.symbolic.png
        │   │   │   │   ├── drive-harddisk-usb-symbolic.symbolic.png
        │   │   │   │   ├── drive-multidisk-symbolic.symbolic.png
        │   │   │   │   ├── drive-optical-symbolic.symbolic.png
        │   │   │   │   ├── drive-removable-media.png
        │   │   │   │   ├── drive-removable-media-symbolic.symbolic.png
        │   │   │   │   ├── input-dialpad-symbolic.symbolic.png
        │   │   │   │   ├── input-gaming-symbolic.symbolic.png
        │   │   │   │   ├── input-keyboard-symbolic.symbolic.png
        │   │   │   │   ├── input-mouse-symbolic.symbolic.png
        │   │   │   │   ├── input-tablet-symbolic.symbolic.png
        │   │   │   │   ├── input-touchpad-symbolic.symbolic.png
        │   │   │   │   ├── media-flash-symbolic.symbolic.png
        │   │   │   │   ├── media-floppy-symbolic.symbolic.png
        │   │   │   │   ├── media-optical-bd-symbolic.symbolic.png
        │   │   │   │   ├── media-optical-cd-audio-symbolic.symbolic.png
        │   │   │   │   ├── media-optical-dvd-symbolic.symbolic.png
        │   │   │   │   ├── media-optical.png
        │   │   │   │   ├── media-optical-symbolic.symbolic.png
        │   │   │   │   ├── media-removable.png
        │   │   │   │   ├── media-removable-symbolic.symbolic.png
        │   │   │   │   ├── media-tape-symbolic.symbolic.png
        │   │   │   │   ├── media-zip-symbolic.symbolic.png
        │   │   │   │   ├── modem-symbolic.symbolic.png
        │   │   │   │   ├── multimedia-player-apple-ipod-touch-symbolic.symbolic.png
        │   │   │   │   ├── multimedia-player-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-symbolic.symbolic.png
        │   │   │   │   ├── network-wired-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-symbolic.symbolic.png
        │   │   │   │   ├── pda-symbolic.symbolic.png
        │   │   │   │   ├── phone-apple-iphone-symbolic.symbolic.png
        │   │   │   │   ├── phone-old-symbolic.symbolic.png
        │   │   │   │   ├── phone-symbolic.symbolic.png
        │   │   │   │   ├── printer-network.png
        │   │   │   │   ├── printer-network-symbolic.symbolic.png
        │   │   │   │   ├── printer.png
        │   │   │   │   ├── printer-symbolic.symbolic.png
        │   │   │   │   ├── scanner-symbolic.symbolic.png
        │   │   │   │   ├── thunderbolt-symbolic.symbolic.png
        │   │   │   │   ├── tv-symbolic.symbolic.png
        │   │   │   │   ├── uninterruptible-power-supply-symbolic.symbolic.png
        │   │   │   │   ├── video-display-symbolic.symbolic.png
        │   │   │   │   ├── video-joined-displays-symbolic.symbolic.png
        │   │   │   │   └── video-single-display-symbolic.symbolic.png
        │   │   │   ├── emblems
        │   │   │   │   ├── emblem-default-symbolic.symbolic.png
        │   │   │   │   ├── emblem-documents-symbolic.symbolic.png
        │   │   │   │   ├── emblem-favorite-symbolic.symbolic.png
        │   │   │   │   ├── emblem-important-symbolic.symbolic.png
        │   │   │   │   ├── emblem-music-symbolic.symbolic.png
        │   │   │   │   ├── emblem-ok-symbolic.symbolic.png
        │   │   │   │   ├── emblem-photos-symbolic.symbolic.png
        │   │   │   │   ├── emblem-readonly.png
        │   │   │   │   ├── emblem-shared.png
        │   │   │   │   ├── emblem-shared-symbolic.symbolic.png
        │   │   │   │   ├── emblem-symbolic-link.png
        │   │   │   │   ├── emblem-synchronizing.png
        │   │   │   │   ├── emblem-synchronizing-symbolic.symbolic.png
        │   │   │   │   ├── emblem-system-symbolic.symbolic.png
        │   │   │   │   ├── emblem-unreadable.png
        │   │   │   │   └── emblem-videos-symbolic.symbolic.png
        │   │   │   ├── emotes
        │   │   │   │   ├── emote-love-symbolic.symbolic.png
        │   │   │   │   ├── face-angel-symbolic.symbolic.png
        │   │   │   │   ├── face-angry-symbolic.symbolic.png
        │   │   │   │   ├── face-confused-symbolic.symbolic.png
        │   │   │   │   ├── face-cool-symbolic.symbolic.png
        │   │   │   │   ├── face-crying-symbolic.symbolic.png
        │   │   │   │   ├── face-devilish-symbolic.symbolic.png
        │   │   │   │   ├── face-embarrassed-symbolic.symbolic.png
        │   │   │   │   ├── face-glasses-symbolic.symbolic.png
        │   │   │   │   ├── face-kiss-symbolic.symbolic.png
        │   │   │   │   ├── face-laugh-symbolic.symbolic.png
        │   │   │   │   ├── face-monkey-symbolic.symbolic.png
        │   │   │   │   ├── face-plain-symbolic.symbolic.png
        │   │   │   │   ├── face-raspberry-symbolic.symbolic.png
        │   │   │   │   ├── face-sad-symbolic.symbolic.png
        │   │   │   │   ├── face-shutmouth-symbolic.symbolic.png
        │   │   │   │   ├── face-sick-symbolic.symbolic.png
        │   │   │   │   ├── face-smile-big-symbolic.symbolic.png
        │   │   │   │   ├── face-smile-symbolic.symbolic.png
        │   │   │   │   ├── face-smirk-symbolic.symbolic.png
        │   │   │   │   ├── face-surprise-symbolic.symbolic.png
        │   │   │   │   ├── face-tired-symbolic.symbolic.png
        │   │   │   │   ├── face-uncertain-symbolic.symbolic.png
        │   │   │   │   ├── face-wink-symbolic.symbolic.png
        │   │   │   │   ├── face-worried-symbolic.symbolic.png
        │   │   │   │   └── face-yawn-symbolic.symbolic.png
        │   │   │   ├── legacy
        │   │   │   │   ├── ac-adapter.png
        │   │   │   │   ├── accessories-calculator.png
        │   │   │   │   ├── accessories-character-map.png
        │   │   │   │   ├── accessories-dictionary.png
        │   │   │   │   ├── accessories-text-editor.png
        │   │   │   ���   ├── address-book-new.png
        │   │   │   │   ├── applets-screenshooter.png
        │   │   │   │   ├── application-exit.png
        │   │   │   │   ├── applications-accessories.png
        │   │   │   │   ├── applications-graphics.png
        │   │   │   │   ├── applications-internet.png
        │   │   │   │   ├── applications-office.png
        │   │   │   │   ├── applications-science.png
        │   │   │   │   ├── applications-system.png
        │   │   │   │   ├── applications-utilities.png
        │   │   │   │   ├── appointment-missed.png
        │   │   │   │   ├── appointment-new.png
        │   │   │   │   ├── appointment-soon.png
        │   │   │   │   ├── audio-card.png
        │   │   │   │   ├── audio-speakers.png
        │   │   │   │   ├── audio-volume-high.png
        │   │   │   │   ├── audio-volume-low.png
        │   │   │   │   ├── audio-volume-medium.png
        │   │   │   │   ├── audio-volume-muted.png
        │   │   │   │   ├── battery-caution-charging.png
        │   │   │   │   ├── battery-caution-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-caution.png
        │   │   │   │   ├── battery-caution-symbolic.symbolic.png
        │   │   │   │   ├── battery-empty-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-empty.png
        │   │   │   │   ├── battery-empty-symbolic.symbolic.png
        │   │   │   │   ├── battery-full-charged.png
        │   │   │   │   ├── battery-full-charged-symbolic.symbolic.png
        │   │   │   │   ├── battery-full-charging.png
        │   │   │   │   ├── battery-full-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-full.png
        │   │   │   │   ├── battery-full-symbolic.symbolic.png
        │   │   │   │   ├── battery-good-charging.png
        │   │   │   │   ├── battery-good-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-good.png
        │   │   │   │   ├── battery-good-symbolic.symbolic.png
        │   │   │   │   ├── battery-low-charging.png
        │   │   │   │   ├── battery-low-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-low.png
        │   │   │   │   ├── battery-low-symbolic.symbolic.png
        │   │   │   │   ├── battery-missing.png
        │   │   │   │   ├── battery.png
        │   │   │   │   ├── bookmark-new.png
        │   │   │   │   ├── call-start.png
        │   │   │   │   ├── call-stop.png
        │   │   │   │   ├── camera-photo.png
        │   │   │   │   ├── camera-video.png
        │   │   │   │   ├── camera-web.png
        │   │   │   │   ├── changes-allow.png
        │   │   │   │   ├── changes-prevent.png
        │   │   │   │   ├── computer-fail.png
        │   │   │   │   ├── computer.png
        │   │   │   │   ├── contact-new.png
        │   │   │   │   ├── dialog-error.png
        │   │   │   │   ├── dialog-information.png
        │   │   │   │   ├── dialog-password.png
        │   │   │   │   ├── dialog-question.png
        │   │   │   │   ├── dialog-warning.png
        │   │   │   │   ├── document-new.png
        │   │   │   │   ├── document-open.png
        │   │   │   │   ├── document-open-recent.png
        │   │   │   │   ├── document-page-setup.png
        │   │   │   │   ├── document-print.png
        │   │   │   │   ├── document-print-preview.png
        │   │   │   │   ├── document-properties.png
        │   │   │   │   ├── document-revert.png
        │   │   │   │   ├── document-revert-rtl.png
        │   │   │   │   ├── document-save-as.png
        │   │   │   │   ├── document-save.png
        │   │   │   │   ├── document-send.png
        │   │   │   │   ├── drive-multidisk.png
        │   │   │   │   ├── drive-optical.png
        │   │   │   │   ├── ebook-reader.png
        │   │   │   │   ├── edit-copy.png
        │   │   │   │   ├── edit-cut.png
        │   │   │   │   ├── edit-delete.png
        │   │   │   │   ├── edit-find.png
        │   │   │   │   ├── edit-find-replace.png
        │   │   │   │   ├── edit-paste.png
        │   │   │   │   ├── edit-redo.png
        │   │   │   │   ├── edit-redo-rtl.png
        │   │   │   │   ├── edit-select-all.png
        │   │   │   │   ├── edit-undo.png
        │   │   │   │   ├── edit-undo-rtl.png
        │   │   │   │   ├── emblem-default.png
        │   │   │   │   ├── emblem-documents.png
        │   │   │   │   ├── emblem-downloads.png
        │   │   │   │   ├── emblem-favorite.png
        │   │   │   │   ├── emblem-generic.png
        │   │   │   │   ├── emblem-important.png
        │   │   │   │   ├── emblem-mail.png
        │   │   │   │   ├── emblem-new.png
        │   │   │   │   ├── emblem-package.png
        │   │   │   │   ├── emblem-photos.png
        │   │   │   │   ├── emblem-system.png
        │   │   │   │   ├── emblem-urgent.png
        │   │   │   │   ├── emblem-web.png
        │   │   │   │   ├── face-angel.png
        │   │   │   │   ├── face-angry.png
        │   │   │   │   ├── face-cool.png
        │   │   │   │   ├── face-crying.png
        │   │   │   │   ├── face-devilish.png
        │   │   │   │   ├── face-embarrassed.png
        │   │   │   │   ├── face-glasses.png
        │   │   │   │   ├── face-kiss.png
        │   │   │   │   ├── face-laugh.png
        │   │   │   │   ├── face-monkey.png
        │   │   │   │   ├── face-plain.png
        │   │   │   │   ├── face-raspberry.png
        │   │   │   │   ├── face-sad.png
        │   │   │   │   ├── face-sick.png
        │   │   │   │   ├── face-smile-big.png
        │   │   │   │   ├── face-smile.png
        │   │   │   │   ├── face-smirk.png
        │   │   │   │   ├── face-surprise.png
        │   │   │   │   ├─��� face-tired.png
        │   │   │   │   ├── face-uncertain.png
        │   │   │   │   ├── face-wink.png
        │   │   │   │   ├── face-worried.png
        │   │   │   │   ├── folder-new.png
        │   │   │   │   ├── folder-visiting.png
        │   │   │   │   ├── format-indent-less.png
        │   │   │   │   ├── format-indent-less-rtl.png
        │   │   │   │   ├── format-indent-more.png
        │   │   │   │   ├── format-indent-more-rtl.png
        │   │   │   │   ├── format-justify-center.png
        │   │   │   │   ├── format-justify-fill.png
        │   │   │   │   ├── format-justify-left.png
        │   │   │   │   ├── format-justify-right.png
        │   │   │   │   ├── format-text-bold.png
        │   │   │   │   ├── format-text-italic.png
        │   │   │   │   ├── format-text-strikethrough.png
        │   │   │   │   ├── format-text-underline.png
        │   │   │   │   ├── go-bottom.png
        │   │   │   │   ├── go-down.png
        │   │   │   │   ├── go-first.png
        │   │   │   │   ├── go-first-rtl.png
        │   │   │   │   ├── go-home.png
        │   │   │   │   ├── go-jump.png
        │   │   │   │   ├── go-last.png
        │   │   │   │   ├── go-last-rtl.png
        │   │   │   │   ├── go-next.png
        │   │   │   │   ├── go-next-rtl.png
        │   │   │   │   ├── go-previous.png
        │   │   │   │   ├── go-previous-rtl.png
        │   │   │   │   ├── go-top.png
        │   │   │   │   ├── go-up.png
        │   │   │   │   ├── help-about.png
        │   │   │   │   ├── help-browser.png
        │   │   │   │   ├── help-contents.png
        │   │   │   │   ├── help-faq.png
        │   │   │   │   ├── image-missing.png
        │   │   │   │   ├── input-dialpad.png
        │   │   │   │   ├── input-gaming.png
        │   │   │   │   ├── input-keyboard.png
        │   │   │   │   ├── input-mouse.png
        │   │   │   │   ├── input-tablet.png
        │   │   │   │   ├── input-touchpad.png
        │   │   │   │   ├── insert-image.png
        │   │   │   │   ├── insert-link.png
        │   │   │   │   ├── insert-object.png
        │   │   │   │   ├── insert-text.png
        │   │   │   │   ├── list-add.png
        │   │   │   │   ├── list-remove.png
        │   │   │   │   ├── mail-attachment.png
        │   │   │   │   ├── mail-forward.png
        │   │   │   │   ├── mail-mark-important.png
        │   │   │   │   ├── mail-mark-junk.png
        │   │   │   │   ├── mail-mark-notjunk.png
        │   │   │   │   ├── mail-mark-read.png
        │   │   │   │   ├── mail-mark-unread.png
        │   │   │   │   ├── mail-message-new.png
        │   │   │   │   ├── mail-read.png
        │   │   │   │   ├── mail-replied.png
        │   │   │   │   ├── mail-reply-all.png
        │   │   │   │   ├── mail-reply-sender.png
        │   │   │   │   ├── mail-send.png
        │   │   │   │   ├── mail-send-receive.png
        │   │   │   │   ├── mail-signed.png
        │   │   │   │   ├── mail-signed-verified.png
        │   │   │   │   ├── mail-unread.png
        │   │   │   │   ├── media-eject.png
        │   │   │   │   ├── media-flash.png
        │   │   │   │   ├── media-floppy.png
        │   │   │   │   ├── media-playback-pause.png
        │   │   │   │   ├── media-playback-start.png
        │   │   │   │   ├── media-playback-stop.png
        │   │   │   │   ├── media-playlist-repeat.png
        │   │   │   │   ├── media-playlist-shuffle.png
        │   │   │   │   ├── media-record.png
        │   │   │   │   ├── media-seek-backward.png
        │   │   │   │   ├── media-seek-forward.png
        │   │   │   │   ├── media-skip-backward.png
        │   │   │   │   ├── media-skip-forward.png
        │   │   │   │   ├── media-tape.png
        │   │   │   │   ├── microphone-sensitivity-high.png
        │   │   │   │   ├── microphone-sensitivity-low.png
        │   │   │   │   ├── microphone-sensitivity-medium.png
        │   │   │   │   ├── microphone-sensitivity-muted.png
        │   │   │   │   ├── modem.png
        │   │   │   │   ├── multimedia-player.png
        │   │   │   │   ├── multimedia-volume-control.png
        │   │   │   │   ├── network-cellular-connected.png
        │   │   │   │   ├── network-error.png
        │   │   │   │   ├── network-idle.png
        │   │   │   │   ├── network-offline.png
        │   │   │   │   ├── network-receive.png
        │   │   │   │   ├── network-transmit.png
        │   │   │   │   ├── network-transmit-receive.png
        │   │   │   │   ├── network-vpn.png
        │   │   │   │   ├── network-wired-disconnected.png
        │   │   │   │   ├── network-wired.png
        │   │   │   │   ├── network-wireless-encrypted.png
        │   │   │   │   ├── network-wireless.png
        │   │   │   │   ├── non-starred.png
        │   │   │   │   ├── object-flip-horizontal.png
        │   │   │   │   ├── object-flip-vertical.png
        │   │   │   │   ├── object-rotate-left.png
        │   │   │   │   ├── object-rotate-right.png
        │   │   │   │   ├── pda.png
        │   │   │   │   ├── phone.png
        │   │   │   │   ├── preferences-desktop-accessibility.png
        │   │   │   │   ├── preferences-desktop-display.png
        │   │   │   │   ├── preferences-desktop-font.png
        │   │   │   │   ├── preferences-desktop-keyboard.png
        │   │   │   │   ├── preferences-desktop-keyboard-shortcuts.png
        │   │   │   │   ├── preferences-desktop-locale.png
        │   │   │   │   ├── preferences-desktop-peripherals.png
        │   │   │   │   ├── preferences-desktop-personal.png
        │   │   │   │   ├── preferences-desktop.png
        │   │   │   │   ├── preferences-desktop-remote-desktop.png
        │   │   │   │   ├── preferences-desktop-screensaver.png
        │   │   │   │   ├── preferences-desktop-theme.png
        │   │   │   │   ├── preferences-desktop-wallpaper.png
        │   │   │   │   ├── preferences-other.png
        │   │   │   │   ├── preferences-system-network.png
        │   │   │   │   ├── preferences-system.png
        │   │   │   │   ├── preferences-system-privacy.png
        │   │   │   │   ├── preferences-system-windows.png
        │   │   │   │   ├── printer-error.png
        │   │   │   │   ├── printer-printing.png
        │   │   │   │   ├── process-stop.png
        │   │   │   │   ├── scanner.png
        │   │   │   │   ├── security-high.png
        │   │   │   │   ├── security-low.png
        │   │   │   │   ├── security-medium.png
        │   │   │   │   ├── semi-starred.png
        │   │   │   │   ├── semi-starred-rtl.png
        │   │   │   │   ├── software-update-available.png
        │   │   │   │   ├── software-update-urgent.png
        │   │   │   │   ├── starred.png
        │   │   │   │   ├── system-file-manager.png
        │   │   │   │   ├── system-help.png
        │   │   │   │   ├── system-lock-screen.png
        │   │   │   │   ├── system-log-out.png
        │   │   │   │   ├── system-run.png
        │   │   │   │   ├── system-search.png
        │   │   │   │   ├── system-shutdown.png
        │   │   │   │   ├── system-software-install.png
        │   │   │   │   ├── system-software-update.png
        │   │   │   │   ├── system-users.png
        │   │   │   │   ├── tab-new.png
        │   │   │   │   ├── task-due.png
        │   │   │   │   ├── task-past-due.png
        │   │   │   │   ├── tools-check-spelling.png
        │   │   │   │   ├── trophy-bronze.png
        │   │   │   │   ├── trophy-gold.png
        │   │   │   │   ├── trophy-silver.png
        │   │   │   │   ├── uninterruptible-power-supply.png
        │   │   │   │   ├── user-available.png
        │   │   │   │   ├── user-away.png
        │   │   │   │   ├── user-busy.png
        │   │   │   │   ├── user-idle.png
        │   │   │   │   ├── user-info.png
        │   │   │   │   ├── user-invisible.png
        │   │   │   │   ├── user-offline.png
        │   │   │   │   ├── utilities-terminal.png
        │   │   │   │   ├── video-display.png
        │   │   │   │   ├── view-fullscreen.png
        │   │   │   │   ├── view-refresh.png
        │   │   │   │   ├── view-restore.png
        │   │   │   │   ├── view-sort-ascending.png
        │   │   │   │   ├── view-sort-descending.png
        │   │   │   │   ├── web-browser.png
        │   │   │   │   ├── window-close.png
        │   │   │   │   ├── window-new.png
        │   │   │   │   ├── zoom-fit-best.png
        │   │   │   │   ├── zoom-in.png
        │   │   │   │   ├── zoom-original.png
        │   │   │   │   └── zoom-out.png
        │   │   │   ├── mimetypes
        │   │   │   │   ├── application-certificate.png
        │   │   │   │   ├── application-certificate-symbolic.symbolic.png
        │   │   │   │   ├── application-rss+xml-symbolic.symbolic.png
        │   │   │   │   ├── application-x-addon.png
        │   │   │   │   ├── application-x-addon-symbolic.symbolic.png
        │   │   │   │   ├── application-x-appliance-symbolic.symbolic.png
        │   │   │   │   ├── application-x-executable.png
        │   │   │   │   ├── application-x-executable-symbolic.symbolic.png
        │   │   │   │   ├── application-x-firmware.png
        │   │   │   │   ├── application-x-firmware-symbolic.symbolic.png
        │   │   │   │   ├── application-x-generic.png
        │   │   │   │   ├── application-x-sharedlib.png
        │   │   │   │   ├── audio-x-generic.png
        │   │   │   │   ├── audio-x-generic-symbolic.symbolic.png
        │   │   │   │   ├── font-x-generic.png
        │   │   │   │   ├── font-x-generic-symbolic.symbolic.png
        │   │   │   │   ├── image-x-generic.png
        │   │   │   │   ├── image-x-generic-symbolic.symbolic.png
        │   │   │   │   ├── inode-directory.png
        │   │   │   │   ├── inode-directory-symbolic.symbolic.png
        │   │   │   │   ├── package-x-generic.png
        │   │   │   │   ├── package-x-generic-symbolic.symbolic.png
        │   │   │   │   ├── text-html.png
        │   │   │   │   ├── text-x-generic.png
        │   │   │   │   ├── text-x-generic-symbolic.symbolic.png
        │   │   │   │   ├── text-x-generic-template.png
        │   │   │   │   ├── text-x-preview.png
        │   │   │   │   ├── text-x-script.png
        │   │   │   │   ├── video-x-generic.png
        │   │   │   │   ├── video-x-generic-symbolic.symbolic.png
        │   │   │   │   ├── x-office-address-book.png
        │   │   │   │   ├── x-office-address-book-symbolic.symbolic.png
        │   │   │   │   ├── x-office-calendar.png
        │   │   │   │   ├── x-office-calendar-symbolic.symbolic.png
        │   │   │   │   ├── x-office-document.png
        │   │   │   │   ├── x-office-document-symbolic.symbolic.png
        │   │   │   │   ├── x-office-document-template.png
        │   │   │   │   ├── x-office-drawing.png
        │   │   │   │   ├── x-office-drawing-symbolic.symbolic.png
        │   │   │   │   ├── x-office-drawing-template.png
        │   │   │   │   ├── x-office-presentation.png
        │   │   │   │   ├── x-office-presentation-symbolic.symbolic.png
        │   │   │   │   ├── x-office-presentation-template.png
        │   │   │   │   ├── x-office-spreadsheet.png
        │   │   │   │   ├── x-office-spreadsheet-symbolic.symbolic.png
        │   │   │   │   ├── x-office-spreadsheet-template.png
        │   │   │   │   └── x-package-repository.png
        │   │   │   ├── places
        │   │   │   │   ├── folder-documents.png
        │   │   │   │   ├── folder-documents-symbolic.symbolic.png
        │   │   │   │   ├── folder-download.png
        │   │   │   │   ├── folder-download-symbolic.symbolic.png
        │   │   │   │   ├── folder-drag-accept.png
        │   │   │   │   ├── folder-music.png
        │   │   │   │   ├── folder-music-symbolic.symbolic.png
        │   │   │   │   ├── folder-open.png
        │   │   │   │   ├── folder-pictures.png
        │   │   │   │   ├── folder-pictures-symbolic.symbolic.png
        │   │   │   │   ├── folder.png
        │   │   │   │   ├── folder-publicshare.png
        │   │   │   │   ├── folder-publicshare-symbolic.symbolic.png
        │   │   │   │   ├── folder-remote.png
        │   │   │   │   ├── folder-remote-symbolic.symbolic.png
        │   │   │   │   ├── folder-saved-search.png
        │   │   │   │   ├── folder-saved-search-symbolic.symbolic.png
        │   │   │   │   ├── folder-symbolic.symbolic.png
        │   │   │   │   ├── folder-templates.png
        │   │   │   │   ├── folder-templates-symbolic.symbolic.png
        │   │   │   │   ├── folder-videos.png
        │   │   │   │   ├── folder-videos-symbolic.symbolic.png
        │   │   │   │   ├── network-server.png
        │   │   │   │   ├── network-server-symbolic.symbolic.png
        │   │   │   │   ├── network-workgroup.png
        │   │   │   │   ├── network-workgroup-symbolic.symbolic.png
        │   │   │   │   ├── start-here.png
        │   │   │   │   ├── start-here-symbolic.symbolic.png
        │   │   │   │   ├── user-bookmarks.png
        │   │   │   │   ├── user-bookmarks-symbolic.symbolic.png
        │   │   │   │   ├── user-desktop.png
        │   │   │   │   ├── user-desktop-symbolic.symbolic.png
        │   │   │   │   ├── user-home.png
        │   │   │   │   ├── user-home-symbolic.symbolic.png
        │   │   │   │   ├── user-trash.png
        │   │   │   │   └── user-trash-symbolic.symbolic.png
        │   │   │   ├── status
        │   │   │   │   ├── airplane-mode-symbolic.symbolic.png
        │   │   │   │   ├── alarm-symbolic.symbolic.png
        │   │   │   │   ├── appointment-missed-symbolic.symbolic.png
        │   │   │   │   ├── appointment-soon-symbolic.symbolic.png
        │   │   │   │   ├── audio-volume-high-symbolic.symbolic.png
        │   │   │   │   ├── audio-volume-low-symbolic.symbolic.png
        │   │   │   │   ├── audio-volume-medium-symbolic.symbolic.png
        │   │   │   │   ├── audio-volume-muted-symbolic.symbolic.png
        │   │   │   │   ├── audio-volume-overamplified-symbolic.symbolic.png
        │   │   │   │   ├── auth-sim-locked-symbolic.symbolic.png
        │   │   │   │   ├── auth-sim-missing-symbolic.symbolic.png
        │   │   │   │   ├── avatar-default.png
        │   │   │   │   ├── avatar-default-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-0-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-0-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-100-charged-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-100-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-10-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-10-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-20-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-20-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-30-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-30-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-40-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-40-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-50-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-50-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-60-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-60-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-70-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-70-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-80-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-80-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-90-charging-symbolic.symbolic.png
        │   │   │   │   ├── battery-level-90-symbolic.symbolic.png
        │   │   │   │   ├── battery-missing-symbolic.symbolic.png
        │   │   │   │   ├── bluetooth-active-symbolic.symbolic.png
        │   │   │   │   ├── bluetooth-disabled-symbolic.symbolic.png
        │   │   │   │   ├── bluetooth-hardware-disabled-symbolic.symbolic.png
        │   │   │   │   ├── call-incoming-symbolic.symbolic.png
        │   │   │   │   ├── call-missed-symbolic.symbolic.png
        │   │   │   │   ├── call-outgoing-symbolic.symbolic.png
        │   │   │   │   ├── camera-disabled-symbolic.symbolic.png
        │   │   │   │   ├── camera-hardware-disabled-symbolic.symbolic.png
        │   │   │   │   ├── changes-allow-symbolic.symbolic.png
        │   │   │   │   ├── changes-prevent-symbolic.symbolic.png
        │   │   │   │   ├── channel-insecure-symbolic.symbolic.png
        │   │   │   │   ├── channel-secure-symbolic.symbolic.png
        │   │   │   │   ├── computer-fail-symbolic.symbolic.png
        │   │   │   │   ├── contact-new-symbolic.symbolic.png
        │   │   │   │   ├── content-loading-symbolic.symbolic.png
        │   │   │   │   ├── daytime-sunrise-symbolic.symbolic.png
        │   │   │   │   ├── daytime-sunset-symbolic.symbolic.png
        │   │   │   │   ├── dialog-error-symbolic.symbolic.png
        │   │   │   │   ├── dialog-information-symbolic.symbolic.png
        │   │   │   │   ├── dialog-password-symbolic.symbolic.png
        │   │   │   │   ├── dialog-question-symbolic.symbolic.png
        │   │   │   │   ├── dialog-warning-symbolic.symbolic.png
        │   │   │   │   ├── display-brightness-symbolic.symbolic.png
        │   │   │   │   ├── folder-drag-accept-symbolic.symbolic.png
        │   │   │   │   ├── folder-open-symbolic.symbolic.png
        │ �� │   │   │   ├── folder-visiting-symbolic.symbolic.png
        │   │   │   │   ├── image-loading.png
        │   │   │   │   ├── image-loading-symbolic.symbolic.png
        │   │   │   │   ├── image-missing.png
        │   │   │   │   ├── keyboard-brightness-symbolic.symbolic.png
        │   │   │   │   ├── location-services-active-symbolic.symbolic.png
        │   │   │   │   ├── location-services-disabled-symbolic.symbolic.png
        │   │   │   │   ├── mail-attachment-symbolic.symbolic.png
        │   │   │   │   ├── mail-read-symbolic.symbolic.png
        │   │   │   │   ├── mail-replied-symbolic.symbolic.png
        │   │   │   │   ├── mail-unread-symbolic.symbolic.png
        │   │   │   │   ├── media-playlist-consecutive-symbolic.symbolic.png
        │   │   │   │   ├── media-playlist-repeat-song-symbolic.symbolic.png
        │   │   │   │   ├── media-playlist-repeat-symbolic.symbolic.png
        │   │   │   │   ├── media-playlist-shuffle-symbolic.symbolic.png
        │   │   │   │   ├── microphone-disabled-symbolic.symbolic.png
        │   │   │   │   ├── microphone-hardware-disabled-symbolic.symbolic.png
        │   │   │   │   ├── microphone-sensitivity-high-symbolic.symbolic.png
        │   │   │   │   ├── microphone-sensitivity-low-symbolic.symbolic.png
        │   │   │   │   ├── microphone-sensitivity-medium-symbolic.symbolic.png
        │   │   │   │   ├── microphone-sensitivity-muted-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-2g-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-3g-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-4g-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-acquiring-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-connected-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-disabled-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-edge-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-gprs-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-hardware-disabled-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-hspa-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-no-route-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-offline-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-signal-excellent-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-signal-good-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-signal-none-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-signal-ok-symbolic.symbolic.png
        │   │   │   │   ├── network-cellular-signal-weak-symbolic.symbolic.png
        │   │   │   │   ├── network-error-symbolic.symbolic.png
        │   │   │   │   ├── network-idle-symbolic.symbolic.png
        │   │   │   │   ├── network-no-route-symbolic.symbolic.png
        │   │   │   │   ├── network-offline-symbolic.symbolic.png
        │   │   │   │   ├── network-receive-symbolic.symbolic.png
        │   │   │   │   ├── network-transmit-receive-symbolic.symbolic.png
        │   │   │   │   ├── network-transmit-symbolic.symbolic.png
        │   │   │   │   ├── network-vpn-acquiring-symbolic.symbolic.png
        │   │   │   │   ├── network-vpn-no-route-symbolic.symbolic.png
        │   │   │   │   ├── network-vpn-symbolic.symbolic.png
        │   │   │   │   ├── network-wired-acquiring-symbolic.symbolic.png
        │   │   │   │   ├── network-wired-disconnected-symbolic.symbolic.png
        │   │   │   │   ├── network-wired-no-route-symbolic.symbolic.png
        │   │   │   │   ├── network-wired-offline-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-acquiring-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-connected-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-disabled-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-encrypted-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-hardware-disabled-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-hotspot-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-no-route-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-offline-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-signal-excellent-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-signal-good-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-signal-none-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-signal-ok-symbolic.symbolic.png
        │   │   │   │   ├── network-wireless-signal-weak-symbolic.symbolic.png
        │   │   │   │   ├── night-light-symbolic.symbolic.png
        │   │   │   │   ├── non-starred-symbolic.symbolic.png
        │   │   │   │   ├── notifications-disabled-symbolic.symbolic.png
        │   │   │   │   ├── orientation-landscape-inverse-symbolic.symbolic.png
        │   │   │   │   ├── orientation-landscape-symbolic.symbolic.png
        │   │   │   │   ├── orientation-portrait-left-symbolic.symbolic.png
        │   │   │   │   ├── orientation-portrait-right-symbolic.symbolic.png
        │   │   │   │   ├── printer-error-symbolic.symbolic.png
        │   │   │   │   ├── printer-printing-symbolic.symbolic.png
        │   │   │   │   ├── printer-warning-symbolic.symbolic.png
        │   │   │   │   ├── rotation-allowed-symbolic.symbolic.png
        │   │   │   │   ├── rotation-locked-symbolic.symbolic.png
        │   │   │   │   ├── screen-shared-symbolic.symbolic.png
        │   │   │   │   ├── security-high-symbolic.symbolic.png
        │   │   │   │   ├── security-low-symbolic.symbolic.png
        │   │   │   │   ├── security-medium-symbolic.symbolic.png
        │   │   │   │   ├── semi-starred-symbolic-rtl.symbolic.png
        │   │   │   │   ├── semi-starred-symbolic.symbolic.png
        │   │   │   │   ├── software-update-available-symbolic.symbolic.png
        │   │   │   │   ├── software-update-urgent-symbolic.symbolic.png
        │   │   │   │   ├── starred-symbolic.symbolic.png
        │   │   │   │   ├── system-lock-screen-symbolic.symbolic.png
        │   │   │   │   ├── task-due-symbolic.symbolic.png
        │   │   │   │   ├── task-past-due-symbolic.symbolic.png
        │   │   │   │   ├── thunderbolt-acquiring-symbolic.symbolic.png
        │   │   │   │   ├── touch-disabled-symbolic.symbolic.png
        │   │   │   │   ├── touchpad-disabled-symbolic.symbolic.png
        │   │   │   │   ├── user-available-symbolic.symbolic.png
        │   │   │   │   ├── user-away-symbolic.symbolic.png
        │   │   │   │   ├── user-busy-symbolic.symbolic.png
        │   │   │   │   ├── user-idle-symbolic.symbolic.png
        │   │   │   │   ├── user-invisible-symbolic.symbolic.png
        │   │   │   │   ├── user-not-tracked-symbolic.symbolic.png
        │   │   │   │   ├── user-offline-symbolic.symbolic.png
        │   │   │   │   ├── user-status-pending-symbolic.symbolic.png
        │   │   │   │   ├── user-trash-full.png
        │   │   │   │   ├── user-trash-full-symbolic.symbolic.png
        │   │   │   │   ├── view-wrapped-symbolic-rtl.symbolic.png
        │   │   │   │   ├── view-wrapped-symbolic.symbolic.png
        │   │   │   │   ├── weather-clear-night-symbolic.symbolic.png
        │   │   │   │   ├── weather-clear-symbolic.symbolic.png
        │   │   │   │   ├── weather-few-clouds-night-symbolic.symbolic.png
        │   │   │   │   ├── weather-few-clouds-symbolic.symbolic.png
        │   │   │   │   ├── weather-fog-symbolic.symbolic.png
        │   │   │   │   ├── weather-overcast-symbolic.symbolic.png
        │   │   │   │   ├── weather-severe-alert-symbolic.symbolic.png
        │   │   │   │   ├── weather-showers-scattered-symbolic.symbolic.png
        │   │   │   │   ├── weather-showers-symbolic.symbolic.png
        │   │   │   │   ├── weather-snow-symbolic.symbolic.png
        │   │   │   │   ├── weather-storm-symbolic.symbolic.png
        │   │   │   │   ├── weather-tornado-symbolic.symbolic.png
        │   │   │   │   └── weather-windy-symbolic.symbolic.png
        │   │   │   └── ui
        │   │   │       ├── checkbox-checked-symbolic.symbolic.png
        │   │   │       ├── checkbox-mixed-symbolic.symbolic.png
        │   │   │       ├── checkbox-symbolic.symbolic.png
        │   │   │       ├── focus-legacy-systray-symbolic.symbolic.png
        │   │   │       ├── focus-top-bar-symbolic.symbolic.png
        │   │   │       ├── focus-windows-symbolic.symbolic.png
        │   │   │       ├── list-drag-handle-symbolic.symbolic.png
        │   │   │       ├── pan-down-symbolic.symbolic.png
        │   │   │       ├── pan-end-symbolic-rtl.symbolic.png
        │   │   │       ├── pan-end-symbolic.symbolic.png
        │   │   │       ├── pan-start-symbolic-rtl.symbolic.png
        │   │   │       ├── pan-start-symbolic.symbolic.png
        │   │   │       ├── pan-up-symbolic.symbolic.png
        │   │   │       ├── radio-checked-symbolic.symbolic.png
        │   │   │       ├── radio-mixed-symbolic.symbolic.png
        │   │   │       ├── radio-symbolic.symbolic.png
        │   │   │       ├── selection-end-symbolic-rtl.symbolic.png
        │   │   │       ├── selection-end-symbolic.symbolic.png
        │   │   │       ├── selection-start-symbolic-rtl.symbolic.png
        │   │   │       ├── selection-start-symbolic.symbolic.png
        │   │   │       ├── tab-new-symbolic.symbolic.png
        │   │   │       ├── window-close-symbolic.symbolic.png
        │   │   │       ├── window-maximize-symbolic.symbolic.png
        │   │   │       ├── window-minimize-symbolic.symbolic.png
        │   │   │       ├── window-new-symbolic.symbolic.png
        │   │   │       └── window-restore-symbolic.symbolic.png
        │   │   └── index.theme
        │   └── hicolor
        │       └── index.theme
        ├── libdrm
        │   └── amdgpu.ids
        ├── libwacom
        │   ├── bamboo-0fg-m-p-alt.tablet
        │   ├── bamboo-0fg-s-p-alt.tablet
        │   ├── bamboo-0fg-s-p.tablet
        │   ├── bamboo-16fg-m-pt.tablet
        │   ├── bamboo-16fg-s-p.tablet
        │   ├── bamboo-16fg-s-pt.tablet
        │   ├── bamboo-16fg-s-t.tablet
        │   ├── bamboo-2fg-fun-m-pt.tablet
        │   ├── bamboo-2fg-fun-s-pt.tablet
        │   ├── bamboo-2fg-m-p.tablet
        │   ├── bamboo-2fg-s-p.tablet
        │   ├── bamboo-2fg-s-pt.tablet
        │   ├── bamboo-2fg-s-t.tablet
        │   ├── bamboo-4fg-fun-m.tablet
        │   ├── bamboo-4fg-fun-s.tablet
        │   ├── bamboo-4fg-se-m-pt.tablet
        │   ├── bamboo-4fg-se-s-pt.tablet
        │   ├── bamboo-4fg-s-pt.tablet
        │   ├── bamboo-4fg-s-t.tablet
        │   ├── bamboo-one-m-p.tablet
        │   ├── bamboo-one.tablet
        │   ├── bamboo-pad.tablet
        │   ├── bamboo-pad-wireless.tablet
        │   ├── cintiq-12wx.tablet
        │   ├── cintiq-13hd.tablet
        │   ├── cintiq-13hdt.tablet
        │   ├── cintiq-16.tablet
        │   ├── cintiq-20wsx.tablet
        │   ├── cintiq-21ux2.tablet
        │   ├── cintiq-21ux.tablet
        │   ├── cintiq-22hd.tablet
        │   ├── cintiq-22hdt.tablet
        │   ├── cintiq-22.tablet
        │   ├── cintiq-24hd.tablet
        │   ├── cintiq-24hd-touch.tablet
        │   ├── cintiq-27hd.tablet
        │   ├── cintiq-27hdt.tablet
        │   ├── cintiq-companion-2.tablet
        │   ├── cintiq-companion-hybrid.tablet
        │   ├── cintiq-companion.tablet
        │   ├── cintiq-pro-13.tablet
        │   ├── cintiq-pro-16.tablet
        │   ├── cintiq-pro-24-p.tablet
        │   ├── cintiq-pro-24-pt.tablet
        │   ├── cintiq-pro-32.tablet
        │   ├── dell-canvas-27.tablet
        │   ├── dtf-720.tablet
        │   ├── dth-1152.tablet
        │   ├── dth-2242.tablet
        │   ├── dth-2452.tablet
        │   ├── dti-520.tablet
        │   ├── dtk-1651.tablet
        │   ├── dtk-1660e.tablet
        │   ├── dtk-2241.tablet
        │   ├── dtk-2451.tablet
        │   ├── dtu-1031.tablet
        │   ├── dtu-1031x.tablet
        │   ├── dtu-1141b.tablet
        │   ├── dtu-1141.tablet
        │   ├── dtu-1631.tablet
        │   ├── dtu-1931.tablet
        │   ├── dtu-2231.tablet
        │   ├── ek-remote.tablet
        │   ├── elan-2072.tablet
        │   ├── elan-22e2.tablet
        │   ├── elan-24db.tablet
        │   ├── elan-2537.tablet
        │   ├── elan-2627.tablet
        │   ├── elan-264c.tablet
        │   ├── elan-5515.tablet
        │   ├── generic.tablet
        │   ├── graphire2-4x5.tablet
        │   ├── graphire2-5x7.tablet
        │   ├── graphire3-4x5.tablet
        │   ├── graphire3-6x8.tablet
        │   ├── graphire4-4x5.tablet
        │   ├── graphire4-6x8.tablet
        │   ├── graphire-usb.tablet
        │   ├── graphire-wireless-8x6.tablet
        │   ├── huion-h420.tablet
        │   ├── huion-h610-pro.tablet
        │   ├── intuos-12x12.tablet
        │   ├── intuos-12x18.tablet
        │   ├── intuos2-12x12.tablet
        │   ├── intuos2-12x18.tablet
        │   ├── intuos2-4x5.tablet
        │   ├── intuos2-6x8.tablet
        │   ├── intuos2-9x12.tablet
        │   ├── intuos3-12x12.tablet
        │   ├── intuos3-12x19.tablet
        │   ├── intuos3-4x5.tablet
        │   ├── intuos3-4x6.tablet
        │   ├── intuos3-6x11.tablet
        │   ├── intuos3-6x8.tablet
        │   ├── intuos3-9x12.tablet
        │   ├── intuos4-12x19.tablet
        │   ├── intuos4-4x6.tablet
        │   ├── intuos4-6x9.tablet
        │   ├── intuos4-6x9-wl.tablet
        │   ├── intuos4-8x13.tablet
        │   ├── intuos-4x5.tablet
        │   ├── intuos5-m.tablet
        │   ├── intuos5-s.tablet
        │   ├── intuos5-touch-l.tablet
        │   ├── intuos5-touch-m.tablet
        │   ├── intuos5-touch-s.tablet
        │   ├── intuos-6x8.tablet
        │   ├── intuos-9x12.tablet
        │   ├── intuos-m-p2.tablet
        │   ├── intuos-m-p3.tablet
        │   ├── intuos-m-p3-wl.tablet
        │   ├── intuos-m-pt2.tablet
        │   ├── intuos-m-p.tablet
        │   ├── intuos-m-pt.tablet
        │   ├── intuos-pro-2-l.tablet
        │   ├── intuos-pro-2-m.tablet
        │   ├── intuos-pro-2-s.tablet
        │   ├── intuos-pro-l.tablet
        │   ├── intuos-pro-m.tablet
        │   ├── intuos-pro-s.tablet
        │   ├── intuos-s-p2.tablet
        │   ├── intuos-s-p3.tablet
        │   ├── intuos-s-p3-wl.tablet
        │   ├── intuos-s-pt2.tablet
        │   ├── intuos-s-p.tablet
        │   ├── intuos-s-pt.tablet
        │   ├── isdv4-100.tablet
        │   ├── isdv4-101.tablet
        │   ├── isdv4-104.tablet
        │   ├── isdv4-10d.tablet
        │   ├── isdv4-10e.tablet
        │   ├── isdv4-10f.tablet
        │   ├── isdv4-114.tablet
        │   ├── isdv4-116.tablet
        │   ├── isdv4-117.tablet
        │   ├── isdv4-124.tablet
        │   ├── isdv4-12c.tablet
        │   ├── isdv4-2d1f-002e.tablet
        │   ├── isdv4-4004.tablet
        │   ├── isdv4-4800.tablet
        │   ├── isdv4-4806.tablet
        │   ├── isdv4-4807.tablet
        │   ├── isdv4-4809.tablet
        │   ├── isdv4-4814.tablet
        │   ├── isdv4-481a.tablet
        │   ├── isdv4-4822.tablet
        │   ├── isdv4-4824.tablet
        │   ├── isdv4-4831.tablet
        │   ├── isdv4-4841.tablet
        │   ├── isdv4-484c.tablet
        │   ├── isdv4-485e.tablet
        │   ├── isdv4-4865.tablet
        │   ├── isdv4-486a.tablet
        │   ├── isdv4-4870.tablet
        │   ├── isdv4-488f.tablet
        │   ├── isdv4-5000.tablet
        │   ├── isdv4-5002.tablet
        │   ├── isdv4-5010.tablet
        │   ├── isdv4-5013.tablet
        │   ├── isdv4-5014.tablet
        │   ├── isdv4-502a.tablet
        │   ├── isdv4-503e.tablet
        │   ├── isdv4-503f.tablet
        │   ├── isdv4-5040.tablet
        │   ├── isdv4-5044.tablet
        │   ├── isdv4-5048.tablet
        │   ├── isdv4-504a.tablet
        │   ├── isdv4-5090.tablet
        │   ├── isdv4-5099.tablet
        │   ├── isdv4-509d.tablet
        │   ├── isdv4-50b4.tablet
        │   ├── isdv4-50b6.tablet
        │   ├── isdv4-50b8.tablet
        │   ├── isdv4-50db.tablet
        │   ├── isdv4-50e9.tablet
        │   ├── isdv4-50f1.tablet
        │   ├── isdv4-50f8.tablet
        │   ├── isdv4-50fd.tablet
        │   ├── isdv4-5110.tablet
        │   ├── isdv4-5115.tablet
        │   ├── isdv4-5122.tablet
        │   ├── isdv4-5128.tablet
        │   ├── isdv4-513b.tablet
        │   ├── isdv4-5146.tablet
        │   ├── isdv4-5150.tablet
        │   ├── isdv4-5157.tablet
        │   ├── isdv4-5158.tablet
        │   ├── isdv4-515a.tablet
        │   ├── isdv4-5169.tablet
        │   ├── isdv4-516b.tablet
        │   ├── isdv4-517d.tablet
        │   ├── isdv4-90.tablet
        │   ├── isdv4-93.tablet
        │   ├── isdv4-e2.tablet
        │   ├── isdv4-e3.tablet
        │   ├── isdv4-e5.tablet
        │   ├── isdv4-e6.tablet
        │   ├── isdv4-ec.tablet
        │   ├── isdv4-ed.tablet
        │   ├── isdv4-ef.tablet
        │   ├── layouts
        │   │   ├── bamboo-0fg-s-p-alt.svg
        │   │   ├── bamboo-0fg-s-p.svg
        │   │   ├── bamboo-16fg-m-pt.svg
        │   │   ├── bamboo-16fg-s-pt.svg
        │   │   ├── bamboo-16fg-s-t.svg
        │   │   ├── bamboo-2fg-fun-m-pt.svg
        │   │   ├── bamboo-2fg-fun-s-pt.svg
        │   │   ├── bamboo-2fg-s-pt.svg
        │   │   ├── bamboo-2fg-s-t.svg
        │   │   ├── bamboo-4fg-fun-m-pt.svg
        │   │   ├── bamboo-4fg-fun-s-pt.svg
        │   │   ├── bamboo-4fg-se-m-pt.svg
        │   │   ├── bamboo-4fg-se-s-pt.svg
        │   │   ├── bamboo-4fg-s-pt.svg
        │   │   ├── bamboo-4fg-s-t.svg
        │   │   ├── bamboo-pad.svg
        │   │   ├── cintiq-12wx.svg
        │   │   ├── cintiq-13hd.svg
        │   │   ├── cintiq-20wsx.svg
        │   │   ├── cintiq-21ux2.svg
        │   │   ├── cintiq-21ux.svg
        │   │   ├── cintiq-22hd.svg
        │   │   ├── cintiq-24hd.svg
        │   │   ├── cintiq-companion-2.svg
        │   │   ├── cintiq-companion-hybrid.svg
        │   │   ├── cintiq-companion.svg
        │   │   ├── dth-2242.svg
        │   │   ├── dth-2452.svg
        │   │   ├── dti-520.svg
        │   │   ├── dtk-1651.svg
        │   │   ├── dtk-2451.svg
        │   │   ├── dtu-1031.svg
        │   │   ├── dtu-1141b.svg
        │   │   ├── dtu-1141.svg
        │   │   ├── ek-remote.svg
        │   │   ├── graphire4-4x5.svg
        │   │   ├── graphire4-6x8.svg
        │   │   ├── graphire-wireless-8x6.svg
        │   │   ├── huion-h420.svg
        │   │   ├── huion-h610-pro.svg
        │   │   ├── intuos3-12x12.svg
        │   │   ├── intuos3-12x19.svg
        │   │   ├── intuos3-4x5.svg
        │   │   ├── intuos3-4x6.svg
        │   │   ├── intuos3-6x11.svg
        │   │   ├── intuos3-6x8.svg
        │   │   ├── intuos3-9x12.svg
        │   │   ├── intuos4-12x19.svg
        │   │   ├── intuos4-4x6.svg
        │   │   ├── intuos4-6x9.svg
        │   │   ├── intuos4-6x9-wl.svg
        │   │   ├── intuos4-8x13.svg
        │   │   ├── intuos5-l.svg
        │   │   ├── intuos5-m.svg
        │   │   ├── intuos5-s.svg
        │   │   ├── intuos-m-p2.svg
        │   │   ├── intuos-m-p3.svg
        │   │   ├── intuos-m-p.svg
        │   │   ├── intuos-m-pt2.svg
        │   │   ├── intuos-m-pt.svg
        │   │   ├── intuos-pro-2-l.svg
        │   │   ├── intuos-pro-2-m.svg
        │   │   ├── intuos-pro-2-s.svg
        │   │   ├── intuos-pro-l.svg
        │   │   ├── intuos-pro-m.svg
        │   │   ├── intuos-pro-s.svg
        │   │   ├── intuos-s-p2.svg
        │   │   ├── intuos-s-p3.svg
        │   │   ├── intuos-s-p.svg
        │   │   ├── intuos-s-pt2.svg
        │   │   ├── intuos-s-pt.svg
        │   │   ├── mobilestudio-pro-13.svg
        │   │   ├── mobilestudio-pro-16.svg
        │   │   └── xp-pen-star03.svg
        │   ├── libwacom.stylus
        │   ├── mobilestudio-pro-13.tablet
        │   ├── mobilestudio-pro-16.tablet
        │   ├── n-trig-pen.tablet
        │   ├── one-by-wacom-m-p2.tablet
        │   ├── one-by-wacom-m-p.tablet
        │   ├── one-by-wacom-s-p2.tablet
        │   ├── one-by-wacom-s-p.tablet
        │   ├── serial-wacf004.tablet
        │   └── xp-pen-star03.tablet
        ├── mc
        │   ├── examples
        │   │   └── macros.d
        │   │       ├── macro.0.sh
        │   │       ├── macro.1.sh
        │   │       ├── macro.3.sh
        │   │       ├── macro.4.sh
        │   │       ├── macro.5.sh
        │   │       ├── macro.6.sh
        │   │       └── macro.7.sh
        │   ├── help
        │   │   └── mc.hlp
        │   ├── hints
        │   │   └── mc.hint
        │   ├── mc.charsets
        │   ├── mc.lib
        │   ├── skins
        │   │   ├── darkfar.ini
        │   │   ├── dark.ini
        │   │   ├── default.ini
        │   │   ├── double-lines.ini
        │   │   ├── featured.ini
        │   │   ├── gotar.ini
        │   │   ├── gray-green-purple256.ini
        │   │   ├── gray-orange-blue256.ini
        │   │   ├── mc46.ini
        │   │   ├── modarcon16-defbg.ini
        │   │   ├── modarcon16.ini
        │   │   ├── modarcon16root-defbg.ini
        │   │   ├── modarcon16root.ini
        │   │   ├── modarin256-defbg.ini
        │   │   ├── modarin256.ini
        │   │   ├── modarin256root-defbg.ini
        │   │   ├── modarin256root.ini
        │   │   ├── nicedark.ini
        │   │   ├── sand256.ini
        │   │   ├── seasons-autumn16M.ini
        │   │   ├── seasons-spring16M.ini
        │   │   ├── seasons-summer16M.ini
        │   │   ├── seasons-winter16M.ini
        │   │   ├── xoria256.ini
        │   │   ├── yadt256-defbg.ini
        │   │   └── yadt256.ini
        │   └── syntax
        │       ├── ada95.syntax
        │       ├── aspx.syntax
        │       ├── assembler.syntax
        │       ├── as.syntax
        │       ├── awk.syntax
        │       ├── cabal.syntax
        │       ├── changelog.syntax
        │       ├── cmake.syntax
        │       ├── css.syntax
        │       ├── cs.syntax
        │       ├── c.syntax
        │       ├── cuda.syntax
        │       ├── cxx.syntax
        │       ├── cython.syntax
        │       ├── debian-changelog.syntax
        │       ├── debian-control.syntax
        │       ├── debian-description.syntax
        │       ├── debian-sources-list.syntax
        │       ├── diff.syntax
        │       ├── dlink.syntax
        │       ├── dos.syntax
        │       ├── d.syntax
        │       ├── ebuild.syntax
        │       ├── eiffel.syntax
        │       ├── erlang.syntax
        │       ├── f90.syntax
        │       ├── filehighlight.syntax
        │       ├── fortran.syntax
        │       ├── glsl.syntax
        │       ├── go.syntax
        │       ├── haskell.syntax
        │       ├── hive.syntax
        │       ├── html.syntax
        │       ├── idl.syntax
        │       ├── ini.syntax
        │       ├── jal.syntax
        │       ├── java.syntax
        │       ├── js.syntax
        │       ├── j.syntax
        │       ├── latex.syntax
        │       ├── lisp.syntax
        │       ├── lkr.syntax
        │       ├── lsm.syntax
        │       ├── lua.syntax
        │       ├── m4.syntax
        │       ├── mail.syntax
        │       ├── makefile.syntax
        │       ├── markdown.syntax
        │       ├── meson.syntax
        │       ├── ml.syntax
        │       ├── named.syntax
        │       ├── nemerle.syntax
        │       ├── nroff.syntax
        │       ├── octave.syntax
        │       ├── opencl.syntax
        │       ├── osl.syntax
        │       ├── pascal.syntax
        │       ├── perl.syntax
        │       ├── php.syntax
        │       ├── PKGBUILD.syntax
        │       ├── po.syntax
        │       ├── povray.syntax
        │       ├── procmail.syntax
        │       ├── properties.syntax
        │       ├── protobuf.syntax
        │       ├── puppet.syntax
        │       ├── python.syntax
        │       ├── r.syntax
        │       ├── ruby.syntax
        │       ├── rust.syntax
        │       ├── sh.syntax
        │       ├── slang.syntax
        │       ├── smalltalk.syntax
        │       ├── spec.syntax
        │       ├── sql.syntax
        │       ├── strace.syntax
        │       ├── swig.syntax
        │       ├── Syntax
        │       ├── syntax.syntax
        │       ├── tcl.syntax
        │       ├── texinfo.syntax
        │       ├── ts.syntax
        │       ├── tt.syntax
        │       ├── unknown.syntax
        │       ├── verilog.syntax
        │       ├── vhdl.syntax
        │       ├── xml.syntax
        │       ├── yaml.syntax
        │       ├── yum-repo.syntax
        │       └── yxx.syntax
        ├── misc
        │   ├── pci.ids
        │   └── usb.ids
        ├── themes
        │   ├── Onyx
        │   │   └── openbox-3
        │   │       └── themerc
        │   └── oxygen-gtk
        │       └── gtk-2.0
        │           ├── argb-apps.conf
        │           ├── gtkrc
        │           ├── icons4
        │           ├── kdeglobals
        │           ├── oxygenrc
        │           └── special-icons
        │               ├── standardbutton-closetab-16.png
        │               ├── standardbutton-closetab-down-16.png
        │               └── standardbutton-closetab-hover-16.png
        ├── volumeicon
        │   ├── gui
        │   │   ├── appicon.svg
        │   │   └── preferences.ui
        │   └── icons
        │       ├── Black Gnome
        │       │   ├── 1.png
        │       │   ├── 2.png
        │       │   ├── 3.png
        │       │   ├── 4.png
        │       │   ├── 5.png
        │       │   ├── 6.png
        │       │   ├── 7.png
        │       │   └── 8.png
        │       ├── Blue Bar
        │       │   ├── 1.png
        │       │   ├── 2.png
        │       │   ├── 3.png
        │       │   ├── 4.png
        │       │   ├── 5.png
        │       │   ├── 6.png
        │       │   ├── 7.png
        │       │   └── 8.png
        │       ├── tango
        │       │   ├── 1.png
        │       │   ├── 2.png
        │       │   ├── 3.png
        │       │   ├── 4.png
        │       │   ├── 5.png
        │       │   ├── 6.png
        │       │   ├── 7.png
        │       │   └── 8.png
        │       └── White Gnome
        │           ├── 1.png
        │           ├── 2.png
        │           ├── 3.png
        │           ├── 4.png
        │           ├── 5.png
        │           ├── 6.png
        │           ├── 7.png
        │           └── 8.png
        ├── X11
        │   ├── app-defaults
        │   │   ├── XVkbd
        │   │   ├── XVkbd-belgian
        │   │   ├── XVkbd-common
        │   │   ├── XVkbd-danish
        │   │   ├── XVkbd-fitaly
        │   │   ├── XVkbd-french
        │   │   ├── XVkbd-french2
        │   │   ├── XVkbd-german
        │   │   ├── XVkbd-greek
        │   │   ├── XVkbd-hebrew
        │   │   ├── XVkbd-icelandic
        │   │   ├── XVkbd-italian
        │   │   ├── XVkbd-jisx6002
        │   │   ├── XVkbd-jisx6004
        │   │   ├── XVkbd-korean
        │   │   ├── XVkbd-latin1
        │   │   ├── XVkbd-norwegian
        │   │   ├── XVkbd-portuguese
        │   │   ├── XVkbd-russian
        │   │   ├── XVkbd-slovene
        │   │   ├── XVkbd-small
        │   │   ├── XVkbd-spanish
        │   │   ├── XVkbd-strip
        │   │   ├── XVkbd-swedish
        │   │   ├── XVkbd-swissgerman
        │   │   ├── XVkbd-turkish
        │   │   ├── XVkbd-turkishF
        │   │   └── XVkbd-uk
        │   ├── locale
        │   │   ├── am_ET.UTF-8
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── armscii-8
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── C
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── compose.dir
        │   │   ├── cs_CZ.UTF-8
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── el_GR.UTF-8
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── en_US.UTF-8
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── fi_FI.UTF-8
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── georgian-academy
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── georgian-ps
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── ibm-cp1133
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── iscii-dev
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── isiri-3342
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── iso8859-1
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── iso8859-10
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── iso8859-11
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── iso8859-13
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── iso8859-14
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── iso8859-15
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── iso8859-2
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── iso8859-3
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── iso8859-4
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── iso8859-5
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── iso8859-6
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── iso8859-7
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── iso8859-8
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── iso8859-9
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── iso8859-9e
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── ja
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── ja.JIS
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── ja_JP.UTF-8
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── ja.SJIS
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── km_KH.UTF-8
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── ko
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── koi8-c
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── koi8-r
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── koi8-u
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── ko_KR.UTF-8
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── locale.alias
        │   │   ├── locale.dir
        │   │   ├── microsoft-cp1251
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── microsoft-cp1255
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── microsoft-cp1256
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── mulelao-1
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── nokhchi-1
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── pt_BR.UTF-8
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── pt_PT.UTF-8
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── ru_RU.UTF-8
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── sr_RS.UTF-8
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── tatar-cyr
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── th_TH
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── th_TH.UTF-8
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── tscii-0
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── vi_VN.tcvn
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── vi_VN.viscii
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── zh_CN
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── zh_CN.gb18030
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── zh_CN.gbk
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── zh_CN.UTF-8
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── zh_HK.big5
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── zh_HK.big5hkscs
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── zh_HK.UTF-8
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── zh_TW
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   ├── zh_TW.big5
        │   │   │   ├── Compose
        │   │   │   ├── XI18N_OBJS
        │   │   │   └── XLC_LOCALE
        │   │   └── zh_TW.UTF-8
        │   │       ├── Compose
        │   │       ├── XI18N_OBJS
        │   │       └── XLC_LOCALE
        │   ├── xkb
        │   │   ├── compat
        │   │   │   ├── accessx
        │   │   │   ├── basic
        │��  │   │   ├── caps
        │   │   │   ├── complete
        │   │   │   ├── iso9995
        │   │   │   ├── japan
        │   │   │   ├── ledcaps
        │   │   │   ├── ledcompose
        │   │   │   ├── lednum
        │   │   │   ├── ledscroll
        │   │   │   ├── level5
        │   │   │   ├── misc
        │   │   │   ├── mousekeys
        │   │   │   ├── olpc
        │   │   │   ├── pc
        │   │   │   ├── pc98
        │   │   │   ├── README
        │   │   │   ├── xfree86
        │   │   │   └── xtest
        │   │   ├── geometry
        │   │   │   ├── amiga
        │   │   │   ├── ataritt
        │   │   │   ├── chicony
        │   │   │   ├── dell
        │   │   │   ├── digital_vndr
        │   │   │   │   ├── lk
        │   │   │   │   ├── pc
        │   │   │   │   └── unix
        │   │   │   ├── everex
        │   │   │   ├── fujitsu
        │   │   │   ├── hhk
        │   │   │   ├── hp
        │   │   │   ├── keytronic
        │   │   │   ├── kinesis
        │   │   │   ├── macintosh
        │   │   │   ├── microsoft
        │   │   │   ├── nec
        │   │   │   ├── nokia
        │   │   │   ├── northgate
        │   │   │   ├── pc
        │   │   │   ├── README
        │   │   │   ├── sanwa
        │   │   │   ├── sgi_vndr
        │   │   │   │   ├── indigo
        │   │   │   │   ├── indy
        │   │   │   │   └── O2
        │   │   │   ├── sony
        │   │   │   ├── steelseries
        │   │   │   ├── sun
        │   │   │   ├── teck
        │   │   │   ├── thinkpad
        │   │   │   ├── typematrix
        │   │   │   └── winbook
        │   │   ├── keycodes
        │   │   │   ├── aliases
        │   │   │   ├── amiga
        │   │   │   ├── ataritt
        │   │   │   ├── digital_vndr
        │   │   │   │   ├── lk
        │   │   │   │   └── pc
        │   │   │   ├── empty
        │   │   │   ├── evdev
        │   │   │   ├── fujitsu
        │   │   │   ├── hp
        │   │   │   ├── ibm
        │   │   │   ├── jolla
        │   │   │   ├── macintosh
        │   │   │   ├── olpc
        │   │   │   ├── README
        │   │   │   ├── sgi_vndr
        │   │   │   │   ├── indigo
        │   │   │   │   ├── indy
        │   │   │   │   └── iris
        │   │   │   ├── sony
        │   │   │   ├── sun
        │   │   │   ├── xfree86
        │   │   │   └── xfree98
        │   │   ├── rules
        │   │   │   ├── base
        │   │   │   ├── base.extras.xml
        │   │   │   ├── base.lst
        │   │   │   ├── base.xml
        │   │   │   ├── evdev
        │   │   │   ├── evdev.extras.xml
        │   │ �� │   ├── evdev.lst
        │   │   │   ├── evdev.xml
        │   │   │   ├── README
        │   │   │   ├── xfree98
        │   │   │   ├── xkb.dtd
        │   │   │   ├── xorg -> base
        │   │   │   ├── xorg.lst -> base.lst
        │   │   │   └── xorg.xml -> base.xml
        │   │   ├── symbols
        │   │   │   ├── af
        │   │   │   ├── al
        │   │   │   ├── altwin
        │   │   │   ├── am
        │   │   │   ├── apl
        │   │   │   ├── ara
        │   │   │   ├── at
        │   │   │   ├── au
        │   │   │   ├── az
        │   │   │   ├── ba
        │   │   │   ├── bd
        │   │   │   ├── be
        │   │   │   ├── bg
        │   │   │   ├── br
        │   │   │   ├── brai
        │   │   │   ├── bt
        │   │   │   ├── bw
        │   │   │   ├── by
        │   │   │   ├── ca
        │   │   │   ├── capslock
        │   │   │   ├── cd
        │   │   │   ├── ch
        │   │   │   ├── cm
        │   │   │   ├── cn
        │   │   │   ├── compose
        │   │   │   ├── ctrl
        │   │   │   ├── cz
        │   │   │   ├── de
        │   │   │   ├── digital_vndr
        │   │   │   │   ├── lk
        │   │   │   │   ├── pc
        │   │   │   │   ├── us
        │   │   │   │   └── vt
        │   │   │   ├── dk
        │   │   │   ├── dz
        │   │   │   ├── ee
        │   │   │   ├── eg
        │   │   │   ├── empty
        │   │   │   ├── epo
        │   │   │   ├── es
        │   │   │   ├── et
        │   │   │   ├── eu
        │   │   │   ├── eurosign
        │   │   │   ├── fi
        │   │   │   ├── fo
        │   │   │   ├── fr
        │   │   │   ├── fujitsu_vndr
        │   │   │   │   ├── jp
        │   │   │   │   └── us
        │   │   │   ├── gb
        │   │   │   ├── ge
        │   │   │   ├── gh
        │   │   │   ├── gn
        │   │   │   ├── gr
        │   │   │   ├── group
        │   │   │   ├── hp_vndr
        │   │   │   │   └── us
        │   │   │   ├── hr
        │   │   │   ├── hu
        │   │   │   ├── id
        │   │   │   ├── ie
        │   │   │   ├── il
        │   │   │   ├── in
        │   │   │   ├── inet
        │   │   │   ├── iq
        │   │   │   ├── ir
        │   │   │   ├── is
        │   │   │   ├── it
        │   │   │   ├── jolla_vndr
        │   │   │   │   └── sbj
        │   │   │   ├── jp
        │   │   │   ├── jv
        │   │   │   ├── ke
        │   │   │   ├── keypad
        │   │   │   ├── kg
        │   │   │   ├── kh
        │   │   │   ├── kpdl
        │   │   │   ├��─ kr
        │   │   │   ├── kz
        │   │   │   ├── la
        │   │   │   ├── latam
        │   │   │   ├── latin
        │   │   │   ├── level2
        │   │   │   ├── level3
        │   │   │   ├── level5
        │   │   │   ├── lk
        │   │   │   ├── lt
        │   │   │   ├── lv
        │   │   │   ├── ma
        │   │   │   ├── macintosh_vndr
        │   │   │   │   ├── apple
        │   │   │   │   ├── ch
        │   │   │   │   ├── de
        │   │   │   │   ├── dk
        │   │   │   │   ├── fi
        │   │   │   │   ├── fr
        │   │   │   │   ├── gb
        │   │   │   │   ├── is
        │   │   │   │   ├── it
        │   │   │   │   ├── jp
        │   │   │   │   ├── latam
        │   │   │   │   ├── nl
        │   │   │   │   ├── no
        │   │   │   │   ├── pt
        │   │   │   │   ├── se
        │   │   │   │   └── us
        │   │   │   ├── mao
        │   │   │   ├── md
        │   │   │   ├── me
        │   │   │   ├── mk
        │   │   │   ├── ml
        │   │   │   ├── mm
        │   │   │   ├── mn
        │   │   │   ├── mt
        │   │   │   ├── mv
        │   │   │   ├── my
        │   │   │   ├── nbsp
        │   │   │   ├── nec_vndr
        │   │   │   │   └── jp
        │   │   │   ├── ng
        │   │   │   ├── nl
        │   │   │   ├── no
        │   │   │   ├── nokia_vndr
        │   │   │   │   ├── rx-44
        │   │   │   │   ├── rx-51
        │   │   │   │   └── su-8w
        │   │   │   ├── np
        │   │   │   ├── olpc
        │   │   │   ├── parens
        │   │   │   ├── pc
        │   │   │   ├── ph
        │   │   │   ├── pk
        │   │   │   ├── pl
        │   │   │   ├── pt
        │   │   │   ├── ro
        │   │   │   ├── rs
        │   │   │   ├── ru
        │   │   │   ├── rupeesign
        │   │   │   ├── se
        │   │   │   ├── sgi_vndr
        │   │   │   │   └── jp
        │   │   │   ├── sharp_vndr
        │   │   │   │   ├── sl-c3x00
        │   │   │   │   ├── ws003sh
        │   │   │   │   ├── ws007sh
        │   │   │   │   ├── ws011sh
        │   │   │   │   └── ws020sh
        │   │   │   ├── shift
        │   │   │   ├── si
        │   │   │   ├── sk
        │   │   │   ├── sn
        │   │   │   ├── sony_vndr
        │   │   │   │   └── us
        │   │   │   ├── srvr_ctrl
        │   │   │   ├── sun_vndr
        │   │   │   │   ├── ara
        │   │   │   │   ├── be
        │   │   │   │   ├── br
        │   │   │   │   ├── ca
        │   │   │   │   ├── ch
        │   │   │   │   ├── cz
        │   │   │   │   ├── de
        │   │   │   │   ├── dk
        │   │   │   │   ├── ee
        │   │   │   │   ├── es
        │   │   │   │   ├── fi
        │   │   │   │   ├── fr
        │   │   │   │   ├── gb
        │   │   │   │   ├── gr
        │   │   │   │   ├── it
        │   │   │   │   ├── jp
        │   │   │   │   ├── kr
        │   │   │   │   ├── lt
        │   │   │   │   ├── lv
        │   │   │   │   ├── nl
        │   │   │   │   ├── no
        │   │   │   │   ├── pl
        │   │   │   │   ├── pt
        │   │   │   │   ├── ro
        │   │   │   │   ├── ru
        │   │   │   │   ├── se
        │   │   │   │   ├── sk
        │   │   │   │   ├── solaris
        │   │   │   │   ├── tr
        │   │   │   │   ├── tw
        │   │   │   │   ├── ua
        │   │   │   │   └── us
        │   │   │   ├── sy
        │   │   │   ├── terminate
        │   │   │   ├── tg
        │   │   │   ├── th
        │   │   │   ├── tj
        │   │   │   ├── tm
        │   │   │   ├── tr
        │   │   │   ├── trans
        │   │   │   ├── tw
        │   │   │   ├── typo
        │   │   │   ├── tz
        │   │   │   ├── ua
        │   │   │   ├── us
        │   │   │   ├── uz
        │   │   │   ├── vn
        │   │   │   ├── xfree68_vndr
        │   │   │   │   ├── amiga
        │   │   │   │   └── ataritt
        │   │   │   └── za
        │   │   └── types
        │   │       ├── basic
        │   │       ├── cancel
        │   │       ├── caps
        │   │       ├── complete
        │   │       ├── default
        │   │       ├── extra
        │   │       ├── iso9995
        │   │       ├── level5
        │   │       ├── mousekeys
        │   │       ├── nokia
        │   │       ├── numpad
        │   │       ├── pc
        │   │       └── README
        │   └── xorg.conf.d
        │       ├── 10-amdgpu.conf
        │       ├── 10-evdev.conf
        │       ├── 10-quirks.conf
        │       ├── 10-radeon.conf
        │       ├── 70-synaptics.conf
        │       └── 70-wacom.conf
        └── zoneinfo
            ├── Africa
            │   ├── Abidjan
            │   ├── Accra
            │   ├── Addis_Ababa
            │   ├── Algiers
            │   ├── Asmara
            │   ├── Asmera
            │   ├── Bamako
            │   ├── Bangui
            │   ├── Banjul
            │   ├── Bissau
            │   ├── Blantyre
            │   ├── Brazzaville
            │   ├── Bujumbura
            │   ├── Cairo
            │   ├── Casablanca
            │   ├── Ceuta
            │   ├── Conakry
            │   ├── Dakar
            │   ├── Dar_es_Salaam
            │   ├── Djibouti
            │   ├── Douala
            │   ├── El_Aaiun
            │   ├── Freetown
            │   ├── Gaborone
            │   ├── Harare
            │   ├── Johannesburg
            │   ├── Juba
            │   ├── Kampala
            │   ├── Khartoum
            │   ├── Kigali
            │   ├── Kinshasa
            │   ├── Lagos
            │   ├── Libreville
            │   ├── Lome
            │   ├── Luanda
            │   ├── Lubumbashi
            │   ├── Lusaka
            │   ├── Malabo
            │   ├── Maputo
            │   ├── Maseru
            │   ├── Mbabane
            │   ├── Mogadishu
            │   ├── Monrovia
            │   ├── Nairobi
            │   ├── Ndjamena
            │   ├── Niamey
            │   ├── Nouakchott
            │   ├── Ouagadougou
            │   ├── Porto-Novo
            │   ├── Sao_Tome
            │   ├── Timbuktu
            │   ├── Tripoli
            │   ├── Tunis
            │   └── Windhoek
            ├── America
            │   ├── Adak
            │   ├── Anchorage
            │   ├── Anguilla
            │   ├── Antigua
            │   ├── Araguaina
            │   ├── Argentina
            │   │   ├── Buenos_Aires
            │   │   ├── Catamarca
            │   │   ├── ComodRivadavia
            │   │   ├── Cordoba
            │   │   ├── Jujuy
            │   │   ├── La_Rioja
            │   │   ├── Mendoza
            │   │   ├── Rio_Gallegos
            │   │   ├── Salta
            │   │   ├── San_Juan
            │   │   ├── San_Luis
            │   │   ├── Tucuman
            │   │   └── Ushuaia
            │   ├── Aruba
            │   ├── Asuncion
            │   ├── Atikokan
            │   ├── Atka
            │   ├── Bahia
            │   ├── Bahia_Banderas
            │   ├── Barbados
            │   ├── Belem
            │   ├── Belize
            │   ├── Blanc-Sablon
            │   ├── Boa_Vista
            │   ├── Bogota
            │   ├── Boise
            │   ├── Buenos_Aires
            │   ├── Cambridge_Bay
            │   ├── Campo_Grande
            │   ├── Cancun
            │   ├── Caracas
            │   ├── Catamarca
            │   ├── Cayenne
            │   ├── Cayman
            │   ├── Chicago
            │   ├── Chihuahua
            │   ├── Coral_Harbour
            │   ├── Cordoba
            │   ├── Costa_Rica
            │   ├── Creston
            │   ├── Cuiaba
            │   ├── Curacao
            │   ├── Danmarkshavn
            │   ├── Dawson
            │   ├── Dawson_Creek
            │   ├── Denver
            │   ├── Detroit
            │   ├── Dominica
            │   ├── Edmonton
            │   ├── Eirunepe
            │   ├── El_Salvador
            │   ├── Ensenada
            │   ├── Fortaleza
            │   ├── Fort_Nelson
            │   ├── Fort_Wayne
            │   ├── Glace_Bay
            │   ├── Godthab
            │   ├── Goose_Bay
            │   ├── Grand_Turk
            │   ├── Grenada
            │   ├── Guadeloupe
            │   ├── Guatemala
            │   ├── Guayaquil
            │   ├── Guyana
            │   ├── Halifax
            │   ├── Havana
            │   ├── Hermosillo
            │   ├── Indiana
            │   │   ├── Indianapolis
            │   │   ├── Knox
            │   │   ├── Marengo
            │   │   ├── Petersburg
            │   │   ├── Tell_City
            │   │   ├── Vevay
            │   │   ├── Vincennes
            │   │   └── Winamac
            │   ├── Indianapolis
            │   ├── Inuvik
            │   ├── Iqaluit
            │   ├── Jamaica
            │   ├── Jujuy
            │   ├── Juneau
            │   ├── Kentucky
            │   │   ├── Louisville
            │   │   └── Monticello
            │   ├── Knox_IN
            │   ├── Kralendijk
            │   ├── La_Paz
            │   ├── Lima
            │   ├── Los_Angeles
            │   ├── Louisville
            │   ├── Lower_Princes
            │   ├── Maceio
            │   ├── Managua
            │   ├── Manaus
            │   ├── Marigot
            │   ├── Martinique
            │   ├── Matamoros
            │   ├── Mazatlan
            │   ├── Mendoza
            │   ├── Menominee
            │   ├── Merida
            │   ├── Metlakatla
            │   ├── Mexico_City
            │   ├── Miquelon
            │   ├── Moncton
            │   ├── Monterrey
            │   ├── Montevideo
            │   ├── Montreal
            │   ├── Montserrat
            │   ├── Nassau
            │   ├── New_York
            │   ├── Nipigon
            │   ├── Nome
            │   ├── Noronha
            │   ├── North_Dakota
            │   │   ├── Beulah
            │   │   ├── Center
            │   │   └── New_Salem
            │   ├── Nuuk
            │   ├── Ojinaga
            │   ├── Panama
            │   ├── Pangnirtung
            │   ├── Paramaribo
            │   ├── Phoenix
            │   ├── Port-au-Prince
            │   ├── Porto_Acre
            │   ├── Port_of_Spain
            │   ├── Porto_Velho
            │   ├── Puerto_Rico
            │   ├── Punta_Arenas
            │   ├── Rainy_River
            │   ├── Rankin_Inlet
            │   ├── Recife
            │   ├── Regina
            │   ├── Resolute
            │   ├── Rio_Branco
            │   ├── Rosario
            │   ├── Santa_Isabel
            │   ├── Santarem
            │   ├── Santiago
            │   ├── Santo_Domingo
            │   ├── Sao_Paulo
            │   ├── Scoresbysund
            │   ├── Shiprock
            │   ├── Sitka
            │   ├── St_Barthelemy
            │   ├── St_Johns
            │   ├── St_Kitts
            │   ├── St_Lucia
            │   ├── St_Thomas
            │   ├── St_Vincent
            │   ├── Swift_Current
            │   ├── Tegucigalpa
            │   ├── Thule
            │   ├── Thunder_Bay
            │   ├── Tijuana
            │   ├── Toronto
            │   ├── Tortola
            │   ├── Vancouver
            │   ├── Virgin
            │   ├── Whitehorse
            │   ├── Winnipeg
            │   ├── Yakutat
            │   └── Yellowknife
            ├── Antarctica
            │   ├── Casey
            │   ├── Davis
            │   ├── DumontDUrville
            │   ├── Macquarie
            │   ├── Mawson
            │   ├── McMurdo
            │   ├── Palmer
            │   ├── Rothera
            │   ├── South_Pole
            │   ├── Syowa
            │   ├── Troll
            │   └── Vostok
            ├── Arctic
            │   └── Longyearbyen
            ├── Asia
            │   ├── Aden
            │   ├── Almaty
            │   ├── Amman
            │   ├── Anadyr
            │   ├── Aqtau
            │   ├── Aqtobe
            │   ├── Ashgabat
            │   ├── Ashkhabad
            │   ├── Atyrau
            │   ├── Baghdad
            │   ├── Bahrain
            │   ├── Baku
            │   ├── Bangkok
            │   ├── Barnaul
            │   ├── Beirut
            │   ├── Bishkek
            │   ├── Brunei
            │   ├── Calcutta
            │   ├── Chita
            │   ├── Choibalsan
            │   ├── Chongqing
            │   ├── Chungking
            │   ├── Colombo
            │   ├── Dacca
            │   ├── Damascus
            │   ├── Dhaka
            │   ├── Dili
            │   ├── Dubai
            │   ├── Dushanbe
            │   ├── Famagusta
            │   ├── Gaza
            │   ├── Harbin
            │   ├── Hebron
            │   ├── Ho_Chi_Minh
            │   ├── Hong_Kong
            │   ├── Hovd
            │   ├── Irkutsk
            │   ├── Istanbul
            │   ├── Jakarta
            │   ├── Jayapura
            │   ├── Jerusalem
            │   ├── Kabul
            │   ├── Kamchatka
            │   ├── Karachi
            │   ├── Kashgar
            │   ├── Kathmandu
            │   ├── Katmandu
            │   ├── Khandyga
            │   ├── Kolkata
            │   ├── Krasnoyarsk
            │   ├── Kuala_Lumpur
            │   ├── Kuching
            │   ├── Kuwait
            │   ├── Macao
            │   ├── Macau
            │   ├── Magadan
            │   ├── Makassar
            │   ├── Manila
            │   ├── Muscat
            │   ├── Nicosia
            │   ├── Novokuznetsk
            │   ├── Novosibirsk
            │   ├── Omsk
            │   ├── Oral
            │   ├── Phnom_Penh
            │   ├── Pontianak
            │   ├── Pyongyang
            │   ├── Qatar
            │   ├── Qostanay
            │   ├── Qyzylorda
            │   ├── Rangoon
            │   ├── Riyadh
            │   ├── Saigon
            │   ├── Sakhalin
            │   ├── Samarkand
            │   ├── Seoul
            │   ├── Shanghai
            │   ├── Singapore
            │   ├── Srednekolymsk
            │   ├── Taipei
            │   ├── Tashkent
            │   ├── Tbilisi
            │   ├── Tehran
            │   ├── Tel_Aviv
            │   ├── Thimbu
            │   ├── Thimphu
            │   ├── Tokyo
            │   ├── Tomsk
            │   ├── Ujung_Pandang
            │   ├── Ulaanbaatar
            │   ├── Ulan_Bator
            │   ├── Urumqi
            │   ├── Ust-Nera
            │   ├── Vientiane
            │   ├── Vladivostok
            │   ├── Yakutsk
            │   ├── Yangon
            │   ├── Yekaterinburg
            │   └── Yerevan
            ├── Atlantic
            │   ├── Azores
            │   ├── Bermuda
            │   ├── Canary
            │   ├── Cape_Verde
            │   ├── Faeroe
            │   ├── Faroe
            │   ├── Jan_Mayen
            │   ├── Madeira
            │   ├── Reykjavik
            │   ├── South_Georgia
            │   ├── Stanley
            │   └── St_Helena
            ├── Australia
            │   ├── ACT
            │   ├── Adelaide
            │   ├── Brisbane
            │   ├── Broken_Hill
            │   ├── Canberra
            │   ├── Currie
            │   ├── Darwin
            │   ├── Eucla
            │   ├── Hobart
            │   ├── LHI
            │   ├── Lindeman
            │   ├── Lord_Howe
            │   ├── Melbourne
            │   ├── North
            │   ├── NSW
            │   ├── Perth
            │   ├── Queensland
            │   ├── South
            │   ├── Sydney
            │   ├── Tasmania
            │   ├── Victoria
            │   ├── West
            │   └── Yancowinna
            ├── Brazil
            │   ├── Acre
            │   ├── DeNoronha
            │   ├── East
            │   └── West
            ├── Canada
            │   ├── Atlantic
            │   ├── Central
            │   ├── Eastern
            │   ├── Mountain
            │   ├── Newfoundland
            │   ├── Pacific
            │   ├── Saskatchewan
            │   └── Yukon
            ├── CET
            ├── Chile
            │   ├── Continental
            │   └── EasterIsland
            ├── CST6CDT
            ├── Cuba
            ├── EET
            ├── Egypt
            ├── Eire
            ├── EST
            ├── EST5EDT
            ├── Etc
            │   ├── GMT
            │   ├── GMT+0
            │   ├── GMT-0
            │   ├── GMT0
            │   ├── GMT+1
            │   ├── GMT-1
            │   ├── GMT+10
            │   ├── GMT-10
            │   ├── GMT+11
            │   ├── GMT-11
            │   ├── GMT+12
            │   ├── GMT-12
            │   ├── GMT-13
            │   ├── GMT-14
            │   ├── GMT+2
            │   ├── GMT-2
            │   ├── GMT+3
            │   ├── GMT-3
            │   ├── GMT+4
            │   ├── GMT-4
            │   ├── GMT+5
            │   ├── GMT-5
            │   ├── GMT+6
            │   ├── GMT-6
            │   ├── GMT+7
            │   ├── GMT-7
            │   ├── GMT+8
            │   ├── GMT-8
            │   ├── GMT+9
            │   ├── GMT-9
            │   ├── Greenwich
            │   ├── UCT
            │   ├── Universal
            │   ├── UTC
            │   └── Zulu
            ├── Europe
            │   ├── Amsterdam
            │   ├── Andorra
            │   ├── Astrakhan
            │   ├── Athens
            │   ├── Belfast
            │   ├── Belgrade
            │   ├── Berlin
            │   ├── Bratislava
            │   ├── Brussels
            │   ├── Bucharest
            │   ├── Budapest
            │   ├── Busingen
            │   ├── Chisinau
            │   ├── Copenhagen
            │   ├── Dublin
            │   ├── Gibraltar
            │   ├── Guernsey
            │   ├── Helsinki
            │   ├── Isle_of_Man
            │   ├── Istanbul
            │   ├── Jersey
            │   ├── Kaliningrad
            │   ├── Kiev
            │   ├── Kirov
            │   ├── Lisbon
            │   ├── Ljubljana
            │   ├── London
            │   ├── Luxembourg
            │   ├── Madrid
            │   ├── Malta
            │   ├── Mariehamn
            │   ├── Minsk
            │   ├── Monaco
            │   ├── Moscow
            │   ├── Nicosia
            │   ├── Oslo
            │   ├── Paris
            │   ├── Podgorica
            │   ├── Prague
            │   ├── Riga
            │   ├── Rome
            │   ├── Samara
            │   ├── San_Marino
            │   ├── Sarajevo
            │   ├── Saratov
            │   ├── Simferopol
            │   ├── Skopje
            │   ├── Sofia
            │   ├── Stockholm
            │   ├── Tallinn
            │   ├── Tirane
            │   ├── Tiraspol
            │   ├── Ulyanovsk
            │   ├── Uzhgorod
            │   ├── Vaduz
            │   ├── Vatican
            │   ├── Vienna
            │   ├── Vilnius
            │   ├── Volgograd
            │   ├── Warsaw
            │   ├── Zagreb
            │   ├── Zaporozhye
            │   └── Zurich
            ├── Factory
            ├── GB
            ├── GB-Eire
            ├── GMT
            ├── GMT+0
            ├── GMT-0
            ├── GMT0
            ├── Greenwich
            ├── Hongkong
            ├── HST
            ├── Iceland
            ├── Indian
            │   ├── Antananarivo
            │   ├── Chagos
            │   ├── Christmas
            │   ├── Cocos
            │   ├── Comoro
            │   ├── Kerguelen
            │   ├── Mahe
            │   ├── Maldives
            │   ├── Mauritius
            │   ├── Mayotte
            │   └── Reunion
            ├── Iran
            ├── iso3166.tab
            ├── Israel
            ├── Jamaica
            ├── Japan
            ├── Kwajalein
            ├── leap-seconds.list
            ├── Libya
            ├── MET
            ├── Mexico
            │   ├── BajaNorte
            │   ├── BajaSur
            │   └── General
            ├── MST
            ├── MST7MDT
            ├── Navajo
            ├── NZ
            ├── NZ-CHAT
            ├── Pacific
            │   ├── Apia
            │   ├── Auckland
            │   ├── Bougainville
            │   ├── Chatham
            │   ├── Chuuk
            │   ├── Easter
            │   ├── Efate
            │   ├── Enderbury
            │   ├── Fakaofo
            │   ├── Fiji
            │   ├── Funafuti
            │   ├── Galapagos
            │   ├── Gambier
            │   ├── Guadalcanal
            │   ├── Guam
            │   ├── Honolulu
            │   ├── Johnston
            │   ├── Kiritimati
            │   ├── Kosrae
            │   ├── Kwajalein
            │   ├── Majuro
            │   ├── Marquesas
            │   ├── Midway
            │   ├── Nauru
            │   ├── Niue
            │   ├── Norfolk
            │   ├── Noumea
            │   ├── Pago_Pago
            │   ├── Palau
            │   ├── Pitcairn
            │   ├── Pohnpei
            │   ├── Ponape
            │   ├── Port_Moresby
            │   ├── Rarotonga
            │   ├── Saipan
            │   ├── Samoa
            │   ├── Tahiti
            │   ├── Tarawa
            │   ├── Tongatapu
            │   ├── Truk
            │   ├── Wake
            │   ├── Wallis
            │   └── Yap
            ├── Poland
            ├── Portugal
            ├── PRC
            ├── PST8PDT
            ├── ROC
            ├── ROK
            ├── Singapore
            ├── Turkey
            ├── UCT
            ├── Universal
            ├── US
            │   ├── Alaska
            │   ├── Aleutian
            │   ├── Arizona
            │   ├── Central
            │   ├── Eastern
            │   ├── East-Indiana
            │   ├── Hawaii
            │   ├── Indiana-Starke
            │   ├── Michigan
            │   ├── Mountain
            │   ├── Pacific
            │   └── Samoa
            ├── UTC
            ├── WET
            ├── W-SU
            ├── zone1970.tab
            ├── zone.tab
            └── Zulu```
</details>

---

### 003-settings.xzm (Init Scripts & Configuration)

Contains the custom init system, rc.d scripts, kiosk scripts, and configuration files.

```
/tmp/tmp.O7x0keuVBb/003-settings
├── bin
│   ├── bash -> busybox
│   └── sh -> busybox
├── dev
├── etc
│   ├── acpi
│   │   ├── default.sh
│   │   └── events
│   │       └── default
│   ├── dhcpcd.conf
│   ├── group
│   ├── gtk-2.0
│   │   └── gtkrc
│   ├── gtk-3.0
│   │   └── settings.ini
│   ├── inittab
│   ├── issue
│   ├── ld.so.conf
│   ├── localtime-copied-from -> /usr/share/zoneinfo/Factory
│   ├── logrotate.d
│   │   └── rsyslog
│   ├── machine-id
│   ├── mtab -> /proc/self/mounts
│   ├── nsswitch.conf
│   ├── opt
│   │   └── chrome
│   │       └── policies
│   │           └── managed
│   │               └── chrome.json
│   ├── passwd
│   ├── profile
│   ├── profile.d
│   │   ├── lang.sh
│   │   ├── mc.sh
│   │   ├── proxy.sh
│   │   ├── terminal.sh
│   │   └── variables.sh
│   ├── rc.d
│   │   ├── local_cli.d
│   │   │   └── cli_commands
│   │   ├── local_gui.d
│   │   │   └── gui_commands
│   │   ├── local_net.d
│   │   │   └── net_commands
│   │   ├── local_shutdown.d
│   │   │   └── shutdown_commands
│   │   ├── rc.0 -> rc.6
│   │   ├── rc.4
│   │   ├── rc.6
│   │   ├── rc.FireWall
│   │   ├── rc.inet1
│   │   ├── rc.M
│   │   ├── rc.S
│   │   ├── rc.sound
│   │   ├── rc.sshd
│   │   ├── rc.stunnel
│   │   └── rc.vncd
│   ├── rsyslog.conf
│   ├── rsyslog.d
│   │   └── 50-default.conf
│   ├── shadow
│   ├── shells
│   ├── ssl
│   │   └── certs
│   │       ├── 1fd23638.0 -> kiosk.pem
│   │       ├── kiosk.pem
│   │       └── stunnel.pem
│   ├── terminfo
│   │   ├── a
│   │   │   └── ansi
│   │   ├── d
│   │   │   └── dumb
│   │   ├── l
│   │   │   └── linux
│   │   ├── r
│   │   │   ├── rxvt
│   │   │   └── rxvt-unicode
│   │   ├── s
│   │   │   ├── screen
│   │   │   ├── screen-256color
│   │   │   └── screen.xterm-256color -> screen-256color
│   │   ├── v
│   │   │   ├── vt100
│   │   │   ├── vt102
│   │   │   ├── vt200 -> vt220
│   │   │   ├── vt220
│   │   │   └── vt52
│   │   └── x
│   │       ├── xterm
│   │       ├── xterm-256color
│   │       └── xterm-color
│   ├── wvdial.conf
│   ├── X11
│   │   ├── 11-fbdev.conf
│   │   ├── 11-modesetting.conf
│   │   ├── 11-vesa.conf
│   │   ├── xinit
│   │   │   └── xinitrc
│   │   └── xorg.conf.d
│   │       ├── 10-xorg.conf
│   │       └── 20-intel.conf
│   └── xdg
│       ├── openbox
│       │   ├── autostart
│       │   ├── rc.xml
│       │   └── rc.xml-new
│       └── tint2
│           ├── tint2-buttons
│           ├── tint2rc
│           └── tint2rc-exit
├── home
│   └── guest
├── lib64
│   └── udev
│       └── rules.d
│           └── 10-kiosk-auto_mount.rules
├── media
├── mnt
├── opt
│   ├── google
│   │   └── chrome
│   │       ├── chrome-flags.conf
│   │       └── master_preferences
│   └── scripts
│       ├── battery_polling
│       ├── capture-watch
│       ├── debug
│       ├── exit-kiosk
│       ├── exit-menu
│       ├── files
│       │   ├── bookmarks.html.tmp
│       │   ├── Bookmarks.tmp
│       │   ├── GRUB
│       │   │   ├── bootia32.efi
│       │   │   ├── boot.img
│       │   │   ├── bootx64.efi
│       │   │   ├── core.img
│       │   │   ├── grub.cfg
│       │   │   └── startup.nsh
│       │   ├── screensaverURL
│       │   ├── search.json.mozlz4
│       │   ├── shutdown-menu
│       │   ├── slideshow
│       │   ├── unknownContentType.xul
│       │   ├── videoshow
│       │   └── wizard
│       │       ├── keyboards.txt
│       │       ├── license-AdobeFlash.txt
│       │       ├── license-CitrixReceiver.txt
│       │       ├── license-GoogleChrome.txt
│       │       ├── printers.d
│       │       │   ├── bematech
│       │       │   ├── bixolon
│       │       │   ├── cups
│       │       │   ├── dymo-cups-drivers
│       │       │   ├── foomatic
│       │       │   ├── gutenprint
│       │       │   ├── hplip
│       │       │   ├── pnm2ppa
│       │       │   ├── sato
│       │       │   ├── splix
│       │       │   ├── star
│       │       │   ├── xerox-drivers
│       │       │   └── zebra
│       │       ├── timezones.txt
│       │       ├── tooltip-freeze.txt
│       │       ├── tooltip-mem.txt
│       │       ├── tooltip-standby.txt
│       │       └── wizard-functions
│       ├── freeze-idle-watcher
│       ├── gui-app
│       ├── gui-app.old
│       ├── import-certificates
│       ├── kbd-layout-switcher
│       ├── managed-bookmarks
│       ├── persistence
│       ├── pkget
│       ├── power_saver
│       ├── print-test
│       ├── rotate-touch
│       ├── rtc-wake
│       ├── scale-screen
│       ├── scheduled-action
│       ├── screensaver-idle-watcher
│       ├── screensaver-slideshow
│       ├── screen-setup
│       ├── screen-setup-parse
│       ├── session-idle-watcher
│       ├── session-manager
│       ├── set-kbd-layout
│       ├── set-resolution-rate
│       ├── set-system-clock
│       ├── shutdown-idle-watcher
│       ├── standby-idle-watcher
│       ├── start-mon
│       ├── start-panel
│       ├── suspend-idle-watcher
│       ├── watch-xorg
│       ├── welcome
│       ├── wizard-now
│       └── xvkbd
├── proc
├── root
├── run
│   ├── cups
│   │   └── certs
│   ├── dbus
│   ├── lock
│   └── stunnel
├── sbin
│   ├── shutdown
│   ├── telinit -> init
│   └── udev-automount-disabled
├── sys
├── tmp
├── usr
│   ├── bin
│   │   ├── chrome
│   │   ├── ed -> editor
│   │   ├── editor
│   │   ├── firefox
│   │   ├── lsusb -> usb-devices
│   │   ├── mime-open
│   │   ├── nano -> editor
│   │   ├── pico -> editor
│   │   ├── pkget -> /opt/scripts/pkget
│   │   ├── startx
│   │   ├── vi -> editor
│   │   ├── vim -> editor
│   │   └── xdm
│   ├── lib64
│   │   ├── dri
│   │   │   └── i915_dri.so -> i965_dri.so
│   │   ├── firefox
│   │   │   ├── browser
│   │   │   │   ├── chrome
│   │   │   │   ├── extensions
│   │   │   │   │   └── displayinline@samlh.net.xpi
│   │   │   │   ├── icons
│   │   │   │   ├── plugins -> /usr/lib/nsbrowser/plugins
│   │   │   │   └── searchplugins
│   │   │   └── content
│   │   │       └── unknownContentType.xul
│   │   └── terminfo -> /etc/terminfo/
│   ├── sbin
│   │   └── pktunnel
│   └── share
│       ├── applications
│       │   ├── back.desktop
│       │   ├── close.desktop
│       │   ├── forward.desktop
│       │   ├── home.desktop
│       │   ├── print.desktop
│       │   ├── refresh.desktop
│       │   ├── removable.desktop
│       │   ├── show-desktop.desktop
│       │   ├── zoom-in.desktop
│       │   └── zoom-out.desktop
│       ├── dbus-1
│       │   └── services
│       │       └── org.knopwob.dunst.service
│       ├── dunst
│       │   └── dunstrc
│       ├── glib-2.0
│       │   └── schemas
│       │       └── gschemas.compiled
│       ├── icons
│       │   └── oxygen
│       │       ├── 16x16/...
│       │       ├── 22x22/...
│       │       ├── 32x32/...
│       │       ├── 48x48/...
│       │       └── index.theme
│       ├── mime
│       │   ├── mime.cache
│       │   └── packages
│       │       └── kiosk.xml
│       ├── pixmaps
│       │   ├── [various kiosk icons - 48px, 160px variants]
│       │   ├── default/
│       │   ├── large/cursors/...
│       │   └── win8/cursors/...
│       ├── screensaver
│       ├── sounds
│       │   └── alert.wav
│       ├── terminfo -> /etc/terminfo/
│       ├── themes
│       │   └── oxygen-gtk
│       │       └── gtk-2.0
│       │           └── oxygenrc
│       ├── wallpapers
│       └── X11
│           └── xorg.conf.d
│               └── 50-synaptics.conf
│   └── tmp -> /var/tmp
└── var
    ├── cache
    │   ├── fontconfig
    │   └── ldconfig
    ├── empty
    │   └── dev
    ├── lib
    │   ├── alsa
    │   ├── dhcpcd
    │   ├── misc
    │   └── xkb
    ├── lock -> /run/lock
    ├── log
    │   ├── faillog
    │   ├── lastlog
    │   └── wtmp
    ├── run -> /run
    ├── spool
    │   ├── cron
    │   │   ├── crontabs
    │   │   └── lastrun
    │   └── rsyslog
    └── tmp
```

---


### 004-wifi.xzm (Wireless Networking)

Contains wireless tools, wpa_supplicant, USB modem switching, and related libraries.

```
/tmp/tmp.O7x0keuVBb/004-wifi
├── etc
│   ├── libnl
│   │   ├── classid
│   │   └── pktloc
│   ├── modprobe.d
│   │   └── ppp.conf
│   ├── ppp
│   │   ├── chap-secrets.example
│   │   ├── ip-down
│   │   ├── ip-down.d
│   │   │   ├── 30-wins.sh
│   │   │   ├── 40-dns.sh
│   │   │   └── 50-initd.sh
│   │   ├── ip-up
│   │   ├── ip-up.d
│   │   │   ├── 30-wins.sh
│   │   │   ├── 40-dns.sh
│   │   │   └── 50-initd.sh
│   │   ├── options
│   │   ├── pap-secrets.example
│   │   └── peers
│   │       ├── wvdial
│   │       └── wvdial-pipe
│   ├── uniconf.conf
│   ├── usb_modeswitch.conf
│   └── wireless-regdb
│       └── pubkeys
│           └── sforshee.key.pub.pem
├── lib64
│   ├── firmware
│   │   ├── regulatory.db
│   │   └── regulatory.db.p7s
│   ├── libiw.so -> libiw.so.30
│   ├── libiw.so.30
│   └── udev
│       ├── rules.d
│       │   ├── 40-usb_modeswitch.rules
│       │   └── 85-regulatory.rules
│       └── usb_modeswitch
├── sbin
│   ├── iwconfig
│   └── iwlist
├── usr
│   ├── bin
│   │   ├── jimsh
│   │   ├── wpa_passphrase
│   │   ├── wvdial
│   │   └── wvdialconf
│   ├── lib64
│   │   ├── crda
│   │   │   └── regulatory.bin
│   │   ├── libjim.so -> libjim.so.0.78
│   │   ├── libjim.so.0.78
│   │   ├── libnl-3.so -> libnl-3.so.200.26.0
│   │   ├── libnl-3.so.200 -> libnl-3.so.200.26.0
│   │   ├── libnl-3.so.200.26.0
│   │   ├── libnl-genl-3.so -> libnl-genl-3.so.200.26.0
│   │   ├── libnl-genl-3.so.200 -> libnl-genl-3.so.200.26.0
│   │   ├── libnl-genl-3.so.200.26.0
│   │   ├── libreg.so
│   │   ├── libuniconf.so -> libuniconf.so.4.6
│   │   ├── libuniconf.so.4.6
│   │   ├── libwvbase.so -> libwvbase.so.4.6
│   │   ├── libwvbase.so.4.6
│   │   ├── libwvdbus.so -> libwvdbus.so.4.6
│   │   ├── libwvdbus.so.4.6
│   │   ├── libwvstreams.so -> libwvstreams.so.4.6
│   │   ├── libwvstreams.so.4.6
│   │   ├── libwvutils.so -> libwvutils.so.4.6
│   │   ├── libwvutils.so.4.6
│   │   ├── pppd
│   │   │   └── 2.4.8
│   │   │       ├── dhcpc.so
│   │   │       ├── minconn.so
│   │   │       ├── openl2tp.so
│   │   │       ├── passprompt.so
│   │   │       ├── passwordfd.so
│   │   │       ├── pppol2tp.so
│   │   │       ├── rp-pppoe.so
│   │   │       └── winbind.so
│   │   └── valgrind
│   │       └── wvstreams.supp
│   ├── sbin
│   │   ├── chat
│   │   ├── crda
│   │   ├── iw
│   │   ├── plog
│   │   ├── poff
│   │   ├── pon
│   │   ├── pppd
│   │   ├── pppdump
│   │   ├── pppgetpass
│   │   ├── pppoe-discovery
│   │   ├── pppstats
│   │   ├── regdbdump
│   │   ├── rfkill
│   │   ├── uniconfd
│   │   ├── usb_modeswitch
│   │   ├── usb_modeswitch_dispatcher
│   │   └── wpa_supplicant
│   └── share
│       └── usb_modeswitch
│           └── [USB modem config files - 400+ device configs]
└── var
    └── lib
        ├── uniconf
        │   └── uniconfd.ini
        └── usb_modeswitch
```

---

### 06-fonts.xzm (Fonts)

Contains font files for internationalization support.

```
/tmp/tmp.O7x0keuVBb/06-fonts
├── etc
│   └── fonts
│       └── conf.avail
│           ├── 43-wqy-zenhei-sharp.conf
│           ├── 44-wqy-zenhei.conf
│           └── 60-liberation.conf
└── usr
    └── share
        ├── doc
        │   └── corefonts-1-r7
        │       └── license.txt
        └── fonts
            ├── corefonts        - Microsoft core fonts (Arial, Times, etc.)
            │   └── [31 TTF files]
            ├── dejavu           - DejaVu font family
            │   └── [17 TTF files]
            ├── liberation-fonts - Liberation fonts (metric-compatible)
            │   └── [12 TTF files]
            ├── libertine        - Linux Libertine fonts
            │   └── [26 OTF/TTF files]
            ├── noto             - Google Noto fonts (international)
            │   └── [200+ TTF files for various scripts]
            └── wqy-zenhei       - WenQuanYi Chinese fonts
                └── wqy-zenhei.ttc
```

---

### 08-ssh.xzm (SSH)

OpenSSH client and server components.

```
/tmp/tmp.O7x0keuVBb/08-ssh
├── etc
│   └── ssh
│       ├── moduli
│       ├── ssh_config
│       └── sshd_config
└── usr
    ├── bin
    │   ├── scp
    │   ├── sftp
    │   ├── ssh
    │   ├── ssh-add
    │   ├── ssh-agent
    │   ├── ssh-copy-id
    │   ├── ssh-keygen
    │   └── ssh-keyscan
    ├── lib64
    │   └── misc
    │       ├── sftp-server
    │       ├── ssh-keysign
    │       ├── ssh-pkcs11-helper
    │       └── ssh-sk-helper
    └── sbin
        └── sshd
```

---

### 09-x11vnc.xzm (VNC Server)

X11VNC for remote desktop access.

```
/tmp/tmp.O7x0keuVBb/09-x11vnc
├── root
└── usr
    ├── bin
    │   └── x11vnc
    └── lib64
        ├── libvncclient.so -> libvncclient.so.1
        ├── libvncclient.so.0.9.13
        ├── libvncclient.so.1 -> libvncclient.so.0.9.13
        ├── libvncserver.so -> libvncserver.so.1
        ├── libvncserver.so.0.9.13
        └── libvncserver.so.1 -> libvncserver.so.0.9.13
```

---

### firmware.xzm (Broadcom Firmware)

Broadcom/BCM wireless chip firmware for WiFi support.

```
/tmp/tmp.O7x0keuVBb/firmware
└── lib64
    └── firmware
        └── brcm
            ├── bcm4329-fullmac-4.bin
            ├── BCM43341B0.hcd
            ├── bcm43xx-0.fw
            ├── bcm43xx_hdr-0.fw
            ├── brcmfmac43143.bin
            ├── brcmfmac43143-sdio.bin
            ├── brcmfmac43236b.bin
            ├── brcmfmac43241b0-sdio.bin
            ├── brcmfmac43241b4-sdio.bin
            ├── brcmfmac43241b4-sdio.txt
            ├── brcmfmac43241b5-sdio.bin
            ├── brcmfmac43242a.bin
            ├── brcmfmac4329-sdio.bin
            ├── brcmfmac4330-sdio.bin
            ├── brcmfmac4330-sdio.txt
            ├── brcmfmac43340-sdio.bin
            ├── brcmfmac43340-sdio.txt
            ├── brcmfmac4334-sdio.bin
            ├── brcmfmac4335-sdio.bin
            ├── brcmfmac43362-sdio.bin
            ├── brcmfmac4339-sdio.bin
            ├── brcmfmac43430a0-sdio.bin
            ├── brcmfmac43430-sdio.bin
            ├── brcmfmac43430-sdio.txt
            ├── brcmfmac43455-sdio.bin    <- RPi 3B+/4 WiFi
            ├── brcmfmac43455-sdio.txt
            ├── brcmfmac4350c2-pcie.bin
            ├── brcmfmac4350-pcie.bin
            ├── brcmfmac4354-sdio.bin
            ├── brcmfmac43569.bin
            ├── brcmfmac4356-pcie.bin
            ├── brcmfmac4356-sdio.bin
            ├── brcmfmac43570-pcie.bin
            ├── brcmfmac4358-pcie.bin
            ├── brcmfmac43602-pcie.ap.bin
            ├── brcmfmac43602-pcie.bin
            ├── brcmfmac4366b-pcie.bin
            ├── brcmfmac4371-pcie.bin
            └── brcmfmac4373-sdio.bin
```

---

### NextWindow-5.10.25.xzm (Touchscreen Driver)

NextWindow touchscreen driver module and utilities.

```
/tmp/tmp.O7x0keuVBb/NextWindow
├── etc
│   ├── rc.d
│   │   └── local_net.d
│   │       └── nvfermi.sh
│   └── udev
│       └── rules.d
│           └── 40-nw-fermi.rules
├── lib32                              <- 32-bit compatibility libs
│   ├── ld-2.23.so
│   ├── ld-linux.so.2 -> ld-2.23.so
│   ├── libc-2.23.so
│   ├── libc.so.6 -> libc-2.23.so
│   ├── libm-2.23.so
│   ├── libm.so.6 -> libm-2.23.so
│   ├── libpthread-2.23.so
│   └── libpthread.so.0 -> libpthread-2.23.so
├── lib64
│   ├── ld-linux.so.2 -> ../lib32/ld-linux.so.2
│   └── modules
│       └── 5.10.25-kiosk
│           └── misc
│               └── nw-fermi.ko        <- Kernel module
└── usr
    ├── lib64
    │   └── xorg
    │       └── modules
    │           └── input
    │               └── nextwindow_drv.so
    ├── sbin
    │   └── nwfermi_daemon
    └── share
        └── X11
            └── xorg.conf.d
                └── 70-nw-fermi.conf
```

---

### zz-settings.xzm (Override Settings)

Late-loaded override module for daemon and wizard scripts. Loaded last (alphabetically) to override other modules.

```
/tmp/tmp.O7x0keuVBb/zz-settings
├── etc
│   └── rc.d
│       └── local_net.d
│           └── daemon.sh            <- Remote config polling daemon
└── opt
    └── scripts
        ├── files
        │   └── greyos_reboot
        ├── welcome                  <- Network configuration wizard
        ├── wizard                   <- Device configuration wizard
        └── wizard-now               <- Wizard launcher
```

---

## XZM Directory (Module Files)

```
xzm/
├── 000-kernel.xzm           51M   Kernel modules & firmware
├── 001-core.xzm             64M   Core system binaries & libraries
├── 003-settings.xzm         1.2M  Init scripts & kiosk configuration
├── 004-wifi.xzm             1.6M  Wireless networking support
├── 06-fonts.xzm             34M   International font support
├── 08-ssh.xzm               1.4M  OpenSSH client/server
├── 09-x11vnc.xzm            620K  VNC remote desktop
├── firmware.xzm             8.0M  Broadcom WiFi firmware
├── NextWindow-5.10.25.xzm   940K  Touchscreen driver (x86)
├── uefi.zip                 296K  UEFI boot files
└── zz-settings.xzm          12K   Override scripts
```

---

## Key Observations

1. **Architecture:** This is an x86_64 system (kernel shows "x86 boot executable")

2. **Kernel Version:** 5.10.25-kiosk (custom build for kiosk use)

3. **OS Version:** TuxOS/Porteus Kiosk 5.2.0

4. **Module Load Order:** Modules load alphabetically:
   - 000-kernel (base)
   - 001-core (system)
   - 003-settings (config)
   - 004-wifi (networking)
   - 06-fonts (fonts)
   - 08-ssh (SSH)
   - 09-x11vnc (VNC)
   - firmware (device firmware)
   - NextWindow (touchscreen)
   - zz-settings (final overrides)

5. **Key Scripts for ARM64 Port:**
   - `/sbin/init` - Custom init (in 003-settings)
   - `/etc/rc.d/rc.S` - System initialization
   - `/etc/rc.d/rc.4` - X11 startup
   - `/opt/scripts/welcome` - Network wizard
   - `/opt/scripts/wizard` - Device wizard
   - `/etc/rc.d/local_net.d/daemon.sh` - Config polling

6. **x86-Specific Components:**
   - NextWindow touchscreen driver (x86 kernel module)
   - Intel DRI drivers (i915, i965)
   - 32-bit compatibility libraries in NextWindow module

