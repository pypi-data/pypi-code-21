#!/usr/bin/env python
# -*- coding: utf-8 -*-


class CacheSettings:
    def __init__(self, settings):
        try:
            cache_settings = settings.CACHE_HANDLER
            region_init_config = cache_settings['init_config']

            self.region_name = region_init_config['region_name']
            self.backend = region_init_config.get('backend')

            server_config = cache_settings['server_config']
            self.region_arguments = server_config.get('redis')

            ttl_config = cache_settings['ttl_config']
            self.absolute_ttl = ttl_config.get('absolute_ttl')
            self.credentials_ttl = ttl_config.get('credentials_ttl')
            self.authz_info_ttl = ttl_config.get('authz_info_ttl')
            self.session_abs_ttl = ttl_config.get('session_absolute_ttl')

        except (AttributeError, TypeError) as exc:
            msg = ('yosai_dpcache CacheSettings requires a LazySettings instance '
                   'with complete CACHE_HANDLER settings')
            raise exc.__class__(msg)
