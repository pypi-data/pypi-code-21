from ohm2_accounts_light import settings as ohm2_accounts_light_settings


FACEBOOK_LOGIN = getattr(ohm2_accounts_light_settings, "FACEBOOK_LOGIN", False)
GOOGLE_PLUS_LOGIN = getattr(ohm2_accounts_light_settings, "GOOGLE_PLUS_LOGIN", False)
ENABLE_SOCIAL_LOGIN = getattr(ohm2_accounts_light_settings, "ENABLE_SOCIAL_LOGIN")

INCLUDE_PATCHED_URLS = getattr(ohm2_accounts_light_settings, "INCLUDE_PATCHED_URLS")