from rest_framework import response
import SweetPy.response_plus

response.Response = SweetPy.response_plus.Response
from rest_framework import mixins
import SweetPy.mixins_plus

mixins.ListModelMixin = SweetPy.mixins_plus.ListModelMixin
mixins.RetrieveModelMixin = SweetPy.mixins_plus.RetrieveModelMixin
mixins.DestroyModelMixin = SweetPy.mixins_plus.DestroyModelMixin
mixins.CreateModelMixin = SweetPy.mixins_plus.CreateModelMixin
from rest_framework import views
import SweetPy.view_plus

views.exception_handler = SweetPy.view_plus.exception_handler
import SweetPy.swagger_plus
import SweetPy.setting