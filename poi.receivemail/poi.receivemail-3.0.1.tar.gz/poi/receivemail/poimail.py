import base64
import logging
import quopri
from email.Errors import HeaderParseError
from email import message_from_string
from email import utils as email_utils
from email import Header

from zope.event import notify
from AccessControl import Unauthorized
from plone import api
from plone.namedfile import NamedBlobFile
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Five import BrowserView
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from Products.Poi.adapters import IResponseContainer
from Products.Poi.adapters import Response
from Products.Poi.config import DEFAULT_ISSUE_MIME_TYPE
from Products.Poi.config import ISSUE_MIME_TYPES
from Products.Poi.utils import normalize_filename
from zope.component.hooks import getSite
from zope.schema._bootstrapinterfaces import ConstraintNotSatisfied

from poi.receivemail.config import LISTEN_ADDRESSES
from poi.receivemail.config import FAKE_MANAGER
from poi.receivemail.config import ADVANCED_SUBJECT_MATCH
from poi.receivemail.config import ADD_ATTACHMENTS
from poi.receivemail.config import NEEDED_PERMISSIONS


logger = logging.getLogger('poimail')


def cleanup_search_string(s):
    # Taken from livesearch_reply.py
    bad_chars = ["(", ")"]
    for char in bad_chars:
        s = s.replace(char, '"%s"' % char)
    for char in '?-+*':
        s = s.replace(char, ' ')
    return s


