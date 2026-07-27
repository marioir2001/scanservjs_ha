"""Constants for the ScanservJS integration."""

DOMAIN = "scanservjs"
PLATFORMS = ["button", "sensor"]

CONF_URL = "url"
CONF_VERIFY_SSL = "verify_ssl"
CONF_PROFILES = "profiles"
CONF_FILE_ACTION = "file_action"
CONF_SPLIT_PDF = "split_pdf"

SPLIT_PDF_ACTION = "split_pdf"

DEFAULT_VERIFY_SSL = True
DEFAULT_TIMEOUT = 300

STATUS_IDLE = "idle"
STATUS_SCANNING = "scanning"
STATUS_SUCCESS = "success"
STATUS_ERROR = "error"
