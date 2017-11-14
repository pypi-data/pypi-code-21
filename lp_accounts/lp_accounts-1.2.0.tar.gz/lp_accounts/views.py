from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from templated_email import send_templated_mail
from .serializers import AccountSerializer, PasswordResetSerializer, PasswordUpdateSerializer, AuthTokenSerializer
from .models import User
from rest_condition import Or
from .permissions import IsAnonUser


class AccountCreate(generics.CreateAPIView):
    model = User
    serializer_class = AccountSerializer
    permission_classes = [
        Or(IsAnonUser, permissions.IsAdminUser)
    ]

    def perform_create(self, serializer):
        instance = serializer.save()
        Token.objects.get_or_create(user=instance)


class AccountDetails(generics.RetrieveAPIView):
    model = User
    serializer_class = AccountSerializer
    queryset = User.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_object(self):
        return self.request.user


class AccountUpdate(generics.UpdateAPIView):
    model = User
    serializer_class = AccountSerializer
    queryset = User.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.get('partial', False)
        instance = self.get_object()

        account_data = request.data.pop('account', None)
        if account_data:
            account = instance.account
            account_serializer_class = self.get_serializer().get_account_serializer(account_data).__class__
            account_serializer = account_serializer_class(account, data=account_data, partial=partial)
            account_serializer.is_valid(raise_exception=True)
            self.perform_update(account_serializer)

        return super(AccountUpdate, self).update(request, *args, **kwargs)


class PasswordReset(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = {
        IsAnonUser
    }

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token, created = Token.objects.get_or_create(user=serializer.user)
        send_templated_mail(
            template_name=settings.LP_ACCOUNTS_PASSWORD_RESET_TEMPLATE,
            from_email=settings.LP_ACCOUNTS_PASSWORD_RESET_SENDER,
            recipient_list=[request.data['email']],
            context={
                'username': serializer.user.username,
                'full_name': serializer.user.get_full_name(),
                'signup_date': serializer.user.date_joined,
                'token': token.key,
            },
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordUpdate(generics.GenericAPIView):
    model = User
    serializer_class = PasswordUpdateSerializer
    queryset = User.objects.all()
    permission_classes = [
        IsAnonUser
    ]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.user.set_password(request.data['password'])
        serializer.user.save()

        return Response(status=status.HTTP_200_OK)


class ObtainAuthToken(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    permission_classes = [
        IsAnonUser
    ]
