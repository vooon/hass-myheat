"""Constants for MyHeat tests."""

from custom_components.myheat.const import (
    CONF_API_KEY,
    CONF_DEVICE_ID,
    CONF_NAME,
    CONF_USERNAME,
)

MOCK_CONFIG = {
    CONF_USERNAME: "test_username",
    CONF_API_KEY: "test_password",
    CONF_NAME: "test",
    CONF_DEVICE_ID: 12,
}


# Use data from api pdf
MOCK_GET_DEVICES = {
    "data": {
        "devices": [
            {
                "id": 12,
                "name": "У Моста",
                "city": "Новошешминск",
                "severity": 1,
                "severityDesc": "Система работает нормально.",
            },
            {
                "id": 10,
                "name": "Хорошее место",
                "city": "Новошешминск",
                "severity": 1,
                "severityDesc": "Система работает нормально.",
            },
        ]
    },
    "err": 0,
    "refreshPage": False,
}

MOCK_GET_DEVICE_INFO = {
    "data": {
        "heaters": [
            {
                "id": 13,
                "name": "Vaillant правый",
                "disabled": False,
                "flowTemp": 56,
                "returnTemp": 56,
                "pressure": 2.223,
                "targetTemp": 0,
                "burnerHeating": False,
                "burnerWater": False,
                "modulation": 0,
            },
            {
                "id": 37,
                "name": "Vaillant левый",
                "disabled": False,
                "flowTemp": 56,
                "returnTemp": 57,
                "pressure": 2.436,
                "targetTemp": 0,
                "burnerHeating": False,
                "burnerWater": False,
                "modulation": 0,
            },
        ],
        "envs": [
            {
                "id": 21,
                "type": "boiler_temperature",
                "name": "Бойлер",
                "value": 46.687,
                "target": 45,
                "demand": False,
                "severity": 1,
                "severityDesc": "Нормальное состояние.",
            },
            {
                "id": 22,
                "type": "room_temperature",
                "name": "Кафе",
                "value": 24.812,
                "target": 23,
                "demand": False,
                "severity": 1,
                "severityDesc": "Нормальное состояние.",
            },
            {
                "id": 24,
                "type": "circuit_temperature",
                "name": "Контур отопления",
                "value": 56,
                "target": None,
                "demand": False,
                "severity": 1,
                "severityDesc": "Нормальное состояние.",
            },
            {
                "id": 23,
                "type": "room_temperature",
                "name": "Магазин",
                "value": 24.187,
                "target": 23,
                "demand": False,
                "severity": 1,
                "severityDesc": "Нормальное состояние.",
            },
            {
                "id": 20,
                "type": "room_temperature",
                "name": "Бухгалтерия",
                "value": 29.812,
                "target": None,
                "demand": False,
                "severity": 1,
                "severityDesc": "Нормальное состояние.",
            },
            {
                "id": 19,
                "type": "room_temperature",
                "name": "Котельная",
                "value": 27.25,
                "target": None,
                "demand": False,
                "severity": 1,
                "severityDesc": "Нормальное состояние.",
            },
        ],
        "engs": [
            {
                "id": 40,
                "type": "pump",
                "name": "Насос магазин",
                "turnedOn": False,
                "severity": 1,
                "severityDesc": "Насос работает исправно.",
            },
            {
                "id": 41,
                "type": "pump",
                "name": "Насос бойлер",
                "turnedOn": False,
                "severity": 1,
                "severityDesc": "Насос работает исправно.",
            },
            {
                "id": 38,
                "type": "pump",
                "name": "Насос кафе",
                "turnedOn": False,
                "severity": 1,
                "severityDesc": "Насос работает исправно.",
            },
            {
                "id": 39,
                "type": "pump",
                "name": "Насос бухгалтерия",
                "turnedOn": False,
                "severity": 1,
                "severityDesc": "Насос работает исправно.",
            },
        ],
        "alarms": {},
        "dataActual": True,
        "severity": 1,
        "severityDesc": "Система работает нормально.",
        "weatherTemp": "-6.78999999999996",
        "city": "Новошешминск",
    },
    "err": 0,
    "refreshPage": False,
}

MOCK_NO_ERR = {"err": 0, "refreshPage": False}
