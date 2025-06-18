# Sunshine Scooter Integration

## Features

This integration provides complete control and monitoring of Sunshine scooters through Home Assistant.

### Supported Entities

- **Device Tracker** - Real-time GPS location on map
- **Sensors** - Battery level, speed, odometer, status
- **Switch** - Lock/unlock control
- **Select** - Blinkers and sound controls
- **Buttons** - Honk, locate, ping, seatbox, and more

### Services

- `sunshine.trigger_alarm` - Trigger alarm with custom duration
- `sunshine.request_telemetry` - Request fresh telemetry
- `sunshine.update_firmware` - Initiate firmware update

## Configuration

1. Get your API token from https://rescoot.org/account#new_token_form
2. Add the integration through Home Assistant UI
3. Enter your token when prompted

## Requirements

- Home Assistant 2024.1.0 or newer
- Active Sunshine account with API access
- Internet connection for cloud polling