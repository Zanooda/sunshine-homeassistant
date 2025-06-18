"""Constants for the Sunshine Scooter integration."""
from __future__ import annotations

DOMAIN = "sunshine"

CONF_BASE_URL = "base_url"
DEFAULT_BASE_URL = "https://rescoot.org"

ATTR_SCOOTER_ID = "scooter_id"
ATTR_VIN = "vin"
ATTR_DURATION = "duration"
ATTR_SOUND = "sound"
ATTR_STATE = "state"

SERVICE_TRIGGER_ALARM = "trigger_alarm"
SERVICE_PLAY_SOUND = "play_sound"
SERVICE_BLINKERS = "blinkers"
SERVICE_OPEN_SEATBOX = "open_seatbox"
SERVICE_UPDATE_FIRMWARE = "update_firmware"
SERVICE_REQUEST_TELEMETRY = "request_telemetry"

SOUND_ALARM = "alarm"
SOUND_CHIRP = "chirp"
SOUND_FIND_ME = "find_me"

BLINKER_LEFT = "left"
BLINKER_RIGHT = "right"
BLINKER_BOTH = "both"
BLINKER_OFF = "off"