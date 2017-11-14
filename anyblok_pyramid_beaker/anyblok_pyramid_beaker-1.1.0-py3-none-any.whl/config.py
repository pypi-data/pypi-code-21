# This file is a part of the AnyBlok / Pyramid / Beaker project
#
#    Copyright (C) 2016 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.config import Configuration
from anyblok_pyramid import config  # noqa for update config


Configuration.add_configuration_groups('pyramid', ['beaker'])
Configuration.add_configuration_groups('gunicorn', ['beaker'])


def get_db_name(request):
    dbname = request.session.get('dbname')
    if not dbname:
        dbname = Configuration.get('db_name')

    return dbname


@Configuration.add('beaker', label="Beaker session")
def define_beaker_option(group):
    group.add_argument('--beaker-data-dir',
                       dest='beaker.session.data_dir',
                       help="Used with any back-end that stores its data in "
                            "physical files, such as the dbm or file-based "
                            "back-ends. This path should be an absolute path "
                            "to the directory that stores the files.")
    group.add_argument('--beaker-lock-dir',
                       dest='beaker.session.lock_dir',
                       help="Used with every back-end, to coordinate locking. "
                            "With caching, this lock file is used to ensure "
                            "that multiple processes/threads aren’t "
                            "attempting to re-create the same value at the "
                            "same time (The Dog-Pile Effect)")
    group.add_argument('--beaker-memcache-module',
                       dest='beaker.session.memcache_module',
                       help="One of the names memcache, cmemcache, pylibmc, "
                            "or auto. Default is auto. Specifies which "
                            "memcached client library should be imported when "
                            "using the ext:memcached backend. If left at its "
                            "default of auto, pylibmc is favored first, then "
                            "cmemcache, then memcache.")
    group.add_argument('--beaker-type',
                       dest='beaker.session.type',
                       help="The name of the back-end to use for storing the "
                            "sessions or cache objects.\nAvailable back-ends "
                            "supplied with Beaker: file, dbm, memory, "
                            "ext:memcached, ext:database, ext:google\nFor "
                            "sessions, the additional type of cookie is "
                            "available which will store all the session data "
                            "in the cookie itself. As such, size limitations "
                            "apply (4096 bytes).\nSome of these back-ends "
                            "require the url option as listed below.")
    group.add_argument('--beaker-url',
                       dest='beaker.session.url',
                       help="URL is specific to use of either ext:memcached "
                            "or ext:database. When using one of those types, "
                            "this option is required. When used with "
                            "ext:memcached, this should be either a single, "
                            "or semi-colon separated list of memcached "
                            "servers When used with ext:database, this should "
                            "be a valid SQLAlchemy database string.")
    group.add_argument('--beaker-cookie-expires',
                       dest='beaker.session.cookie_expires',
                       help="Determines when the cookie used to track the "
                            "client-side of the session will expire. When set "
                            "to a boolean value, it will either expire at the "
                            "end of the browsers session, or never expire. "
                            "Setting to a datetime forces a hard ending time "
                            "for the session (generally used for setting a "
                            "session to a far off date). Setting to an "
                            "integer will result in the cookie being set to "
                            "expire in that many seconds. I.e. a value of 300 "
                            "will result in the cookie being set to expire in "
                            "300 seconds. Defaults to never expiring.")
    group.add_argument('--beaker-cookie-domain',
                       dest='beaker.session.cookie_domain',
                       help="What domain the cookie should be set to. When "
                            "using sub-domains, this should be set to the "
                            "main domain the cookie should be valid for. For "
                            "example, if a cookie should be valid under "
                            "www.nowhere.com and files.nowhere.com then it "
                            "should be set to .nowhere.com. Defaults to the "
                            "current domain in its entirety.")
    group.add_argument('--beaker-key',
                       dest='beaker.session.key',
                       help="Name of the cookie key used to save the session "
                            "under.")
    group.add_argument('--beaker-secret',
                       dest='beaker.session.secret',
                       help="Used with the HMAC to ensure session integrity. "
                            "This value should ideally be a randomly "
                            "generated string. When using in a cluster "
                            "environment, the secret must be the same on "
                            "every machine.")
    group.add_argument('--beaker-secure',
                       dest='beaker.session.secure',
                       help="Whether or not the session cookie should be "
                            "marked as secure. When marked as secure, "
                            "browsers are instructed to not send the cookie "
                            "over anything other than an SSL connection.")
    group.add_argument('--beaker-timeout',
                       dest='beaker.session.timeout',
                       help="Seconds until the session is considered invalid, "
                            "after which it will be ignored and invalidated. "
                            "This number is based on the time since the "
                            "session was last accessed, not from when the "
                            "session was created. Defaults to never expiring.")
    group.add_argument('--beaker-encrypt-key',
                       dest='beaker.session.encrypt_key',
                       help="Encryption key to use for the AES cipher. This "
                            "should be a fairly long randomly generated "
                            "string.")
    group.add_argument('--beaker-validate-key',
                       dest='beaker.session.validate_key',
                       help="Validation key used to sign the AES encrypted "
                            "data.")


@Configuration.add('plugins')
def update_plugins(group):
    group.set_defaults(get_db_name='anyblok_pyramid_beaker.config:get_db_name')
