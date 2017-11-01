"""
hudai.resources.person
"""
from ..helpers.resource import Resource


class OrganizationResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/organizations')
        self.resource_name = 'Organization'

    def list(self, name=None, email_domain=None, signup_key=None, page=None):
        return self._list(name=name,
                          email_domain=email_domain,
                          signup_key=signup_key,
                          page=page)

    def create(self,
               name=None,
               email_domain=None,
               max_billable_accounts=None,
               signed_license_agreement_at=None):
        return self._create(name=name,
                            email_domain=email_domain,
                            max_billable_accounts=max_billable_accounts,
                            signed_license_agreement_at=signed_license_agreement_at)

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def update(self, entity_id,
               name=None,
               email_domain=None,
               max_billable_accounts=None,
               signed_license_agreement_at=None):
        return self._update(entity_id,
                            name=name,
                            email_domain=email_domain,
                            max_billable_accounts=max_billable_accounts,
                            signed_license_agreement_at=signed_license_agreement_at)

    def delete(self, entity_id):
        return self._delete(entity_id)
