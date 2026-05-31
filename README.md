# MyHeat.net

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

Custom Home Assistant integration for [MyHeat.net](https://myheat.net) heating
controllers.

The integration is configured from the Home Assistant UI. It polls the MyHeat
cloud API, creates Home Assistant entities for the selected controller, and can
optionally enrich/control supported devices through the controller's local LAN
API.

## Features

| Platform        | What is exposed                                                                                                                                                                                     |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `binary_sensor` | Controller data freshness, overall severity, alarm summary, individual alarms, per-environment and per-engineering severity, heater disabled/burner states, and engineering component on/off state. |
| `climate`       | Room and floor temperature environments with current temperature, target temperature, heat/off mode, heating action, and preset modes.                                                              |
| `sensor`        | Outdoor/weather temperature, heater flow/return/target temperatures, pressure, modulation, and optional local GSM RSSI/balance diagnostics.                                                         |
| `switch`        | Security alarm switch and local heater enable switches when local control is available.                                                                                                             |
| `water_heater`  | Non-room temperature environments such as boiler, DHW, and heating circuit temperatures with target temperature and on/off control.                                                                 |

Entity availability depends on the objects returned by your MyHeat controller.

## Installation

### HACS

[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=vooon&repository=hass-myheat&category=integration)

1. Open the repository in HACS and install it.
2. Restart Home Assistant.
3. Go to **Settings** -> **Devices & services** -> **Add integration**.
4. Search for **MyHeat.net**.

### Manual

1. Open your Home Assistant configuration directory, the one containing
   `configuration.yaml`.
2. Create `custom_components` if it does not already exist.
3. Copy this repository's `custom_components/myheat` directory to
   `custom_components/myheat` in your Home Assistant configuration directory.
4. Restart Home Assistant.
5. Go to **Settings** -> **Devices & services** -> **Add integration**.
6. Search for **MyHeat.net**.

The installed layout should look like this:

```text
custom_components/myheat/translations/*.json
custom_components/myheat/*.py
custom_components/myheat/manifest.json
```

## Configuration

YAML configuration is not supported. Add and manage the integration from the
Home Assistant UI.

During setup, enter:

- MyHeat username.
- API key from `https://my.myheat.net` user preferences.
- The controller to add, selected from devices returned by the MyHeat cloud API.
- A Home Assistant display name for the controller.

Only one config entry can be created for the same MyHeat controller.

## Optional Local API

The integration can use the controller's local web API as a fallback/enrichment
source and for supported local write operations. Configure it from the
integration's **Options** flow.

Local API options:

| Option              | Default      | Notes                                                  |
| ------------------- | ------------ | ------------------------------------------------------ |
| Enable local API    | disabled     | Turns on LAN polling and local writes where supported. |
| Host                | none         | Controller LAN hostname or IP address.                 |
| Protocol            | `http`       | `http` or `https`.                                     |
| Username/password   | none         | Credentials accepted by the controller local UI.       |
| Request timeout     | `15` seconds | Valid range: 1-60 seconds.                             |
| Local poll interval | `10` seconds | Valid range: 5-300 seconds.                            |

Cloud polling runs every 30 seconds. When local API is enabled, the coordinator
polls at the shorter of the cloud interval and configured local interval, while
the hybrid client separately caches cloud and local data according to their
respective intervals.

Supported local writes are used automatically when the local API is configured
and the requested object is available locally. Otherwise the integration falls
back to the cloud API where that operation is supported.

## Services

The integration registers these services under the `myheat` domain:

| Service                     | Purpose                                                         |
| --------------------------- | --------------------------------------------------------------- |
| `myheat.get_devices`        | Return controllers available for the configured MyHeat account. |
| `myheat.get_device_info`    | Return current state for the target controller.                 |
| `myheat.set_env_goal`       | Set or clear an environment target temperature.                 |
| `myheat.set_env_curve`      | Set an environment to use a heating curve.                      |
| `myheat.set_eng_goal`       | Set an engineering component goal/mode.                         |
| `myheat.set_heater_enabled` | Enable or disable a heater through the local API.               |
| `myheat.set_heating_mode`   | Select a heating mode or schedule.                              |
| `myheat.set_security_mode`  | Arm or disarm security mode.                                    |
| `myheat.refresh`            | Force a data coordinator refresh.                               |

Most services target a MyHeat entity. Some accept `alt_device_id` when you need
to call the cloud API for a different MyHeat device ID than the configured
controller.

## Development

This repository contains tests for the cloud API client, local API client,
config flow, setup, and entity platforms.

```bash
uv run pytest
```

The integration metadata currently targets Home Assistant `2026.5.0` or newer
for HACS installs.

## Contributions

Contributions are welcome. Please read the [contribution guidelines](CONTRIBUTING.md)
before opening a pull request.

## Credits

This project was originally generated from
[@oncleben31](https://github.com/oncleben31)'s
[Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component)
template.

The initial code template was mainly taken from
[@Ludeeus](https://github.com/ludeeus)'s
[integration_blueprint][integration_blueprint] template.

---

[integration_blueprint]: https://github.com/custom-components/integration_blueprint
[black]: https://github.com/psf/black
[black-shield]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/vooon/hass-myheat.svg?style=for-the-badge
[commits]: https://github.com/vooon/hass-myheat/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/vooon/hass-myheat.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40vooon-blue.svg?style=for-the-badge
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/vooon/hass-myheat.svg?style=for-the-badge
[releases]: https://github.com/vooon/hass-myheat/releases
[user_profile]: https://github.com/vooon
