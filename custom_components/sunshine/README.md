# Sunshine Scooter Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=zanooda&repository=sunshine-homeassistant&category=integration)

This custom component integrates Sunshine scooters with Home Assistant, providing full control and monitoring capabilities.

## Features

### Entities Created per Scooter

#### Device Tracker
- **Location**: GPS tracking with map visualization
- Shows scooter location on Home Assistant map
- Enables zone-based automations

#### Sensors
- **Battery Level**: Current battery percentage
- **Speed**: Current speed in km/h
- **Odometer**: Total distance traveled in km
- **Status**: Current scooter status

#### Switch
- **Lock**: Lock/unlock the scooter

#### Select Controls
- **Blinkers**: Control turn signals (off, left, right, both)
- **Play Sound**: Play various sounds (alarm, chirp, find_me)

#### Buttons
- **Honk**: Activate horn
- **Locate**: Find your scooter
- **Ping**: Check connectivity
- **Make Noise**: Alternative noise function
- **Open Seatbox**: Open storage compartment
- **Request Telemetry**: Get fresh data
- **Update Firmware**: Initiate firmware update
- **Alarm (5s)**: Quick 5-second alarm

### Services

The integration provides these services:

- `sunshine.trigger_alarm`: Trigger alarm with custom duration
- `sunshine.request_telemetry`: Request fresh telemetry data
- `sunshine.update_firmware`: Initiate firmware update

## Installation

### Option 1: HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=zanooda&repository=sunshine-homeassistant&category=integration)

1. Click the button above to add this repository to HACS
2. Or manually add the repository:
   - Open HACS in Home Assistant
   - Go to "Integrations"
   - Click the three dots menu → "Custom repositories"
   - Add `https://github.com/zanooda/sunshine-homeassistant` as an Integration
3. Search for "Sunshine Scooter" in HACS
4. Click "Download"
5. Restart Home Assistant
6. Go to Settings → Devices & Services → Add Integration
7. Search for "Sunshine Scooter"
8. Enter your API token (get from https://rescoot.org/account#new_token_form)

### Option 2: Manual Installation

1. Copy the `custom_components/sunshine` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Sunshine Scooter"
5. Enter your API token (get from https://rescoot.org/account#new_token_form)

## Configuration

The integration is configured through the UI. You'll need:
- **API Token**: Your Sunshine API bearer token
- **Base URL** (optional): Default is https://rescoot.org

## Architecture Improvements

This integration implements several best practices:

1. **Centralized Data Coordinator**: Uses `DataUpdateCoordinator` to fetch data once for all entities, preventing N+1 API calls
2. **Native Device Tracking**: Implements `DeviceTrackerEntity` for proper GPS visualization
3. **Smart Entity Selection**: Uses `SelectEntity` for mutually exclusive options (blinkers, sounds)
4. **Service Flexibility**: Custom services accept duration parameters for alarms

## Example Automations

### Zone-based Locking
```yaml
automation:
  - alias: "Auto-lock scooter when leaving home"
    trigger:
      - platform: zone
        entity_id: device_tracker.scooter_vin_location
        zone: zone.home
        event: leave
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.scooter_vin_lock
```

### Low Battery Alert
```yaml
automation:
  - alias: "Low battery notification"
    trigger:
      - platform: numeric_state
        entity_id: sensor.scooter_vin_battery_level
        below: 20
    action:
      - service: notify.mobile_app
        data:
          message: "Scooter battery is low: {{ states('sensor.scooter_vin_battery_level') }}%"
```

## Development

The component uses:
- `aiohttp` for async HTTP requests
- Home Assistant's `DataUpdateCoordinator` for efficient polling
- Proper error handling and logging

All API endpoints from the sunshine.paw specification are implemented.