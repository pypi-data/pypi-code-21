from rest_framework import generics, permissions
from .models import NotificationReceipt
from .serializers import NotificationReceiptSerializer


class NotificationReceiptListCreateView(generics.ListAPIView):
    serializer_class = NotificationReceiptSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):
        NotificationReceipt.objects.filter(user=self.request.user)
