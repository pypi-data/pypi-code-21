from snapp_email.datacontract import utils
from snapp_email.datacontract.classes import User_14, StreamUser_22, AccountEmail_14, ListOfAccounts_14, Post_22, \
    DiscussionBase_22, File_14, ListOfFiles_14, ListOfResources_13


def post(client, content, existing_card_id, attachment_ids=None, impersonate_user_id=None):
    """
    Post a message to an existing card (stream card or chat card).
    WARNING: When posting to a chat card, you can either post content or 1 attachment.

    :param client:
    :type client: snapp_email.api_client.ApiClient
    :param content:
    :param existing_card_id:
    :param attachment_ids:
    :param impersonate_user_id:
    :return:
    :rtype: Post_22
    """
    parent = DiscussionBase_22()
    parent.set_Id(existing_card_id)
    post_obj = Post_22(Text=content, Parent=parent)
    # TODO if False: post_obj = Post_22(BodyHtml=html)
    if attachment_ids:
        files = []
        for attachment_id in attachment_ids:
            file = File_14()
            file.set_Id(attachment_id)
            files.append(file)
        post_obj.set_Files(ListOfFiles_14(files))
    created_post = client.post.Post_22.create(post_obj, impersonate_user_id=impersonate_user_id)
    if attachment_ids and len(attachment_ids) > 0:
        pass
    return created_post


def post_create_card(client, content, subject, recipients=None, attachment_ids=None, impersonate_user_id=None):
    """
    Post a message to a new card.

    :param client:
    :type client: snapp_email.api_client.ApiClient
    :param content: str
    :param subject: str
    :param recipients: A list of emails
    :param attachment_ids: A list of document IDs
    :param impersonate_user_id:
    :return:
    :rtype: Post_22
    """
    if type(recipients) is not list:
        recipients = [recipients]

    _share_list = []
    for recipient_email in recipients:
        _share_list.append(create_user_object_from_email(recipient_email))
    share_list = ListOfResources_13(_share_list)

    post_obj = Post_22(Text=content, ShareList=share_list)
    # TODO if False: post_obj = Post_22(BodyHtml=html)
    post_obj.set_Name(subject)
    if attachment_ids:
        files = []
        for attachment_id in attachment_ids:
            file = File_14()
            file.set_Id(attachment_id)
            files.append(file)
        post_obj.set_Files(ListOfFiles_14(files))

    created_post = client.post.Post_22.create(post_obj, impersonate_user_id=impersonate_user_id)
    return created_post


def get_user_chat_card(client, user_email, impersonate_user_id=None):
    """
    :param client:
    :type client: snapp_email.api_client.ApiClient
    :param user_email:
    :param impersonate_user_id:
    :return:
    :rtype: StreamUser_22
    """
    data = StreamUser_22(
        User_14(
            AccountList=ListOfAccounts_14([
                AccountEmail_14(user_email)
            ])
        )
    )
    feed = client.stream.StreamUser_22.create(data, impersonate_user_id=impersonate_user_id)
    return feed


def get_user_chat_id(client, user_email, impersonate_user_id=None):
    """
    :param client:
    :type client: snapp_email.api_client.ApiClient
    :param user_email:
    :param impersonate_user_id:
    :return:
    """
    feed = get_user_chat_card(client, user_email, impersonate_user_id=impersonate_user_id)
    return feed.Id


def create_attachment(client, attachment_path, attachment_name):
    """
    :param client:
    :type client: snapp_email.api_client.ApiClient
    :param attachment_path:
    :param attachment_name:
    :return:
    :rtype: Document_18
    """
    with open(attachment_path, 'rb') as f:
        file_contents = f.read()
    doc = client.document.Document_18.create(file_contents, attachment_name)
    return doc


def get_attachment(client, document_id, download=False):
    """
    :param download:
    :param client:
    :type client: snapp_email.api_client.ApiClient
    :param document_id:
    :return: returns a Document_18 object, or file if download parameter is set to True
    """
    accept_type = 'application/octet-stream' if download else None
    return client.document.Document_18.get(document_id, accept_type=accept_type)


def create_user_object_from_email(email):
    return User_14(
        AccountList=ListOfAccounts_14([
            AccountEmail_14(email)
        ])
    )


def get_user_by_email(client, user_email, accept_type=None):
    """
    :param client:
    :type client: snapp_email.api_client.ApiClient
    :param self:
    :param user_email:
    :param accept_type:
    :return:
    :rtype: User_14
    """
    url_parameters = {
        'email': user_email,
    }
    endpoint = 'user'
    add_headers = {
        'Content-Type': 'application/vnd.4thoffice.user-4.0+json',
        'Accept': 'application/vnd.4thoffice.user-4.0+json' if accept_type is None else accept_type,
    }
    response = client.api_call('get', endpoint, url_parameters, add_headers)

    return utils.fill(User_14, response.json())
