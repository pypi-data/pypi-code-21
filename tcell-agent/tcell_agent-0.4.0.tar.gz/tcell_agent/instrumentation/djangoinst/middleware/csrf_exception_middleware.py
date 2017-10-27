from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.instrumentation.manager import InstrumentationManager
from tcell_agent.appsensor.django import django_meta


def instrument_csrf_view_middleware():
    from django.middleware.csrf import CsrfViewMiddleware

    def _tcell_reject(_tcell_original_reject, self, request, reason):
        appsensor_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
        if appsensor_policy is not None:
            meta = django_meta(request)
            appsensor_policy.csrf_rejected(meta)

        return _tcell_original_reject(self, request, reason)

    InstrumentationManager.instrument(CsrfViewMiddleware, "_reject", _tcell_reject)
