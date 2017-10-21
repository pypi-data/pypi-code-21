#!/usr/bin/env python

#
# Generated Sat Oct 21 20:01:50 2017 by generateDS.py version 2.23a.
#
# Command line options:
#   ('-a', 'bc:')
#   ('-o', 'snapp_email\\datacontract\\classes.py')
#   ('-s', 'snapp_email\\datacontract\\subclasses.py')
#   ('--export', '')
#   ('--member-specs', 'dict')
#
# Command line arguments:
#   generate\SdkWebServiceDataContract.xsd
#
# Command line:
#   C:\Users\uroshe\AppData\Local\Programs\Python\Python35-32\Scripts\generateDS.py -a "bc:" -o "snapp_email\datacontract\classes.py" -s "snapp_email\datacontract\subclasses.py" --export --member-specs="dict" generate\SdkWebServiceDataContract.xsd
#
# Current working directory (os.getcwd()):
#   4thOfficeClient.py
#

import sys
from lxml import etree as etree_

import ??? as supermod

def parsexml_(infile, parser=None, **kwargs):
    if parser is None:
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        parser = etree_.ETCompatXMLParser()
    doc = etree_.parse(infile, parser=parser, **kwargs)
    return doc

#
# Globals
#

ExternalEncoding = 'utf-8'

#
# Data representation classes
#


class ApiIndex_1Sub(supermod.ApiIndex_1):
    def __init__(self, ProductName=None, HttpHeaderList=None, UrlParameterList=None, ApiIndexLinkList=None):
        super(ApiIndex_1Sub, self).__init__(ProductName, HttpHeaderList, UrlParameterList, ApiIndexLinkList, )
supermod.ApiIndex_1.subclass = ApiIndex_1Sub
# end class ApiIndex_1Sub


class ListOfHttpHeaders_12Sub(supermod.ListOfHttpHeaders_12):
    def __init__(self, HttpHeader=None):
        super(ListOfHttpHeaders_12Sub, self).__init__(HttpHeader, )
supermod.ListOfHttpHeaders_12.subclass = ListOfHttpHeaders_12Sub
# end class ListOfHttpHeaders_12Sub


class HttpHeader_12Sub(supermod.HttpHeader_12):
    def __init__(self, Name=None, Description=None, Required=None, SupportedValues=None):
        super(HttpHeader_12Sub, self).__init__(Name, Description, Required, SupportedValues, )
supermod.HttpHeader_12.subclass = HttpHeader_12Sub
# end class HttpHeader_12Sub


class HttpValueDescriptionSub(supermod.HttpValueDescription):
    def __init__(self, Value=None, Description=None):
        super(HttpValueDescriptionSub, self).__init__(Value, Description, )
supermod.HttpValueDescription.subclass = HttpValueDescriptionSub
# end class HttpValueDescriptionSub


class ListOfHttpValueDescriptionsSub(supermod.ListOfHttpValueDescriptions):
    def __init__(self, ValueDescription=None):
        super(ListOfHttpValueDescriptionsSub, self).__init__(ValueDescription, )
supermod.ListOfHttpValueDescriptions.subclass = ListOfHttpValueDescriptionsSub
# end class ListOfHttpValueDescriptionsSub


class ListOfApiIndexLinks_1Sub(supermod.ListOfApiIndexLinks_1):
    def __init__(self, ApiIndexLink=None):
        super(ListOfApiIndexLinks_1Sub, self).__init__(ApiIndexLink, )
supermod.ListOfApiIndexLinks_1.subclass = ListOfApiIndexLinks_1Sub
# end class ListOfApiIndexLinks_1Sub


class ApiIndexLink_1Sub(supermod.ApiIndexLink_1):
    def __init__(self, Name=None, Description=None, Href=None, ContentTypes=None, Methods=None):
        super(ApiIndexLink_1Sub, self).__init__(Name, Description, Href, ContentTypes, Methods, )
supermod.ApiIndexLink_1.subclass = ApiIndexLink_1Sub
# end class ApiIndexLink_1Sub


class ListOfContentTypesSub(supermod.ListOfContentTypes):
    def __init__(self, ContentType=None):
        super(ListOfContentTypesSub, self).__init__(ContentType, )
supermod.ListOfContentTypes.subclass = ListOfContentTypesSub
# end class ListOfContentTypesSub


class ListOfApiIndexOptions_4Sub(supermod.ListOfApiIndexOptions_4):
    def __init__(self, Options=None):
        super(ListOfApiIndexOptions_4Sub, self).__init__(Options, )
supermod.ListOfApiIndexOptions_4.subclass = ListOfApiIndexOptions_4Sub
# end class ListOfApiIndexOptions_4Sub


class ApiIndexOptions_1Sub(supermod.ApiIndexOptions_1):
    def __init__(self, Name=None, Methods=None):
        super(ApiIndexOptions_1Sub, self).__init__(Name, Methods, )
supermod.ApiIndexOptions_1.subclass = ApiIndexOptions_1Sub
# end class ApiIndexOptions_1Sub


class ApiIndexMethod_1Sub(supermod.ApiIndexMethod_1):
    def __init__(self, Type=None, Description=None, Parameters=None, HttpHeaderList=None, HttpErrorList=None):
        super(ApiIndexMethod_1Sub, self).__init__(Type, Description, Parameters, HttpHeaderList, HttpErrorList, )
supermod.ApiIndexMethod_1.subclass = ApiIndexMethod_1Sub
# end class ApiIndexMethod_1Sub


class ListOfApiIndexMethods_1Sub(supermod.ListOfApiIndexMethods_1):
    def __init__(self, ApiIndexMethod=None):
        super(ListOfApiIndexMethods_1Sub, self).__init__(ApiIndexMethod, )
supermod.ListOfApiIndexMethods_1.subclass = ListOfApiIndexMethods_1Sub
# end class ListOfApiIndexMethods_1Sub


class ApiIndexParameter_1Sub(supermod.ApiIndexParameter_1):
    def __init__(self, Type=None, Name=None, Description=None, AvailableValues=None, Required=None, IsList=None):
        super(ApiIndexParameter_1Sub, self).__init__(Type, Name, Description, AvailableValues, Required, IsList, )
supermod.ApiIndexParameter_1.subclass = ApiIndexParameter_1Sub
# end class ApiIndexParameter_1Sub


class ListOfApiIndexParameters_1Sub(supermod.ListOfApiIndexParameters_1):
    def __init__(self, ApiIndexParameter=None):
        super(ListOfApiIndexParameters_1Sub, self).__init__(ApiIndexParameter, )
supermod.ListOfApiIndexParameters_1.subclass = ListOfApiIndexParameters_1Sub
# end class ListOfApiIndexParameters_1Sub


class ApiIndexError_1Sub(supermod.ApiIndexError_1):
    def __init__(self, Description=None, HttpStatusCode=None, ErrorCode=None):
        super(ApiIndexError_1Sub, self).__init__(Description, HttpStatusCode, ErrorCode, )
supermod.ApiIndexError_1.subclass = ApiIndexError_1Sub
# end class ApiIndexError_1Sub


class ListOfApiIndexErrors_1Sub(supermod.ListOfApiIndexErrors_1):
    def __init__(self, Error=None):
        super(ListOfApiIndexErrors_1Sub, self).__init__(Error, )
supermod.ListOfApiIndexErrors_1.subclass = ListOfApiIndexErrors_1Sub
# end class ListOfApiIndexErrors_1Sub


class LogOnSub(supermod.LogOn):
    def __init__(self, ServiceId=None, KeepMeLoggedIn=None, Token=None):
        super(LogOnSub, self).__init__(ServiceId, KeepMeLoggedIn, Token, )
supermod.LogOn.subclass = LogOnSub
# end class LogOnSub


class LogOnUserMobile_4Sub(supermod.LogOnUserMobile_4):
    def __init__(self, Identity=None, AuthenticationType=None, AuthenticationToken=None, ApplicationVersion=None, Device=None):
        super(LogOnUserMobile_4Sub, self).__init__(Identity, AuthenticationType, AuthenticationToken, ApplicationVersion, Device, )
supermod.LogOnUserMobile_4.subclass = LogOnUserMobile_4Sub
# end class LogOnUserMobile_4Sub


class LogOnBase_14Sub(supermod.LogOnBase_14):
    def __init__(self, Token=None):
        super(LogOnBase_14Sub, self).__init__(Token, )
supermod.LogOnBase_14.subclass = LogOnBase_14Sub
# end class LogOnBase_14Sub


class LogOnUser_14Sub(supermod.LogOnUser_14):
    def __init__(self, Authentication=None, ClientApplication=None):
        super(LogOnUser_14Sub, self).__init__(Authentication, ClientApplication, )
supermod.LogOnUser_14.subclass = LogOnUser_14Sub
# end class LogOnUser_14Sub


class ClientApplication_14Sub(supermod.ClientApplication_14):
    def __init__(self, Type=None, Version=None, CodeName=None):
        super(ClientApplication_14Sub, self).__init__(Type, Version, CodeName, )
supermod.ClientApplication_14.subclass = ClientApplication_14Sub
# end class ClientApplication_14Sub


class Authentication_13Sub(supermod.Authentication_13):
    def __init__(self, AuthenticationType=None, AuthenticationId=None, AuthenticationToken=None, AuthenticationProviderUri=None, AuthenticationProviderDomain=None, AuthenticationProviderUsername=None):
        super(Authentication_13Sub, self).__init__(AuthenticationType, AuthenticationId, AuthenticationToken, AuthenticationProviderUri, AuthenticationProviderDomain, AuthenticationProviderUsername, )
supermod.Authentication_13.subclass = Authentication_13Sub
# end class Authentication_13Sub


class ListOfAuthentications_13Sub(supermod.ListOfAuthentications_13):
    def __init__(self, Authentication=None):
        super(ListOfAuthentications_13Sub, self).__init__(Authentication, )
supermod.ListOfAuthentications_13.subclass = ListOfAuthentications_13Sub
# end class ListOfAuthentications_13Sub


class AccountBase_14Sub(supermod.AccountBase_14):
    def __init__(self, Id=None, Authentication=None):
        super(AccountBase_14Sub, self).__init__(Id, Authentication, )
supermod.AccountBase_14.subclass = AccountBase_14Sub
# end class AccountBase_14Sub


class AccountEmail_14Sub(supermod.AccountEmail_14):
    def __init__(self, Email=None):
        super(AccountEmail_14Sub, self).__init__(Email, )
supermod.AccountEmail_14.subclass = AccountEmail_14Sub
# end class AccountEmail_14Sub


class ListOfAccounts_14Sub(supermod.ListOfAccounts_14):
    def __init__(self, Account=None):
        super(ListOfAccounts_14Sub, self).__init__(Account, )
supermod.ListOfAccounts_14.subclass = ListOfAccounts_14Sub
# end class ListOfAccounts_14Sub


class Attachment_4Sub(supermod.Attachment_4):
    def __init__(self, Id=None, IdString=None, Version=None, File=None, Hidden=None, ServiceId=None):
        super(Attachment_4Sub, self).__init__(Id, IdString, Version, File, Hidden, ServiceId, )
supermod.Attachment_4.subclass = Attachment_4Sub
# end class Attachment_4Sub


class ListOfAttachments_4Sub(supermod.ListOfAttachments_4):
    def __init__(self, Attachment=None):
        super(ListOfAttachments_4Sub, self).__init__(Attachment, )
supermod.ListOfAttachments_4.subclass = ListOfAttachments_4Sub
# end class ListOfAttachments_4Sub


class File_1Sub(supermod.File_1):
    def __init__(self, Content=None, Name=None):
        super(File_1Sub, self).__init__(Content, Name, )
supermod.File_1.subclass = File_1Sub
# end class File_1Sub


class ListOfFiles_1Sub(supermod.ListOfFiles_1):
    def __init__(self, File=None):
        super(ListOfFiles_1Sub, self).__init__(File, )
supermod.ListOfFiles_1.subclass = ListOfFiles_1Sub
# end class ListOfFiles_1Sub


class File_4Sub(supermod.File_4):
    def __init__(self, Name=None, Content=None):
        super(File_4Sub, self).__init__(Name, Content, )
supermod.File_4.subclass = File_4Sub
# end class File_4Sub


class ListOfFiles_4Sub(supermod.ListOfFiles_4):
    def __init__(self, File=None):
        super(ListOfFiles_4Sub, self).__init__(File, )
supermod.ListOfFiles_4.subclass = ListOfFiles_4Sub
# end class ListOfFiles_4Sub


class ListOfFiles_14Sub(supermod.ListOfFiles_14):
    def __init__(self, File=None):
        super(ListOfFiles_14Sub, self).__init__(File, )
supermod.ListOfFiles_14.subclass = ListOfFiles_14Sub
# end class ListOfFiles_14Sub


class ListOfDocuments_14Sub(supermod.ListOfDocuments_14):
    def __init__(self, Document=None):
        super(ListOfDocuments_14Sub, self).__init__(Document, )
supermod.ListOfDocuments_14.subclass = ListOfDocuments_14Sub
# end class ListOfDocuments_14Sub


class ListOfDocumentsPage_14Sub(supermod.ListOfDocumentsPage_14):
    def __init__(self, Documents=None, Paging=None):
        super(ListOfDocumentsPage_14Sub, self).__init__(Documents, Paging, )
supermod.ListOfDocumentsPage_14.subclass = ListOfDocumentsPage_14Sub
# end class ListOfDocumentsPage_14Sub


class DocumentShareList_14Sub(supermod.DocumentShareList_14):
    def __init__(self, ShareList=None):
        super(DocumentShareList_14Sub, self).__init__(ShareList, )
supermod.DocumentShareList_14.subclass = DocumentShareList_14Sub
# end class DocumentShareList_14Sub


class DocumentPinnedToList_15Sub(supermod.DocumentPinnedToList_15):
    def __init__(self, BoardList=None):
        super(DocumentPinnedToList_15Sub, self).__init__(BoardList, )
supermod.DocumentPinnedToList_15.subclass = DocumentPinnedToList_15Sub
# end class DocumentPinnedToList_15Sub


class DocumentThumbnail_4Sub(supermod.DocumentThumbnail_4):
    def __init__(self, DocumentId=None, Size=None, File=None, NumberOfPages=None, CurrentPage=None):
        super(DocumentThumbnail_4Sub, self).__init__(DocumentId, Size, File, NumberOfPages, CurrentPage, )
supermod.DocumentThumbnail_4.subclass = DocumentThumbnail_4Sub
# end class DocumentThumbnail_4Sub


class ThumbnailPageInfo_13Sub(supermod.ThumbnailPageInfo_13):
    def __init__(self, Width=None, Height=None, HasTextMap=None, HasPdf=None):
        super(ThumbnailPageInfo_13Sub, self).__init__(Width, Height, HasTextMap, HasPdf, )
supermod.ThumbnailPageInfo_13.subclass = ThumbnailPageInfo_13Sub
# end class ThumbnailPageInfo_13Sub


class ListOfThumbnailPageInfo_13Sub(supermod.ListOfThumbnailPageInfo_13):
    def __init__(self, ThumbnailPageInfo=None):
        super(ListOfThumbnailPageInfo_13Sub, self).__init__(ThumbnailPageInfo, )
supermod.ListOfThumbnailPageInfo_13.subclass = ListOfThumbnailPageInfo_13Sub
# end class ListOfThumbnailPageInfo_13Sub


class DocumentThumbnailPageInfo_13Sub(supermod.DocumentThumbnailPageInfo_13):
    def __init__(self, DocumentId=None, NumberOfPages=None, PageNumber=None):
        super(DocumentThumbnailPageInfo_13Sub, self).__init__(DocumentId, NumberOfPages, PageNumber, )
supermod.DocumentThumbnailPageInfo_13.subclass = DocumentThumbnailPageInfo_13Sub
# end class DocumentThumbnailPageInfo_13Sub


class DocumentThumbnailInfo_13Sub(supermod.DocumentThumbnailInfo_13):
    def __init__(self, DocumentId=None, NumberOfPages=None, PageInfoList=None, PreviewNotSupported=None, GeneratedFromHtml=None):
        super(DocumentThumbnailInfo_13Sub, self).__init__(DocumentId, NumberOfPages, PageInfoList, PreviewNotSupported, GeneratedFromHtml, )
supermod.DocumentThumbnailInfo_13.subclass = DocumentThumbnailInfo_13Sub
# end class DocumentThumbnailInfo_13Sub


class ThumbnailPreview_15Sub(supermod.ThumbnailPreview_15):
    def __init__(self, ThumbnailPageList=None, Ready=None):
        super(ThumbnailPreview_15Sub, self).__init__(ThumbnailPageList, Ready, )
supermod.ThumbnailPreview_15.subclass = ThumbnailPreview_15Sub
# end class ThumbnailPreview_15Sub


class ThumbnailTextMapPage_19Sub(supermod.ThumbnailTextMapPage_19):
    def __init__(self, TextMapListPage=None, Paging=None):
        super(ThumbnailTextMapPage_19Sub, self).__init__(TextMapListPage, Paging, )
supermod.ThumbnailTextMapPage_19.subclass = ThumbnailTextMapPage_19Sub
# end class ThumbnailTextMapPage_19Sub


class ListOfTextMaps_19Sub(supermod.ListOfTextMaps_19):
    def __init__(self, ListItem=None):
        super(ListOfTextMaps_19Sub, self).__init__(ListItem, )
supermod.ListOfTextMaps_19.subclass = ListOfTextMaps_19Sub
# end class ListOfTextMaps_19Sub


class TextMap_19Sub(supermod.TextMap_19):
    def __init__(self, Text=None, Position=None, Spacing=None, Font=None, HorizontalScaling=None, PageInfo=None, Link=None):
        super(TextMap_19Sub, self).__init__(Text, Position, Spacing, Font, HorizontalScaling, PageInfo, Link, )
supermod.TextMap_19.subclass = TextMap_19Sub
# end class TextMap_19Sub


class Rectangle_19Sub(supermod.Rectangle_19):
    def __init__(self, StartX=None, StartY=None, StopX=None, StopY=None):
        super(Rectangle_19Sub, self).__init__(StartX, StartY, StopX, StopY, )
supermod.Rectangle_19.subclass = Rectangle_19Sub
# end class Rectangle_19Sub


class PageInfo_19Sub(supermod.PageInfo_19):
    def __init__(self, PageNumber=None, PageWidth=None, PageHeight=None):
        super(PageInfo_19Sub, self).__init__(PageNumber, PageWidth, PageHeight, )
supermod.PageInfo_19.subclass = PageInfo_19Sub
# end class PageInfo_19Sub


class Font_19Sub(supermod.Font_19):
    def __init__(self, Name=None, Size=None):
        super(Font_19Sub, self).__init__(Name, Size, )
supermod.Font_19.subclass = Font_19Sub
# end class Font_19Sub


class Spacing_19Sub(supermod.Spacing_19):
    def __init__(self, Line=None, Word=None, Char=None):
        super(Spacing_19Sub, self).__init__(Line, Word, Char, )
