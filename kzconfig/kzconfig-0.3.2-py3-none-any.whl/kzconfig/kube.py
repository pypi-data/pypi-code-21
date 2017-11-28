import pyrkube


class Kube:
    def __init__(self, context):
        self.context = context
        try:
            self.api = pyrkube.KubeAPIClient()
        except pyrkube.KubeConfigNotFound:
            pass
