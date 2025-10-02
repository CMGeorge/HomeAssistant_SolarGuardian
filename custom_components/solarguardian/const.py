"""Constants for the SolarGuardian integration."""

DOMAIN = "solarguardian"

# Configuration keys
CONF_APP_KEY = "app_key"
CONF_APP_SECRET = "app_secret"
CONF_DOMAIN = "domain"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_TEST_MODE = "test_mode"

# Default values
DEFAULT_UPDATE_INTERVAL = (
    15  # seconds - safe for most installations, respects 30 calls/minute API limit
)
DEFAULT_TIMEOUT = 30  # seconds

# API domains
DOMAIN_CHINA = "openapi.epsolarpv.com"
DOMAIN_INTERNATIONAL = "glapi.mysolarguardian.com"

# Device classes for sensors
DEVICE_CLASS_POWER = "power"
DEVICE_CLASS_VOLTAGE = "voltage"
DEVICE_CLASS_CURRENT = "current"
DEVICE_CLASS_ENERGY = "energy"
DEVICE_CLASS_TEMPERATURE = "temperature"
DEVICE_CLASS_BATTERY = "battery"

# Units
UNIT_WATT = "W"
UNIT_VOLT = "V"
UNIT_AMPERE = "A"
UNIT_KWH = "kWh"
UNIT_CELSIUS = "°C"
UNIT_PERCENT = "%"

# API endpoints
ENDPOINT_AUTH = "/epCloud/user/getAuthToken"
ENDPOINT_POWER_STATIONS = "/epCloud/vn/openApi/getPowerStationListPage"
ENDPOINT_DEVICES = "/epCloud/vn/openApi/getEquipmentList"
ENDPOINT_DEVICE_PARAMETERS = "/epCloud/vn/openApi/getEquipment"
ENDPOINT_DEVICE_HISTORY = "/epCloud/vn/openApi/getDataPoint"
ENDPOINT_LATEST_DATA = "/history/lastDatapoint"  # Different host:port - see API docs

# Special endpoint configuration for latest data (uses different host/port)
LATEST_DATA_PORT = 7002

# Rate limiting
RATE_LIMIT_AUTH = 10  # calls per minute
RATE_LIMIT_DATA = 30  # calls per minute

# Mock data for testing when API is unavailable
MOCK_POWER_STATION = {
    "id": 999999,
    "powerStationName": "Test Solar Station",
    "capacity": 5000,
    "location": "Test Location",
}

MOCK_DEVICE = {
    "id": 888888,
    "equipmentName": "Test Solar Inverter",
    "productName": "Mock Inverter Model",
    "version": "1.0.0",
}

MOCK_VARIABLE_GROUPS = [
    {
        "variableGroupNameE": "Power Parameters",
        "variableGroupNameC": "功率参数",
        "variableList": [
            {
                "dataIdentifier": "OutputPower",
                "variableNameE": "Output Power",
                "variableNameC": "输出功率",
                "unit": "W",
                "decimal": "0",
                "dataPointId": 101754260,
                "deviceNo": "2023021512345678900001",
            },
            {
                "dataIdentifier": "InputPower",
                "variableNameE": "Input Power",
                "variableNameC": "输入功率",
                "unit": "W",
                "decimal": "0",
                "dataPointId": 101754261,
                "deviceNo": "2023021512345678900001",
            },
            {
                "dataIdentifier": "loadpower",
                "variableNameE": "Load Power",
                "variableNameC": "负载功率",
                "unit": "W",
                "decimal": "0",
                "dataPointId": 101754262,
                "deviceNo": "2023021512345678900001",
            },
        ],
    },
    {
        "variableGroupNameE": "Voltage Parameters",
        "variableGroupNameC": "电压参数",
        "variableList": [
            {
                "dataIdentifier": "OutputVoltage",
                "variableNameE": "Output Voltage",
                "variableNameC": "输出电压",
                "unit": "V",
                "decimal": "1",
                "dataPointId": 101754263,
                "deviceNo": "2023021512345678900001",
            },
            {
                "dataIdentifier": "InputVoltage",
                "variableNameE": "Input Voltage",
                "variableNameC": "输入电压",
                "unit": "V",
                "decimal": "1",
                "dataPointId": 101754264,
                "deviceNo": "2023021512345678900001",
            },
            {
                "dataIdentifier": "BatteryVoltage",
                "variableNameE": "Battery Voltage",
                "variableNameC": "电池电压",
                "unit": "V",
                "decimal": "2",
                "dataPointId": 101754265,
                "deviceNo": "2023021512345678900001",
            },
        ],
    },
    {
        "variableGroupNameE": "Current Parameters",
        "variableGroupNameC": "电流参数",
        "variableList": [
            {
                "dataIdentifier": "OutputCurrent",
                "variableNameE": "Output Current",
                "variableNameC": "输出电流",
                "unit": "A",
                "decimal": "2",
                "dataPointId": 101754266,
                "deviceNo": "2023021512345678900001",
            },
            {
                "dataIdentifier": "InputCurrent",
                "variableNameE": "Input Current",
                "variableNameC": "输入电流",
                "unit": "A",
                "decimal": "2",
                "dataPointId": 101754267,
                "deviceNo": "2023021512345678900001",
            },
        ],
    },
]