supermod.Spacing_19.subclass = Spacing_19Sub
# end class Spacing_19Sub


class ValueNameSub(supermod.ValueName):
    def __init__(self, Name=None, Value=None):
        super(ValueNameSub, self).__init__(Name, Value, )
supermod.ValueName.subclass = ValueNameSub
# end class ValueNameSub


class ListOfValueNamesSub(supermod.ListOfValueNames):
    def __init__(self, ListItem=None):
        super(ListOfValueNamesSub, self).__init__(ListItem, )
supermod.ListOfValueNames.subclass = ListOfValueNamesSub
# end class ListOfValueNamesSub


class TypedValueName_4Sub(supermod.TypedValueName_4):
    def __init__(self, Type=None):
        super(TypedValueName_4Sub, self).__init__(Type, )
supermod.TypedValueName_4.subclass = TypedValueName_4Sub
# end class TypedValueName_4Sub


class ListOfTypedValueNames_4Sub(supermod.ListOfTypedValueNames_4):
    def __init__(self, ListItem=None):
        super(ListOfTypedValueNames_4Sub, self).__init__(ListItem, )
supermod.ListOfTypedValueNames_4.subclass = ListOfTypedValueNames_4Sub
# end class ListOfTypedValueNames_4Sub


class SearchResults_22Sub(supermod.SearchResults_22):
    def __init__(self, ResultGroups=None):
        super(SearchResults_22Sub, self).__init__(ResultGroups, )
supermod.SearchResults_22.subclass = SearchResults_22Sub
# end class SearchResults_22Sub


class ListOfSearchGroups_22Sub(supermod.ListOfSearchGroups_22):
    def __init__(self, Group=None):
        super(ListOfSearchGroups_22Sub, self).__init__(Group, )
supermod.ListOfSearchGroups_22.subclass = ListOfSearchGroups_22Sub
# end class ListOfSearchGroups_22Sub


class SearchGroup_22Sub(supermod.SearchGroup_22):
    def __init__(self, Id=None, Name=None, ResultPage=None):
        super(SearchGroup_22Sub, self).__init__(Id, Name, ResultPage, )
supermod.SearchGroup_22.subclass = SearchGroup_22Sub
# end class SearchGroup_22Sub


class ListOfSearchResourcesPage_22Sub(supermod.ListOfSearchResourcesPage_22):
    def __init__(self, SearchResourceList=None, Paging=None):
        super(ListOfSearchResourcesPage_22Sub, self).__init__(SearchResourceList, Paging, )
supermod.ListOfSearchResourcesPage_22.subclass = ListOfSearchResourcesPage_22Sub
# end class ListOfSearchResourcesPage_22Sub


class ListOfSearchResources_22Sub(supermod.ListOfSearchResources_22):
    def __init__(self, SearchResource=None):
        super(ListOfSearchResources_22Sub, self).__init__(SearchResource, )
supermod.ListOfSearchResources_22.subclass = ListOfSearchResources_22Sub
# end class ListOfSearchResources_22Sub


class SearchResource_22Sub(supermod.SearchResource_22):
    def __init__(self, Resource=None, Highlights=None, HintResourceIds=None, SearchHit=None, BadgeCount=None, Weight=None):
        super(SearchResource_22Sub, self).__init__(Resource, Highlights, HintResourceIds, SearchHit, BadgeCount, Weight, )
supermod.SearchResource_22.subclass = SearchResource_22Sub
# end class SearchResource_22Sub


class SearchResults_20Sub(supermod.SearchResults_20):
    def __init__(self, ResultGroups=None):
        super(SearchResults_20Sub, self).__init__(ResultGroups, )
supermod.SearchResults_20.subclass = SearchResults_20Sub
# end class SearchResults_20Sub


class ListOfSearchGroups_20Sub(supermod.ListOfSearchGroups_20):
    def __init__(self, Group=None):
        super(ListOfSearchGroups_20Sub, self).__init__(Group, )
supermod.ListOfSearchGroups_20.subclass = ListOfSearchGroups_20Sub
# end class ListOfSearchGroups_20Sub


class SearchGroup_20Sub(supermod.SearchGroup_20):
    def __init__(self, Id=None, Name=None, ResultPage=None):
        super(SearchGroup_20Sub, self).__init__(Id, Name, ResultPage, )
supermod.SearchGroup_20.subclass = SearchGroup_20Sub
# end class SearchGroup_20Sub


class ListOfSearchResourcesPage_20Sub(supermod.ListOfSearchResourcesPage_20):
    def __init__(self, SearchResourceList=None, Paging=None):
        super(ListOfSearchResourcesPage_20Sub, self).__init__(SearchResourceList, Paging, )
supermod.ListOfSearchResourcesPage_20.subclass = ListOfSearchResourcesPage_20Sub
# end class ListOfSearchResourcesPage_20Sub


class ListOfSearchResources_20Sub(supermod.ListOfSearchResources_20):
    def __init__(self, SearchResource=None):
        super(ListOfSearchResources_20Sub, self).__init__(SearchResource, )
supermod.ListOfSearchResources_20.subclass = ListOfSearchResources_20Sub
# end class ListOfSearchResources_20Sub


class SearchResource_20Sub(supermod.SearchResource_20):
    def __init__(self, Resource=None, Highlights=None, SearchHit=None, BadgeCount=None, Weight=None):
        super(SearchResource_20Sub, self).__init__(Resource, Highlights, SearchHit, BadgeCount, Weight, )
supermod.SearchResource_20.subclass = SearchResource_20Sub
# end class SearchResource_20Sub


class SearchResultsGroupedPage_18Sub(supermod.SearchResultsGroupedPage_18):
    def __init__(self, Groups=None, Paging=None):
        super(SearchResultsGroupedPage_18Sub, self).__init__(Groups, Paging, )
supermod.SearchResultsGroupedPage_18.subclass = SearchResultsGroupedPage_18Sub
# end class SearchResultsGroupedPage_18Sub


class ListOfSearchGroups_18Sub(supermod.ListOfSearchGroups_18):
    def __init__(self, Group=None):
        super(ListOfSearchGroups_18Sub, self).__init__(Group, )
supermod.ListOfSearchGroups_18.subclass = ListOfSearchGroups_18Sub
# end class ListOfSearchGroups_18Sub


class SearchGroup_18Sub(supermod.SearchGroup_18):
    def __init__(self, Id=None, Name=None, ResultPage=None):
        super(SearchGroup_18Sub, self).__init__(Id, Name, ResultPage, )
supermod.SearchGroup_18.subclass = SearchGroup_18Sub
# end class SearchGroup_18Sub


class ListOfSearchResourcesPage_18Sub(supermod.ListOfSearchResourcesPage_18):
    def __init__(self, SearchResourceList=None, Paging=None):
        super(ListOfSearchResourcesPage_18Sub, self).__init__(SearchResourceList, Paging, )
supermod.ListOfSearchResourcesPage_18.subclass = ListOfSearchResourcesPage_18Sub
# end class ListOfSearchResourcesPage_18Sub


class ListOfSearchResources_18Sub(supermod.ListOfSearchResources_18):
    def __init__(self, SearchResource=None):
        super(ListOfSearchResources_18Sub, self).__init__(SearchResource, )
supermod.ListOfSearchResources_18.subclass = ListOfSearchResources_18Sub
# end class ListOfSearchResources_18Sub


class SearchResource_18Sub(supermod.SearchResource_18):
    def __init__(self, Resource=None, Highlights=None, SearchHit=None, BadgeCount=None):
        super(SearchResource_18Sub, self).__init__(Resource, Highlights, SearchHit, BadgeCount, )
supermod.SearchResource_18.subclass = SearchResource_18Sub
# end class SearchResource_18Sub


class Device_4Sub(supermod.Device_4):
    def __init__(self, Id=None, Name=None):
        super(Device_4Sub, self).__init__(Id, Name, )
supermod.Device_4.subclass = Device_4Sub
# end class Device_4Sub


class ListOfActors_13Sub(supermod.ListOfActors_13):
    def __init__(self, Actor=None):
        super(ListOfActors_13Sub, self).__init__(Actor, )
supermod.ListOfActors_13.subclass = ListOfActors_13Sub
# end class ListOfActors_13Sub


class ListOfActors_14Sub(supermod.ListOfActors_14):
    def __init__(self, Actor=None):
        super(ListOfActors_14Sub, self).__init__(Actor, )
supermod.ListOfActors_14.subclass = ListOfActors_14Sub
# end class ListOfActors_14Sub


class ListOfUsers_14Sub(supermod.ListOfUsers_14):
    def __init__(self, User=None):
        super(ListOfUsers_14Sub, self).__init__(User, )
supermod.ListOfUsers_14.subclass = ListOfUsers_14Sub
# end class ListOfUsers_14Sub


class ListOfUsersPage_14Sub(supermod.ListOfUsersPage_14):
    def __init__(self, Users=None, Paging=None):
        super(ListOfUsersPage_14Sub, self).__init__(Users, Paging, )
supermod.ListOfUsersPage_14.subclass = ListOfUsersPage_14Sub
# end class ListOfUsersPage_14Sub


class UserAvatar_17Sub(supermod.UserAvatar_17):
    def __init__(self, UserId=None):
        super(UserAvatar_17Sub, self).__init__(UserId, )
supermod.UserAvatar_17.subclass = UserAvatar_17Sub
# end class UserAvatar_17Sub


class UserSettingsBase_14Sub(supermod.UserSettingsBase_14):
    def __init__(self, Id=None, Name=None):
        super(UserSettingsBase_14Sub, self).__init__(Id, Name, )
supermod.UserSettingsBase_14.subclass = UserSettingsBase_14Sub
# end class UserSettingsBase_14Sub


class ListOfUserSettings_14Sub(supermod.ListOfUserSettings_14):
    def __init__(self, UserSettings=None):
        super(ListOfUserSettings_14Sub, self).__init__(UserSettings, )
supermod.ListOfUserSettings_14.subclass = ListOfUserSettings_14Sub
# end class ListOfUserSettings_14Sub


class ListOfUserSettingsPage_14Sub(supermod.ListOfUserSettingsPage_14):
    def __init__(self, UserSettingsList=None, Paging=None):
        super(ListOfUserSettingsPage_14Sub, self).__init__(UserSettingsList, Paging, )
supermod.ListOfUserSettingsPage_14.subclass = ListOfUserSettingsPage_14Sub
# end class ListOfUserSettingsPage_14Sub


class UserSettings_14Sub(supermod.UserSettings_14):
    def __init__(self, FirstName=None, LastName=None, CultureCode=None, RegionCode=None, TimeZoneId=None, EmailDisabled=None):
        super(UserSettings_14Sub, self).__init__(FirstName, LastName, CultureCode, RegionCode, TimeZoneId, EmailDisabled, )
supermod.UserSettings_14.subclass = UserSettings_14Sub
# end class UserSettings_14Sub


class UserSettingsNotification_20Sub(supermod.UserSettingsNotification_20):
    def __init__(self, GroupNotification=None, AssistantNotification=None, DiscussionNotification=None, ChatNotification=None):
        super(UserSettingsNotification_20Sub, self).__init__(GroupNotification, AssistantNotification, DiscussionNotification, ChatNotification, )
supermod.UserSettingsNotification_20.subclass = UserSettingsNotification_20Sub
# end class UserSettingsNotification_20Sub


class UserSettingsLocationTracking_20Sub(supermod.UserSettingsLocationTracking_20):
    def __init__(self, Enabled=None):
        super(UserSettingsLocationTracking_20Sub, self).__init__(Enabled, )
supermod.UserSettingsLocationTracking_20.subclass = UserSettingsLocationTracking_20Sub
# end class UserSettingsLocationTracking_20Sub


class UserSettingsGMailSync_14Sub(supermod.UserSettingsGMailSync_14):
    def __init__(self, SyncApplicationId=None, IsEnabled=None, AuthorizationCode=None, RefreshToken=None, TopContactsList=None, Account=None):
        super(UserSettingsGMailSync_14Sub, self).__init__(SyncApplicationId, IsEnabled, AuthorizationCode, RefreshToken, TopContactsList, Account, )
supermod.UserSettingsGMailSync_14.subclass = UserSettingsGMailSync_14Sub
# end class UserSettingsGMailSync_14Sub


class GmailAccountInfo_14Sub(supermod.GmailAccountInfo_14):
    def __init__(self, UserId=None, Name=None, Email=None):
        super(GmailAccountInfo_14Sub, self).__init__(UserId, Name, Email, )
supermod.GmailAccountInfo_14.subclass = GmailAccountInfo_14Sub
# end class GmailAccountInfo_14Sub


class ListOfTopContacts_14Sub(supermod.ListOfTopContacts_14):
    def __init__(self, Contact=None):
        super(ListOfTopContacts_14Sub, self).__init__(Contact, )
supermod.ListOfTopContacts_14.subclass = ListOfTopContacts_14Sub
# end class ListOfTopContacts_14Sub


class UserSettingsGMailSync_16Sub(supermod.UserSettingsGMailSync_16):
    def __init__(self, SyncApplicationId=None, IsEnabled=None, AuthorizationCode=None, RefreshToken=None, Account=None, MarkAsRead=None, ImportDayRange=None, FolderItems=None):
        super(UserSettingsGMailSync_16Sub, self).__init__(SyncApplicationId, IsEnabled, AuthorizationCode, RefreshToken, Account, MarkAsRead, ImportDayRange, FolderItems, )
supermod.UserSettingsGMailSync_16.subclass = UserSettingsGMailSync_16Sub
# end class UserSettingsGMailSync_16Sub


class ListOfFolders_16Sub(supermod.ListOfFolders_16):
    def __init__(self, Folder=None):
        super(ListOfFolders_16Sub, self).__init__(Folder, )
supermod.ListOfFolders_16.subclass = ListOfFolders_16Sub
# end class ListOfFolders_16Sub


class UserSettingsMicrosoftExchangeSync_16Sub(supermod.UserSettingsMicrosoftExchangeSync_16):
    def __init__(self, SyncApplicationId=None, IsEnabled=None, Email=None, Secret=None, Domain=None, MarkAsRead=None, ImportDayRange=None, FolderItems=None):
        super(UserSettingsMicrosoftExchangeSync_16Sub, self).__init__(SyncApplicationId, IsEnabled, Email, Secret, Domain, MarkAsRead, ImportDayRange, FolderItems, )
supermod.UserSettingsMicrosoftExchangeSync_16.subclass = UserSettingsMicrosoftExchangeSync_16Sub
# end class UserSettingsMicrosoftExchangeSync_16Sub


class GroupEmail_17Sub(supermod.GroupEmail_17):
    def __init__(self, Address=None, NameSuffix=None):
        super(GroupEmail_17Sub, self).__init__(Address, NameSuffix, )
supermod.GroupEmail_17.subclass = GroupEmail_17Sub
# end class GroupEmail_17Sub


class GroupAvatar_17Sub(supermod.GroupAvatar_17):
    def __init__(self, GroupId=None):
        super(GroupAvatar_17Sub, self).__init__(GroupId, )
supermod.GroupAvatar_17.subclass = GroupAvatar_17Sub
# end class GroupAvatar_17Sub


class BoardAvatar_22Sub(supermod.BoardAvatar_22):
    def __init__(self, BoardId=None):
        super(BoardAvatar_22Sub, self).__init__(BoardId, )
supermod.BoardAvatar_22.subclass = BoardAvatar_22Sub
# end class BoardAvatar_22Sub


class GroupNotificationSettings_17Sub(supermod.GroupNotificationSettings_17):
    def __init__(self, GroupId=None, Disabled=None):
        super(GroupNotificationSettings_17Sub, self).__init__(GroupId, Disabled, )
supermod.GroupNotificationSettings_17.subclass = GroupNotificationSettings_17Sub
# end class GroupNotificationSettings_17Sub


class Campaign_12Sub(supermod.Campaign_12):
    def __init__(self, UtmSource=None, UtmMedium=None, UtmCampaign=None, LandingPage=None):
        super(Campaign_12Sub, self).__init__(UtmSource, UtmMedium, UtmCampaign, LandingPage, )
supermod.Campaign_12.subclass = Campaign_12Sub
# end class Campaign_12Sub


class Referral_13Sub(supermod.Referral_13):
    def __init__(self, CommunityReferralId=None, ForeignReferralId=None):
        super(Referral_13Sub, self).__init__(CommunityReferralId, ForeignReferralId, )
supermod.Referral_13.subclass = Referral_13Sub
# end class Referral_13Sub


class Language_12Sub(supermod.Language_12):
    def __init__(self, CultureCode=None, Name=None):
        super(Language_12Sub, self).__init__(CultureCode, Name, )
supermod.Language_12.subclass = Language_12Sub
# end class Language_12Sub


class ListOfLanguages_12Sub(supermod.ListOfLanguages_12):
    def __init__(self, Language=None):
        super(ListOfLanguages_12Sub, self).__init__(Language, )
supermod.ListOfLanguages_12.subclass = ListOfLanguages_12Sub
# end class ListOfLanguages_12Sub


class Language_14Sub(supermod.Language_14):
    def __init__(self, CultureCode=None, Name=None):
        super(Language_14Sub, self).__init__(CultureCode, Name, )
supermod.Language_14.subclass = Language_14Sub
# end class Language_14Sub


class ListOfLanguages_14Sub(supermod.ListOfLanguages_14):
    def __init__(self, Language=None):
        super(ListOfLanguages_14Sub, self).__init__(Language, )
supermod.ListOfLanguages_14.subclass = ListOfLanguages_14Sub
# end class ListOfLanguages_14Sub


class ListOfLanguagesPage_14Sub(supermod.ListOfLanguagesPage_14):
    def __init__(self, ListOfLanguages=None, Paging=None):
        super(ListOfLanguagesPage_14Sub, self).__init__(ListOfLanguages, Paging, )
supermod.ListOfLanguagesPage_14.subclass = ListOfLanguagesPage_14Sub
# end class ListOfLanguagesPage_14Sub


class Region_14Sub(supermod.Region_14):
    def __init__(self, RegionCode=None, Name=None):
        super(Region_14Sub, self).__init__(RegionCode, Name, )
supermod.Region_14.subclass = Region_14Sub
# end class Region_14Sub


class ListOfRegions_14Sub(supermod.ListOfRegions_14):
    def __init__(self, Region=None):
        super(ListOfRegions_14Sub, self).__init__(Region, )
supermod.ListOfRegions_14.subclass = ListOfRegions_14Sub
# end class ListOfRegions_14Sub


class ListOfRegionsPage_14Sub(supermod.ListOfRegionsPage_14):
    def __init__(self, ListOfRegions=None, Paging=None):
        super(ListOfRegionsPage_14Sub, self).__init__(ListOfRegions, Paging, )
supermod.ListOfRegionsPage_14.subclass = ListOfRegionsPage_14Sub
# end class ListOfRegionsPage_14Sub


class TimeZone_14Sub(supermod.TimeZone_14):
    def __init__(self, Id=None, Name=None):
        super(TimeZone_14Sub, self).__init__(Id, Name, )
