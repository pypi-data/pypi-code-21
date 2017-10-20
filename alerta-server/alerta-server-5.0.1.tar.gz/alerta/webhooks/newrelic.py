
from flask import request, g, jsonify
from flask_cors import cross_origin

from alerta.auth.utils import permission
from alerta.exceptions import ApiError, RejectException
from alerta.models.alert import Alert
from alerta.utils.api import process_alert, add_remote_ip
from . import webhooks


def parse_newrelic(alert):

    if 'version' not in alert:
        raise ValueError("New Relic Legacy Alerting is not supported")

    status = alert['current_state'].lower()
    if status == 'open':
        severity = alert['severity'].lower()
    elif status == 'acknowledged':
        severity = alert['severity'].lower()
        status = 'ack'
    elif status == 'closed':
        severity = 'ok'
    else:
        severity = alert['severity'].lower()

    return Alert(
        resource=alert['targets'][0]['name'],
        event=alert['condition_name'],
        environment='Production',
        severity=severity,
        status=status,
        service=[alert['account_name']],
        group=alert['targets'][0]['type'],
        text=alert['details'],
        tags=['%s:%s' % (key, value) for (key, value) in alert['targets'][0]['labels'].items()],
        attributes={
            'moreInfo': '<a href="%s" target="_blank">Incident URL</a>' % alert['incident_url'],
            'runBook': '<a href="%s" target="_blank">Runbook URL</a>' % alert['runbook_url']
        },
        origin='New Relic/v%s' % alert['version'],
        event_type=alert['event_type'].lower(),
        raw_data=alert
    )


@webhooks.route('/webhooks/newrelic', methods=['OPTIONS', 'POST'])
@cross_origin()
@permission('write:webhooks')
def newrelic():

    try:
        incomingAlert = parse_newrelic(request.json)
    except ValueError as e:
        raise ApiError(str(e), 400)

    if g.get('customer', None):
        incomingAlert.customer = g.get('customer')

    add_remote_ip(request, incomingAlert)

    try:
        alert = process_alert(incomingAlert)
    except RejectException as e:
        raise ApiError(str(e), 403)
    except Exception as e:
        raise ApiError(str(e), 500)

    if alert:
        return jsonify(status="ok", id=alert.id, alert=alert.serialize), 201
    else:
        raise ApiError("insert or update of New Relic alert failed", 500)
