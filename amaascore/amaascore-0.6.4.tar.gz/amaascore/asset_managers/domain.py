from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.core.amaas_model import AMaaSModel

class Domain(AMaaSModel):

    def __init__(self, asset_manager_id, domain, is_primary=True, domain_status='Active',
                 *args, **kwargs):
        self.asset_manager_id = asset_manager_id
        self.domain = domain
        self.is_primary = is_primary
        self.domain_status = domain_status
        super(Domain, self).__init__(*args, **kwargs)
