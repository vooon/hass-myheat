"""Constants for MyHeat tests."""

from custom_components.myheat.const import (
    CONF_API_KEY,
    CONF_DEVICE_ID,
    CONF_NAME,
    CONF_USERNAME,
)

MOCK_USER_CONFIG = {
    CONF_USERNAME: "test_username",
    CONF_API_KEY: "test_password",
}
MOCK_DEVICE_CONFIG = {
    CONF_NAME: "test_device",
    CONF_DEVICE_ID: "12 - У Моста - Новошешминск",
}


MOCK_CONFIG = {}
MOCK_CONFIG.update(MOCK_USER_CONFIG)
MOCK_CONFIG.update(MOCK_DEVICE_CONFIG)
MOCK_CONFIG[CONF_DEVICE_ID] = 12

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
                "id": 25,
                "type": "floor_temperature",
                "name": "Теплый пол",
                "value": 26.5,
                "target": 27,
                "demand": True,
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
            {
                "id": 302,
                "type": "water_shutoff_valve",
                "name": "Кран перекрытия воды Neptune",
                "turnedOn": False,
                "mode": -1,
                "severity": 1,
                "severityDesc": "Дана команда на выключение.",
            },
            {
                "id": 1778385071,
                "type": "pump",
                "name": "Насос ГВС рециркуляции",
                "turnedOn": True,
                "mode": -1,
                "severity": 1,
                "severityDesc": "Дана команда на включение.",
            },
            {
                "id": 349,
                "type": "two_way_valve",
                "name": "Сервопривод 2этаж ТП Ванная",
                "turnedOn": False,
                "mode": -1,
                "severity": 1,
                "severityDesc": "Дана команда на закрытие.",
            },
            {
                "id": 149,
                "type": "three_way_valve",
                "name": "Клапан 3-ходовой Баня/Конвекторы",
                "turnedOn": True,
                "mode": -1,
                "severity": 1,
                "severityDesc": "Режим регулирования.",
            },
        ],
        "alarms": [
            {
                "id": 301,
                "type": "water_leakage",
                "name": "Протечка воды",
                "alarm": False,
                "severity": 1,
                "severityDesc": "Нормальное состояние.",
            },
            {
                "id": 1778385145,
                "type": "water_leakage",
                "name": "Протечка воды Котельная",
                "alarm": False,
                "severity": 1,
                "severityDesc": "Нормальное состояние.",
            },
        ],
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

MOCK_LOCAL_OBJ_STATE = {
    "deviceFlags": 24961,
    "deviceSeverity": 1,
    "simSignal": 71,
    "simBalance": 137.7,
    "envs": [
        {
            "n": "Room1",
            "i": 67,
            "t": 101,
            "f": 0,
            "sev": 1,
            "st": {
                "p1": 22.5,
                "p4": 1,
            },
            "s": {
                "p3008": "23.5",
                "p3022": "1",
                "p3026": "1",
                "p3049": "1",
                "p3012": "10",
                "p3011": "35",
            },
        },
        {
            "n": "Outdoor sensor",
            "i": 68,
            "t": 101,
            "f": 0,
            "sev": 1,
            "st": {
                "p1": -16777216,
            },
            "s": {
                "p3026": "0",
            },
        },
    ],
    "heaters": [
        {
            "n": "Boiler",
            "i": 45,
            "t": 303,
            "f": 2336,
            "sev": 1,
            "st": {
                "p100": 51,
                "p101": 41,
                "p109": 1.8,
            },
            "s": {
                "p3013": "0",
            },
        }
    ],
    "engs": [
        {
            "n": "Pump",
            "i": 123,
            "t": 302,
            "f": 0,
            "sev": 1,
            "st": {
                "p4": 0,
            },
            "s": {
                "p3008": "-16777216",
            },
        }
    ],
    "alarms": [
        {
            "n": "Leak",
            "i": 301,
            "t": 901,
            "f": 0,
            "sev": 1,
            "st": {
                "p1": 0,
            },
            "s": {},
        }
    ],
    "curves": [
        {
            "i": 1,
            "n": "Curve 1",
            "d": [-30, 49, -28, 48],
        }
    ],
    "hModes": [
        {
            "i": 1,
            "n": "Home",
        }
    ],
    "scheds": [
        {
            "i": 10,
            "n": "Week",
        }
    ],
}

MOCK_LOCAL_GET_STATE = {
    "status": 1,
    "inet": "1",
    "serial": "serial",
    "regkey": "sensitive",
    "wifiSsid": "wifi",
    "gsmCarrier": "carrier",
    "gsmRssi": "71",
    "gsmBalance": "137.70",
}
