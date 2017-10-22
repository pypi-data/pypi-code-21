# -*- coding: utf-8 -*-

from flask import current_app as app, g, abort


def get_restricted_resources(app):

    ''' Retrieve the list of the restricted
        resources (that have eve_rights restriction fields)

            >>> app = Eve()
            >>> app.register_rights()
            >>> get_restricted_resources(app)
            ['people', 'project']
            >>>

        :param app The eve application to retrieve the config

        :returns the restricted resources string list (eg. ['people', 'project'])
    '''

    resources = []
    domain = app.config['DOMAIN']
    for res in domain:
        schema = domain.get(res, {}).get('schema', {})
        if app.config['ACL_FIELDS_READ'] in schema and app.config['ACL_FIELDS_WRITE'] in schema:
            resources.append(res)
    return resources


def on_list(resource, request, lookup):

    ''' Hook called when a user try to list a resource
        Here, we need to check is the current user id is
        in the w_reads user array .

            >>> app.on_pre_GET += on_list

        :param resource The resource being listed
        :param request The flask request
        :param lookup The request made to the database (to tamper)
    '''

    resources = get_restricted_resources(app)
    if resource in resources:
        user_id = g.auth_value
        lookup[app.config['ACL_FIELDS_READ']] = user_id


def on_delete(resource, item):

    ''' Hook called when an item will be deleted

            >>> app.on_delete_item += on_delete

        :param resource The resource associated to the item
        :param item The item thats will be deleted
    '''

    resources = get_restricted_resources(app)
    if resource in resources:
        user_id = g.auth_value
        if user_id not in item.get(app.config['ACL_FIELDS_WRITE'], []):
            abort(403)  # The user don't have access to this item


def init_document_with_acl(resource, items):

    ''' Set the fields w_writes and w_reads accordinally
        to the user who inserting documents.

            >>> app.on_insert += init_document_with_acl

        :param resource The resource in which the documents are inserted
        :param items The items that will be inserted
    '''

    resources = get_restricted_resources(app)
    if resource in resources:
        # The resource have to be protected
        user_id = g.auth_value
        for item in items:
            item[app.config['ACL_FIELDS_READ']] = [user_id]
            item[app.config['ACL_FIELDS_WRITE']] = [user_id]


def on_update(resource, updates, original):

    ''' Hook called when a user try to update a update an item
 
            >>> app.on_update += on_update

        :param resource The resource where the item being tamper is
        :param updates The changes being made on the item
        :param original ?
    '''

    resources = get_restricted_resources(app)
    if resource in resources:
        user_id = g.auth_value
        if user_id not in original.get(app.config['ACL_FIELDS_WRITE'], {}):
            abort(403)
