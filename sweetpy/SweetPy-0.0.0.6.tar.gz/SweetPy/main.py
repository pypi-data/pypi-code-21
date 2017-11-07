from rest_framework import response
import response_plus
response.Response = response_plus.Response
from rest_framework import mixins
import mixins_plus
mixins.ListModelMixin = mixins_plus.ListModelMixin
mixins.RetrieveModelMixin = mixins_plus.RetrieveModelMixin
mixins.DestroyModelMixin = mixins_plus.DestroyModelMixin
mixins.CreateModelMixin = mixins_plus.CreateModelMixin
from rest_framework import views
import view_plus
views.exception_handler = view_plus.exception_handler
import swagger_plus