class Receiver(BrowserView):

    def __call__(self):
        mail = self.request.get('Mail')
        mail = mail.strip()
        if not mail:
            msg = u'No mail found in request'
            logger.warn(msg)
            return msg
        message = message_from_string(mail)
        self.encoding = self._get_encoding(message)

        logger.debug('--------')
        logger.debug(mail)
        logger.debug('--------')
        logger.debug(message)
        from_addresses = self.get_addresses(message, 'From')
        to_addresses = self.get_addresses(message, 'To')
        if not from_addresses or not to_addresses:
            msg = u'No From or To address found in request'
            logger.warn(msg)
            return msg
        # Pick the first one; strange anyway if there would be more.
        from_name, from_address = from_addresses[0]
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        email_from_address = portal.getProperty('email_from_address')
        if from_address.lower() == email_from_address.lower():
            # This too easily means that a message sent by Poi ends up
            # being added as a reply on an issue that we have just
            # created.
            msg = u'Ignoring mail from portal email_from_address'
            logger.info(msg)
            return msg

        subject_line = message.get('Subject', '')
        subjects = []
        decoded = Header.decode_header(subject_line)
        for decoded_string, charset in decoded:
            if charset:
                decoded_string = decoded_string.decode(charset)
            subjects.append(decoded_string)
        subject = u' '.join(subjects)

        logger.info(
            "Tracker at %s received mail from %r to %r with "
            "subject %r", self.context.absolute_url(),
            from_address, to_addresses, subject)
        details, mimetype = self.get_details_and_mimetype(message)
        logger.debug('Got payload with mimetype %s from email.', mimetype)
        # Transform to an allowed mime type, if needed.
        details, mimetype = self.to_allowed_mimetype(details, mimetype)
        if not details:
            # Details is a required field.
            details = '.'
            mimetype = 'text/plain'
            logger.info('No details found in email.')

        # Create an attachment from the complete email.
        attachment = mail

        tags = self.get_tags(message)
        if tags:
            logger.debug("Determined tags: %r", tags)
        else:
            logger.debug("Could not determine tags.")

        # Get all info that we need from the mail.
        mail_info = {
            'subject': subject,
            'tags': tags,
            'message': message,
            'details': details,
            'from_address': from_address,
            'attachment': attachment,
            'mimetype': mimetype,
        }

        # Possibly switch to a different user.
        user = self.find_user_for_switching(from_address)
        if user is None:
            result = self.create_content(**mail_info)
        else:
            with api.env.adopt_user(user=user):
                current_user = api.user.get_current()
                user_id = current_user.getId()
                user_name = current_user.getUserName()
                logger.info("Switched email=%s to user name=%s (id=%s)",
                            from_address, user_name, user_id)
                role = self.find_role_to_fake()
                if not role:
                    result = self.create_content(**mail_info)
                else:
                    logger.info("Faking %s role for user %s", role, user_id)
                    # Fake a few extra roles as well.  For example,
                    # TrackerManager may not have the 'Copy or Move'
                    # permission, but Anonymous may have.  Go figure.
                    roles = [role, 'Member', 'Anonymous']
                    with api.env.adopt_roles(roles):
                        result = self.create_content(**mail_info)

        # We need to return something.
        if result:
            # error
            return result
        return mail

    def create_content(self, **kwargs):
        subject = kwargs['subject']
        tags = kwargs['tags']
        message = kwargs['message']
        details = kwargs['details']
        from_address = kwargs['from_address']
        attachment = kwargs['attachment']
        mimetype = kwargs['mimetype']
        issue = self.find_issue(subject, tags, message)
        if issue is None:
            manager = self.get_manager(message, tags)
            logger.debug("Determined manager: %s", manager)
            if not subject:
                # When there is no subject, we always want to create a
                # new issue, as we do not want to try to match a empty
                # or fake subject.
                # We also want to flay the user alive...
                subject = '[no subject]'
            try:
                issue = self.create_issue(
                    title=subject, details=details, contactEmail=from_address,
                    attachment=attachment, responsibleManager=manager,
                    subject=tags)
            except Unauthorized, exc:
                logger.error(u'Unauthorized to create issue: %s', exc)
                return u'Unauthorized'
            logger.info('Created issue from email at %s', issue.absolute_url())
        else:
            attachment = NamedBlobFile(
                attachment,
                contentType='message/rfc822',
                filename=u'email.eml')
            try:
                self.add_response(issue, text=details, mimetype=mimetype,
                                  attachment=attachment)
            except Unauthorized, exc:
                logger.error(u'Unauthorized to add response: %s', exc)
                return u'Unauthorized'
            logger.info('Added mail as response to issue %s',
                        issue.absolute_url())

        if ADD_ATTACHMENTS:
            attachments = self.get_attachments(message)
            for name, att in attachments:
                logger.info("Adding attachment as response: %r, length %d",
                            name, len(att))
                name = safe_unicode(name)
                try:
                    attachment = NamedBlobFile(att, filename=name)
                except ConstraintNotSatisfied:
                    # Found in live data: a filename that includes a newline...
                    logger.info('Trying to normalize filename %s', name)
                    name = normalize_filename(name, self.request)
                    logger.info('Normalize to %s', name)
                    attachment = NamedBlobFile(att, filename=name)
                try:
                    self.add_response(issue, text='', mimetype='text/plain',
                                      attachment=attachment)
                except Unauthorized, exc:
                    # We mark this as unauthorized, but the main issue
                    # or response is already created, which is
                    # actually fine.
                    logger.error(u'Unauthorized to add response: %s', exc)
                    return u'Unauthorized'

    def find_user_for_switching(self, from_address):
        """Find user to switch to.

        We want a different user for two things:

        1. Switch to the user that belongs to the given email address.

        2. Give the user the Manage role for the duration of this
           request.

        This view is normally used by the smtp2zope script (or
        something similar) on the local machine.  That script may
        submit anonymously.  That could mean the current user does not
        have enough permissions to submit an issue or add a response.
        So we elevate his privileges by giving him the Manager role.
        But when we do that, this means anonymous users could abuse
        this to submit through the web.  That is not good.  So we only
        elevate privileges when the request originates on the local
        computer.
        """
        remote_address = self.request.get('HTTP_X_FORWARDED_FOR')
        if not remote_address:
            # Note that request.get('HTTP_something') always returns
            # at least an empty string, also when the key is not in
            # the request, so a default value would be ignored.
            remote_address = self.request.get('REMOTE_ADDR')
        if remote_address not in LISTEN_ADDRESSES:
            return

        # First, see if we can get an existing user based on the From
        # address.
        pas = getToolByName(self.context, 'acl_users')
        users = pas.searchUsers(email=from_address)
        # Also try lowercase
        from_address = from_address.lower()
        if not users:
            users = pas.searchUsers(email=from_address)
        # If 'email' is not in the properties (say: ldap), we can get
        # far too many results; so we do a double check.  Also,
        # apparently ldap can leave '\r\n' at the end of the email
        # address, so we strip it.  And we compare lowercase.
        for user in users:
            # user is a dictionary
            email = user.get('email')
            if not email:
                continue
            if email.strip().lower() != from_address:
                continue
            user_id = user['userid']
            user_object = pas.getUserById(user_id)
            if user_object:
                return user_object

    def find_role_to_fake(self):
        # See if this user already has the needed permissions,
        # otherwise return a role that we should fake.
        if not FAKE_MANAGER:
            return
        faked = False
        for permission in NEEDED_PERMISSIONS:
            if api.user.has_permission(permission, obj=self.context):
                continue
            faked = True
            break
        if not faked:
            return
        # We need to fake a role.
        site = getSite()
        role = 'TrackerManager'
        if role not in site.__ac_roles__:
            # On Plone 3 Poi has no TrackerManager role yet.
            role = 'Manager'
        return role

    def get_addresses(self, message, header_name):
        """Get addresses from the header_name.

        This is usually 'From' or 'To', but other headers may contain
        addresses too, so we allow all, unlike we used to do.

        We expect just one From address and one To address, but
        multiple addresses can also be checked.

        May easily be something ugly like this:
        =?utf-8?q?Portal_Administrator_?=<m.van.rees@zestsoftware.nl>

        From the Python docs:

        decode_header(header)

          Decode a message header value without converting charset.

          Returns a list of (decoded_string, charset) pairs containing
          each of the decoded parts of the header.  Charset is None
          for non-encoded parts of the header, otherwise a lower-case
          string containing the name of the character set specified in
          the encoded string.

          An email.Errors.HeaderParseError may be raised when certain
          decoding error occurs (e.g. a base64 decoding exception).
        """
        if not header_name:
            raise ValueError

        address = message.get(header_name, '')
        try:
            decoded = Header.decode_header(address)
        except HeaderParseError:
            logger.warn("Could not parse header %r", address)
            return []
        logger.debug('Decoded header: %r', decoded)
        for decoded_string, charset in decoded:
            if charset is not None:
                # Surely this is no email address but a name.
                continue
            if '@' not in decoded_string:
                continue

            return email_utils.getaddresses((decoded_string, ))
        return []

    def get_manager(self, message, tags):
        """Determine the responsible manager.

        A custom implementation could pick a manager based on the tags
        that have already been determined.
        """
        default = '(UNASSIGNED)'
        return default

    def get_tags(self, message):
        """Determine the tags that should be set for this issue.

        You could add tags based on e.g. the To or From address.
        """
        return []

    def add_response(self, issue, text, mimetype, attachment):
        new_response = Response(text)
        new_response.mimetype = mimetype
        new_response.attachment = attachment
        folder = IResponseContainer(issue)
        folder.add(new_response)

    def find_issue_by_number(self, subject, tags='', message=''):
        """Find an issue for which this email is a response.

        In this simple version we only search for email subjects that
        look like they are a response to an email that Poi has sent
        out.  We are just interested in '#123' somewhere in the
        subject, as long as the current tracker has an issue with that
        number.
        """
        idx = subject.find('#')
        if idx == -1:
            return
        number = subject[idx + 1:]
        number = number[:number.find(' ')]
        try:
            # We only try this; we do not need the integer value.
            int(number)
        except ValueError:
            number = None
        if number is None:
            return
        issue = getattr(self.context, number, None)
        if issue:
            logger.debug('Found issue by number: #%s', number)
            return issue

    def find_issue(self, subject, tags, message):
        """Find an issue for which this email is a response.

        The default way of finding an issue is simple: we search
        '#123' in the email subject and see if we have such an issue
        number.

        You may want to set ADVANCED_SUBJECT_MATCH to True to search
        for issues matching the given title and tags as well.  Note
        that a Subject like 'printer does not work' or 'Hi' will
        likely match too many unrelated issues, so that may defeat the
        advanced matching.

        The message is passed in as argument as well, to make
        alternative schemes possible.
        """
        if not ADVANCED_SUBJECT_MATCH:
            # We only want the simple form.
            return self.find_issue_by_number(subject, tags, message)
        for bad in ('Re:', 'Fw:', 'Fwd:', 'Antw:'):
            subject = subject.replace(bad, '').replace(bad.upper(), '')
        subject = subject.strip()
        if not subject:
            # C'mon people: learn how to use email!
            return
        # Now we might have something like this:
        # '[Issue Tracker] #45 - Nieuw issue: Heehee'
        tracker_prefix = '[%s]' % self.context.Title()
        if subject.find(tracker_prefix) != -1:
            # Looks like an answer to an issue report from this
            # tracker.  See if we have such an issue number.
            issue = self.find_issue_by_number(subject, tags, message)
            if issue:
                return issue

        search_path = '/'.join(self.context.getPhysicalPath())
        catalog = getToolByName(self.context, 'portal_catalog')
        # Search for issue in this tracker with the same Title and
        # Subject/keywords/tags/categories.  Pick the most recentely
        # created one.

        filter = dict(
            path=search_path,
            Title=cleanup_search_string(subject),
            sort_on='created',
            sort_order='reverse')
        if tags:
            filter['Subject'] = tags
        results = catalog.searchResults(filter)
        if results:
            logger.debug('Found issue by title: %r', subject)
            return results[0].getObject()
        return None

    def get_details_and_mimetype(self, message):
        """Get text and mimetype for the details field of the issue.

        The mimetype is not always needed, but it is good to know
        whether we have html or plain text.

        We prefer to get plain text.  Actually, getting the html from
        the email looks quite okay as long as we put it through the
        safe html transform.
        And the Poi config must allow text/html.
        """
        payload = message.get_payload()
        if not message.is_multipart():
            mimetype = message.get_content_type()
            charset = message.get_content_charset()
            encoding = self._get_encoding(message)
            payload = self._decode(payload, encoding)
            logger.debug("Charset: %r", charset)
            if charset and charset != 'utf-8':
                # We only want to store unicode or ascii or utf-8 in
                # Plone.
                # Decode to unicode:
                payload = payload.decode(charset, 'replace')
                # Encode to utf-8:
                payload = payload.encode('utf-8', 'replace')
            return payload, mimetype
        for part in payload:
            if part.is_multipart():
                text, mimetype = self.get_details_and_mimetype(part)
            else:
                text, mimetype = self.part_to_text_and_mimetype(part)
            text = text.strip()
            # Might be empty?
            if text:
                return text, mimetype
        return '', 'text/plain'

    def _get_encoding(self, message):
        # Especially base64 or quoted-printable.
        return message.get('Content-Transfer-Encoding', '').lower()

    def part_to_text_and_mimetype(self, part):
        payload = part.get_payload()
        encoding = self._get_encoding(part)
        payload = self._decode(payload, encoding)
        if part.get_content_type() == 'text/plain':
            return payload, 'text/plain'
        tt = getToolByName(self.context, 'portal_transforms')
        if part.get_content_type() == 'text/html':
            mimetype = 'text/x-html-safe'
            safe = tt.convertTo(mimetype, payload,
                                mimetype='text/html')
            # Poi responses fail on view when you have the x-html-safe
            # mime type.  Fixed in Poi 1.2.12 (unreleased) but hey, we
            # only need that safe mimetype for the conversion.
            mimetype = 'text/html'
        else:
            # This might not work in all cases, e.g. for attachments,
            # but that is not tested yet.
            mimetype = 'text/plain'
            safe = tt.convertTo(mimetype, payload)
        if safe is None:
            logger.warn("Converting part to mimetype %s failed.", mimetype)
            return u'', 'text/plain'
        return safe.getData(), mimetype

    def to_allowed_mimetype(self, text, mimetype):
        if mimetype not in ISSUE_MIME_TYPES:
            tt = getToolByName(self.context, 'portal_transforms')
            logger.info('Converting mail text mimetype from %s to %s.',
                        mimetype, DEFAULT_ISSUE_MIME_TYPE)
            text = tt.convertTo(
                DEFAULT_ISSUE_MIME_TYPE, text, mimetype=mimetype)
            if text is None:
                logger.warn("Converting text to mimetype %s failed.", mimetype)
                return u'', 'text/plain'
            text = text.getData().strip()
        return text, mimetype

    def _decode(self, payload, encoding=''):
        # Decode from base64 or quoted-printable.
        if not encoding:
            # Take the encoding of the main message.
            encoding = self.encoding
        if encoding == 'base64':
            try:
                return base64.decodestring(payload)
            except TypeError:
                return payload
        if encoding == 'quoted-printable':
            return quopri.decodestring(payload)
        if encoding == 'binary':
            return payload
        # If there is no encoding, we could try a few, but that may also
        # destroy a perfectly fine text that does not need extra handling.
        return payload

    def get_attachments(self, message):
        """Get attachments.
        """
        payload = message.get_payload()
        if not message.is_multipart():
            mimetype = message.get_content_type()
            if mimetype.startswith('text'):
                return []
            filename = message.get_filename()
            if not filename:
                return []
            encoding = self._get_encoding(message)
            data = self._decode(payload, encoding)
            return [(filename, data)]
        attachments = []
        for part in payload:
            attachments.extend(self.get_attachments(part))
        return attachments

    def create_issue(self, **kwargs):
        """Create an issue in the given tracker.

        Also perform workflow and
        rename-after-creation initialisation.

        Renaming can give hard to debug permission problems
        in combination with our adopt_user and adopt_roles,
        so we simply determine the good id in the first place.
        """
        tracker = self.context
        # newId = tracker.generateUniqueId('PoiIssue')
        # Taken over from PoiIssue._renameAfterCreation:
        maxId = 0
        for id in tracker.objectIds():
            try:
                intId = int(id)
                maxId = max(maxId, intId)
            except (TypeError, ValueError):
                pass
        newId = str(maxId + 1)
        _createObjectByType('PoiIssue', tracker, newId,
                            **kwargs)
        issue = getattr(tracker, newId)
        # issue._renameAfterCreation()

        # Some fields have no effect when set with the above
        # _createObjectByType call.
        for fieldname, value in kwargs.items():
            field = issue.getField(fieldname)
            if field:
                if fieldname == 'attachment':
                    field.set(issue, value, mimetype='message/rfc822',
                              filename=u'email.eml')
                else:
                    field.set(issue, value)

        # Some fields are required.  We pick the first available
        # option.
        issue.setIssueType(tracker.getAvailableIssueTypes()[0]['id'])
        issue.setArea(tracker.getAvailableAreas()[0]['id'])

        # This is done by default already when you do not specify anything:
        # issue.setSeverity(tracker.getDefaultSeverity())
        # This could be interesting:
        # issue.setSteps(steps, mimetype='text/x-web-intelligent')
        valid = issue.isValid()
        if not valid:
            logger.warn('Issue is not valid. '
                        'Any following exception is probably caused by that.')

        # Creation has finished, so we remove the archetypes flag for
        # that, otherwise the issue gets renamed when someone edits
        # it.
        issue.unmarkCreationFlag()
        try:
            notify(ObjectInitializedEvent(issue))
        except WorkflowException:
            logger.warn('Caught workflow exception when initializing issue.')
        workflow_tool = getToolByName(tracker, 'portal_workflow')
        # The 'post' transition is only available when the issue is valid.  And
        # it is only available on Plone 3, as on Plone 4 it is already
        # transitioned from new to unconfirmed during the handling of the
        # ObjectInitializedEvent.
        if workflow_tool.getInfoFor(issue, 'review_state') == 'new':
            if valid:
                workflow_tool.doActionFor(issue, 'post')
            else:
                logger.warn(
                    'Invalid issue is in new state and may be invisible: %s',
                    issue.absolute_url())
        issue.reindexObject()
        return issue
