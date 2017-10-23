"""Module for handling reading comments.
"""

import datetime
import csv
import os
import doctest
import re
import urllib.parse

import dateutil.parser

from requests.models import Response


class SingleComment(object):  # pylint: disable=too-many-instance-attributes
    """Class to hold information about a single comment.

    SingleComment instances will usually be collected into a list of
    instances in a CommentSection representing a thread of discussion.
    """

    def __init__(self, user, timestamp, body, url, summary=None, markup=None,
                 summary_cls=None):
        """Initializer.

        :arg user:        String name for user creating/owning comment.

        :arg timestamp:   String timestamp for when comment last edited.

        :arg body:        String body of comment.

        :arg url:         String url where comment lives.

        :arg summary=None:    One line text summar of comment.

        :arg markup=None:     Text of comment marked up with HTML or
                              other way of display. If not provided, we just
                              use body.

        :arg summary_cls=None:  Optional string representing CSS class for
                                summary. You can set this as late as you like.
                                If provided, comment_view.html will apply this
                                class to the summary which can be helpful in
                                making certain posts stand out.

        """
        self.user = user
        self.timestamp = timestamp
        self.body = body
        self.markup = markup if markup else body
        self.url = url
        self.summary = summary if summary else (
            body.split('\n')[0][0:40] + ' ...')
        self.summary_cls = None
        self.display_timestamp = timestamp

    def make_anchor_id(self):
        """Return string to use as URL anchor for this comment.
        """
        result = re.sub(
            '[^a-zA-Z0-9_]', '_', self.user + '_' + self.timestamp)
        return result

    def make_url(self, my_request, anchor_id=None):
        """Make URL to this comment.

        :arg my_request:  The request object where this comment is seen from.

        :arg anchor_id=None:    Optional anchor id. If None, we use
                                self.make_anchor_id()

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:       String URL to this comment.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:        Be able to create links to this comment.

        """
        if anchor_id is None:
            anchor_id = self.make_anchor_id()
        result = '{}?{}#{}'.format(
            my_request.path, urllib.parse.urlencode(my_request.args),
            anchor_id)

        return result

    def to_dict(self):
        """Return description of self in dict format.

        This is useful for serializing to something like json later.
        """
        jdict = {
            'user': self.user,
            'body': self.body,
            'markup': self.markup,
            'url': self.url,
            'timestamp': self.timestamp
            }
        return jdict

    def set_display_mode(self, mytz, fmt):
        """Set the display mode for self.

        :arg mytz:        A pytz.timezone object.

        :arg fmt:         A format string for strftime.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:        Modifies self.display_timestamp to first parse
                        self.timestamp and then format according to given
                        timezone and format string.

        """
        my_stamp = dateutil.parser.parse(self.timestamp)
        tz_stamp = my_stamp.astimezone(
            mytz) if my_stamp.tzinfo is not None else my_stamp
        self.display_timestamp = tz_stamp.strftime(fmt)

    def __str__(self):
        return 'Subject: %s\nTimestamp: %s\n%s\n%s' % (
            self.summary, self.display_timestamp, '-'*10, self.body)


class CommentSection(object):
    """Class to represent a section, thread or other collection of comments.

    A CommentSection has the following useful features:

       self.comments:  Sequence of SingleComment instances with the comments.
       self.display:   Function to dislay the comments.

    """

    def __init__(self, comments):
        """Initializer.

        :arg comments:        Sequence of SingleComment instances representing
                              a thread or other collection of related comments.

        """
        self.comments = comments

    def set_display_mode(self, mytz, fmt="%Y-%m-%d %H:%M:%S %Z%z"):
        """Call set_display_mode on items in self.comments with given args.

        :arg mytz:      A pytz.timezone object.

        :arg fmt="%Y-%m-%d%H:%M:%S%Z%z":   Optional format string.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:        Call set_display_mode(mytz, fmt) for everything in
                        self.comments.

        """
        for item in self.comments:
            item.set_display_mode(mytz, fmt)

    def show(self):
        "Return string showing the comments."
        result = '\n'.join(['%s\n%s' % ('=' * 40, c) for c in self.comments])
        return result

    def __str__(self):
        return self.show()


