"""Constants for the ScanservJS integration."""

DOMAIN = "scanservjs"
PLATFORMS = ["button", "sensor"]

CONF_URL = "url"
CONF_VERIFY_SSL = "verify_ssl"
CONF_PROFILES = "profiles"

DEFAULT_VERIFY_SSL = True
DEFAULT_TIMEOUT = 300

STATUS_IDLE = "idle"
STATUS_SCANNING = "scanning"
STATUS_SUCCESS = "success"
STATUS_ERROR = "error"
