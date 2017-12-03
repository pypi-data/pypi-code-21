class AuditToLog:
    def __init__(self, log_handler):
        self._log = log_handler

    def user_verified(self, user_name, is_success):
        if is_success:
            self._log.info("Access granted for user %s." % (user_name,))
        else:
            self._log.warn("Access denied for user %s." % (user_name,))

    def restricted_node_accessed(self, user_name, path, is_granted):
        if is_granted:
            self._log.info(
                "The user %s is authorized to access %s." % (user_name, path)
            )
        else:
            self._log.warn(
                "The user %s is denied to access %s." % (user_name, path)
            )
