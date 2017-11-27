from __future__ import absolute_import, unicode_literals

#: Task state is unknown (assumed pending since you know the id).
PENDING = 'PENDING'
#: Task was received by a worker.
RECEIVED = 'RECEIVED'
#: Task was started by a worker (:setting:`CELERY_TRACK_STARTED`).
STARTED = 'STARTED'
#: Task succeeded
SUCCESS = 'SUCCESS'
#: Task failed
FAILURE = 'FAILURE'
#: Task was revoked.
REVOKED = 'REVOKED'
#: Task is waiting for retry.
RETRY = 'RETRY'
IGNORED = 'IGNORED'
REJECTED = 'REJECTED'

READY_STATES = frozenset([SUCCESS, FAILURE, REVOKED])
UNREADY_STATES = frozenset([PENDING, RECEIVED, STARTED, RETRY])
EXCEPTION_STATES = frozenset([RETRY, FAILURE, REVOKED])
PROPAGATE_STATES = frozenset([FAILURE, REVOKED])

ALL_STATES = (
    (PENDING, PENDING),
    (RECEIVED, RECEIVED),
    (STARTED, STARTED),
    (SUCCESS, SUCCESS),
    (FAILURE, FAILURE),
    (RETRY, RETRY),
    (REVOKED, REVOKED),
)