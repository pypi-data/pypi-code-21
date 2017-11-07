from django.views import View
from django.http.response import JsonResponse
import psutil


class StatsView(View):
    def get(self, request):
        """
        Returns statistics about a system
        """
        virtual_memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return JsonResponse({
            'CPUPercent': psutil.cpu_percent(percpu=True),
            'virtualMemoryUsage': '{0:.2f}%'.format(virtual_memory.percent),
            'totalMemoryUsage': '{0:.2f}%'.format((virtual_memory.used + swap.used) / (swap.total + virtual_memory.total) * 100),
            'freeMemory': '{0:.0f} MB'.format((virtual_memory.free + swap.free) / 1000000)
        })
