[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

**This component will set up the following platforms.**

| Platform        | Description                         |
| --------------- | ----------------------------------- |
| `binary_sensor` | Show something `True` or `False`.   |
| `climate`       | Manage heating controller. |
| `sensor`        | Show info from API.                 |
| `switch`        | Switch something `True` or `False`. |

{% if not installed %}

## Installation

1. Click install.
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "MyHeat".

{% endif %}

## Configuration is done in the UI

<!---->

## Credits

This project was generated from [@oncleben31](https://github.com/oncleben31)'s [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component) template.

Code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint] template

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
