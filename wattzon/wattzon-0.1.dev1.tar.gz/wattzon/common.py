import os


def getenv(priority, envkey):
    if priority is not None:
        return priority
    return os.getenv(envkey)

