"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""
__license__ = 'Apache 2.0'
__author__ = 'Darin Gordon'
__credits__ = ['Michael, Alex, Marcel']
__maintainer__ = 'Darin Gordon'
__email__ = 'dkcdkg@gmail.com'
__status__ = 'Development'

import threading

from .exceptions import (
    AbsoluteExpiredSessionException,
    AccountException,
    AdditionalAuthenticationRequired,
    AuthenticationException,
    AuthorizationException,
    ConsumedTOTPToken,
    ExpiredSessionException,
    IdleExpiredSessionException,
    IncorrectCredentialsException,
    InvalidAuthenticationSequenceException,
    InvalidSessionException,
    LockedAccountException,
    MultiRealmAuthenticationException,
    SessionException,
    StoppedSessionException,
    UnauthenticatedException,
    UnauthorizedException,
    YosaiException,
)

from yosaipy2.core.event.event import (
    EVENT_TOPIC,
    EventLogger,
    event_bus,
)

from yosaipy2.core.serialize import abcs as serialize_abcs
from yosaipy2.core.event import abcs as event_abcs
from yosaipy2.core.account import abcs as account_abcs
from yosaipy2.core.authc import abcs as authc_abcs
from yosaipy2.core.realm import abcs as realm_abcs
from yosaipy2.core.authz import abcs as authz_abcs
from yosaipy2.core.session import abcs as session_abcs
from yosaipy2.core.subject import abcs as subject_abcs
from yosaipy2.core.mgt import abcs as mgt_abcs
from yosaipy2.core.cache import abcs as cache_abcs

from yosaipy2.core.utils.utils import (
    OrderedSet,
    ThreadStateManager,
    maybe_resolve,
    memoized_property,
    qualified_name,
    resolve_reference,
    unix_epoch_time,
)

from yosaipy2.core.conf.yosaisettings import (
    LazySettings,
    Settings,
)

from yosaipy2.core.mgt.mgt_settings import (
    RememberMeSettings,
    SecurityManagerSettings,
)

from yosaipy2.core.session.session_settings import (
    SessionSettings,
)

from yosaipy2.core.authc.authc_settings import (
    AuthenticationSettings,
)

from yosaipy2.core.logging.slogging import (
    load_logconfig,
)

from yosaipy2.core.account.account import (
    Account,
)

from yosaipy2.core.concurrency.concurrency import (
    StoppableScheduledExecutor,
)

from yosaipy2.core.subject.identifier import (
    SimpleIdentifierCollection,
)

from yosaipy2.core.session.session import (
    AbstractSessionStore,
    CachingSessionStore,
    SessionKey,
    NativeSessionManager,
    SessionStorageEvaluator,
    DelegatingSession,
    MemorySessionStore,
    NativeSessionHandler,
    SimpleSession,
)

from yosaipy2.core.serialize.serialize import (
    SerializationManager,
)

thread_local = threading.local()  # use only one global instance

from yosaipy2.core.subject.subject import (
    Yosai,
    SubjectContext,
    SubjectStore,
    DelegatingSubject,
    SecurityManagerCreator,
    global_subject_context,
    global_yosai_context,
)

from yosaipy2.core.authc.strategy import (
    AuthenticationAttempt,
    all_realms_successful_strategy,
    at_least_one_realm_successful_strategy,
    first_realm_successful_strategy,
)

from yosaipy2.core.authc.authc import (
    DefaultAuthenticator,
    TOTPToken,
    UsernamePasswordToken,
    token_info,
)

from yosaipy2.core.authc.credential import (
    PasslibVerifier,
    create_totp_factory,
)

from yosaipy2.core.authz.authz import (
    DefaultPermissionVerifier,
    ModularRealmAuthorizer,
    Permission,
)

from yosaipy2.core.realm.realm import (
    AccountStoreRealm,
)

from yosaipy2.core.mgt.mgt import (
    AbstractRememberMeManager,
    NativeSecurityManager,
)
