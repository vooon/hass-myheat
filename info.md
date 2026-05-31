[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

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

{% if not installed %}

## Installation

1. Click install.
2. Restart Home Assistant.
3. Go to **Settings** -> **Devices & services** -> **Add integration**.
4. Search for **MyHeat.net**.

{% endif %}

## Configuration

YAML configuration is not supported. Add and manage the integration from the
Home Assistant UI.

During setup, enter your MyHeat username, API key from `https://my.myheat.net`,
the controller to add, and a Home Assistant display name.

Only one config entry can be created for the same MyHeat controller.

## Optional Local API

The integration can use the controller's local web API as a fallback/enrichment
source and for supported local write operations. Configure it from the
integration's **Options** flow.

Local API options include host, protocol (`http` or `https`), local UI
username/password, request timeout, and local poll interval. Cloud polling runs
every 30 seconds; local polling defaults to 10 seconds.

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
[commits-shield]: https://img.shields.io/github/commit-activity/y/vooon/hass-myheat.svg?style=for-the-badge
[commits]: https://github.com/vooon/hass-myheat/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license]: https://github.com/vooon/hass-myheat/blob/main/LICENSE
[license-shield]: https://img.shields.io/github/license/vooon/hass-myheat.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40vooon-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/vooon/hass-myheat.svg?style=for-the-badge
[releases]: https://github.com/vooon/hass-myheat/releases
[user_profile]: https://github.com/vooon