supermod.TimeZone_14.subclass = TimeZone_14Sub
# end class TimeZone_14Sub


class ListOfTimeZones_14Sub(supermod.ListOfTimeZones_14):
    def __init__(self, TimeZone=None):
        super(ListOfTimeZones_14Sub, self).__init__(TimeZone, )
supermod.ListOfTimeZones_14.subclass = ListOfTimeZones_14Sub
# end class ListOfTimeZones_14Sub


class ListOfTimeZonesPage_14Sub(supermod.ListOfTimeZonesPage_14):
    def __init__(self, ListOfTimeZones=None, Paging=None):
        super(ListOfTimeZonesPage_14Sub, self).__init__(ListOfTimeZones, Paging, )
supermod.ListOfTimeZonesPage_14.subclass = ListOfTimeZonesPage_14Sub
# end class ListOfTimeZonesPage_14Sub


class Feed_22Sub(supermod.Feed_22):
    def __init__(self, DiscussionListPage=None):
        super(Feed_22Sub, self).__init__(DiscussionListPage, )
supermod.Feed_22.subclass = Feed_22Sub
# end class Feed_22Sub


class Feed_20Sub(supermod.Feed_20):
    def __init__(self, DiscussionListPage=None):
        super(Feed_20Sub, self).__init__(DiscussionListPage, )
supermod.Feed_20.subclass = Feed_20Sub
# end class Feed_20Sub


class ListOfDiscussionsPage_22Sub(supermod.ListOfDiscussionsPage_22):
    def __init__(self, DiscussionList=None, Paging=None):
        super(ListOfDiscussionsPage_22Sub, self).__init__(DiscussionList, Paging, )
supermod.ListOfDiscussionsPage_22.subclass = ListOfDiscussionsPage_22Sub
# end class ListOfDiscussionsPage_22Sub


class ListOfDiscussions_22Sub(supermod.ListOfDiscussions_22):
    def __init__(self, Discussion=None):
        super(ListOfDiscussions_22Sub, self).__init__(Discussion, )
supermod.ListOfDiscussions_22.subclass = ListOfDiscussions_22Sub
# end class ListOfDiscussions_22Sub


class ListOfDiscussionCardsPage_22Sub(supermod.ListOfDiscussionCardsPage_22):
    def __init__(self, CardList=None, Paging=None):
        super(ListOfDiscussionCardsPage_22Sub, self).__init__(CardList, Paging, )
supermod.ListOfDiscussionCardsPage_22.subclass = ListOfDiscussionCardsPage_22Sub
# end class ListOfDiscussionCardsPage_22Sub


class ListOfDiscussionCards_22Sub(supermod.ListOfDiscussionCards_22):
    def __init__(self, Discussion=None):
        super(ListOfDiscussionCards_22Sub, self).__init__(Discussion, )
supermod.ListOfDiscussionCards_22.subclass = ListOfDiscussionCards_22Sub
# end class ListOfDiscussionCards_22Sub


class ListOfDiscussionsPage_20Sub(supermod.ListOfDiscussionsPage_20):
    def __init__(self, DiscussionList=None, Paging=None):
        super(ListOfDiscussionsPage_20Sub, self).__init__(DiscussionList, Paging, )
supermod.ListOfDiscussionsPage_20.subclass = ListOfDiscussionsPage_20Sub
# end class ListOfDiscussionsPage_20Sub


class ListOfDiscussions_20Sub(supermod.ListOfDiscussions_20):
    def __init__(self, Discussion=None):
        super(ListOfDiscussions_20Sub, self).__init__(Discussion, )
supermod.ListOfDiscussions_20.subclass = ListOfDiscussions_20Sub
# end class ListOfDiscussions_20Sub


class ListOfDiscussionsPage_18Sub(supermod.ListOfDiscussionsPage_18):
    def __init__(self, DiscussionList=None, Paging=None):
        super(ListOfDiscussionsPage_18Sub, self).__init__(DiscussionList, Paging, )
supermod.ListOfDiscussionsPage_18.subclass = ListOfDiscussionsPage_18Sub
# end class ListOfDiscussionsPage_18Sub


class ListOfDiscussions_18Sub(supermod.ListOfDiscussions_18):
    def __init__(self, Discussion=None):
        super(ListOfDiscussions_18Sub, self).__init__(Discussion, )
supermod.ListOfDiscussions_18.subclass = ListOfDiscussions_18Sub
# end class ListOfDiscussions_18Sub


class ListOfDiscussionActivityItemsPage_18Sub(supermod.ListOfDiscussionActivityItemsPage_18):
    def __init__(self, DiscussionActivityItemList=None, MoreUnreadCount=None, TotalUnreadCount=None, Paging=None):
        super(ListOfDiscussionActivityItemsPage_18Sub, self).__init__(DiscussionActivityItemList, MoreUnreadCount, TotalUnreadCount, Paging, )
supermod.ListOfDiscussionActivityItemsPage_18.subclass = ListOfDiscussionActivityItemsPage_18Sub
# end class ListOfDiscussionActivityItemsPage_18Sub


class ListOfDiscussionActivityItems_18Sub(supermod.ListOfDiscussionActivityItems_18):
    def __init__(self, DiscussionActivityItem=None):
        super(ListOfDiscussionActivityItems_18Sub, self).__init__(DiscussionActivityItem, )
supermod.ListOfDiscussionActivityItems_18.subclass = ListOfDiscussionActivityItems_18Sub
# end class ListOfDiscussionActivityItems_18Sub


class DiscussionActivityItemPost_18Sub(supermod.DiscussionActivityItemPost_18):
    def __init__(self, Post=None, Unread=None, ErrorSending=None, ImportedViaEmail=None, ForwardedCopy=None, BodyFormat=None):
        super(DiscussionActivityItemPost_18Sub, self).__init__(Post, Unread, ErrorSending, ImportedViaEmail, ForwardedCopy, BodyFormat, )
supermod.DiscussionActivityItemPost_18.subclass = DiscussionActivityItemPost_18Sub
# end class DiscussionActivityItemPost_18Sub


class BodyFormat_18Sub(supermod.BodyFormat_18):
    def __init__(self, MimeTypeList=None, DefaultMimeType=None, DefaultThumbnailPreview=None):
        super(BodyFormat_18Sub, self).__init__(MimeTypeList, DefaultMimeType, DefaultThumbnailPreview, )
supermod.BodyFormat_18.subclass = BodyFormat_18Sub
# end class BodyFormat_18Sub


class ListOfPostsPage_22Sub(supermod.ListOfPostsPage_22):
    def __init__(self, Posts=None, Paging=None):
        super(ListOfPostsPage_22Sub, self).__init__(Posts, Paging, )
supermod.ListOfPostsPage_22.subclass = ListOfPostsPage_22Sub
# end class ListOfPostsPage_22Sub


class ListOfPosts_22Sub(supermod.ListOfPosts_22):
    def __init__(self, Post=None):
        super(ListOfPosts_22Sub, self).__init__(Post, )
supermod.ListOfPosts_22.subclass = ListOfPosts_22Sub
# end class ListOfPosts_22Sub


class ListOfPostUnreadPage_22Sub(supermod.ListOfPostUnreadPage_22):
    def __init__(self, PostUnreads=None, Paging=None):
        super(ListOfPostUnreadPage_22Sub, self).__init__(PostUnreads, Paging, )
supermod.ListOfPostUnreadPage_22.subclass = ListOfPostUnreadPage_22Sub
# end class ListOfPostUnreadPage_22Sub


class ListOfPostUnread_22Sub(supermod.ListOfPostUnread_22):
    def __init__(self, PostUnread=None):
        super(ListOfPostUnread_22Sub, self).__init__(PostUnread, )
supermod.ListOfPostUnread_22.subclass = ListOfPostUnread_22Sub
# end class ListOfPostUnread_22Sub


class ListOfPostsPage_20Sub(supermod.ListOfPostsPage_20):
    def __init__(self, Posts=None, Paging=None):
        super(ListOfPostsPage_20Sub, self).__init__(Posts, Paging, )
supermod.ListOfPostsPage_20.subclass = ListOfPostsPage_20Sub
# end class ListOfPostsPage_20Sub


class ListOfPosts_20Sub(supermod.ListOfPosts_20):
    def __init__(self, Post=None):
        super(ListOfPosts_20Sub, self).__init__(Post, )
supermod.ListOfPosts_20.subclass = ListOfPosts_20Sub
# end class ListOfPosts_20Sub


class PostPreview_20Sub(supermod.PostPreview_20):
    def __init__(self, Files=None, BodyHtml=None):
        super(PostPreview_20Sub, self).__init__(Files, BodyHtml, )
supermod.PostPreview_20.subclass = PostPreview_20Sub
# end class PostPreview_20Sub


class PostPinnedToList_22Sub(supermod.PostPinnedToList_22):
    def __init__(self, BoardList=None):
        super(PostPinnedToList_22Sub, self).__init__(BoardList, )
supermod.PostPinnedToList_22.subclass = PostPinnedToList_22Sub
# end class PostPinnedToList_22Sub


class PostPinnedToList_21Sub(supermod.PostPinnedToList_21):
    def __init__(self, BoardList=None):
        super(PostPinnedToList_21Sub, self).__init__(BoardList, )
supermod.PostPinnedToList_21.subclass = PostPinnedToList_21Sub
# end class PostPinnedToList_21Sub


class PostPinnedToList_20Sub(supermod.PostPinnedToList_20):
    def __init__(self, BoardList=None):
        super(PostPinnedToList_20Sub, self).__init__(BoardList, )
supermod.PostPinnedToList_20.subclass = PostPinnedToList_20Sub
# end class PostPinnedToList_20Sub


class PostBoardLink_22Sub(supermod.PostBoardLink_22):
    def __init__(self, BoardId=None, Action=None):
        super(PostBoardLink_22Sub, self).__init__(BoardId, Action, )
supermod.PostBoardLink_22.subclass = PostBoardLink_22Sub
# end class PostBoardLink_22Sub


class Invite_20Sub(supermod.Invite_20):
    def __init__(self, InviteUrl=None, InviteBody=None):
        super(Invite_20Sub, self).__init__(InviteUrl, InviteBody, )
supermod.Invite_20.subclass = Invite_20Sub
# end class Invite_20Sub


class ListOfSignatures_20Sub(supermod.ListOfSignatures_20):
    def __init__(self, Signature=None):
        super(ListOfSignatures_20Sub, self).__init__(Signature, )
supermod.ListOfSignatures_20.subclass = ListOfSignatures_20Sub
# end class ListOfSignatures_20Sub


class ListOfSignaturesPage_20Sub(supermod.ListOfSignaturesPage_20):
    def __init__(self, Default=None, ListOfSignatures=None, Paging=None):
        super(ListOfSignaturesPage_20Sub, self).__init__(Default, ListOfSignatures, Paging, )
supermod.ListOfSignaturesPage_20.subclass = ListOfSignaturesPage_20Sub
# end class ListOfSignaturesPage_20Sub


class AssistantInsight_22Sub(supermod.AssistantInsight_22):
    def __init__(self, Insight=None, Snippet=None):
        super(AssistantInsight_22Sub, self).__init__(Insight, Snippet, )
supermod.AssistantInsight_22.subclass = AssistantInsight_22Sub
# end class AssistantInsight_22Sub


class ListOfAgendaPage_22Sub(supermod.ListOfAgendaPage_22):
    def __init__(self, AgendaList=None, Paging=None):
        super(ListOfAgendaPage_22Sub, self).__init__(AgendaList, Paging, )
supermod.ListOfAgendaPage_22.subclass = ListOfAgendaPage_22Sub
# end class ListOfAgendaPage_22Sub


class AgendaItem_22Sub(supermod.AgendaItem_22):
    def __init__(self, DueDate=None, AgendaItem=None):
        super(AgendaItem_22Sub, self).__init__(DueDate, AgendaItem, )
supermod.AgendaItem_22.subclass = AgendaItem_22Sub
# end class AgendaItem_22Sub


class ListOfAgendaItems_22Sub(supermod.ListOfAgendaItems_22):
    def __init__(self, Resource=None):
        super(ListOfAgendaItems_22Sub, self).__init__(Resource, )
supermod.ListOfAgendaItems_22.subclass = ListOfAgendaItems_22Sub
# end class ListOfAgendaItems_22Sub


class AgendaSummary_22Sub(supermod.AgendaSummary_22):
    def __init__(self, ListOfFirstItems=None, ListOfUpcomingItems=None, PreviousItem=None):
        super(AgendaSummary_22Sub, self).__init__(ListOfFirstItems, ListOfUpcomingItems, PreviousItem, )
supermod.AgendaSummary_22.subclass = AgendaSummary_22Sub
# end class AgendaSummary_22Sub


class AppointmentListPage_20Sub(supermod.AppointmentListPage_20):
    def __init__(self, AppointmentList=None, Paging=None):
        super(AppointmentListPage_20Sub, self).__init__(AppointmentList, Paging, )
supermod.AppointmentListPage_20.subclass = AppointmentListPage_20Sub
# end class AppointmentListPage_20Sub


class ListOfAppointment_20Sub(supermod.ListOfAppointment_20):
    def __init__(self, Appointment=None):
        super(ListOfAppointment_20Sub, self).__init__(Appointment, )
supermod.ListOfAppointment_20.subclass = ListOfAppointment_20Sub
# end class ListOfAppointment_20Sub


class AppointmentResponse_20Sub(supermod.AppointmentResponse_20):
    def __init__(self, CalendarUId=None, PostId=None, Status=None):
        super(AppointmentResponse_20Sub, self).__init__(CalendarUId, PostId, Status, )
supermod.AppointmentResponse_20.subclass = AppointmentResponse_20Sub
# end class AppointmentResponse_20Sub


class ListOfAttendees_20Sub(supermod.ListOfAttendees_20):
    def __init__(self, Resource=None):
        super(ListOfAttendees_20Sub, self).__init__(Resource, )
supermod.ListOfAttendees_20.subclass = ListOfAttendees_20Sub
# end class ListOfAttendees_20Sub


class AppointmentTime_20Sub(supermod.AppointmentTime_20):
    def __init__(self, StartTime=None, EndTime=None, IsAllDay=None, Timezone=None):
        super(AppointmentTime_20Sub, self).__init__(StartTime, EndTime, IsAllDay, Timezone, )
supermod.AppointmentTime_20.subclass = AppointmentTime_20Sub
# end class AppointmentTime_20Sub


class ListOfAppointmentReminders_20Sub(supermod.ListOfAppointmentReminders_20):
    def __init__(self, AppointmentReminder=None):
        super(ListOfAppointmentReminders_20Sub, self).__init__(AppointmentReminder, )
supermod.ListOfAppointmentReminders_20.subclass = ListOfAppointmentReminders_20Sub
# end class ListOfAppointmentReminders_20Sub


class AppointmentReminder_20Sub(supermod.AppointmentReminder_20):
    def __init__(self, MinutesReminder=None):
        super(AppointmentReminder_20Sub, self).__init__(MinutesReminder, )
supermod.AppointmentReminder_20.subclass = AppointmentReminder_20Sub
# end class AppointmentReminder_20Sub


class ListOfAppointmentRecurrence_20Sub(supermod.ListOfAppointmentRecurrence_20):
    def __init__(self, AppointmentRecurrence=None):
        super(ListOfAppointmentRecurrence_20Sub, self).__init__(AppointmentRecurrence, )
supermod.ListOfAppointmentRecurrence_20.subclass = ListOfAppointmentRecurrence_20Sub
# end class ListOfAppointmentRecurrence_20Sub


class AppointmentRecurrence_20Sub(supermod.AppointmentRecurrence_20):
    def __init__(self, RecurrenceInterval=None, RecurrenceType=None, RecurrenceStopTime=None, RecurrenceDayOfWeek=None, RecurrenceDayOfMonth=None, RecurrenceMonth=None):
        super(AppointmentRecurrence_20Sub, self).__init__(RecurrenceInterval, RecurrenceType, RecurrenceStopTime, RecurrenceDayOfWeek, RecurrenceDayOfMonth, RecurrenceMonth, )
supermod.AppointmentRecurrence_20.subclass = AppointmentRecurrence_20Sub
# end class AppointmentRecurrence_20Sub


class ListOfContactCardItem_22Sub(supermod.ListOfContactCardItem_22):
    def __init__(self, ContactCardItem=None):
        super(ListOfContactCardItem_22Sub, self).__init__(ContactCardItem, )
supermod.ListOfContactCardItem_22.subclass = ListOfContactCardItem_22Sub
# end class ListOfContactCardItem_22Sub


class ContactCardItem_22Sub(supermod.ContactCardItem_22):
    def __init__(self, Value=None, Type=None):
        super(ContactCardItem_22Sub, self).__init__(Value, Type, )
supermod.ContactCardItem_22.subclass = ContactCardItem_22Sub
# end class ContactCardItem_22Sub


class BadgeBase_15Sub(supermod.BadgeBase_15):
    def __init__(self, Count=None):
        super(BadgeBase_15Sub, self).__init__(Count, )
supermod.BadgeBase_15.subclass = BadgeBase_15Sub
# end class BadgeBase_15Sub


class ActivityChart_13Sub(supermod.ActivityChart_13):
    def __init__(self, Start=None, End=None, ActivityList=None):
        super(ActivityChart_13Sub, self).__init__(Start, End, ActivityList, )
supermod.ActivityChart_13.subclass = ActivityChart_13Sub
# end class ActivityChart_13Sub


class ListOfActivities_13Sub(supermod.ListOfActivities_13):
    def __init__(self, Activity=None):
        super(ListOfActivities_13Sub, self).__init__(Activity, )
supermod.ListOfActivities_13.subclass = ListOfActivities_13Sub
# end class ListOfActivities_13Sub


class ActivityItem_13Sub(supermod.ActivityItem_13):
    def __init__(self, Day=None, Index=None):
        super(ActivityItem_13Sub, self).__init__(Day, Index, )
supermod.ActivityItem_13.subclass = ActivityItem_13Sub
# end class ActivityItem_13Sub


class SelectedSortAction_13Sub(supermod.SelectedSortAction_13):
    def __init__(self, Direction=None):
        super(SelectedSortAction_13Sub, self).__init__(Direction, )
supermod.SelectedSortAction_13.subclass = SelectedSortAction_13Sub
# end class SelectedSortAction_13Sub


class ListOfSortActions_13Sub(supermod.ListOfSortActions_13):
    def __init__(self, SortAction=None):
        super(ListOfSortActions_13Sub, self).__init__(SortAction, )
supermod.ListOfSortActions_13.subclass = ListOfSortActions_13Sub
# end class ListOfSortActions_13Sub


class SortDirectionHint_13Sub(supermod.SortDirectionHint_13):
    def __init__(self, Ascending=None, Descending=None):
        super(SortDirectionHint_13Sub, self).__init__(Ascending, Descending, )
