import json
from ..output import row_gen, output


def account(client, account=False, history=False, monitors=False,
            organization=False, quotas=None, sources=False, teamstream=False,
            **kwargs):
    rows = None
    if account:
        kwargs['rotate'] = not kwargs['rotate']
        headers = [
            "enterpriseUser", "admin", "jobRole",
            "searchApiQuotaExceeded", "searchWebQuotaExceeded",
            "projectPrivateQuotaExceeded", "projectPublicQuotaExceeded",
            "organization"
        ]
        strip = [
            "verified", "country", "event_code", "firstActive",
            "firstName", "fullName", "lastActive", "lastName",
            "phoneNumber", "stateOrRegion", "suppliedOrganization", "user_hash",
            "user_id", "username", "approvedSources"
        ]
        results = client.get_account().data
        rows = row_gen(
            [results],
            headers=headers,
            strip=strip,
            **kwargs
        )
    elif history:
        results = client.get_history().data
        rows = row_gen(
            results['history'],
            **kwargs
        )
    elif monitors:
        results = client.get_monitors().data
        rows = row_gen(
            results['monitors'],
            **kwargs
        )
    elif organization:
        kwargs['rotate'] = not kwargs['rotate']
        results = client.get_organization().data
        strip = [
            'inactiveMembers', 'activeMembers', 'admins'
        ]
        rows = row_gen(
            [results],
            strip=strip,
            **kwargs
        )
    elif quotas:
        kwargs['rotate'] = not kwargs['rotate']
        kwargs['order'] = kwargs['order'] or ['owner']
        results = client.get_quotas().data
        if quotas != 'both':
            results = {quotas: results[quotas]}
        rows = row_gen(
            [results[i] for i in results],
            **kwargs
        )
    elif sources:
        results = client.get_sources().data
        rows = row_gen(
            results["sources"],
            **kwargs
        )
    elif teamstream:
        results = client.get_teamstream().data
        rows = row_gen(
            results["teamstream"],
            **kwargs
        )

    if kwargs.get('json'):
        return json.dumps(results, indent=4)
    if rows:
        return output(list(rows), **kwargs)
    return None
