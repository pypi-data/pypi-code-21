# Copyright (C) 2016-2017,BGI ltd.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may not
#   use this file except in compliance with the License. You may obtain a copy
#   of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#
import sys
import json
import time
import utils.print_funtion as print_funtion


class Error(Exception):
    '''Base class for exceptions in this package.'''


BACKEND_ERR_DIST = {
    'backend_msg_internal_error': 'Internal error',
    'backend_msg_insufficient_parameters': 'Insufficient parameters',
    'backend_msg_insufficient_privilege': 'Insufficient privilege',
    'backend_msg_invalid_parameters': 'Invalid parameters',
    'backend_msg_user_name_used': 'User name has been used',
    'backend_msg_email_address_used': 'E-mail address has been used',
    'backend_msg_token_expired': 'Session expired, please login again',
    'backend_msg_token_invalid': 'Invalid session, please login again',
    'backend_msg_invalid_credentials': 'Invalid credentials',
    'backend_msg_inactivated_account': 'Account inactivated',
    'backend_msg_invalid_account': 'Account status is not available',
    'backend_msg_activated_account': 'Account activated',
    'backend_msg_refresh_token_expired': 'Refresh token expired',
    'backend_msg_refresh_token_invalid': 'Invalid refresh token',
    'backend_msg_activation_token_expired': 'Activation token expired',
    'backend_msg_activation_token_invalid': 'Invalid activation token',
    'backend_msg_reset_token_expired': 'Reset token expired',
    'backend_msg_reset_token_invalid': 'Invalid reset token',
    'backend_msg_invalid_invitation_code': 'Invalid invitation code',
    'backend_msg_cannot_allocate_invitation_code': 'Failed to allocate the invitation code',
    'backend_msg_invalid_role': 'Invalid role',
    'backend_msg_invalid_user_name': 'Invalid user name',
    'backend_msg_invalid_user_name_password': 'Invalid user name or password',
    'backend_msg_invalid_user_name_email': 'Invalid user name or email.',
    'backend_msg_exist_user_name_email': 'This user is already a member of the project',
    'backend_msg_invalid_password': 'Invalid password',
    'backend_msg_access_denied': 'Access denied',
    'backend_msg_app_not_found': 'Pipeline not found',
    'backend_msg_tool_not_found': 'Tool not found',
    'backend_msg_tool_not_accessible': 'Tool not accessible',
    'backend_msg_project_not_found': 'Project not found',
    'backend_msg_file_not_found': 'File not found',
    'backend_msg_file_not_accessible': 'File not accessible',
    'backend_msg_user_not_found': 'User not found',
    'backend_msg_job_not_found': 'Job not found',
    'backend_msg_job_to_rerun_not_found': 'Job to be re-run not found',
    'backend_msg_job_already_stopped': 'Job [{{name}}] is already stopped',
    'backend_msg_target_not_found': 'Target not found',
    'backend_msg_wallet_not_found': 'Wallet not found',
    'backend_msg_fail_save_app': 'Failed to save pipeline at backend',
    'backend_msg_invalid_specification': 'Invalid specification: ',
    'backend_msg_fail_create_activity': 'Failed to create activity',
    'backend_msg_no_pending_publish_request': 'No pending publish request',
    'backend_msg_cannot_delete_file': 'Cannot delete file, please try again later.',
    'backend_msg_you_must_have_run_permission': 'You must have run job permission to start a job',
    'backend_msg_app_modified_before_rerun': 'Pipeline has been modified after last job started',
    'backend_msg_user_assigned_must_be_member': 'Assigned user must be project member',
    'backend_msg_project_owner_not_removable': 'Project owner not removable',
    'backend_msg_invalid_decision': 'Invalid decision',
    'backend_msg_tool_valid_author': 'Tool must be uploaded by valid author',
    'backend_msg_cannot_delete_published_tool': 'Cannot delete published tool',
    'backend_msg_invalid_status': 'Invalid status',
    'backend_msg_json_parsing_error': 'JSON parsing error',
    'backend_msg_invalid_schema': 'Invalid specification',
    'backend_msg_invalid_app_empty_node': 'Invalid pipeline specification: unexpected empty nodes',
    'backend_msg_invalid_config_empty_input': 'Invalid configuration: unexpected empty input',
    'backend_msg_app_model_primary_key': 'Pipeline model must have a primary key',
    'backend_msg_cannot_get_info_from_engine': 'Cannot get information from engine',
    'backend_msg_not_s3_file': 'URL must be a S3 file',
    'backend_msg_fail_save_file': 'Failed to save file at backend',
    'backend_msg_fail_delete_file': 'Failed to delete file at backend',
    'backend_msg_fail_save_file_sharing': 'Failed to save file sharing at backend',
    'backend_msg_fail_save_project': 'Failed to save project at backend',
    'backend_msg_linked_file_cannot_copy': 'Linked file cannot be copied',
    'backend_msg_linked_file_cannot_share': 'Linked file cannot be shared',
    'backend_msg_file_cannot_copy': 'File cannot be copied',
    'backend_msg_file_cannot_share': 'File cannot be shared',
    'backend_msg_file_already_under_project': 'File is already under the project',
    'backend_msg_file_not_linkable': 'File is not linkable',
    'backend_msg_file_already_deleted': 'File already deleted',
    'backend_msg_cannot_freeze_link': 'Cannot freeze link',
    'backend_msg_cannot_freeze_web_file': 'Cannot freeze web file',
    'backend_msg_cannot_freeze_shared_file': 'Cannot freeze shared file',
    'backend_msg_fail_freeze_file': 'Failed to freeze file',
    'backend_msg_cannot_warm_up_link': 'Cannot warm up link',
    'backend_msg_cannot_warm_up_web_file': 'Cannot warm up web file',
    'backend_msg_fail_warm_up_file': 'Failed to warm up file',
    'backend_msg_file_already_cold': 'File is already cold',
    'backend_msg_file_not_cold': 'File is not cold',
    'backend_msg_app_contain_distrusted_tool': 'Pipeline contain distrusted tool',
    'backend_msg_transaction_amount_integer': 'Transaction amount must be integer',
    'backend_msg_user_name_requirement': 'User name must be between 4 and 40 characters and contain alphanumeric characters and underscores only',
    'backend_msg_fail_save_transaction': 'Failed to transaction at backend',
    'backend_msg_transaction_not_found': 'Transaction not found',
    'invite_user_title': 'Invite user to join BGI Online',
    'invite_user_desc': 'The user {{user}} has not joined BGI Online yet. Please input his/her email address below and an invitation will be sent to him/her.',
    'invite_user_email': 'New user email',
    'invite_message': 'Your message (optional)',
    'invite_success': 'Invitation sent',
    'invite_fail': 'Fail to send invitation',
    'invite_user_link': 'Invite {{user}} to join BGI Online',
    'backend_msg_cloned_app_price_not_editable': 'Price of cloned app is not editable',
    'backend_msg_price_must_be_positive': 'Price must be positive integer.',
    'backend_msg_date_invalid': 'Date Invalid',
    'backend_msg_fail_save_app_revise_version': 'Fail to Save Pipeline Revise Version',
    'backend_msg_fail_update_app': 'Fail to Update Pipeline',
    'backend_msg_app_status_error': 'The status of Pipeline Has Error',
    'backend_msg_fail_error_dict_type': 'Failed Dictionary Type',
    'backend_msg_parameters_conflict': 'Parameters Conflict',
    'backend_msg_fail_no_this_path': 'No This Path',
    'backend_msg_fail_no_this_file': 'No This File',
    'backend_msg_message_not_found': 'Message Not Found',
    # 'backend_msg_project_does_not_exist':'Project does not exist',
    'backend_msg_this_public_project_cannot_upload_file': 'This Public Project Cannot Upload File',
    'backend_msg_project_type_error': 'Project Type Error',
    'backend_msg_project_status_error': 'Project Status Error',
    'backend_msg_project_no_files': 'No Files of Project',
    'backend_msg_unpublish_project_error': 'Fail to Unpublish Project',
    'backend_msg_unShare_project_files_error': 'Fail to UnShare Project Files',
    'backend_msg_fail_no_this_project': 'No This Project',
    'backend_msg_tool_status_error': 'Tool Status Error',
    'backend_msg_app_revise_version_not_found': 'Not Found The Pipeline Revise Version',
    'backend_msg_invalid_parameterss': 'Invalid Parameterss',
    'backend_msg_exist_the_same_name_folder': 'Exist The Same Name Folder',
    'backend_msg_unvaliable_folder_path': 'Unvaliable Folder Path',
    'backend_msg_no_this_folder': 'No such file or directory',
    'backend_msg_file_name_null': 'File Name Is Null',
    'backend_msg_parent_cannot_file': 'Parent Cannot File',
    'backend_msg_folder_is_exist': 'Folder is exist',
    'backend_msg_file_size_null': 'File Size Is Null',
    'backend_msg_file_size_is_not_number': 'File Size Is Not Number',
    'backend_msg_call_engine_failed': 'Call Engine Failed',
    'backend_msg_save_meta_info_error': 'Save Meta Info Error',
    'backend_msg_metadata_is_not_array': 'Metadata Is Not Array',
    'backend_msg_change_file_status_error': 'Change File Status Error',
    'backend_msg_update_tool_status_error': 'Update Tool Status Error',
    'backend_msg_save_tool_sharing_error': 'save Tool Sharing Error',
    'backend_msg_update_app_status_error': 'Update Pipeline Status Error',
    'backend_msg_save_app_sharing_error': 'save Pipeline Sharing Error',
    'backend_msg_feedback_error': 'Feedback error',
    'backend_msg_save_share_relation_error': 'Save Share Relation Error',
    'backend_msg_save_approval_result_error': 'save Approval Result Error',
    'backend_msg_the_project_name_is_exist': 'The ProjectName Is Exist',
    'backend_msg_the_user_has_the_same_name_project': 'The User Has The Same Name Project',
    'backend_msg_opt_not_enough_credit': 'credit not enough',
    'backend_msg_opt_tool_not_published': 'Tool not published : Tool#',
    'backend_msg_file_does_not_exist':'File does not exist',
}


class APIError(Error):
    def __init__(self, url, content):
        self.time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        self.url = url
        self.name = content["name"]
        self.code = content["code"]
        self.message = content["message"]

    def msg(self):
        if self.message in BACKEND_ERR_DIST.keys():
            output = print_funtion.RED(BACKEND_ERR_DIST[self.message])
            output += "\nDetails [%s url: %s %s - [code:%s] %s] " % (
                self.time, self.url, self.name, self.code, self.message)
        else:
            output = "DATE: %s\nURL: %s\n%s - [code:%s]\n%s\n" % (
                self.time, self.url, self.name, self.code, self.message)
        return output

    def __str__(self):
        return self.msg()


class BadJSONFormat(ValueError):
    """"""


def err_exit(message="", exit_code="1"):
    print
    print(message)
    sys.exit()


if __name__ == "__main__":
    e = APIError(json.loads('''{"code":401,"name":"Unauthorized","message":"backend_msg_invalid_user_name_email"}'''))
    print e