supermod.SortDirectionHint_13.subclass = SortDirectionHint_13Sub
# end class SortDirectionHint_13Sub


class Drive_14Sub(supermod.Drive_14):
    def __init__(self, DriveItemGroupList=None, AvailableSortActionList=None):
        super(Drive_14Sub, self).__init__(DriveItemGroupList, AvailableSortActionList, )
supermod.Drive_14.subclass = Drive_14Sub
# end class Drive_14Sub


class DriveItemGroupBase_14Sub(supermod.DriveItemGroupBase_14):
    def __init__(self, Id=None, Name=None):
        super(DriveItemGroupBase_14Sub, self).__init__(Id, Name, )
supermod.DriveItemGroupBase_14.subclass = DriveItemGroupBase_14Sub
# end class DriveItemGroupBase_14Sub


class ListOfDriveItemGroups_14Sub(supermod.ListOfDriveItemGroups_14):
    def __init__(self, DriveItemGroup=None):
        super(ListOfDriveItemGroups_14Sub, self).__init__(DriveItemGroup, )
supermod.ListOfDriveItemGroups_14.subclass = ListOfDriveItemGroups_14Sub
# end class ListOfDriveItemGroups_14Sub


class DriveItemGroupDocuments_14Sub(supermod.DriveItemGroupDocuments_14):
    def __init__(self, DocumentListPage=None):
        super(DriveItemGroupDocuments_14Sub, self).__init__(DocumentListPage, )
supermod.DriveItemGroupDocuments_14.subclass = DriveItemGroupDocuments_14Sub
# end class DriveItemGroupDocuments_14Sub


class ClientEventLog_15Sub(supermod.ClientEventLog_15):
    def __init__(self, Application=None, Action=None, Created=None, ParameterList=None):
        super(ClientEventLog_15Sub, self).__init__(Application, Action, Created, ParameterList, )
supermod.ClientEventLog_15.subclass = ClientEventLog_15Sub
# end class ClientEventLog_15Sub


class ClientOnboardingEventLog_15Sub(supermod.ClientOnboardingEventLog_15):
    def __init__(self):
        super(ClientOnboardingEventLog_15Sub, self).__init__()
supermod.ClientOnboardingEventLog_15.subclass = ClientOnboardingEventLog_15Sub
# end class ClientOnboardingEventLog_15Sub


class ClientStatisticEventLog_15Sub(supermod.ClientStatisticEventLog_15):
    def __init__(self):
        super(ClientStatisticEventLog_15Sub, self).__init__()
supermod.ClientStatisticEventLog_15.subclass = ClientStatisticEventLog_15Sub
# end class ClientStatisticEventLog_15Sub


class Parameter_15Sub(supermod.Parameter_15):
    def __init__(self, Name=None, Value=None):
        super(Parameter_15Sub, self).__init__(Name, Value, )
supermod.Parameter_15.subclass = Parameter_15Sub
# end class Parameter_15Sub


class ListOfParameters_15Sub(supermod.ListOfParameters_15):
    def __init__(self, Parameter=None):
        super(ListOfParameters_15Sub, self).__init__(Parameter, )
supermod.ListOfParameters_15.subclass = ListOfParameters_15Sub
# end class ListOfParameters_15Sub


class ListOfClientEventLogs_15Sub(supermod.ListOfClientEventLogs_15):
    def __init__(self, ClientEventLog=None):
        super(ListOfClientEventLogs_15Sub, self).__init__(ClientEventLog, )
supermod.ListOfClientEventLogs_15.subclass = ListOfClientEventLogs_15Sub
# end class ListOfClientEventLogs_15Sub


class ListOfClientEventLogsPage_15Sub(supermod.ListOfClientEventLogsPage_15):
    def __init__(self, ClientEventLogList=None, Paging=None):
        super(ListOfClientEventLogsPage_15Sub, self).__init__(ClientEventLogList, Paging, )
supermod.ListOfClientEventLogsPage_15.subclass = ListOfClientEventLogsPage_15Sub
# end class ListOfClientEventLogsPage_15Sub


class ClientErrorLog_4Sub(supermod.ClientErrorLog_4):
    def __init__(self, Message=None):
        super(ClientErrorLog_4Sub, self).__init__(Message, )
supermod.ClientErrorLog_4.subclass = ClientErrorLog_4Sub
# end class ClientErrorLog_4Sub


class Paging_1Sub(supermod.Paging_1):
    def __init__(self, Offset=None, Size=None):
        super(Paging_1Sub, self).__init__(Offset, Size, )
supermod.Paging_1.subclass = Paging_1Sub
# end class Paging_1Sub


class Paging_13Sub(supermod.Paging_13):
    def __init__(self, TotalSize=None):
        super(Paging_13Sub, self).__init__(TotalSize, )
supermod.Paging_13.subclass = Paging_13Sub
# end class Paging_13Sub


class AccessTokenInfo_13Sub(supermod.AccessTokenInfo_13):
    def __init__(self, Id=None, UserId=None, CommunityId=None, CultureCode=None, Created=None, ValidTill=None):
        super(AccessTokenInfo_13Sub, self).__init__(Id, UserId, CommunityId, CultureCode, Created, ValidTill, )
supermod.AccessTokenInfo_13.subclass = AccessTokenInfo_13Sub
# end class AccessTokenInfo_13Sub


class AccessTokenInfoUser_13Sub(supermod.AccessTokenInfoUser_13):
    def __init__(self):
        super(AccessTokenInfoUser_13Sub, self).__init__()
supermod.AccessTokenInfoUser_13.subclass = AccessTokenInfoUser_13Sub
# end class AccessTokenInfoUser_13Sub


class AccessTokenInfo_17Sub(supermod.AccessTokenInfo_17):
    def __init__(self, Id=None, UserId=None, Created=None, ValidTill=None, AccessScopeList=None):
        super(AccessTokenInfo_17Sub, self).__init__(Id, UserId, Created, ValidTill, AccessScopeList, )
supermod.AccessTokenInfo_17.subclass = AccessTokenInfo_17Sub
# end class AccessTokenInfo_17Sub


class AccessScope_17Sub(supermod.AccessScope_17):
    def __init__(self, Id=None, Type=None):
        super(AccessScope_17Sub, self).__init__(Id, Type, )
supermod.AccessScope_17.subclass = AccessScope_17Sub
# end class AccessScope_17Sub


class ListOfAccessScopes_17Sub(supermod.ListOfAccessScopes_17):
    def __init__(self, AccessScope=None):
        super(ListOfAccessScopes_17Sub, self).__init__(AccessScope, )
supermod.ListOfAccessScopes_17.subclass = ListOfAccessScopes_17Sub
# end class ListOfAccessScopes_17Sub


class AccessToken_14Sub(supermod.AccessToken_14):
    def __init__(self, AccessToken=None, RefreshToken=None, TokenType=None):
        super(AccessToken_14Sub, self).__init__(AccessToken, RefreshToken, TokenType, )
supermod.AccessToken_14.subclass = AccessToken_14Sub
# end class AccessToken_14Sub


class GoogleTokenSub(supermod.GoogleToken):
    def __init__(self, AccessToken=None, RefreshToken=None):
        super(GoogleTokenSub, self).__init__(AccessToken, RefreshToken, )
supermod.GoogleToken.subclass = GoogleTokenSub
# end class GoogleTokenSub


class ListOfBoardsPage_22Sub(supermod.ListOfBoardsPage_22):
    def __init__(self, BoardList=None, Paging=None):
        super(ListOfBoardsPage_22Sub, self).__init__(BoardList, Paging, )
supermod.ListOfBoardsPage_22.subclass = ListOfBoardsPage_22Sub
# end class ListOfBoardsPage_22Sub


class ListOfBoards_22Sub(supermod.ListOfBoards_22):
    def __init__(self, Board=None):
        super(ListOfBoards_22Sub, self).__init__(Board, )
supermod.ListOfBoards_22.subclass = ListOfBoards_22Sub
# end class ListOfBoards_22Sub


class ListOfPinnedItems_22Sub(supermod.ListOfPinnedItems_22):
    def __init__(self, PinnedItem=None):
        super(ListOfPinnedItems_22Sub, self).__init__(PinnedItem, )
supermod.ListOfPinnedItems_22.subclass = ListOfPinnedItems_22Sub
# end class ListOfPinnedItems_22Sub


class PinnedItem_22Sub(supermod.PinnedItem_22):
    def __init__(self, Resource=None, SortOrder=None):
        super(PinnedItem_22Sub, self).__init__(Resource, SortOrder, )
supermod.PinnedItem_22.subclass = PinnedItem_22Sub
# end class PinnedItem_22Sub


class BoardName_22Sub(supermod.BoardName_22):
    def __init__(self, BoardName=None):
        super(BoardName_22Sub, self).__init__(BoardName, )
supermod.BoardName_22.subclass = BoardName_22Sub
# end class BoardName_22Sub


class ListOfBoardsPage_21Sub(supermod.ListOfBoardsPage_21):
    def __init__(self, BoardList=None, Paging=None):
        super(ListOfBoardsPage_21Sub, self).__init__(BoardList, Paging, )
supermod.ListOfBoardsPage_21.subclass = ListOfBoardsPage_21Sub
# end class ListOfBoardsPage_21Sub


class ListOfBoards_21Sub(supermod.ListOfBoards_21):
    def __init__(self, Board=None):
        super(ListOfBoards_21Sub, self).__init__(Board, )
supermod.ListOfBoards_21.subclass = ListOfBoards_21Sub
# end class ListOfBoards_21Sub


class ListOfPinnedItems_21Sub(supermod.ListOfPinnedItems_21):
    def __init__(self, PinnedItem=None):
        super(ListOfPinnedItems_21Sub, self).__init__(PinnedItem, )
supermod.ListOfPinnedItems_21.subclass = ListOfPinnedItems_21Sub
# end class ListOfPinnedItems_21Sub


class PinnedItem_21Sub(supermod.PinnedItem_21):
    def __init__(self, Resource=None, SortOrder=None):
        super(PinnedItem_21Sub, self).__init__(Resource, SortOrder, )
supermod.PinnedItem_21.subclass = PinnedItem_21Sub
# end class PinnedItem_21Sub


class ListOfBoardsPage_20Sub(supermod.ListOfBoardsPage_20):
    def __init__(self, BoardList=None, Paging=None):
        super(ListOfBoardsPage_20Sub, self).__init__(BoardList, Paging, )
supermod.ListOfBoardsPage_20.subclass = ListOfBoardsPage_20Sub
# end class ListOfBoardsPage_20Sub


class ListOfBoards_20Sub(supermod.ListOfBoards_20):
    def __init__(self, Board=None):
        super(ListOfBoards_20Sub, self).__init__(Board, )
supermod.ListOfBoards_20.subclass = ListOfBoards_20Sub
# end class ListOfBoards_20Sub


class ListOfBoardsPage_15Sub(supermod.ListOfBoardsPage_15):
    def __init__(self, BoardList=None, Paging=None):
        super(ListOfBoardsPage_15Sub, self).__init__(BoardList, Paging, )
supermod.ListOfBoardsPage_15.subclass = ListOfBoardsPage_15Sub
# end class ListOfBoardsPage_15Sub


class ListOfBoards_15Sub(supermod.ListOfBoards_15):
    def __init__(self, Board=None):
        super(ListOfBoards_15Sub, self).__init__(Board, )
supermod.ListOfBoards_15.subclass = ListOfBoards_15Sub
# end class ListOfBoards_15Sub


class NotificationTrigger_18Sub(supermod.NotificationTrigger_18):
    def __init__(self, ResourceId=None, NotificationTriggerType=None):
        super(NotificationTrigger_18Sub, self).__init__(ResourceId, NotificationTriggerType, )
supermod.NotificationTrigger_18.subclass = NotificationTrigger_18Sub
# end class NotificationTrigger_18Sub


class ListOfNotificationTriggers_18Sub(supermod.ListOfNotificationTriggers_18):
    def __init__(self, NotificationTrigger=None):
        super(ListOfNotificationTriggers_18Sub, self).__init__(NotificationTrigger, )
supermod.ListOfNotificationTriggers_18.subclass = ListOfNotificationTriggers_18Sub
# end class ListOfNotificationTriggers_18Sub


class ListOfNotificationsPage_22Sub(supermod.ListOfNotificationsPage_22):
    def __init__(self, LastNotificationId=None, NotificationListPage=None, Paging=None):
        super(ListOfNotificationsPage_22Sub, self).__init__(LastNotificationId, NotificationListPage, Paging, )
supermod.ListOfNotificationsPage_22.subclass = ListOfNotificationsPage_22Sub
# end class ListOfNotificationsPage_22Sub


class ListOfNotifications_22Sub(supermod.ListOfNotifications_22):
    def __init__(self, Notification=None):
        super(ListOfNotifications_22Sub, self).__init__(Notification, )
supermod.ListOfNotifications_22.subclass = ListOfNotifications_22Sub
# end class ListOfNotifications_22Sub


class NotificationBase_22Sub(supermod.NotificationBase_22):
    def __init__(self, Id=None, Created=None, Recipient=None, TriggerList=None, AlertMessage=None, Sender=None):
        super(NotificationBase_22Sub, self).__init__(Id, Created, Recipient, TriggerList, AlertMessage, Sender, )
supermod.NotificationBase_22.subclass = NotificationBase_22Sub
# end class NotificationBase_22Sub


class NotificationStreamCreated_22Sub(supermod.NotificationStreamCreated_22):
    def __init__(self, Stream=None):
        super(NotificationStreamCreated_22Sub, self).__init__(Stream, )
supermod.NotificationStreamCreated_22.subclass = NotificationStreamCreated_22Sub
# end class NotificationStreamCreated_22Sub


class NotificationStreamUpdated_22Sub(supermod.NotificationStreamUpdated_22):
    def __init__(self, Stream=None):
        super(NotificationStreamUpdated_22Sub, self).__init__(Stream, )
supermod.NotificationStreamUpdated_22.subclass = NotificationStreamUpdated_22Sub
# end class NotificationStreamUpdated_22Sub


class NotificationStreamDeleted_22Sub(supermod.NotificationStreamDeleted_22):
    def __init__(self, Stream=None):
        super(NotificationStreamDeleted_22Sub, self).__init__(Stream, )
supermod.NotificationStreamDeleted_22.subclass = NotificationStreamDeleted_22Sub
# end class NotificationStreamDeleted_22Sub


class NotificationUserTokenInvalid_22Sub(supermod.NotificationUserTokenInvalid_22):
    def __init__(self, TokenProvider=None):
        super(NotificationUserTokenInvalid_22Sub, self).__init__(TokenProvider, )
supermod.NotificationUserTokenInvalid_22.subclass = NotificationUserTokenInvalid_22Sub
# end class NotificationUserTokenInvalid_22Sub


class NotificationMailboxMissing_22Sub(supermod.NotificationMailboxMissing_22):
    def __init__(self, TokenProvider=None):
        super(NotificationMailboxMissing_22Sub, self).__init__(TokenProvider, )
supermod.NotificationMailboxMissing_22.subclass = NotificationMailboxMissing_22Sub
# end class NotificationMailboxMissing_22Sub


class NotificationOnboardingComplete_22Sub(supermod.NotificationOnboardingComplete_22):
    def __init__(self):
        super(NotificationOnboardingComplete_22Sub, self).__init__()
supermod.NotificationOnboardingComplete_22.subclass = NotificationOnboardingComplete_22Sub
# end class NotificationOnboardingComplete_22Sub


class NotificationPostCreated_22Sub(supermod.NotificationPostCreated_22):
    def __init__(self, Post=None):
        super(NotificationPostCreated_22Sub, self).__init__(Post, )
supermod.NotificationPostCreated_22.subclass = NotificationPostCreated_22Sub
# end class NotificationPostCreated_22Sub


class NotificationPostUpdated_22Sub(supermod.NotificationPostUpdated_22):
    def __init__(self, Post=None):
        super(NotificationPostUpdated_22Sub, self).__init__(Post, )
supermod.NotificationPostUpdated_22.subclass = NotificationPostUpdated_22Sub
# end class NotificationPostUpdated_22Sub


class NotificationPostUnread_22Sub(supermod.NotificationPostUnread_22):
    def __init__(self, UnreadInfo=None):
        super(NotificationPostUnread_22Sub, self).__init__(UnreadInfo, )
supermod.NotificationPostUnread_22.subclass = NotificationPostUnread_22Sub
# end class NotificationPostUnread_22Sub


class NotificationPostActionListUpdated_22Sub(supermod.NotificationPostActionListUpdated_22):
    def __init__(self, PostActionList=None):
        super(NotificationPostActionListUpdated_22Sub, self).__init__(PostActionList, )
supermod.NotificationPostActionListUpdated_22.subclass = NotificationPostActionListUpdated_22Sub
# end class NotificationPostActionListUpdated_22Sub


class NotificationCardCreated_22Sub(supermod.NotificationCardCreated_22):
    def __init__(self, Card=None):
        super(NotificationCardCreated_22Sub, self).__init__(Card, )
supermod.NotificationCardCreated_22.subclass = NotificationCardCreated_22Sub
# end class NotificationCardCreated_22Sub


class NotificationCardUpdated_22Sub(supermod.NotificationCardUpdated_22):
    def __init__(self, Card=None):
        super(NotificationCardUpdated_22Sub, self).__init__(Card, )
supermod.NotificationCardUpdated_22.subclass = NotificationCardUpdated_22Sub
# end class NotificationCardUpdated_22Sub


class NotificationCardPinnedToListUpdated_22Sub(supermod.NotificationCardPinnedToListUpdated_22):
    def __init__(self, CardPinnedToList=None):
        super(NotificationCardPinnedToListUpdated_22Sub, self).__init__(CardPinnedToList, )
supermod.NotificationCardPinnedToListUpdated_22.subclass = NotificationCardPinnedToListUpdated_22Sub
# end class NotificationCardPinnedToListUpdated_22Sub


class NotificationUserStatusChange_22Sub(supermod.NotificationUserStatusChange_22):
    def __init__(self, OnlineStatus=None, LastActivityAt=None):
        super(NotificationUserStatusChange_22Sub, self).__init__(OnlineStatus, LastActivityAt, )
supermod.NotificationUserStatusChange_22.subclass = NotificationUserStatusChange_22Sub
# end class NotificationUserStatusChange_22Sub


class NotificationBoardCreated_22Sub(supermod.NotificationBoardCreated_22):
    def __init__(self, Board=None):
        super(NotificationBoardCreated_22Sub, self).__init__(Board, )
supermod.NotificationBoardCreated_22.subclass = NotificationBoardCreated_22Sub
# end class NotificationBoardCreated_22Sub


class NotificationBoardUpdated_22Sub(supermod.NotificationBoardUpdated_22):
    def __init__(self, Board=None):
        super(NotificationBoardUpdated_22Sub, self).__init__(Board, )
supermod.NotificationBoardUpdated_22.subclass = NotificationBoardUpdated_22Sub
# end class NotificationBoardUpdated_22Sub


