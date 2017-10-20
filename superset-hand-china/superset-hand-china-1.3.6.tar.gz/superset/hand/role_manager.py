from flask_appbuilder.security.sqla.manager import SecurityManager
from .role_views import (
    MyRoleViewModel, MyUserDBViewModel, MyUserStatsChartView,
    MyPermissionViewViewModel)

class MySecurityManager(SecurityManager):
    rolemodelview = MyRoleViewModel
    userdbmodelview = MyUserDBViewModel
    userstatschartview = MyUserStatsChartView
    permissionviewmodelview  = MyPermissionViewViewModel

