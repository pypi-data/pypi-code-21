import flask
import types


def raise_error_if_no_static_folders_are_defined(app):
    if app.static_folder is None:
        if app.static_folders is None:
            raise RuntimeError("There's no static folder for this object")


def send_static_file(self, filename):
    raise_error_if_no_static_folders_are_defined(self)

    #  cache_timeout is needed for Blueprints
    cache_timeout = self.get_send_file_max_age(filename)

    if self.static_folders:
        for static_folder in self.static_folders:
            try:
                return flask.helpers.send_from_directory(static_folder, filename, cache_timeout=cache_timeout)
            except:
                continue
        raise RuntimeError('Static file not found')
    else:
        return flask.helpers.send_from_directory(self.static_folder, filename, cache_timeout=cache_timeout)


def remove_app_old_static_endpoint(app):
    del app.view_functions['static']


def modify_send_static_file_function(app):
    app.send_static_file = types.MethodType(send_static_file, app)


def add_app_modified_static_endpoint(app):
    app.add_url_rule(app.static_url_path + '/<path:filename>',
                      endpoint='static',
                      view_func=app.send_static_file)


def transform_from_single_static_to_multiple_static_app(app):
    remove_app_old_static_endpoint(app)
    modify_send_static_file_function(app)
    add_app_modified_static_endpoint(app)

    return app


def app_already_has_static_folders(app):
    return hasattr(app, 'static_folders')


def transform_app(app):
    if app_already_has_static_folders(app):
        return app
    return transform_from_single_static_to_multiple_static_app(app)