class CommentThread(object):
    """Abstract class used to interact with discussion threads.

    The idea is that we have the CommentThread as an abstract class which
    various backends can implement. Then you can use say GitHub issues as
    your comment thread or switch easily to a local database or cloud
    database or whatever relatively painlessly.
    """

    # Regular expression for what consistutes a hashtag.
    hashtag_re = r'\s+(#[-.a-zA-Z_/]+[a-zA-Z_])'

    # Regular expression for valid attachment location
    valid_attachment_loc_re = '^[-.a-zA-Z0-9_,/]+$'

    def __init__(self, owner, realm, topic,
                 user=None, token=None, thread_id=None):
        """Initializer.

        :arg owner:    String owner (e.g., the repository owner if using
                       GitHub as a backend).

        :arg realm:    The realm (e.g., repository name on GitHub).

        :arg topic:    Topic or title of comment thread.

        :arg user:     String user name.

        :arg token:    Password or token to use to connect to backend.

        :arg thread_id=None: Optional thread id. Can leave as None if you want
                             this dynamically looked up via lookup_thread_id.

        """
        self.owner = owner
        self.realm = realm
        self.topic = topic
        self.user = user
        self.token = token
        self.thread_id = thread_id
        self.content = None

    def lookup_thread_id(self):
        """Find the thread id for the given owner, realm, topic, etc.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:       The thread id (either integer, string, etc., depending
                        on the backend) used for the given thread indicated
                        by args to init.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:        Basically this serves to lookup the thread id if/when
                        necessary so we can interact with the comments.
                        It is an abstract method so that we can write higher
                        level methods in the CommentThread object which need
                        it.

        """
        raise NotImplementedError

    def add_comment(self, body, allow_create=False, allow_hashes=False):
        """Add the string comments to the thread.

        :arg body:        String/text of comment to add.

        :arg allow_create=False: Whether to automatically create a new thread
                                 if a thread does not exist (usually by calling
                                 self.create_thread).

        :arg allow_hashes=False: Whether to support hashtag mentions of other
                                 topics and automatically insert comment in
                                 body into those topics as well.

                                 *IMPORTANT*: if you recursively call
                                 add_comment to insert the hashes, you should
                                 make sure to set this to False to prevent
                                 infinite hash processing loops.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:       Usually a response object from an HTTP call indicating
                        what happend. Otherwise, somethng with a status_code
                        and reason argument will suffice.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:        Add a comment to the discussion thread.

        """
        raise NotImplementedError

    def lookup_comments(self, reverse=False):
        """Return CommentSection instance showing all comments for thread.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:        Require backend implementations to do this so it can
                        be called in higher level functions like
                        get_comment_section.

                        Note that the user probably should call
                        get_comment_section and not call this directly.
        """
        raise NotImplementedError

    def create_thread(self, body):
        """Create a new thread.

        :arg body:        Text for the initial comment in the thread.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:       A response object indicating what happened.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:        Create a thread for self.topic.

        """
        raise NotImplementedError

    def get_comment_section(self, force_reload=False, reverse=False):
        """Get CommentSection instance representing all comments for thread.

        :arg force_reload=False:  Whether to force reloading comments
                                  directly or allow using what is cached
                                  in self.content if possible.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:       CommentSection representing all comments for thread.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:        High-level function called by user to get comments.

        """
        if self.content is not None and not force_reload:
            return self.content
        if self.thread_id is None:
            self.thread_id = self.lookup_thread_id()
        self.content = self.lookup_comments(reverse=reverse)

        return self.content

    def validate_attachment_location(self, location):
        """Validate a proposed attachment location.

        :arg location:     String representing location to put attachment.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Raises an exception if attachment location is bad.
                   By default, this just forces reasonable characters.
                   Sub-classes can override as desired.

        """
        if not re.compile(self.valid_attachment_loc_re).match(location):
            raise ValueError(
                'Bad chars in attachment location. Must match %s' % (
                    self.valid_attachment_loc_re))

    def upload_attachment(self, location, data):
        """Upload an attachment.

        :arg location:    String identifying name or location to store
                          the attachment. Usually just a file name is
                          a good thing to use.

        :arg data:        Either str or bytes or a file-like object with
                          a read method represneting data for the attachment.
                          If a string, it must be a base 64 encoded
                          representation of the bytes. If bytes, then we
                          will base64.b64encode(data).decode('ascii').

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:    A string that can be added to a comment to reference
                     the attachment.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:     Provide a way to upload a file attachment.  Ideally
                     sub-classes should call validate_attachment_location
                     to make sure the proposed location is valid.

        """
        raise NotImplementedError


