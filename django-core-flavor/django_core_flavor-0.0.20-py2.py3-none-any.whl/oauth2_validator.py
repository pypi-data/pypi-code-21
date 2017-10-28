from oauth2_provider.oauth2_validators import OAuth2Validator


class OAuth2RequestValidator(OAuth2Validator):

    def validate_grant_type(self, *args, **kwargs):
        return True
