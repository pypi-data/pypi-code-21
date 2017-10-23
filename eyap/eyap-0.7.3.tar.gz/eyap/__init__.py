"""Extended yap package for comment management.

With eyap, you can choose a backend to manage your comments. A key goal of
the eyap package is that you can write your code in a generic way and easily
switch the back-end. For example, you can use a simple file back-end with
something like like the following:

```

>>> import eyap, tempfile, os, shutil  # Import some things used for demo.
>>> backend = 'file'                   #  Use a simple file backend for demo.
>>> finfo = {'owner': 'emin63', 'realm': tempfile.mkdtemp(), 'topic': 'test'}
>>> comment_thread = eyap.Make.comment_thread('file', **finfo)
>>> comment_thread.add_comment('Testing things', allow_create=True)
>>> comment_thread.add_comment('is great!')

```

The code above will create a new comment thread and add a comment to it
while also creating the thread if it does not exist. Later, you could
access the thread via something like:

```
>>> print(str(comment_thread.lookup_comments())) # doctest: +ELLIPSIS
========================================
Subject: Testing things ...
Timestamp: ...
----------
Testing things
========================================
Subject: is great! ...
Timestamp: ...
----------
is great!

```

The main reason for the existence of something like eyap is so that you
could use pretty much the same exact code with a different backend. For
example, using 'github' instead of 'file' and setting realm/owner to the
organization/repo in github while providing a valid user/token for github
access will post or read an issue from github.

```

>>> ginfo = {'owner': 'emin63', 'realm': 'eyap', 'topic': 'Describe usage'}
>>> g_thread = eyap.Make.comment_thread('github', **ginfo)
>>> print(str(g_thread.lookup_comments())) # doctest: +ELLIPSIS
========================================
Subject: We need a simple description of how to u ...
Timestamp: 2017-07-19T22:26:51Z
----------
We need a simple description of how to use eyap.
========================================
Subject: Start with top-level README.md ...
Timestamp: 2017-07-19T22:22:56Z
----------
Start with top-level README.md
========================================
Subject: All done! ...
Timestamp: 2017-07-19T22:26:51Z
----------
All done!

```

Note that in the above, we only read from github since we did not provide
any username or password. If you had a username and token or password, you
could post comments to github as well.

   Plesae do *NOT* post to above issue; use your own repo for tests.  :)

Finally, we cleanup the file based backend since we don't need it anymore.

```

>>> shutil.rmtree(finfo['realm'])  # Remove the directory to cleanup test.
>>> os.path.exists(finfo['realm']) # Verify we cleaned up.
False

```
"""

import doctest

from eyap.core import comments, github_comments

class Make(object):

    known_backends = {
        'file': comments.FileCommentThread,
        'github': github_comments.GitHubCommentThread,
        }

    @classmethod
    def comment_thread(cls, backend, *args, **kwargs):
        ct_cls = cls.known_backends.get(backend)
        if not ct_cls:
            return None
        return ct_cls(*args, **kwargs)

if __name__ == '__main__':
    doctest.testmod()
    print('Finished Tests')
