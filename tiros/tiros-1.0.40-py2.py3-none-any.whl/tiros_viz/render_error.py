
from flask import render_template, Markup
import json
import pprint

error_alert = "alert alert-danger alert-error"


def snap_error(code, m_error):
    try:
        # It reached Tiros Service (tiros error)
        j = json.loads(m_error)
        error = j.get('error')
        m = error.get('message')
        msg = Markup("<strong>Error Code: %d</strong>\n %s" % (code, m))
    except (AttributeError, ValueError):
        # It didn't reach Tiros Service (boto error)
        msg = Markup("<strong>Error Code: %d</strong> %s" % (code, m_error))
    return render_template('index.html',
                           alert=error_alert,
                           snapshot_validation=msg)


def error(err_msg):
    msg = Markup("<strong>Error!</strong> %s." % err_msg)
    return render_template('index.html',
                           alert=error_alert,
                           snapshot_validation=msg)


def async_error(msg):
    error_msg = Markup("<strong>Error!</strong> %s." % msg)
    return {'results': [],
            'messages': [error_msg],
            'colors': []}
