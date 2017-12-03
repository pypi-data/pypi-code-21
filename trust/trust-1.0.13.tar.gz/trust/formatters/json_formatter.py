import trust
import json


class JsonFormatter():
    def __init__(self, finder):
        self._finder = finder

    def process(self, query, credentials, optional=False):
        self._finder.access_as(credentials)

        try:
            return json.dumps({
                "result": self._finder.find(query, optional=optional)
            })
        except trust.exceptions.AuthenticationException:
            return self._generate_error_response([
                self._generate_error_object(
                    "credentials-invalid",
                    "Either the user name doesn't exist or the password " +
                    "is invalid."
                )
            ])
        except PermissionError:
            return self._generate_error_response([
                self._generate_error_object(
                    "permission-required",
                    "A permission is required to be able to access the " +
                    "requested element."
                )
            ])
        except trust.exceptions.NodeNotFoundException:
            return self._generate_error_response([
                self._generate_error_object(
                    "node-not-found",
                    "The specified node doesn't exist."
                )
            ])
        except trust.exceptions.CircularInheritanceException:
            return self._generate_error_response([
                self._generate_error_object(
                    "circular-inheritance",
                    "The data contains a circular inheritance."
                )
            ])

    def reject_invalid(self):
        return self._generate_error_response([
            self._generate_error_object(
                "query-invalid",
                "The query contains invalid characters or parts."
            )
        ])

    def _generate_error_object(self, error_type, description):
        return {
            "type": error_type,
            "uri": "http://services.pelicandd.com/trust/error/" + error_type,
            "description": description
        }

    def _generate_error_response(self, error_objects):
        return json.dumps({
            "errors": error_objects
        })
