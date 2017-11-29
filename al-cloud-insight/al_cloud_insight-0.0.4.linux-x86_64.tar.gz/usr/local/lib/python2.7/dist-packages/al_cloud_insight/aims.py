import logging
import json
import requests
import simplejson

class AIMS(object):
    def __init__(self, parent):
        self.ci = parent.ci.aims(parent.version)
        self.account_id = parent.account_id

    def add_accessible_location_to_account(self, location, account_id=None):
        """Add accessible location to an account
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Account_Resources-AddAccessibleLocation
        /aims/v1/:account_id/account/accessible_locations/:location
        """
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).account.accessible_locations(location).PUT()
        if api_resp.status_code == requests.codes.ok:
            return True
        else:
            return api_resp

    def create_account(self, **data):
        """Create an account
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Account_Resources-CreateAccount
        /aims/v1/account"""
        api_resp = self.ci.account.POST(data=json.dumps(data))
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def create_account_relationship(self, relationship, related_account_id, account_id=None):
        """AIMS Account Resources - Create Account Relationship
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Account_Resources-CreateAccount
        /aims/v1/:account_id/accounts/:relationship/:related_account_id"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).accounts(relationship)(related_account_id).POST()
        if api_resp.status_code == requests.codes.ok:
            return True
        else:
            return api_resp

    def delete_account(self, account_id):
        """AIMS Account Resources - Delete Account
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Account_Resources-DeleteAccount
        /aims/v1/:account_id/account"""
        api_resp = self.ci(account_id).account.DELETE()
        if api_resp.status_code == requests.codes.ok:
            return True
        else:
            return api_resp

    def delete_account_relationship(self, relationship, related_account_id, account_id=None):
        """AIMS Account Resources - Delete Account Relationship
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Account_Resources-Delete_AccountRelationship
        /aims/v1/:account_id/accounts/:relationship/:related_account_id"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).accounts(relationship)(related_account_id).POST()
        if api_resp.status_code == requests.codes.ok:
            return True
        else:
            return api_resp

    def account_details(self, account_id):
        """AIMS Account Resources - Get Account Details
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Account_Resources-GetAccountDetails
        /aims/v1/:account_id/account"""
        api_resp = self.ci(account_id).account.GET()
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def account_details_by_name(self, name):
        """AIMS Account Resources - Get Details of Accounts by Name
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Account_Resources-GetAccountsDetailsByName
        /aims/v1/accounts/name/:name"""
        api_resp = self.ci.accounts.name(name).GET()
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def account_ids_by_relationship(self, relationship, account_id=None, **params):
        """AIMS Account Resources - List Account IDs by Relationship
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Account_Resources-ListAccountIdsByRelationship
        /aims/v1/:account_id/account_ids/:relationship?active=:active"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).account_ids(relationship).GET(params=params)
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def accounts_by_relationship(self, relationship, account_id=None, **params):
        """AIMS Account Resources - List Accounts by Relationship
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Account_Resources-ListAccountsByRelationship
        /aims/v1/:account_id/accounts/:relationship?active=:active"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).accounts(relationship).GET(params=params)
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def update_account_details(self, account_id, **data):
        """AIMS Account Resources - Update Account Details
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Account_Resources-UpdateAccount
        /aims/v1/:account_id/account"""
        api_resp = self.ci(account_id).account.POST(data=json.dumps(data))
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def authorize(self, user_id, account_id=None, **params):
        """AIMS Authentication and Authorization Resources - Authorize
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Authentication_and_Authorization_Resources-Authorize
        /aims/v1/:account_id/authorize/:user_id?required_permission=:required_permission"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).authorize(user_id).GET(params=json.dumps(params))
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp


    def change_password(self, **data):
        """AIMS Authentication and Authorization Resources - Change User Password
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Authentication_and_Authorization_Resources-ChangePassword
        /aims/v1/change_password"""
        api_resp = self.ci.change_password(data=json.dumps(data))
        if api_resp.status_code == requests.codes.ok:
            return True
        else:
            return api_resp


    def federation_domain(self):
        """AIMS Authentication and Authorization Resources - Get Federation Domain
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Authentication_and_Authorization_Resources-FederationDomain
        /aims/v1/federation_domain"""
        api_resp = self.ci.federation_domain.GET()
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def reset_password(self, **data):
        """AIMS Authentication and Authorization Resources - Initiate Password Reset
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Authentication_and_Authorization_Resources-InitiatePasswordReset
        /aims/v1/reset_password"""
        api_resp = self.ci.reset_password.POST(data=json.dumps(data))
        if api_resp.status_code == requests.codes.ok:
            return True
        else:
            return api_resp

    def reset_password_token(self, token, **data):
        """AIMS Authentication and Authorization Resources - Reset Password
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Authentication_and_Authorization_Resources-ResetPassword
        /aims/v1/reset_password/:token"""
        api_resp = self.ci.reset_password(token).POST(data=json.dumps(data))
        if api_resp.status_code == requests.codes.ok:
            return True
        else:
            return api_resp

    def create_role(self, account_id=None, **data):
        """AIMS Role Resources - Create Role
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Role_Resources-CreateRole
        /aims/v1/:account_id/roles"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).roles.POST(data=json.dumps(data))
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def delete_role(self, role_id, account_id=None):
        """AIMS Role Resources - Delete Role
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Role_Resources-DeleteRole
        /aims/v1/:account_id/roles/:role_id"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).roles(role_id).DELETE()
        if api_resp.status_code == requests.codes.ok:
            return True
        else:
            return api_resp

    def role_details(self, role_id, account_id=None):
        """AIMS Role Resources - Get Role Details
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Role_Resources-GetRole
        /aims/v1/:account_id/roles/:role_id"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).roles(role_id)
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def roles(self, account_id=None):
        """AIMS Role Resources - List Roles
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Role_Resources-ListRoles
        /aims/v1/:account_id/roles"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).roles.GET()
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def update_role_details(self, role_id, account_id=None, **data):
        """AIMS Role Resources - Update Role Details
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_Role_Resources-UpdateRole
        /aims/v1/:account_id/roles/:role_id"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).roles(role_id).POST(data=json.dumps(data))
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def add_linked_alws_user_to_user(self, user_id, location, alws_user_id, account_id=None):
        """AIMS User Resources - Add Linked ALWS User to User
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_User_Resources-AddLinkedUser
        /aims/v1/:account_id/users/:user_id/link/:location/:alws_user_id"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).users(user_id).link(location)(alws_user_id).PUT()
        if api_resp.status_code == requests.codes.ok:
            return True
        else:
            return api_resp

    def create_access_key(self, user_id, account_id=None):
        """AIMS User Resources - Create Access Key
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_User_Resources-CreateAccessKey
        /aims/v1/:account_id/users/:user_id/access_keys"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).users(user_id).access_keys.POST()
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def create_user(self, account_id=None, **params):
        """AIMS User Resources - Create User
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_User_Resources-CreateUser
        /aims/v1/:account_id/users?one_time_password=:one_time_password"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).users.POST(params=params)
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def delete_access_key(self, user_id, access_key_id, account_id=None):
        """AIMS User Resources - Delete Access Key
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_User_Resources-DeleteAccessKey
        /aims/v1/:account_id/users/:user_id/access_keys/:access_key_id"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).users(user_id).access_keys(access_key_id).DELETE()
        if api_resp.status_code == requests.codes.ok:
            return True
        else:
            return api_resp

    def delete_user(self, user_id, account_id=None):
        """AIMS User Resources - Delete User
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_User_Resources-DeleteUser
        /aims/v1/:account_id/users/:user_id"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).users(user_id).DELETE()
        if api_resp.status_code == requests.codes.ok:
            return True
        else:
            return api_resp

    def access_keys(self, user_id, account_id=None):
        """AIMS User Resources - Get Access Keys
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_User_Resources-GetAccessKeys
        /aims/v1/:account_id/users/:user_id/access_keys"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).users(user_id).access_keys.GET()
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def assigned_roles(self, user_id, account_id=None):
        """AIMS User Resources - Get Assigned Roles
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_User_Resources-GetUserRoles
        /aims/v1/:account_id/users/:user_id/roles"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).users(user_id).roles.GET()
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def authentication_fail_counter(self, user_id, account_id=None):
        """AIMS User Resources - Get Authentication Fail Counter
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_User_Resources-GetAuthenticationFailCounter
        /aims/v1/:account_id/users/:user_id/authentication_fail_counter"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).users(user_id).authentication_fail_counter.GET()
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def user_details(self, user_id, account_id=None):
        """AIMS User Resources - Get User Details
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_User_Resources-GetUserDetails
        /aims/v1/:account_id/users/:user_id"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).users(user_id).GET()
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def user_details_by_email(self, email):
        """AIMS User Resources - Get User Details by Email
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_User_Resources-GetUserDetailsByEmail
        /aims/v1/user/email/:email"""
        api_resp = self.ci.user.email(email).GET()
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def user_details_by_id(self, user_id):
        """AIMS User Resources - Get User Details by User ID
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_User_Resources-GetUserDetailsByUserId
        /aims/v1/user/:user_id"""
        api_resp = self.ci.user(user_id).GET()
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def user_permissions(self, user_id, account_id=None):
        """AIMS User Resources - Get User Permissions
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_User_Resources-GetUserPermissions
        /aims/v1/:account_id/users/:user_id/permissions"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).users(user_id).permissions.GET()
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def grant_user_role(self, user_id, role_id, account_id=None):
        """AIMS User Resources - Grant User Role
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_User_Resources-GrantUserRole
        /aims/v1/:account_id/users/:user_id/roles/:role_id"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).users(user_id).roles(role_id).PUT()
        if api_resp.status_code == requests.codes.ok:
            return True
        else:
            return api_resp

    def users(self, account_id=None):
        """AIMS User Resources - List Users
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_User_Resources-ListUsers
        /aims/v1/:account_id/users"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).users.GET()
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp

    def revoke_user_role(self, user_id, role_id, account_id=None):
        """AIMS User Resources - Revoke User Role
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_User_Resources-RevokeRole
        /aims/v1/:account_id/users/:user_id/roles/:role_id"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).users(user_id).roles(role_id).DELETE()
        if api_resp.status_code == requests.codes.ok:
            return True
        else:
            return api_resp

    def update_user_details(self, user_id, account_id=None, **params):
        """AIMS User Resources - Update User Details
        https://console.cloudinsight.alertlogic.com/api/aims/#api-AIMS_User_Resources-UpdateUser
        /aims/v1/:account_id/users/:user_id?one_time_password=:one_time_password"""
        if not account_id:
            account_id = self.account_id
        api_resp = self.ci(account_id).users(user_id).POST(params=params)
        try:
            resp = api_resp.json()
        except simplejson.decoder.JSONDecodeError as error:
            logging.info(error)
            return api_resp
        else:
            return resp