class NotificationBoardDeleted_22Sub(supermod.NotificationBoardDeleted_22):
    def __init__(self, Board=None):
        super(NotificationBoardDeleted_22Sub, self).__init__(Board, )
supermod.NotificationBoardDeleted_22.subclass = NotificationBoardDeleted_22Sub
# end class NotificationBoardDeleted_22Sub


class NotificationPostAssistantCreated_22Sub(supermod.NotificationPostAssistantCreated_22):
    def __init__(self, PostAssistant=None):
        super(NotificationPostAssistantCreated_22Sub, self).__init__(PostAssistant, )
supermod.NotificationPostAssistantCreated_22.subclass = NotificationPostAssistantCreated_22Sub
# end class NotificationPostAssistantCreated_22Sub


class NotificationPostAssistantUpdated_22Sub(supermod.NotificationPostAssistantUpdated_22):
    def __init__(self, PostAssistant=None):
        super(NotificationPostAssistantUpdated_22Sub, self).__init__(PostAssistant, )
supermod.NotificationPostAssistantUpdated_22.subclass = NotificationPostAssistantUpdated_22Sub
# end class NotificationPostAssistantUpdated_22Sub


class NotificationPostAssistantDeleted_22Sub(supermod.NotificationPostAssistantDeleted_22):
    def __init__(self, PostAssistant=None):
        super(NotificationPostAssistantDeleted_22Sub, self).__init__(PostAssistant, )
supermod.NotificationPostAssistantDeleted_22.subclass = NotificationPostAssistantDeleted_22Sub
# end class NotificationPostAssistantDeleted_22Sub


class NotificationStreamAssistantCreated_22Sub(supermod.NotificationStreamAssistantCreated_22):
    def __init__(self, StreamAssistant=None):
        super(NotificationStreamAssistantCreated_22Sub, self).__init__(StreamAssistant, )
supermod.NotificationStreamAssistantCreated_22.subclass = NotificationStreamAssistantCreated_22Sub
# end class NotificationStreamAssistantCreated_22Sub


class NotificationStreamAssistantUpdated_22Sub(supermod.NotificationStreamAssistantUpdated_22):
    def __init__(self, StreamAssistant=None):
        super(NotificationStreamAssistantUpdated_22Sub, self).__init__(StreamAssistant, )
supermod.NotificationStreamAssistantUpdated_22.subclass = NotificationStreamAssistantUpdated_22Sub
# end class NotificationStreamAssistantUpdated_22Sub


class NotificationStreamAssistantDeleted_22Sub(supermod.NotificationStreamAssistantDeleted_22):
    def __init__(self, StreamAssistant=None):
        super(NotificationStreamAssistantDeleted_22Sub, self).__init__(StreamAssistant, )
supermod.NotificationStreamAssistantDeleted_22.subclass = NotificationStreamAssistantDeleted_22Sub
# end class NotificationStreamAssistantDeleted_22Sub


class NotificationAppointmentCreated_22Sub(supermod.NotificationAppointmentCreated_22):
    def __init__(self, Appointment=None):
        super(NotificationAppointmentCreated_22Sub, self).__init__(Appointment, )
supermod.NotificationAppointmentCreated_22.subclass = NotificationAppointmentCreated_22Sub
# end class NotificationAppointmentCreated_22Sub


class NotificationAppointmentUpdated_22Sub(supermod.NotificationAppointmentUpdated_22):
    def __init__(self, Appointment=None):
        super(NotificationAppointmentUpdated_22Sub, self).__init__(Appointment, )
supermod.NotificationAppointmentUpdated_22.subclass = NotificationAppointmentUpdated_22Sub
# end class NotificationAppointmentUpdated_22Sub


class NotificationAppointmentDeleted_22Sub(supermod.NotificationAppointmentDeleted_22):
    def __init__(self, Appointment=None):
        super(NotificationAppointmentDeleted_22Sub, self).__init__(Appointment, )
supermod.NotificationAppointmentDeleted_22.subclass = NotificationAppointmentDeleted_22Sub
# end class NotificationAppointmentDeleted_22Sub


class NotificationReminderCreated_22Sub(supermod.NotificationReminderCreated_22):
    def __init__(self, Reminder=None):
        super(NotificationReminderCreated_22Sub, self).__init__(Reminder, )
supermod.NotificationReminderCreated_22.subclass = NotificationReminderCreated_22Sub
# end class NotificationReminderCreated_22Sub


class NotificationReminderUpdated_22Sub(supermod.NotificationReminderUpdated_22):
    def __init__(self, Reminder=None):
        super(NotificationReminderUpdated_22Sub, self).__init__(Reminder, )
supermod.NotificationReminderUpdated_22.subclass = NotificationReminderUpdated_22Sub
# end class NotificationReminderUpdated_22Sub


class NotificationReminderDeleted_22Sub(supermod.NotificationReminderDeleted_22):
    def __init__(self, Reminder=None):
        super(NotificationReminderDeleted_22Sub, self).__init__(Reminder, )
supermod.NotificationReminderDeleted_22.subclass = NotificationReminderDeleted_22Sub
# end class NotificationReminderDeleted_22Sub


class NotificationSignatureCreated_22Sub(supermod.NotificationSignatureCreated_22):
    def __init__(self, Signature=None):
        super(NotificationSignatureCreated_22Sub, self).__init__(Signature, )
supermod.NotificationSignatureCreated_22.subclass = NotificationSignatureCreated_22Sub
# end class NotificationSignatureCreated_22Sub


class NotificationSignatureUpdated_22Sub(supermod.NotificationSignatureUpdated_22):
    def __init__(self, Signature=None):
        super(NotificationSignatureUpdated_22Sub, self).__init__(Signature, )
supermod.NotificationSignatureUpdated_22.subclass = NotificationSignatureUpdated_22Sub
# end class NotificationSignatureUpdated_22Sub


class NotificationSignatureDeleted_22Sub(supermod.NotificationSignatureDeleted_22):
    def __init__(self, Signature=None):
        super(NotificationSignatureDeleted_22Sub, self).__init__(Signature, )
supermod.NotificationSignatureDeleted_22.subclass = NotificationSignatureDeleted_22Sub
# end class NotificationSignatureDeleted_22Sub


class NotificationReminderDue_22Sub(supermod.NotificationReminderDue_22):
    def __init__(self):
        super(NotificationReminderDue_22Sub, self).__init__()
supermod.NotificationReminderDue_22.subclass = NotificationReminderDue_22Sub
# end class NotificationReminderDue_22Sub


class NotificationReminderListUpdated_22Sub(supermod.NotificationReminderListUpdated_22):
    def __init__(self, BadgeCountPending=None, BadgeCountToday=None, BadgeCountTomorrow=None, BadgeCountLater=None):
        super(NotificationReminderListUpdated_22Sub, self).__init__(BadgeCountPending, BadgeCountToday, BadgeCountTomorrow, BadgeCountLater, )
supermod.NotificationReminderListUpdated_22.subclass = NotificationReminderListUpdated_22Sub
# end class NotificationReminderListUpdated_22Sub


class ListOfNotificationsPage_20Sub(supermod.ListOfNotificationsPage_20):
    def __init__(self, LastNotificationId=None, NotificationListPage=None, Paging=None):
        super(ListOfNotificationsPage_20Sub, self).__init__(LastNotificationId, NotificationListPage, Paging, )
supermod.ListOfNotificationsPage_20.subclass = ListOfNotificationsPage_20Sub
# end class ListOfNotificationsPage_20Sub


class ListOfNotifications_20Sub(supermod.ListOfNotifications_20):
    def __init__(self, Notification=None):
        super(ListOfNotifications_20Sub, self).__init__(Notification, )
supermod.ListOfNotifications_20.subclass = ListOfNotifications_20Sub
# end class ListOfNotifications_20Sub


class NotificationBase_20Sub(supermod.NotificationBase_20):
    def __init__(self, Id=None, Recipient=None, TriggerList=None, AlertMessage=None, Sender=None):
        super(NotificationBase_20Sub, self).__init__(Id, Recipient, TriggerList, AlertMessage, Sender, )
supermod.NotificationBase_20.subclass = NotificationBase_20Sub
# end class NotificationBase_20Sub


class NotificationUserStreamUpdated_20Sub(supermod.NotificationUserStreamUpdated_20):
    def __init__(self, Scope=None, StreamId=None):
        super(NotificationUserStreamUpdated_20Sub, self).__init__(Scope, StreamId, )
supermod.NotificationUserStreamUpdated_20.subclass = NotificationUserStreamUpdated_20Sub
# end class NotificationUserStreamUpdated_20Sub


class NotificationUserTokenInvalid_20Sub(supermod.NotificationUserTokenInvalid_20):
    def __init__(self, TokenProvider=None):
        super(NotificationUserTokenInvalid_20Sub, self).__init__(TokenProvider, )
supermod.NotificationUserTokenInvalid_20.subclass = NotificationUserTokenInvalid_20Sub
# end class NotificationUserTokenInvalid_20Sub


class NotificationOnboardingComplete_20Sub(supermod.NotificationOnboardingComplete_20):
    def __init__(self):
        super(NotificationOnboardingComplete_20Sub, self).__init__()
supermod.NotificationOnboardingComplete_20.subclass = NotificationOnboardingComplete_20Sub
# end class NotificationOnboardingComplete_20Sub


class NotificationPost_20Sub(supermod.NotificationPost_20):
    def __init__(self, Post=None):
        super(NotificationPost_20Sub, self).__init__(Post, )
supermod.NotificationPost_20.subclass = NotificationPost_20Sub
# end class NotificationPost_20Sub


class NotificationUserStatusChange_20Sub(supermod.NotificationUserStatusChange_20):
    def __init__(self, OnlineStatus=None, LastActivityAt=None):
        super(NotificationUserStatusChange_20Sub, self).__init__(OnlineStatus, LastActivityAt, )
supermod.NotificationUserStatusChange_20.subclass = NotificationUserStatusChange_20Sub
# end class NotificationUserStatusChange_20Sub


class NotificationAssistantNudge_20Sub(supermod.NotificationAssistantNudge_20):
    def __init__(self, ShowAssistant=None):
        super(NotificationAssistantNudge_20Sub, self).__init__(ShowAssistant, )
supermod.NotificationAssistantNudge_20.subclass = NotificationAssistantNudge_20Sub
# end class NotificationAssistantNudge_20Sub


class NotificationActionListUpdated_20Sub(supermod.NotificationActionListUpdated_20):
    def __init__(self):
        super(NotificationActionListUpdated_20Sub, self).__init__()
supermod.NotificationActionListUpdated_20.subclass = NotificationActionListUpdated_20Sub
# end class NotificationActionListUpdated_20Sub


class NotificationActionListUpdatedLast_20Sub(supermod.NotificationActionListUpdatedLast_20):
    def __init__(self, ActionableResourceId=None, Read=None):
        super(NotificationActionListUpdatedLast_20Sub, self).__init__(ActionableResourceId, Read, )
supermod.NotificationActionListUpdatedLast_20.subclass = NotificationActionListUpdatedLast_20Sub
# end class NotificationActionListUpdatedLast_20Sub


class ListOfNotificationsPage_15Sub(supermod.ListOfNotificationsPage_15):
    def __init__(self, LastNotificationId=None, NotificationListPage=None, Paging=None):
        super(ListOfNotificationsPage_15Sub, self).__init__(LastNotificationId, NotificationListPage, Paging, )
supermod.ListOfNotificationsPage_15.subclass = ListOfNotificationsPage_15Sub
# end class ListOfNotificationsPage_15Sub


class ListOfNotifications_15Sub(supermod.ListOfNotifications_15):
    def __init__(self, Notification=None):
        super(ListOfNotifications_15Sub, self).__init__(Notification, )
supermod.ListOfNotifications_15.subclass = ListOfNotifications_15Sub
# end class ListOfNotifications_15Sub


class NotificationBase_15Sub(supermod.NotificationBase_15):
    def __init__(self, Id=None, Recipient=None, TriggerList=None):
        super(NotificationBase_15Sub, self).__init__(Id, Recipient, TriggerList, )
supermod.NotificationBase_15.subclass = NotificationBase_15Sub
# end class NotificationBase_15Sub


class NotificationUserStreamUpdated_15Sub(supermod.NotificationUserStreamUpdated_15):
    def __init__(self, Scope=None, StreamId=None):
        super(NotificationUserStreamUpdated_15Sub, self).__init__(Scope, StreamId, )
supermod.NotificationUserStreamUpdated_15.subclass = NotificationUserStreamUpdated_15Sub
# end class NotificationUserStreamUpdated_15Sub


class NotificationUserTokenInvalid_15Sub(supermod.NotificationUserTokenInvalid_15):
    def __init__(self, TokenProvider=None):
        super(NotificationUserTokenInvalid_15Sub, self).__init__(TokenProvider, )
supermod.NotificationUserTokenInvalid_15.subclass = NotificationUserTokenInvalid_15Sub
# end class NotificationUserTokenInvalid_15Sub


class NotificationOnboardingComplete_15Sub(supermod.NotificationOnboardingComplete_15):
    def __init__(self):
        super(NotificationOnboardingComplete_15Sub, self).__init__()
supermod.NotificationOnboardingComplete_15.subclass = NotificationOnboardingComplete_15Sub
# end class NotificationOnboardingComplete_15Sub


class Notification_15Sub(supermod.Notification_15):
    def __init__(self, Sender=None, ActionMessage=None, ActionComment=None):
        super(Notification_15Sub, self).__init__(Sender, ActionMessage, ActionComment, )
supermod.Notification_15.subclass = Notification_15Sub
# end class Notification_15Sub


class NotificationPost_15Sub(supermod.NotificationPost_15):
    def __init__(self, Post=None, PostId=None, StreamId=None, ClientResourceId=None):
        super(NotificationPost_15Sub, self).__init__(Post, PostId, StreamId, ClientResourceId, )
supermod.NotificationPost_15.subclass = NotificationPost_15Sub
# end class NotificationPost_15Sub


class NotificationActionListUpdated_18Sub(supermod.NotificationActionListUpdated_18):
    def __init__(self):
        super(NotificationActionListUpdated_18Sub, self).__init__()
supermod.NotificationActionListUpdated_18.subclass = NotificationActionListUpdated_18Sub
# end class NotificationActionListUpdated_18Sub


class NotificationActionListUpdatedLast_18Sub(supermod.NotificationActionListUpdatedLast_18):
    def __init__(self, ActionableResourceId=None, Read=None):
        super(NotificationActionListUpdatedLast_18Sub, self).__init__(ActionableResourceId, Read, )
supermod.NotificationActionListUpdatedLast_18.subclass = NotificationActionListUpdatedLast_18Sub
# end class NotificationActionListUpdatedLast_18Sub


class NotificationUserStatusChange_18Sub(supermod.NotificationUserStatusChange_18):
    def __init__(self, OnlineStatus=None, LastActivityAt=None):
        super(NotificationUserStatusChange_18Sub, self).__init__(OnlineStatus, LastActivityAt, )
supermod.NotificationUserStatusChange_18.subclass = NotificationUserStatusChange_18Sub
# end class NotificationUserStatusChange_18Sub


class ListOfStreamsPage_22Sub(supermod.ListOfStreamsPage_22):
    def __init__(self, StreamList=None, Paging=None):
        super(ListOfStreamsPage_22Sub, self).__init__(StreamList, Paging, )
supermod.ListOfStreamsPage_22.subclass = ListOfStreamsPage_22Sub
# end class ListOfStreamsPage_22Sub


class ListOfStreams_22Sub(supermod.ListOfStreams_22):
    def __init__(self, Discussion=None):
        super(ListOfStreams_22Sub, self).__init__(Discussion, )
supermod.ListOfStreams_22.subclass = ListOfStreams_22Sub
# end class ListOfStreams_22Sub


class ListOfGroupAssistant_22Sub(supermod.ListOfGroupAssistant_22):
    def __init__(self, GroupAssistant=None):
        super(ListOfGroupAssistant_22Sub, self).__init__(GroupAssistant, )
supermod.ListOfGroupAssistant_22.subclass = ListOfGroupAssistant_22Sub
# end class ListOfGroupAssistant_22Sub


class ListOfGroupAssistantPage_22Sub(supermod.ListOfGroupAssistantPage_22):
    def __init__(self, GroupAssistants=None, Paging=None):
        super(ListOfGroupAssistantPage_22Sub, self).__init__(GroupAssistants, Paging, )
supermod.ListOfGroupAssistantPage_22.subclass = ListOfGroupAssistantPage_22Sub
# end class ListOfGroupAssistantPage_22Sub


class StreamVisibility_22Sub(supermod.StreamVisibility_22):
    def __init__(self, IsVisible=None):
        super(StreamVisibility_22Sub, self).__init__(IsVisible, )
supermod.StreamVisibility_22.subclass = StreamVisibility_22Sub
# end class StreamVisibility_22Sub


class StreamName_22Sub(supermod.StreamName_22):
    def __init__(self, StreamName=None):
        super(StreamName_22Sub, self).__init__(StreamName, )
supermod.StreamName_22.subclass = StreamName_22Sub
# end class StreamName_22Sub


class Menu_22Sub(supermod.Menu_22):
    def __init__(self, StreamListPage=None, BadgeCountTotal=None, HasUnreadItems=None):
        super(Menu_22Sub, self).__init__(StreamListPage, BadgeCountTotal, HasUnreadItems, )
supermod.Menu_22.subclass = Menu_22Sub
# end class Menu_22Sub


class ListOfLocationsPage_19Sub(supermod.ListOfLocationsPage_19):
    def __init__(self, LocationListPage=None, Paging=None):
        super(ListOfLocationsPage_19Sub, self).__init__(LocationListPage, Paging, )
supermod.ListOfLocationsPage_19.subclass = ListOfLocationsPage_19Sub
# end class ListOfLocationsPage_19Sub


class ListOfLocations_19Sub(supermod.ListOfLocations_19):
    def __init__(self, Location=None):
        super(ListOfLocations_19Sub, self).__init__(Location, )
supermod.ListOfLocations_19.subclass = ListOfLocations_19Sub
# end class ListOfLocations_19Sub


class Location_19Sub(supermod.Location_19):
    def __init__(self, Date=None, Position=None):
        super(Location_19Sub, self).__init__(Date, Position, )
supermod.Location_19.subclass = Location_19Sub
# end class Location_19Sub


class Position_19Sub(supermod.Position_19):
    def __init__(self, Id=None, Latitude=None, Longitude=None, Altitude=None, Accuracy=None, Speed=None):
        super(Position_19Sub, self).__init__(Id, Latitude, Longitude, Altitude, Accuracy, Speed, )
supermod.Position_19.subclass = Position_19Sub
# end class Position_19Sub


class ListOfActionableResourcesPage_22Sub(supermod.ListOfActionableResourcesPage_22):
    def __init__(self, ActionableResourceList=None, Paging=None):
        super(ListOfActionableResourcesPage_22Sub, self).__init__(ActionableResourceList, Paging, )
