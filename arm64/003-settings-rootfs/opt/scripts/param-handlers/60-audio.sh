#!/bin/bash
# =============================================================================
# Parameter Handler: 60-audio.sh
# =============================================================================
# Handles: default_sound_card, default_microphone, volume_level
#
# To add a new parameter:
#   1. Add parameter check below
#   2. Test: echo "param=value" >> /opt/scripts/files/lcon && /opt/scripts/apply-config
# =============================================================================

# Source config if not already sourced
[ -z "$CONFIG" ] && CONFIG="/opt/scripts/files/lcon"
[ -f "$CONFIG" ] && source "$CONFIG"

log() { echo "[$(basename "$0")] $*" >> "${LOG_FILE:-/tmp/apply-config.log}"; }

# ----- Parameter: default_sound_card -----
# Description: Default audio output device
# Values: Device name or index (e.g., "hdmi", "analog", 0, 1)
if [ -n "$default_sound_card" ]; then
    log "Setting default sound card: $default_sound_card"

    # Using ALSA
    if command -v amixer >/dev/null 2>&1; then
        # List available cards
        cards=$(cat /proc/asound/cards 2>/dev/null)

        # Find card index by name or use directly if numeric
        if echo "$default_sound_card" | grep -qE '^[0-9]+$'; then
            card_index="$default_sound_card"
        else
            # Search for card by name (case insensitive)
            card_index=$(echo "$cards" | grep -i "$default_sound_card" | head -1 | awk '{print $1}')
        fi

        if [ -n "$card_index" ]; then
            # Set as default in ALSA
            mkdir -p /etc/asound.conf.d
            cat > /etc/asound.conf << EOF
# Default sound card from kiosk config
defaults.pcm.card $card_index
defaults.ctl.card $card_index
EOF
            log "Default sound card set to index: $card_index"
        else
            log "WARNING: Sound card not found: $default_sound_card"
        fi
    fi

    # Using PulseAudio
    if command -v pactl >/dev/null 2>&1; then
        # Get sink by name
        sink=$(pactl list short sinks 2>/dev/null | grep -i "$default_sound_card" | head -1 | cut -f1)
        if [ -n "$sink" ]; then
            pactl set-default-sink "$sink" 2>/dev/null && \
                log "PulseAudio default sink: $sink"
        fi
    fi
fi

# ----- Parameter: default_microphone -----
# Description: Default audio input device
# Values: Device name or index
if [ -n "$default_microphone" ]; then
    log "Setting default microphone: $default_microphone"

    # Using PulseAudio
    if command -v pactl >/dev/null 2>&1; then
        source=$(pactl list short sources 2>/dev/null | grep -i "$default_microphone" | head -1 | cut -f1)
        if [ -n "$source" ]; then
            pactl set-default-source "$source" 2>/dev/null && \
                log "PulseAudio default source: $source"
        fi
    fi

    # Using ALSA
    if command -v amixer >/dev/null 2>&1; then
        # Find capture device
        if echo "$default_microphone" | grep -qE '^[0-9]+$'; then
            mic_card="$default_microphone"
        else
            mic_card=$(cat /proc/asound/cards 2>/dev/null | grep -i "$default_microphone" | head -1 | awk '{print $1}')
        fi

        if [ -n "$mic_card" ]; then
            log "Default microphone set to card: $mic_card"
        fi
    fi
fi

# ----- Parameter: volume_level -----
# Description: Audio volume percentage
# Values: 0-100
if [ -n "$volume_level" ]; then
    log "Setting volume level: $volume_level%"

    # Validate volume range
    if [ "$volume_level" -lt 0 ] 2>/dev/null; then
        volume_level=0
    elif [ "$volume_level" -gt 100 ] 2>/dev/null; then
        volume_level=100
    fi

    # Using ALSA amixer
    if command -v amixer >/dev/null 2>&1; then
        # Try common control names
        for control in "Master" "PCM" "Speaker" "Headphone"; do
            amixer -q sset "$control" "${volume_level}%" 2>/dev/null && break
        done
        log "ALSA volume set to $volume_level%"
    fi

    # Using PulseAudio
    if command -v pactl >/dev/null 2>&1; then
        # Set volume on all sinks
        for sink in $(pactl list short sinks 2>/dev/null | cut -f1); do
            pactl set-sink-volume "$sink" "${volume_level}%" 2>/dev/null
        done
        log "PulseAudio volume set to $volume_level%"
    fi

    # Using ALSA directly via /dev
    if [ -d /dev/snd ] && command -v alsactl >/dev/null 2>&1; then
        alsactl store 2>/dev/null
    fi
fi

log "Audio handler completed"
