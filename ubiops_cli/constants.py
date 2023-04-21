STRUCTURED_TYPE = 'structured'
PLAIN_TYPE = 'plain'
ML_MODEL_FILE_NAME_KEY = "ML_MODEL_FILE_NAME"
ML_MODEL_FILE_NAME_VALUE = "model"
SYS_DEPLOYMENT_FILE_NAME_KEY = "SYS_DEPLOYMENT_FILE_NAME"
SYS_DEPLOYMENT_FILE_NAME_VALUE = "deployment"

STATUS_UNAVAILABLE = 'unavailable'
SUCCESS_STATUSES = ['completed', 'available', 'success']
WARNING_STATUSES = ['queued', 'pending', 'processing', 'building', 'validating', 'deploying', 'running',
                    'confirmation', 'confirmation_pending']
ERROR_STATUSES = ['failed', 'cancelled_pending', 'cancelled']
DEFAULT_IGNORE_FILE = '.ubiops-ignore'
IMPLICIT_ENVIRONMENT_FILES = ['ubiops.yaml', 'requirements.txt', 'install_packages.R', 'environment.yaml']

UPDATE_TIME = 30  # seconds to wait between update and new zip upload