supermod.ListOfActionableResourcesPage_22.subclass = ListOfActionableResourcesPage_22Sub
# end class ListOfActionableResourcesPage_22Sub


class ListOfActionableResources_22Sub(supermod.ListOfActionableResources_22):
    def __init__(self, ActionableResource=None):
        super(ListOfActionableResources_22Sub, self).__init__(ActionableResource, )
supermod.ListOfActionableResources_22.subclass = ListOfActionableResources_22Sub
# end class ListOfActionableResources_22Sub


class ListOfActionableResourcesPage_21Sub(supermod.ListOfActionableResourcesPage_21):
    def __init__(self, ActionableResourceList=None, Paging=None):
        super(ListOfActionableResourcesPage_21Sub, self).__init__(ActionableResourceList, Paging, )
supermod.ListOfActionableResourcesPage_21.subclass = ListOfActionableResourcesPage_21Sub
# end class ListOfActionableResourcesPage_21Sub


class ListOfActionableResources_21Sub(supermod.ListOfActionableResources_21):
    def __init__(self, ActionableResource=None):
        super(ListOfActionableResources_21Sub, self).__init__(ActionableResource, )
supermod.ListOfActionableResources_21.subclass = ListOfActionableResources_21Sub
# end class ListOfActionableResources_21Sub


class ListOfActionableResourcesPage_20Sub(supermod.ListOfActionableResourcesPage_20):
    def __init__(self, ActionableResourceList=None, Paging=None):
        super(ListOfActionableResourcesPage_20Sub, self).__init__(ActionableResourceList, Paging, )
supermod.ListOfActionableResourcesPage_20.subclass = ListOfActionableResourcesPage_20Sub
# end class ListOfActionableResourcesPage_20Sub


class ListOfActionableResources_20Sub(supermod.ListOfActionableResources_20):
    def __init__(self, ActionableResource=None):
        super(ListOfActionableResources_20Sub, self).__init__(ActionableResource, )
supermod.ListOfActionableResources_20.subclass = ListOfActionableResources_20Sub
# end class ListOfActionableResources_20Sub


class ActionableResourceAvailability_20Sub(supermod.ActionableResourceAvailability_20):
    def __init__(self, Mode=None, ActionableResourceId=None):
        super(ActionableResourceAvailability_20Sub, self).__init__(Mode, ActionableResourceId, )
supermod.ActionableResourceAvailability_20.subclass = ActionableResourceAvailability_20Sub
# end class ActionableResourceAvailability_20Sub


class ActionableResource_18Sub(supermod.ActionableResource_18):
    def __init__(self, ActionResource=None, NotificationType=None):
        super(ActionableResource_18Sub, self).__init__(ActionResource, NotificationType, )
supermod.ActionableResource_18.subclass = ActionableResource_18Sub
# end class ActionableResource_18Sub


class ListOfActionableResources_18Sub(supermod.ListOfActionableResources_18):
    def __init__(self, ActionableResource=None):
        super(ListOfActionableResources_18Sub, self).__init__(ActionableResource, )
supermod.ListOfActionableResources_18.subclass = ListOfActionableResources_18Sub
# end class ListOfActionableResources_18Sub


class ListOfActions_18Sub(supermod.ListOfActions_18):
    def __init__(self, Action=None):
        super(ListOfActions_18Sub, self).__init__(Action, )
supermod.ListOfActions_18.subclass = ListOfActions_18Sub
# end class ListOfActions_18Sub


class ListOfUserStatisticResponseTimes_20Sub(supermod.ListOfUserStatisticResponseTimes_20):
    def __init__(self, UserStatisticResponseTime=None):
        super(ListOfUserStatisticResponseTimes_20Sub, self).__init__(UserStatisticResponseTime, )
supermod.ListOfUserStatisticResponseTimes_20.subclass = ListOfUserStatisticResponseTimes_20Sub
# end class ListOfUserStatisticResponseTimes_20Sub


class ListOfUserStatistics_20Sub(supermod.ListOfUserStatistics_20):
    def __init__(self, UserStatistics=None):
        super(ListOfUserStatistics_20Sub, self).__init__(UserStatistics, )
supermod.ListOfUserStatistics_20.subclass = ListOfUserStatistics_20Sub
# end class ListOfUserStatistics_20Sub


class UserStatistics_20Sub(supermod.UserStatistics_20):
    def __init__(self, User=None, PostCount=None, QuickestResponse=None, AverageResponse=None, NoResponse=None):
        super(UserStatistics_20Sub, self).__init__(User, PostCount, QuickestResponse, AverageResponse, NoResponse, )
supermod.UserStatistics_20.subclass = UserStatistics_20Sub
# end class UserStatistics_20Sub


class ResponseStatistics_20Sub(supermod.ResponseStatistics_20):
    def __init__(self, DateTimeRange=None, TimeRange=None, ResponseTime=None):
        super(ResponseStatistics_20Sub, self).__init__(DateTimeRange, TimeRange, ResponseTime, )
supermod.ResponseStatistics_20.subclass = ResponseStatistics_20Sub
# end class ResponseStatistics_20Sub


class FlagManagedByAssistantBase_20Sub(supermod.FlagManagedByAssistantBase_20):
    def __init__(self, ManagedByAssistant=None):
        super(FlagManagedByAssistantBase_20Sub, self).__init__(ManagedByAssistant, )
supermod.FlagManagedByAssistantBase_20.subclass = FlagManagedByAssistantBase_20Sub
# end class FlagManagedByAssistantBase_20Sub


class Result_1Sub(supermod.Result_1):
    def __init__(self, Message=None, ErrorCode=None, Conflict=None, Successful=None):
        super(Result_1Sub, self).__init__(Message, ErrorCode, Conflict, Successful, )
supermod.Result_1.subclass = Result_1Sub
# end class Result_1Sub


class ConflictInfo_1Sub(supermod.ConflictInfo_1):
    def __init__(self, PostedResource=None, ConflictedResource=None):
        super(ConflictInfo_1Sub, self).__init__(PostedResource, ConflictedResource, )
supermod.ConflictInfo_1.subclass = ConflictInfo_1Sub
# end class ConflictInfo_1Sub


class LocalizedResult_1Sub(supermod.LocalizedResult_1):
    def __init__(self, LocalizedMessage=None):
        super(LocalizedResult_1Sub, self).__init__(LocalizedMessage, )
supermod.LocalizedResult_1.subclass = LocalizedResult_1Sub
# end class LocalizedResult_1Sub


class ResourceBase_13Sub(supermod.ResourceBase_13):
    def __init__(self, Id=None, Name=None, Revision=None, ClientResourceIdList=None, Created=None, Modified=None, IsFull=None):
        super(ResourceBase_13Sub, self).__init__(Id, Name, Revision, ClientResourceIdList, Created, Modified, IsFull, )
supermod.ResourceBase_13.subclass = ResourceBase_13Sub
# end class ResourceBase_13Sub


class ListOfResources_13Sub(supermod.ListOfResources_13):
    def __init__(self, Resource=None):
        super(ListOfResources_13Sub, self).__init__(Resource, )
supermod.ListOfResources_13.subclass = ListOfResources_13Sub
# end class ListOfResources_13Sub


class ListOfResourcesPage_13Sub(supermod.ListOfResourcesPage_13):
    def __init__(self, ResourceList=None, Paging=None):
        super(ListOfResourcesPage_13Sub, self).__init__(ResourceList, Paging, )
supermod.ListOfResourcesPage_13.subclass = ListOfResourcesPage_13Sub
# end class ListOfResourcesPage_13Sub


class DateTimeRangeSub(supermod.DateTimeRange):
    def __init__(self, Start=None, End=None):
        super(DateTimeRangeSub, self).__init__(Start, End, )
supermod.DateTimeRange.subclass = DateTimeRangeSub
# end class DateTimeRangeSub


class TimeRangeSub(supermod.TimeRange):
    def __init__(self, Start=None, End=None):
        super(TimeRangeSub, self).__init__(Start, End, )
supermod.TimeRange.subclass = TimeRangeSub
# end class TimeRangeSub


class ListOfStringsSub(supermod.ListOfStrings):
    def __init__(self, stringItem=None):
        super(ListOfStringsSub, self).__init__(stringItem, )
supermod.ListOfStrings.subclass = ListOfStringsSub
# end class ListOfStringsSub


class BatchRequest_22Sub(supermod.BatchRequest_22):
    def __init__(self):
        super(BatchRequest_22Sub, self).__init__()
supermod.BatchRequest_22.subclass = BatchRequest_22Sub
# end class BatchRequest_22Sub


class AsyncJobStatus_22Sub(supermod.AsyncJobStatus_22):
    def __init__(self):
        super(AsyncJobStatus_22Sub, self).__init__()
supermod.AsyncJobStatus_22.subclass = AsyncJobStatus_22Sub
# end class AsyncJobStatus_22Sub


class StatisticsGroupActivity_20Sub(supermod.StatisticsGroupActivity_20):
    def __init__(self, Group=None, MostActiveMembers=None, ActivityChart=None):
        super(StatisticsGroupActivity_20Sub, self).__init__(Group, MostActiveMembers, ActivityChart, )
supermod.StatisticsGroupActivity_20.subclass = StatisticsGroupActivity_20Sub
# end class StatisticsGroupActivity_20Sub


class StatisticsUserResponseTime_20Sub(supermod.StatisticsUserResponseTime_20):
    def __init__(self, Me=None, Other=None, ViewType=None):
        super(StatisticsUserResponseTime_20Sub, self).__init__(Me, Other, ViewType, )
supermod.StatisticsUserResponseTime_20.subclass = StatisticsUserResponseTime_20Sub
# end class StatisticsUserResponseTime_20Sub


class StatisticsUserResponseTimeList_20Sub(supermod.StatisticsUserResponseTimeList_20):
    def __init__(self, UserResponseTimeList=None):
        super(StatisticsUserResponseTimeList_20Sub, self).__init__(UserResponseTimeList, )
supermod.StatisticsUserResponseTimeList_20.subclass = StatisticsUserResponseTimeList_20Sub
# end class StatisticsUserResponseTimeList_20Sub


class ActionBase_18Sub(supermod.ActionBase_18):
    def __init__(self, Description=None, ResponseMessage=None, ActionType=None, AssistantEmail=None, Primary=None):
        super(ActionBase_18Sub, self).__init__(Description, ResponseMessage, ActionType, AssistantEmail, Primary, )
supermod.ActionBase_18.subclass = ActionBase_18Sub
# end class ActionBase_18Sub


class ActionableResource_20Sub(supermod.ActionableResource_20):
    def __init__(self, NotificationType=None, Resource=None, DescriptionList=None, ActionList=None, InsightList=None):
        super(ActionableResource_20Sub, self).__init__(NotificationType, Resource, DescriptionList, ActionList, InsightList, )
supermod.ActionableResource_20.subclass = ActionableResource_20Sub
# end class ActionableResource_20Sub


class ActionableResource_21Sub(supermod.ActionableResource_21):
    def __init__(self, NotificationType=None, Resource=None, DescriptionList=None, ActionList=None, InsightList=None):
        super(ActionableResource_21Sub, self).__init__(NotificationType, Resource, DescriptionList, ActionList, InsightList, )
supermod.ActionableResource_21.subclass = ActionableResource_21Sub
# end class ActionableResource_21Sub


class ActionableResource_22Sub(supermod.ActionableResource_22):
    def __init__(self, NotificationType=None, Resource=None, DescriptionList=None, ActionList=None, InsightList=None):
        super(ActionableResource_22Sub, self).__init__(NotificationType, Resource, DescriptionList, ActionList, InsightList, )
supermod.ActionableResource_22.subclass = ActionableResource_22Sub
# end class ActionableResource_22Sub


class OnboardingHintReminderList_20Sub(supermod.OnboardingHintReminderList_20):
    def __init__(self):
        super(OnboardingHintReminderList_20Sub, self).__init__()
supermod.OnboardingHintReminderList_20.subclass = OnboardingHintReminderList_20Sub
# end class OnboardingHintReminderList_20Sub


class OnboardingHintBoardList_20Sub(supermod.OnboardingHintBoardList_20):
    def __init__(self):
        super(OnboardingHintBoardList_20Sub, self).__init__()
supermod.OnboardingHintBoardList_20.subclass = OnboardingHintBoardList_20Sub
# end class OnboardingHintBoardList_20Sub


class OnboardingHintGroupList_20Sub(supermod.OnboardingHintGroupList_20):
    def __init__(self):
        super(OnboardingHintGroupList_20Sub, self).__init__()
supermod.OnboardingHintGroupList_20.subclass = OnboardingHintGroupList_20Sub
# end class OnboardingHintGroupList_20Sub


class OnboardingHintInvite_20Sub(supermod.OnboardingHintInvite_20):
    def __init__(self):
        super(OnboardingHintInvite_20Sub, self).__init__()
supermod.OnboardingHintInvite_20.subclass = OnboardingHintInvite_20Sub
# end class OnboardingHintInvite_20Sub


class OnboardingHintLibrary_20Sub(supermod.OnboardingHintLibrary_20):
    def __init__(self):
        super(OnboardingHintLibrary_20Sub, self).__init__()
supermod.OnboardingHintLibrary_20.subclass = OnboardingHintLibrary_20Sub
# end class OnboardingHintLibrary_20Sub


class OnboardingHintUserList_20Sub(supermod.OnboardingHintUserList_20):
    def __init__(self):
        super(OnboardingHintUserList_20Sub, self).__init__()
supermod.OnboardingHintUserList_20.subclass = OnboardingHintUserList_20Sub
# end class OnboardingHintUserList_20Sub


class OnboardingHintUserStream_20Sub(supermod.OnboardingHintUserStream_20):
    def __init__(self, UserStream=None):
        super(OnboardingHintUserStream_20Sub, self).__init__(UserStream, )
supermod.OnboardingHintUserStream_20.subclass = OnboardingHintUserStream_20Sub
# end class OnboardingHintUserStream_20Sub


class OnboardingHintImportantStreamList_20Sub(supermod.OnboardingHintImportantStreamList_20):
    def __init__(self):
        super(OnboardingHintImportantStreamList_20Sub, self).__init__()
supermod.OnboardingHintImportantStreamList_20.subclass = OnboardingHintImportantStreamList_20Sub
# end class OnboardingHintImportantStreamList_20Sub


class OnboardingHintMutedStreamList_20Sub(supermod.OnboardingHintMutedStreamList_20):
    def __init__(self):
        super(OnboardingHintMutedStreamList_20Sub, self).__init__()
supermod.OnboardingHintMutedStreamList_20.subclass = OnboardingHintMutedStreamList_20Sub
# end class OnboardingHintMutedStreamList_20Sub


class OnboardingHintFollowup_20Sub(supermod.OnboardingHintFollowup_20):
    def __init__(self):
        super(OnboardingHintFollowup_20Sub, self).__init__()
supermod.OnboardingHintFollowup_20.subclass = OnboardingHintFollowup_20Sub
# end class OnboardingHintFollowup_20Sub


class StreamBase_17Sub(supermod.StreamBase_17):
    def __init__(self, IsVisible=None):
        super(StreamBase_17Sub, self).__init__(IsVisible, )
supermod.StreamBase_17.subclass = StreamBase_17Sub
# end class StreamBase_17Sub


class StreamGroup_17Sub(supermod.StreamGroup_17):
    def __init__(self, Members=None, MemberCount=None, Administrators=None, AdministratorCount=None, Description=None):
        super(StreamGroup_17Sub, self).__init__(Members, MemberCount, Administrators, AdministratorCount, Description, )
supermod.StreamGroup_17.subclass = StreamGroup_17Sub
# end class StreamGroup_17Sub


class StreamUser_17Sub(supermod.StreamUser_17):
    def __init__(self, User=None):
        super(StreamUser_17Sub, self).__init__(User, )
supermod.StreamUser_17.subclass = StreamUser_17Sub
# end class StreamUser_17Sub


class StreamChat_22Sub(supermod.StreamChat_22):
    def __init__(self, PostListPage=None):
        super(StreamChat_22Sub, self).__init__(PostListPage, )
supermod.StreamChat_22.subclass = StreamChat_22Sub
# end class StreamChat_22Sub


class StreamCards_22Sub(supermod.StreamCards_22):
    def __init__(self, CardListPage=None):
        super(StreamCards_22Sub, self).__init__(CardListPage, )
supermod.StreamCards_22.subclass = StreamCards_22Sub
# end class StreamCards_22Sub


class GroupAssistant_22Sub(supermod.GroupAssistant_22):
    def __init__(self, FlagType=None, Parent=None, Users=None):
        super(GroupAssistant_22Sub, self).__init__(FlagType, Parent, Users, )
supermod.GroupAssistant_22.subclass = GroupAssistant_22Sub
# end class GroupAssistant_22Sub


class StreamAssistant_22Sub(supermod.StreamAssistant_22):
    def __init__(self, FlagType=None, Parent=None, NudgeText=None, EmailText=None, InviteText=None, Percentage=None, TotalSent=None):
        super(StreamAssistant_22Sub, self).__init__(FlagType, Parent, NudgeText, EmailText, InviteText, Percentage, TotalSent, )
supermod.StreamAssistant_22.subclass = StreamAssistant_22Sub
# end class StreamAssistant_22Sub


class StreamBase_22Sub(supermod.StreamBase_22):
    def __init__(self, IsVisible=None, LastPost=None, LastUnreadPost=None, BadgeCount=None, BadgeCountCardStream=None, BadgeCountChatStream=None, SortModified=None, Parent=None, StreamAssistant=None):
        super(StreamBase_22Sub, self).__init__(IsVisible, LastPost, LastUnreadPost, BadgeCount, BadgeCountCardStream, BadgeCountChatStream, SortModified, Parent, StreamAssistant, )
supermod.StreamBase_22.subclass = StreamBase_22Sub
# end class StreamBase_22Sub


class Chat_15Sub(supermod.Chat_15):
    def __init__(self):
        super(Chat_15Sub, self).__init__()
supermod.Chat_15.subclass = Chat_15Sub
# end class Chat_15Sub


class BoardBase_15Sub(supermod.BoardBase_15):
    def __init__(self):
        super(BoardBase_15Sub, self).__init__()
supermod.BoardBase_15.subclass = BoardBase_15Sub
# end class BoardBase_15Sub


class BoardBase_20Sub(supermod.BoardBase_20):
    def __init__(self):
        super(BoardBase_20Sub, self).__init__()
supermod.BoardBase_20.subclass = BoardBase_20Sub
# end class BoardBase_20Sub


class BoardPersonal_21Sub(supermod.BoardPersonal_21):
    def __init__(self, PinnedItemList=None):
        super(BoardPersonal_21Sub, self).__init__(PinnedItemList, )
supermod.BoardPersonal_21.subclass = BoardPersonal_21Sub
# end class BoardPersonal_21Sub


class BoardBase_22Sub(supermod.BoardBase_22):
    def __init__(self, Type=None, PinnedItemList=None, PinnedItemCount=None, LastPost=None, ParentGroup=None):
        super(BoardBase_22Sub, self).__init__(Type, PinnedItemList, PinnedItemCount, LastPost, ParentGroup, )
