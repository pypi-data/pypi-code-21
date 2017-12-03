import flask


class Stub:
    def __init__(self, users, return_uri="/"):
        """
        users: the users to display on the login page. The list contains tuples
            where the elements are the user name and the avatar size.
        """
        self.users = users
        self.return_uri = return_uri

    def create(self, auth_blueprint):
        pass

    def _generate_avatar_uri(self, user_id):
        return "https://s.pelicandd.com/avatars/{user_id}-{size}.jpg".format(
            user_id=user_id,
            size=240
        )

    def login(self):
        user = flask.session.get("user")
        html_users = ""
        for user_name in self.users:
            user_id = user_name.lower().replace(" ", ".")
            additional_attributes = \
                ' class="current"' if user == user_id else ""

            html_users += """
    <a href="/authorized?u={user_id}"{additional_attributes}>
        <img src="{avatar_uri}" alt="">
        <span>{user_name}</span>
    </a>""".format(
                user_id=user_id,
                user_name=user_name,
                avatar_uri=self._generate_avatar_uri(user_id),
                additional_attributes=additional_attributes)

        css = """
@import url(http://fonts.googleapis.com/css?family=Lato:400);
body{font:400 1em Lato;margin:10em auto;width:65%;}
h1{font:400 2em Lato;}
#users a{
    color:inherit;float:left;margin:1em 2em 1em 0;text-align:center;
    text-decoration:none;
}
#users img{height:90px;width:90px;}
#users span{display:block;}
"""
        html = """<!DOCTYPE html>
<meta charset="utf-8">
<style type="text/css">{css}</style>
<title>Login</title>
<h1>Login</h1>
<p>
    The application is configured to use the sample authentication mechanism.
    This makes it possible to showcase the application in offline mode without
    using Google's OAuth2 provider or a similar service.
</p>
<p>
    In order to authenticate, pick the user of your choice. You can logoff
    later to switch to a different user.
</p>
<div id="users">{users}
</div>
""".format(css=css, users=html_users)
        return flask.Response(html, mimetype="text/html")

    def logout(self):
        flask.session.pop("user")
        return flask.redirect(self.return_uri, code=302)

    def authorized(self, onauthorizing):
        user_id = flask.request.args.get("u")
        user_info = {
            "source": {
                "name": "stub",
                "version": 1
            },
            "id": user_id,
            "name": user_id.replace(".", " ").title(),
            "picture": self._generate_avatar_uri(user_id)
        }

        if onauthorizing:
            custom_response = onauthorizing(user_info)
            if custom_response:
                return custom_response

        flask.session["user"] = user_info
        return flask.redirect(self.return_uri, code=302)
