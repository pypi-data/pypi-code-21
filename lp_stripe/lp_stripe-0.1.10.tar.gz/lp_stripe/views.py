from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .client import Client
from .models import Subscription, Customer
from .serializers import SubscriptionCreateSerializer, SubscriptionSerializer


class SubscriptionCreateView(generics.CreateAPIView):
    serializer_class = SubscriptionCreateSerializer
    queryset = Subscription.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def create(self, request, *args, **kwargs):
        source = request.data.get('source')
        plan = request.data.get('plan')
        user = self.request.user

        client = Client()
        try:
            stripe_customer = client.create_customer(description='Customer for %s' % user.username, source=source)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Could not create Stripe Customer: %s' % e})

        try:
            stripe_subscription = client.create_subscription(customer=stripe_customer['id'], plan=plan)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Could not create Stripe Subscription: %s' % e})

        customer = Customer.objects.create(user=user, stripe_id=stripe_customer['id'])
        subscription = Subscription.objects.create(customer=customer, stripe_id=stripe_subscription['id'], verbose_name=stripe_subscription['plan']['id'])

        return Response(status=status.HTTP_201_CREATED)


class SubscriptionRetrieveView(generics.RetrieveAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_object(self):
        return get_object_or_404(Subscription, customer__user=self.request.user)


class PlanListView(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        client = Client()
        return Response(status=status.HTTP_200_OK, data=client.plans())


class SubscriptionCancelView(generics.DestroyAPIView):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.cancel()
        return super(SubscriptionCancelView, self).destroy(request, *args, **kwargs)
