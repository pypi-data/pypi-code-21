# aalam_common initializer
STATE_STARTED = 1
STATE_RESTARTED = 2
STATE_MIGRATE = 3
STATE_POST_MIGRATE = 4
STATE_VALIDATION = 5  # Called by the packager's validators


CALLBACK_ROUTES = "routes"
CALLBACK_CLEANUP = "cleanup"
CALLBACK_MIGRATE = "migrate"
CALLBACK_MIGRATE_COMPLETED = "migrate_completed"
