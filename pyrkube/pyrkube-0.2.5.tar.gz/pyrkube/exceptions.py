class PyrKubeError(Exception):
    """Generic app-level exception."""

class KubeConfigNotFound(PyrKubeError, FileNotFoundError):
    """PyrKube was unable to detect any form of kubeconfig."""
    def __init__(self, message=None):
        if not message:
            message = "PyrKube was unable to detect any form of kubeconfig"
        PyrKubeError.__init__(self, message)
