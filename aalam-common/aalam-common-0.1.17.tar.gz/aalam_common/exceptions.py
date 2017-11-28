
class MissingConfigParameter(Exception):
    def __init__(self, param, section="DEFAULT"):
        msg = "Error: Missing config parameter - " + section + "." + param
        super(MissingConfigParameter, self).__init__(msg)


class NotAQueryObject(Exception):
    def __init__(self, res):
        msg = "Method returned '%s', expected 'sqlalchemy.orm.query.Query" % \
            type(res)
        super(NotAQueryObject, self).__init__(msg)


class ExpectedRouteArgs(Exception):
    def __init__(self, args):
        msg = "Routeargs for the app should have '%s' argument" % str(args)
        super(ExpectedRouteArgs, self).__init__(msg)


class SQASessionsNotFlushed(Exception):
    def __init__(self):
        msg = "sqa_sessions should be flushed by the handler"
        super(SQASessionsNotFlushed, self).__init__(msg)


class DatabaseNotFound(Exception):
    def __init__(self, db_name):
        msg = "Database '%s' not found" % db_name
        super(DatabaseNotFound, self).__init__(msg)


class CreatePermissionsGroupFailed(Exception):
    def __init__(self, group_name, addn_msg):
        msg = "Unable to create permissions group %(name)s, because %(msg)s" \
            % {"name": group_name, "msg": addn_msg}
        super(CreatePermissionsGroupFailed, self).__init__(msg)


class CreatePermissionsFailed(Exception):
    def __init__(self, group_name, addn_msg):
        msg = "Unable to create permission for group %s, because %s" % \
            (group_name, addn_msg)
        super(CreatePermissionsFailed, self).__init__(msg)


class UnableToUpdateRoleCache(Exception):
    def __init__(self, group_name, status_code, addn_msg):
        msg = "Unable to create permission for group %s, because %d<%s>" % \
            (group_name, status_code, addn_msg)
        super(UnableToUpdateRoleCache, self).__init__(msg)


class InvalidPermissionFormat(ValueError):
    def __init__(self):
        msg = "Permission is wrongly formatted, should be pgroup::permission"
        super(InvalidPermissionFormat, self).__init__(msg)


class InvalidFilterField(KeyError):
    def __init__(self, field):
        msg = "Field %s not valid" % field
        super(InvalidFilterField, self).__init__(msg)


class AppLaunchFailed(Exception):
    def __init__(self, app_name, reason):
        msg = "Unable to launch application %s, because <%s>" % \
            (app_name, reason)
        super(AppLaunchFailed, self).__init__(msg)