supermod.BoardBase_22.subclass = BoardBase_22Sub
# end class BoardBase_22Sub


class BoardPersonal_22Sub(supermod.BoardPersonal_22):
    def __init__(self):
        super(BoardPersonal_22Sub, self).__init__()
supermod.BoardPersonal_22.subclass = BoardPersonal_22Sub
# end class BoardPersonal_22Sub


class BoardGroup_22Sub(supermod.BoardGroup_22):
    def __init__(self):
        super(BoardGroup_22Sub, self).__init__()
supermod.BoardGroup_22.subclass = BoardGroup_22Sub
# end class BoardGroup_22Sub


class SortActionBase_13Sub(supermod.SortActionBase_13):
    def __init__(self, DirectionHint=None, DefaultDirection=None, IsSelected=None):
        super(SortActionBase_13Sub, self).__init__(DirectionHint, DefaultDirection, IsSelected, )
supermod.SortActionBase_13.subclass = SortActionBase_13Sub
# end class SortActionBase_13Sub


class ContextBase_13Sub(supermod.ContextBase_13):
    def __init__(self):
        super(ContextBase_13Sub, self).__init__()
supermod.ContextBase_13.subclass = ContextBase_13Sub
# end class ContextBase_13Sub


class AppointmentResponse_22Sub(supermod.AppointmentResponse_22):
    def __init__(self, Status=None):
        super(AppointmentResponse_22Sub, self).__init__(Status, )
supermod.AppointmentResponse_22.subclass = AppointmentResponse_22Sub
# end class AppointmentResponse_22Sub


class SignatureImage_20Sub(supermod.SignatureImage_20):
    def __init__(self):
        super(SignatureImage_20Sub, self).__init__()
supermod.SignatureImage_20.subclass = SignatureImage_20Sub
# end class SignatureImage_20Sub


class Signature_20Sub(supermod.Signature_20):
    def __init__(self, Title=None, Text=None, Html=None):
        super(Signature_20Sub, self).__init__(Title, Text, Html, )
supermod.Signature_20.subclass = Signature_20Sub
# end class Signature_20Sub


class PostFlagManagedByAssistant_20Sub(supermod.PostFlagManagedByAssistant_20):
    def __init__(self, ReminderType=None, AutomaticDetection=None):
        super(PostFlagManagedByAssistant_20Sub, self).__init__(ReminderType, AutomaticDetection, )
supermod.PostFlagManagedByAssistant_20.subclass = PostFlagManagedByAssistant_20Sub
# end class PostFlagManagedByAssistant_20Sub


class Post_15Sub(supermod.Post_15):
    def __init__(self, Text=None, ShareList=None, ParentId=None, Files=None, Author=None, StreamId=None):
        super(Post_15Sub, self).__init__(Text, ShareList, ParentId, Files, Author, StreamId, )
supermod.Post_15.subclass = Post_15Sub
# end class Post_15Sub


class Post_18Sub(supermod.Post_18):
    def __init__(self, Text=None, ShareList=None, VisibilityListCount=None, Files=None, Author=None, Parent=None, Unread=None, UnreadClearedAt=None, ErrorSending=None, ImportedViaEmail=None, ForwardedCopy=None, BodyFormat=None, ManagedByAssistant=None):
        super(Post_18Sub, self).__init__(Text, ShareList, VisibilityListCount, Files, Author, Parent, Unread, UnreadClearedAt, ErrorSending, ImportedViaEmail, ForwardedCopy, BodyFormat, ManagedByAssistant, )
supermod.Post_18.subclass = Post_18Sub
# end class Post_18Sub


class Post_20Sub(supermod.Post_20):
    def __init__(self, Text=None, ShareList=None, VisibilityListCount=None, Author=None, Parent=None, Files=None, Unread=None, UnreadClearedAt=None, ErrorSending=None, ImportedViaEmail=None, ForwardedCopy=None, BodyFormat=None, BodyHtml=None, BodySnippet=None, ManagedByAssistant=None, ReminderType=None, ClientResourceId=None):
        super(Post_20Sub, self).__init__(Text, ShareList, VisibilityListCount, Author, Parent, Files, Unread, UnreadClearedAt, ErrorSending, ImportedViaEmail, ForwardedCopy, BodyFormat, BodyHtml, BodySnippet, ManagedByAssistant, ReminderType, ClientResourceId, )
supermod.Post_20.subclass = Post_20Sub
# end class Post_20Sub


class PostSeparator_22Sub(supermod.PostSeparator_22):
    def __init__(self):
        super(PostSeparator_22Sub, self).__init__()
supermod.PostSeparator_22.subclass = PostSeparator_22Sub
# end class PostSeparator_22Sub


class PostAssistant_22Sub(supermod.PostAssistant_22):
    def __init__(self, Insight=None, FlagType=None, Parent=None):
        super(PostAssistant_22Sub, self).__init__(Insight, FlagType, Parent, )
supermod.PostAssistant_22.subclass = PostAssistant_22Sub
# end class PostAssistant_22Sub


class PostBody_22Sub(supermod.PostBody_22):
    def __init__(self, MimeType=None, Content=None, Parent=None):
        super(PostBody_22Sub, self).__init__(MimeType, Content, Parent, )
supermod.PostBody_22.subclass = PostBody_22Sub
# end class PostBody_22Sub


class PostActionList_22Sub(supermod.PostActionList_22):
    def __init__(self, ActionList=None, Parent=None):
        super(PostActionList_22Sub, self).__init__(ActionList, Parent, )
supermod.PostActionList_22.subclass = PostActionList_22Sub
# end class PostActionList_22Sub


class PostUnread_22Sub(supermod.PostUnread_22):
    def __init__(self, Unread=None, Parent=None, ParentDiscussion=None, ParentStream=None):
        super(PostUnread_22Sub, self).__init__(Unread, Parent, ParentDiscussion, ParentStream, )
supermod.PostUnread_22.subclass = PostUnread_22Sub
# end class PostUnread_22Sub


class Post_22Sub(supermod.Post_22):
    def __init__(self, Text=None, Author=None, Parent=None, ShareList=None, CcList=None, BccList=None, VisibilityList=None, VisibilityListCount=None, Files=None, UnreadInfo=None, Unread=None, UnreadClearedAt=None, EmailMessageId=None, ImportedViaEmail=None, ErrorSending=None, ForwardedCopy=None, Body=None, BodyFormat=None, BodySnippet=None, BodyHtml=None, Assistant=None, ManagedByAssistant=None, ReminderType=None, AssistantInsight=None, ReminderDue=None, ClientResourceId=None, Actions=None):
        super(Post_22Sub, self).__init__(Text, Author, Parent, ShareList, CcList, BccList, VisibilityList, VisibilityListCount, Files, UnreadInfo, Unread, UnreadClearedAt, EmailMessageId, ImportedViaEmail, ErrorSending, ForwardedCopy, Body, BodyFormat, BodySnippet, BodyHtml, Assistant, ManagedByAssistant, ReminderType, AssistantInsight, ReminderDue, ClientResourceId, Actions, )
supermod.Post_22.subclass = Post_22Sub
# end class Post_22Sub


class DiscussionBase_18Sub(supermod.DiscussionBase_18):
    def __init__(self, Parent=None):
        super(DiscussionBase_18Sub, self).__init__(Parent, )
supermod.DiscussionBase_18.subclass = DiscussionBase_18Sub
# end class DiscussionBase_18Sub


class DiscussionBase_20Sub(supermod.DiscussionBase_20):
    def __init__(self, Parent=None):
        super(DiscussionBase_20Sub, self).__init__(Parent, )
supermod.DiscussionBase_20.subclass = DiscussionBase_20Sub
# end class DiscussionBase_20Sub


class CardPinnedToList_22Sub(supermod.CardPinnedToList_22):
    def __init__(self, BoardList=None, Parent=None):
        super(CardPinnedToList_22Sub, self).__init__(BoardList, Parent, )
supermod.CardPinnedToList_22.subclass = CardPinnedToList_22Sub
# end class CardPinnedToList_22Sub


class DiscussionCardTrash_22Sub(supermod.DiscussionCardTrash_22):
    def __init__(self, IsInTrash=None, Parent=None):
        super(DiscussionCardTrash_22Sub, self).__init__(IsInTrash, Parent, )
supermod.DiscussionCardTrash_22.subclass = DiscussionCardTrash_22Sub
# end class DiscussionCardTrash_22Sub


class DiscussionBase_22Sub(supermod.DiscussionBase_22):
    def __init__(self, Parent=None):
        super(DiscussionBase_22Sub, self).__init__(Parent, )
supermod.DiscussionBase_22.subclass = DiscussionBase_22Sub
# end class DiscussionBase_22Sub


class GroupLeave_22Sub(supermod.GroupLeave_22):
    def __init__(self):
        super(GroupLeave_22Sub, self).__init__()
supermod.GroupLeave_22.subclass = GroupLeave_22Sub
# end class GroupLeave_22Sub


class Group_17Sub(supermod.Group_17):
    def __init__(self, Description=None, Email=None, ShareOnlyMembers=None, ShareOnlyMembersCount=None, Members=None, MemberCount=None, Administrators=None, AdministratorCount=None, Boards=None, EmailSendDisabled=None):
        super(Group_17Sub, self).__init__(Description, Email, ShareOnlyMembers, ShareOnlyMembersCount, Members, MemberCount, Administrators, AdministratorCount, Boards, EmailSendDisabled, )
supermod.Group_17.subclass = Group_17Sub
# end class Group_17Sub


class MicrosoftExchangeSyncInfo_16Sub(supermod.MicrosoftExchangeSyncInfo_16):
    def __init__(self, IsEnabled=None, SyncTaskRunning=None, IsInitialSyncTaskFinished=None, ImportedMessageCount=None, ImportedThreadCount=None):
        super(MicrosoftExchangeSyncInfo_16Sub, self).__init__(IsEnabled, SyncTaskRunning, IsInitialSyncTaskFinished, ImportedMessageCount, ImportedThreadCount, )
supermod.MicrosoftExchangeSyncInfo_16.subclass = MicrosoftExchangeSyncInfo_16Sub
# end class MicrosoftExchangeSyncInfo_16Sub


class FolderBase_16Sub(supermod.FolderBase_16):
    def __init__(self, SyncEnabled=None, CanDisableSync=None):
        super(FolderBase_16Sub, self).__init__(SyncEnabled, CanDisableSync, )
supermod.FolderBase_16.subclass = FolderBase_16Sub
# end class FolderBase_16Sub


class GMailSyncInfo_16Sub(supermod.GMailSyncInfo_16):
    def __init__(self, IsEnabled=None, SyncTaskRunning=None, IsInitialSyncTaskFinished=None, ImportedMessageCount=None, ImportedThreadCount=None):
        super(GMailSyncInfo_16Sub, self).__init__(IsEnabled, SyncTaskRunning, IsInitialSyncTaskFinished, ImportedMessageCount, ImportedThreadCount, )
supermod.GMailSyncInfo_16.subclass = GMailSyncInfo_16Sub
# end class GMailSyncInfo_16Sub


class ActorBase_14Sub(supermod.ActorBase_14):
    def __init__(self):
        super(ActorBase_14Sub, self).__init__()
supermod.ActorBase_14.subclass = ActorBase_14Sub
# end class ActorBase_14Sub


class ActorBase_13Sub(supermod.ActorBase_13):
    def __init__(self):
        super(ActorBase_13Sub, self).__init__()
supermod.ActorBase_13.subclass = ActorBase_13Sub
# end class ActorBase_13Sub


class MobileDevice_4Sub(supermod.MobileDevice_4):
    def __init__(self, Type=None, NotificationVersion=None, PushNotificationId=None):
        super(MobileDevice_4Sub, self).__init__(Type, NotificationVersion, PushNotificationId, )
supermod.MobileDevice_4.subclass = MobileDevice_4Sub
# end class MobileDevice_4Sub


class Document_18Sub(supermod.Document_18):
    def __init__(self, Description=None, Owner=None, File=None, ShareList=None, Size=None, Parent=None):
        super(Document_18Sub, self).__init__(Description, Owner, File, ShareList, Size, Parent, )
supermod.Document_18.subclass = Document_18Sub
# end class Document_18Sub


class Document_14Sub(supermod.Document_14):
    def __init__(self, Description=None, Owner=None, File=None, ShareList=None, Size=None, Parent=None):
        super(Document_14Sub, self).__init__(Description, Owner, File, ShareList, Size, Parent, )
supermod.Document_14.subclass = Document_14Sub
# end class Document_14Sub


class File_14Sub(supermod.File_14):
    def __init__(self, ThumbnailSupported=None, ThumbnailGenerationFailed=None, ThumbnailPreview=None, Parent=None, Size=None, ForwardedCopy=None, Hidden=None):
        super(File_14Sub, self).__init__(ThumbnailSupported, ThumbnailGenerationFailed, ThumbnailPreview, Parent, Size, ForwardedCopy, Hidden, )
supermod.File_14.subclass = File_14Sub
# end class File_14Sub


class ActionDeclineAppointment_18Sub(supermod.ActionDeclineAppointment_18):
    def __init__(self):
        super(ActionDeclineAppointment_18Sub, self).__init__()
supermod.ActionDeclineAppointment_18.subclass = ActionDeclineAppointment_18Sub
# end class ActionDeclineAppointment_18Sub


class ActionTentativelyAcceptAppointment_18Sub(supermod.ActionTentativelyAcceptAppointment_18):
    def __init__(self):
        super(ActionTentativelyAcceptAppointment_18Sub, self).__init__()
supermod.ActionTentativelyAcceptAppointment_18.subclass = ActionTentativelyAcceptAppointment_18Sub
# end class ActionTentativelyAcceptAppointment_18Sub


class ActionAcceptAppointment_18Sub(supermod.ActionAcceptAppointment_18):
    def __init__(self):
        super(ActionAcceptAppointment_18Sub, self).__init__()
supermod.ActionAcceptAppointment_18.subclass = ActionAcceptAppointment_18Sub
# end class ActionAcceptAppointment_18Sub


class ActionMarkAsUnread_18Sub(supermod.ActionMarkAsUnread_18):
    def __init__(self):
        super(ActionMarkAsUnread_18Sub, self).__init__()
supermod.ActionMarkAsUnread_18.subclass = ActionMarkAsUnread_18Sub
# end class ActionMarkAsUnread_18Sub


class ActionPin_18Sub(supermod.ActionPin_18):
    def __init__(self):
        super(ActionPin_18Sub, self).__init__()
supermod.ActionPin_18.subclass = ActionPin_18Sub
# end class ActionPin_18Sub


class ActionForward_18Sub(supermod.ActionForward_18):
    def __init__(self):
        super(ActionForward_18Sub, self).__init__()
supermod.ActionForward_18.subclass = ActionForward_18Sub
# end class ActionForward_18Sub


class ActionToggleNotifications_18Sub(supermod.ActionToggleNotifications_18):
    def __init__(self, SendNotifications=None):
        super(ActionToggleNotifications_18Sub, self).__init__(SendNotifications, )
supermod.ActionToggleNotifications_18.subclass = ActionToggleNotifications_18Sub
# end class ActionToggleNotifications_18Sub


class ActionFollowup_18Sub(supermod.ActionFollowup_18):
    def __init__(self):
        super(ActionFollowup_18Sub, self).__init__()
supermod.ActionFollowup_18.subclass = ActionFollowup_18Sub
# end class ActionFollowup_18Sub


class ActionReplyToAll_18Sub(supermod.ActionReplyToAll_18):
    def __init__(self):
        super(ActionReplyToAll_18Sub, self).__init__()
supermod.ActionReplyToAll_18.subclass = ActionReplyToAll_18Sub
# end class ActionReplyToAll_18Sub


class ActionReply_18Sub(supermod.ActionReply_18):
    def __init__(self):
        super(ActionReply_18Sub, self).__init__()
supermod.ActionReply_18.subclass = ActionReply_18Sub
# end class ActionReply_18Sub


class ActionDelete_18Sub(supermod.ActionDelete_18):
    def __init__(self, Resource=None):
        super(ActionDelete_18Sub, self).__init__(Resource, )
supermod.ActionDelete_18.subclass = ActionDelete_18Sub
# end class ActionDelete_18Sub


class ActionFinishWorkflow_18Sub(supermod.ActionFinishWorkflow_18):
    def __init__(self):
        super(ActionFinishWorkflow_18Sub, self).__init__()
supermod.ActionFinishWorkflow_18.subclass = ActionFinishWorkflow_18Sub
# end class ActionFinishWorkflow_18Sub


class ActionNextStep_18Sub(supermod.ActionNextStep_18):
    def __init__(self, NextActionListId=None):
        super(ActionNextStep_18Sub, self).__init__(NextActionListId, )
supermod.ActionNextStep_18.subclass = ActionNextStep_18Sub
# end class ActionNextStep_18Sub


class ActionHideStream_18Sub(supermod.ActionHideStream_18):
    def __init__(self, Stream=None):
        super(ActionHideStream_18Sub, self).__init__(Stream, )
supermod.ActionHideStream_18.subclass = ActionHideStream_18Sub
# end class ActionHideStream_18Sub


class ActionDeletePinNotification_18Sub(supermod.ActionDeletePinNotification_18):
    def __init__(self, Resource=None):
        super(ActionDeletePinNotification_18Sub, self).__init__(Resource, )
supermod.ActionDeletePinNotification_18.subclass = ActionDeletePinNotification_18Sub
# end class ActionDeletePinNotification_18Sub


class ActionDeleteMention_18Sub(supermod.ActionDeleteMention_18):
    def __init__(self, Resource=None):
        super(ActionDeleteMention_18Sub, self).__init__(Resource, )
supermod.ActionDeleteMention_18.subclass = ActionDeleteMention_18Sub
# end class ActionDeleteMention_18Sub


class ActionDeleteQuestion_18Sub(supermod.ActionDeleteQuestion_18):
    def __init__(self, Resource=None):
        super(ActionDeleteQuestion_18Sub, self).__init__(Resource, )
supermod.ActionDeleteQuestion_18.subclass = ActionDeleteQuestion_18Sub
# end class ActionDeleteQuestion_18Sub


class ActionDeleteReminder_18Sub(supermod.ActionDeleteReminder_18):
    def __init__(self, Resource=None):
        super(ActionDeleteReminder_18Sub, self).__init__(Resource, )
supermod.ActionDeleteReminder_18.subclass = ActionDeleteReminder_18Sub
# end class ActionDeleteReminder_18Sub


class ActionRescheduleReminder_18Sub(supermod.ActionRescheduleReminder_18):
    def __init__(self, Resource=None, Date=None, Timeframe=None):
        super(ActionRescheduleReminder_18Sub, self).__init__(Resource, Date, Timeframe, )
supermod.ActionRescheduleReminder_18.subclass = ActionRescheduleReminder_18Sub
# end class ActionRescheduleReminder_18Sub


