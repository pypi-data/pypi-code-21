
class Implementation:
    _impl = None

    def __init__(self, cls):
        self._cls = cls

    def	__getattr__(self, name):
        return getattr(self._impl, name)

    def set_implementation(self, impl):
        assert issubclass(impl.__class__, self._cls)
        self._impl = impl


class Injector:
    """
    This will serve as a dependency injector system as a singleton
    """
    _IMPLEMENTATIONS_REGISTERED = []
    _IMPLEMENTATIONS_REQUESTED = []

    @staticmethod
    def _resolve_and_inject_dependencies():
        provided = []

        for request in Injector._IMPLEMENTATIONS_REQUESTED:
            if request in provided:
                continue

            for implementation in Injector._IMPLEMENTATIONS_REGISTERED:
                if request["interface_cls"] == implementation["interface_cls"]:
                    obj = implementation["instance"]
                    request["implementation"].set_implementation(obj)
                    provided.append(request)
                    break

        for request in provided:
            Injector._IMPLEMENTATIONS_REQUESTED.remove(request)

    def provide_implementation(self, interface_cls, instance):
        assert issubclass(instance.__class__, interface_cls)
        assert interface_cls not in [impl["interface_cls"] for impl in Injector._IMPLEMENTATIONS_REGISTERED]

        provide = {
            "interface_cls": interface_cls,
            "instance": instance
        }

        Injector._IMPLEMENTATIONS_REGISTERED.append(provide)
        Injector._resolve_and_inject_dependencies()

    def request_implementation(self, interface_cls):
        implementation = Implementation(interface_cls)

        request = {
            "interface_cls": interface_cls,
            "implementation": implementation
        }

        Injector._IMPLEMENTATIONS_REQUESTED.append(request)
        Injector._resolve_and_inject_dependencies()

        return implementation


injector = Injector()
