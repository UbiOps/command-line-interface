STRUCTURED_TYPE = 'structured'
ML_MODEL_FILE_NAME_KEY = "ML_MODEL_FILE_NAME"
ML_MODEL_FILE_NAME_VALUE = "model"
SYS_DEPLOYMENT_FILE_NAME_KEY = "SYS_DEPLOYMENT_FILE_NAME"
SYS_DEPLOYMENT_FILE_NAME_VALUE = "deployment"

STATUS_UNAVAILABLE = 'unavailable'
SUCCESS_STATUSES = ['completed', 'available', 'success']
WARNING_STATUSES = ['queued', 'pending', 'processing', 'building', 'validating', 'deploying', 'running']
ERROR_STATUSES = ['failed']
DEFAULT_IGNORE_FILE = '.ubiops-ignore'

UPDATE_TIME = 30  # seconds to wait between update and new zip upload