class ActionSetReminder_18Sub(supermod.ActionSetReminder_18):
    def __init__(self, Resource=None, Date=None, Timeframe=None):
        super(ActionSetReminder_18Sub, self).__init__(Resource, Date, Timeframe, )
supermod.ActionSetReminder_18.subclass = ActionSetReminder_18Sub
# end class ActionSetReminder_18Sub


class Action_18Sub(supermod.Action_18):
    def __init__(self, Comment=None, IsCommentRequired=None):
        super(Action_18Sub, self).__init__(Comment, IsCommentRequired, )
supermod.Action_18.subclass = Action_18Sub
# end class Action_18Sub


class ReminderBase_20Sub(supermod.ReminderBase_20):
    def __init__(self, Timeframe=None, Date=None):
        super(ReminderBase_20Sub, self).__init__(Timeframe, Date, )
supermod.ReminderBase_20.subclass = ReminderBase_20Sub
# end class ReminderBase_20Sub


class Reminder_21Sub(supermod.Reminder_21):
    def __init__(self, ReminderType=None, Timeframe=None, Date=None):
        super(Reminder_21Sub, self).__init__(ReminderType, Timeframe, Date, )
supermod.Reminder_21.subclass = Reminder_21Sub
# end class Reminder_21Sub


class Reminder_22Sub(supermod.Reminder_22):
    def __init__(self, ReminderType=None, Timeframe=None, Date=None, IsAllDay=None, DisableDefaultActions=None, ReminderSnippet=None):
        super(Reminder_22Sub, self).__init__(ReminderType, Timeframe, Date, IsAllDay, DisableDefaultActions, ReminderSnippet, )
supermod.Reminder_22.subclass = Reminder_22Sub
# end class Reminder_22Sub


class ActionableResourceOverview_20Sub(supermod.ActionableResourceOverview_20):
    def __init__(self, NumberOfRemainingItems=None, NumberOfCompletedItems=None):
        super(ActionableResourceOverview_20Sub, self).__init__(NumberOfRemainingItems, NumberOfCompletedItems, )
supermod.ActionableResourceOverview_20.subclass = ActionableResourceOverview_20Sub
# end class ActionableResourceOverview_20Sub


class ActionableResourceOverview_21Sub(supermod.ActionableResourceOverview_21):
    def __init__(self, NumberOfRemainingItems=None, NumberOfCompletedItems=None):
        super(ActionableResourceOverview_21Sub, self).__init__(NumberOfRemainingItems, NumberOfCompletedItems, )
supermod.ActionableResourceOverview_21.subclass = ActionableResourceOverview_21Sub
# end class ActionableResourceOverview_21Sub


class ActionableResourceOverview_22Sub(supermod.ActionableResourceOverview_22):
    def __init__(self, NumberOfRemainingItems=None, NumberOfCompletedItems=None):
        super(ActionableResourceOverview_22Sub, self).__init__(NumberOfRemainingItems, NumberOfCompletedItems, )
supermod.ActionableResourceOverview_22.subclass = ActionableResourceOverview_22Sub
# end class ActionableResourceOverview_22Sub


class StreamGroup_22Sub(supermod.StreamGroup_22):
    def __init__(self, Group=None):
        super(StreamGroup_22Sub, self).__init__(Group, )
supermod.StreamGroup_22.subclass = StreamGroup_22Sub
# end class StreamGroup_22Sub


class StreamUser_22Sub(supermod.StreamUser_22):
    def __init__(self, User=None):
        super(StreamUser_22Sub, self).__init__(User, )
supermod.StreamUser_22.subclass = StreamUser_22Sub
# end class StreamUser_22Sub


class BoardPersonal_15Sub(supermod.BoardPersonal_15):
    def __init__(self, PinnedItemList=None):
        super(BoardPersonal_15Sub, self).__init__(PinnedItemList, )
supermod.BoardPersonal_15.subclass = BoardPersonal_15Sub
# end class BoardPersonal_15Sub


class BoardPersonal_20Sub(supermod.BoardPersonal_20):
    def __init__(self, PinnedItemList=None):
        super(BoardPersonal_20Sub, self).__init__(PinnedItemList, )
supermod.BoardPersonal_20.subclass = BoardPersonal_20Sub
# end class BoardPersonal_20Sub


class SortActionCustom_13Sub(supermod.SortActionCustom_13):
    def __init__(self):
        super(SortActionCustom_13Sub, self).__init__()
supermod.SortActionCustom_13.subclass = SortActionCustom_13Sub
# end class SortActionCustom_13Sub


class SortActionByStatus_13Sub(supermod.SortActionByStatus_13):
    def __init__(self):
        super(SortActionByStatus_13Sub, self).__init__()
supermod.SortActionByStatus_13.subclass = SortActionByStatus_13Sub
# end class SortActionByStatus_13Sub


class SortActionByModifiedDate_13Sub(supermod.SortActionByModifiedDate_13):
    def __init__(self):
        super(SortActionByModifiedDate_13Sub, self).__init__()
supermod.SortActionByModifiedDate_13.subclass = SortActionByModifiedDate_13Sub
# end class SortActionByModifiedDate_13Sub


class SortActionByCreatedDate_13Sub(supermod.SortActionByCreatedDate_13):
    def __init__(self):
        super(SortActionByCreatedDate_13Sub, self).__init__()
supermod.SortActionByCreatedDate_13.subclass = SortActionByCreatedDate_13Sub
# end class SortActionByCreatedDate_13Sub


class SortActionByName_13Sub(supermod.SortActionByName_13):
    def __init__(self):
        super(SortActionByName_13Sub, self).__init__()
supermod.SortActionByName_13.subclass = SortActionByName_13Sub
# end class SortActionByName_13Sub


class ContextSyncApplication_13Sub(supermod.ContextSyncApplication_13):
    def __init__(self):
        super(ContextSyncApplication_13Sub, self).__init__()
supermod.ContextSyncApplication_13.subclass = ContextSyncApplication_13Sub
# end class ContextSyncApplication_13Sub


class Appointment_20Sub(supermod.Appointment_20):
    def __init__(self, CalendarUId=None, AppointmentTime=None, Location=None, LocationImage=None, LocationLat=None, LocationLng=None, Attendees=None, Recurrence=None, Reminder=None):
        super(Appointment_20Sub, self).__init__(CalendarUId, AppointmentTime, Location, LocationImage, LocationLat, LocationLng, Attendees, Recurrence, Reminder, )
supermod.Appointment_20.subclass = Appointment_20Sub
# end class Appointment_20Sub


class Appointment_22Sub(supermod.Appointment_22):
    def __init__(self, CalendarUId=None, AppointmentTime=None, Location=None, LocationImage=None, LocationLat=None, LocationLng=None, Attendees=None, Recurrence=None, Reminder=None, IsCanceled=None, Response=None, IsOccurrence=None, RecurringMasterResponse=None):
        super(Appointment_22Sub, self).__init__(CalendarUId, AppointmentTime, Location, LocationImage, LocationLat, LocationLng, Attendees, Recurrence, Reminder, IsCanceled, Response, IsOccurrence, RecurringMasterResponse, )
supermod.Appointment_22.subclass = Appointment_22Sub
# end class Appointment_22Sub


class Invoice_22Sub(supermod.Invoice_22):
    def __init__(self, Price=None, Currency=None):
        super(Invoice_22Sub, self).__init__(Price, Currency, )
supermod.Invoice_22.subclass = Invoice_22Sub
# end class Invoice_22Sub


class DiscussionSeparatorUnread_18Sub(supermod.DiscussionSeparatorUnread_18):
    def __init__(self):
        super(DiscussionSeparatorUnread_18Sub, self).__init__()
supermod.DiscussionSeparatorUnread_18.subclass = DiscussionSeparatorUnread_18Sub
# end class DiscussionSeparatorUnread_18Sub


class DiscussionChat_18Sub(supermod.DiscussionChat_18):
    def __init__(self, Post=None, Unread=None):
        super(DiscussionChat_18Sub, self).__init__(Post, Unread, )
supermod.DiscussionChat_18.subclass = DiscussionChat_18Sub
# end class DiscussionChat_18Sub


class DiscussionCard_18Sub(supermod.DiscussionCard_18):
    def __init__(self, DiscussionItemListPage=None, FirstPost=None, PreviousPost=None, ShareList=None, VisibilityListCount=None, VisibilityListNonGroupMembers=None, PinnedToList=None, Files=None, Author=None, ManagedByAssistant=None):
        super(DiscussionCard_18Sub, self).__init__(DiscussionItemListPage, FirstPost, PreviousPost, ShareList, VisibilityListCount, VisibilityListNonGroupMembers, PinnedToList, Files, Author, ManagedByAssistant, )
supermod.DiscussionCard_18.subclass = DiscussionCard_18Sub
# end class DiscussionCard_18Sub


class DiscussionSeparatorBase_20Sub(supermod.DiscussionSeparatorBase_20):
    def __init__(self):
        super(DiscussionSeparatorBase_20Sub, self).__init__()
supermod.DiscussionSeparatorBase_20.subclass = DiscussionSeparatorBase_20Sub
# end class DiscussionSeparatorBase_20Sub


class DiscussionChat_20Sub(supermod.DiscussionChat_20):
    def __init__(self, Post=None):
        super(DiscussionChat_20Sub, self).__init__(Post, )
supermod.DiscussionChat_20.subclass = DiscussionChat_20Sub
# end class DiscussionChat_20Sub


class DiscussionCard_20Sub(supermod.DiscussionCard_20):
    def __init__(self, PostListPage=None, MoreUnreadCount=None, TotalUnreadCount=None, FirstPost=None, PreviousPost=None, ShareList=None, VisibilityListCount=None, VisibilityListNonGroupMembers=None, PinnedToList=None, Files=None, Author=None, ManagedByAssistant=None, RelatedCardCount=None):
        super(DiscussionCard_20Sub, self).__init__(PostListPage, MoreUnreadCount, TotalUnreadCount, FirstPost, PreviousPost, ShareList, VisibilityListCount, VisibilityListNonGroupMembers, PinnedToList, Files, Author, ManagedByAssistant, RelatedCardCount, )
supermod.DiscussionCard_20.subclass = DiscussionCard_20Sub
# end class DiscussionCard_20Sub


class DiscussionCardCombined_20Sub(supermod.DiscussionCardCombined_20):
    def __init__(self, PostListPage=None, RelatedDiscussionList=None):
        super(DiscussionCardCombined_20Sub, self).__init__(PostListPage, RelatedDiscussionList, )
supermod.DiscussionCardCombined_20.subclass = DiscussionCardCombined_20Sub
# end class DiscussionCardCombined_20Sub


class DiscussionSeparatorBase_22Sub(supermod.DiscussionSeparatorBase_22):
    def __init__(self):
        super(DiscussionSeparatorBase_22Sub, self).__init__()
supermod.DiscussionSeparatorBase_22.subclass = DiscussionSeparatorBase_22Sub
# end class DiscussionSeparatorBase_22Sub


class DiscussionChat_22Sub(supermod.DiscussionChat_22):
    def __init__(self, Post=None):
        super(DiscussionChat_22Sub, self).__init__(Post, )
supermod.DiscussionChat_22.subclass = DiscussionChat_22Sub
# end class DiscussionChat_22Sub


class DiscussionCardCombined_22Sub(supermod.DiscussionCardCombined_22):
    def __init__(self, PostListPage=None, RelatedDiscussionList=None):
        super(DiscussionCardCombined_22Sub, self).__init__(PostListPage, RelatedDiscussionList, )
supermod.DiscussionCardCombined_22.subclass = DiscussionCardCombined_22Sub
# end class DiscussionCardCombined_22Sub


class DiscussionCard_22Sub(supermod.DiscussionCard_22):
    def __init__(self, PostListPage=None, MoreUnreadCount=None, TotalUnreadCount=None, FirstPost=None, PreviousPost=None, ShareList=None, VisibilityListCount=None, PinnedToList=None, Files=None, Author=None, ManagedByAssistant=None, RelatedCardCount=None, IsForward=None, ForwardedCopy=None, CombinedCardId=None, TrashStatus=None):
        super(DiscussionCard_22Sub, self).__init__(PostListPage, MoreUnreadCount, TotalUnreadCount, FirstPost, PreviousPost, ShareList, VisibilityListCount, PinnedToList, Files, Author, ManagedByAssistant, RelatedCardCount, IsForward, ForwardedCopy, CombinedCardId, TrashStatus, )
supermod.DiscussionCard_22.subclass = DiscussionCard_22Sub
# end class DiscussionCard_22Sub


class User_14Sub(supermod.User_14):
    def __init__(self, FirstName=None, LastName=None, CultureCode=None, RegionCode=None, TimeZoneId=None, ChatId=None, AccountList=None, Token=None, OnboardingComplete=None, OnlineStatus=None, LastActivityAt=None, Registered=None):
        super(User_14Sub, self).__init__(FirstName, LastName, CultureCode, RegionCode, TimeZoneId, ChatId, AccountList, Token, OnboardingComplete, OnlineStatus, LastActivityAt, Registered, )
supermod.User_14.subclass = User_14Sub
# end class User_14Sub


class ReminderCalendar_20Sub(supermod.ReminderCalendar_20):
    def __init__(self):
        super(ReminderCalendar_20Sub, self).__init__()
supermod.ReminderCalendar_20.subclass = ReminderCalendar_20Sub
# end class ReminderCalendar_20Sub


class ReminderAppointment_20Sub(supermod.ReminderAppointment_20):
    def __init__(self):
        super(ReminderAppointment_20Sub, self).__init__()
supermod.ReminderAppointment_20.subclass = ReminderAppointment_20Sub
# end class ReminderAppointment_20Sub


class ReminderFollowup_20Sub(supermod.ReminderFollowup_20):
    def __init__(self):
        super(ReminderFollowup_20Sub, self).__init__()
supermod.ReminderFollowup_20.subclass = ReminderFollowup_20Sub
# end class ReminderFollowup_20Sub


class ReminderQuestion_20Sub(supermod.ReminderQuestion_20):
    def __init__(self):
        super(ReminderQuestion_20Sub, self).__init__()
supermod.ReminderQuestion_20.subclass = ReminderQuestion_20Sub
# end class ReminderQuestion_20Sub


class ReminderMention_20Sub(supermod.ReminderMention_20):
    def __init__(self):
        super(ReminderMention_20Sub, self).__init__()
supermod.ReminderMention_20.subclass = ReminderMention_20Sub
# end class ReminderMention_20Sub


class Reminder_20Sub(supermod.Reminder_20):
    def __init__(self):
        super(Reminder_20Sub, self).__init__()
supermod.Reminder_20.subclass = Reminder_20Sub
# end class Reminder_20Sub


class ContactCard_22Sub(supermod.ContactCard_22):
    def __init__(self, Organization=None, Notes=None, Position=None):
        super(ContactCard_22Sub, self).__init__(Organization, Notes, Position, )
supermod.ContactCard_22.subclass = ContactCard_22Sub
# end class ContactCard_22Sub


class Attendee_20Sub(supermod.Attendee_20):
    def __init__(self, IsOptional=None, Status=None, Email=None, StatusUpdatedAt=None):
        super(Attendee_20Sub, self).__init__(IsOptional, Status, Email, StatusUpdatedAt, )
supermod.Attendee_20.subclass = Attendee_20Sub
# end class Attendee_20Sub


class DiscussionCardSeparator_20Sub(supermod.DiscussionCardSeparator_20):
    def __init__(self):
        super(DiscussionCardSeparator_20Sub, self).__init__()
supermod.DiscussionCardSeparator_20.subclass = DiscussionCardSeparator_20Sub
# end class DiscussionCardSeparator_20Sub


class DiscussionChatSeparator_20Sub(supermod.DiscussionChatSeparator_20):
    def __init__(self):
        super(DiscussionChatSeparator_20Sub, self).__init__()
supermod.DiscussionChatSeparator_20.subclass = DiscussionChatSeparator_20Sub
# end class DiscussionChatSeparator_20Sub


class DiscussionCardSeparator_22Sub(supermod.DiscussionCardSeparator_22):
    def __init__(self):
        super(DiscussionCardSeparator_22Sub, self).__init__()
supermod.DiscussionCardSeparator_22.subclass = DiscussionCardSeparator_22Sub
# end class DiscussionCardSeparator_22Sub


class DiscussionChatSeparator_22Sub(supermod.DiscussionChatSeparator_22):
    def __init__(self):
        super(DiscussionChatSeparator_22Sub, self).__init__()
supermod.DiscussionChatSeparator_22.subclass = DiscussionChatSeparator_22Sub
# end class DiscussionChatSeparator_22Sub


def get_root_tag(node):
    tag = supermod.Tag_pattern_.match(node.tag).groups()[-1]
    rootClass = None
    rootClass = supermod.GDSClassesMapping.get(tag)
    if rootClass is None and hasattr(supermod, tag):
        rootClass = getattr(supermod, tag)
    return tag, rootClass


def parse(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'ApiIndex_1'
        rootClass = supermod.ApiIndex_1
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    if not silence:
        sys.stdout.write('<?xml version="1.0" ?>\n')
        rootObj.export(
            sys.stdout, 0, name_=rootTag,
            namespacedef_='xmlns:bc="http://www.bcsocial.io/Sdk/WebService"',
            pretty_print=True)
    return rootObj


def parseEtree(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'ApiIndex_1'
        rootClass = supermod.ApiIndex_1
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    mapping = {}
    rootElement = rootObj.to_etree(None, name_=rootTag, mapping_=mapping)
    reverse_mapping = rootObj.gds_reverse_node_mapping(mapping)
    if not silence:
        content = etree_.tostring(
            rootElement, pretty_print=True,
            xml_declaration=True, encoding="utf-8")
        sys.stdout.write(content)
        sys.stdout.write('\n')
    return rootObj, rootElement, mapping, reverse_mapping


def parseString(inString, silence=False):
    from StringIO import StringIO
    parser = None
    doc = parsexml_(StringIO(inString), parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'ApiIndex_1'
        rootClass = supermod.ApiIndex_1
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    if not silence:
        sys.stdout.write('<?xml version="1.0" ?>\n')
        rootObj.export(
            sys.stdout, 0, name_=rootTag,
            namespacedef_='xmlns:bc="http://www.bcsocial.io/Sdk/WebService"')
    return rootObj


def parseLiteral(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'ApiIndex_1'
        rootClass = supermod.ApiIndex_1
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    if not silence:
        sys.stdout.write('#from ??? import *\n\n')
        sys.stdout.write('import ??? as model_\n\n')
        sys.stdout.write('rootObj = model_.rootClass(\n')
        rootObj.exportLiteral(sys.stdout, 0, name_=rootTag)
        sys.stdout.write(')\n')
    return rootObj


USAGE_TEXT = """
Usage: python ???.py <infilename>
"""


def usage():
    print(USAGE_TEXT)
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        usage()
    infilename = args[0]
    parse(infilename)


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    main()