class FileCommentThread(CommentThread):
    """Example file based comment thread for testing and showing example usage.

    This is a subclass of CommentThread which implements the required functions
    to store the comments in files. The realm argument to __init__ must be
    an existing directory. The topic argument to __init__ will be the name
    of the file to store comments in.
    """

    header = ['user', 'timestamp', 'body', 'url']  # header for csv file

    def lookup_thread_id(self):
        "Lookup the thread id as path to comment file."

        path = os.path.join(self.realm, self.topic + '.csv')
        return path

    def lookup_comments(self, reverse=False):
        "Implement as required by parent to lookup comments in file system."

        comments = []
        if self.thread_id is None:
            self.thread_id = self.lookup_thread_id()
        path = self.thread_id
        with open(self.thread_id, 'r', newline='') as fdesc:
            reader = csv.reader(fdesc)
            header = reader.__next__()
            assert header == self.header
            for num, line in enumerate(reader):
                if not line:
                    continue
                assert len(line) == 4, 'Line %i in path %s misformatted' % (
                    num+1, path)
                comments.append(SingleComment(*line))
        if reverse:
            comments = list(reversed(comments))

        return CommentSection(comments)

    def create_thread(self, body):
        """Implement create_thread as required by parent.

        This basically just calls add_comment with allow_create=True
        and then builds a response object to indicate everything is fine.
        """
        self.add_comment(body, allow_create=True)
        the_response = Response()
        the_response.code = "OK"
        the_response.status_code = 200

    def add_comment(self, body, allow_create=False, allow_hashes=False):
        "Implement as required by parent to store comment in CSV file."

        if allow_hashes:
            raise ValueError('allow_hashes not implemented for %s yet' % (
                self.__class__.__name__))
        if self.thread_id is None:
            self.thread_id = self.lookup_thread_id()
        if not os.path.exists(self.thread_id):
            if not allow_create:
                raise KeyError(self.topic)
            with open(self.thread_id, 'a', newline='') as fdesc:
                csv.writer(fdesc).writerow(self.header)

        with open(self.thread_id, 'a', newline='') as fdesc:
            writer = csv.writer(fdesc)
            writer.writerow([self.user, datetime.datetime.utcnow(), body, ''])

    @staticmethod
    def _regr_tests():
        """
>>> import os, tempfile, shutil
>>> from eyap.core import comments
>>> tempdir = tempfile.mkdtemp()
>>> owner, realm, topic, user = 'test_owner', tempdir, 'test_topic', 't_user'
>>> ctest = comments.FileCommentThread(owner, realm, topic, user, None)
>>> ctest.add_comment('testing comment%ccool stuff here' % 10, allow_create=1)
>>> print(ctest.lookup_comments()) # doctest: +ELLIPSIS
========================================
Subject: testing comment ...
Timestamp: ...
----------
testing comment
cool stuff here
>>> shutil.rmtree(tempdir)
>>> os.path.exists(tempdir)
False
"""

if __name__ == '__main__':
    doctest.testmod()
    print('Finished tests.')
