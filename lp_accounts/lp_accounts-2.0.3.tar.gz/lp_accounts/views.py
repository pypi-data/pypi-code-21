from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from templated_email import send_templated_mail
from .serializers import AccountSerializer, PasswordResetSerializer, PasswordUpdateSerializer
from .models import User


class AccountCreate(generics.CreateAPIView):
    model = User
    serializer_class = AccountSerializer
    permission_classes = (permissions.AllowAny,)


class AccountDetails(generics.RetrieveAPIView):
    model = User
    serializer_class = AccountSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class AccountUpdate(generics.UpdateAPIView):
    model = User
    serializer_class = AccountSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

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
            if not instance.account:
                instance.account = account_serializer.Meta.model.objects.create(**account_data)
            self.perform_update(account_serializer)

        return super(AccountUpdate, self).update(request, *args, **kwargs)


class PasswordReset(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = (permissions.AllowAny,)
    token_generator = PasswordResetTokenGenerator()

    def post(self, request):
        # Ensure this is a valid request
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data['email']

        # Retrieve User and generate token
        user = User.objects.get(email=email)
        token = self.token_generator.make_token(user)

        # Send Email
        send_templated_mail(
            template_name=settings.LP_ACCOUNTS_PASSWORD_RESET_TEMPLATE,
            from_email=settings.LP_ACCOUNTS_PASSWORD_RESET_SENDER,
            recipient_list=[user.email],
            context={
                'username': user.username,
                'token': token,
            },
        )

        return Response(status=status.HTTP_200_OK)


class PasswordUpdate(generics.GenericAPIView):
    model = User
    serializer_class = PasswordUpdateSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    token_generator = PasswordResetTokenGenerator()

    def post(self, request):
        # Ensure this is a valid request
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data['email']
        password = serializer.data['password']
        token = serializer.data['token']

        # Retrieve User and validate token
        user = User.objects.get(email=email)
        is_valid_token = self.token_generator.check_token(user, token)

        if not is_valid_token:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='Invalid Token')

        user.set_password(password)
        user.save()

        return Response(status=status.HTTP_200_OK)
