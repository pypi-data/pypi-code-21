from superset import app, db
from . import models
import superset.models.core as superset_models
from flask_mail import Mail as FMail, Message
from flask_babel import gettext as __
from flask_babel import lazy_gettext as _
import json, datetime, time, os
import logging
import base64

class Mail:

    "user to get slice content and send mail"

    def testConn(server, port, ssl, email, password):
        app.config.update(
            # EMAIL SETTINGS
            MAIL_SERVER=server,
            MAIL_PORT=port,
            MAIL_USE_TLS=False,
            MAIL_USE_SSL=(ssl == 'true' and True or False),
            MAIL_USE_SMTP=True,
            MAIL_USERNAME=email,
            MAIL_PASSWORD=password,
        )
        mail = FMail(app)
        msg = Message(
            subject= _("Test Connection"),
            sender=email,
            recipients=['kaiwen.xu@hand-china.com']
        )
        msg.html = _("<h3>Email Connection Test!</h3>")
        with app.app_context():
            try:
                mail.send(msg)
                return 'true'
            except Exception as e:
                logging.exception(e)
                return str(e)


    def findSliceException(scheduler, cookies, userId, language):
        print('====== monitor slice =====')
        mail = db.session.query(models.Mail).filter_by(user_id=userId).one()
        condition = db.session.query(models.Condition).filter_by(warn_scheduler_id=scheduler.id).one()
        # get monitor slice json data
        monitorSlc = db.session.query(superset_models.Slice).filter_by(id=condition.slice_id).one()
        monitorViz = json.loads(monitorSlc.get_viz().get_json())

        # get send slice json data
        sendSlc = db.session.query(superset_models.Slice).filter_by(id=condition.send_slice_id).one()
        sendViz = json.loads(sendSlc.get_viz().get_json())

        viz_type = sendViz['form_data']['viz_type']
        standalone_endpoint = sendSlc.slice_url + '&standalone=true'
        # print(standalone_endpoint)
        records = monitorViz['json_data']['records']
        # print(records)
        for record in records:
            expr = condition.expr.replace('x', str(record[condition.metric]))
            if eval(expr):
                print('==============exception has occured=================')
                # get html content
                address = 'http://' + app.config.get('SERVER_ADDRESS')
                if language == 'en':
                    pageContent = '<html><head><meta charset="utf-8"/></html><body><div style="margin-bottom: 20px;">Abnormal monitoring of the Dashboard Slice ---' + sendSlc.slice_name+ ', <a target="_blank" href="' + (address + standalone_endpoint) + '">View Details</a></div>'
                else:
                    pageContent = '<html><head><meta charset="utf-8"/></html><body><div style="margin-bottom: 20px;">仪表盘切片监控异常---' + sendSlc.slice_name+ ', <a target="_blank" href="' + (address + standalone_endpoint) + '">查看详情</a></div>'
                # send mail and write mail log
                print('======== send mail =======')
                receiver = condition.receive_address
                Mail.send(mail, pageContent, sendSlc.slice_name, receiver, scheduler.id, language)
                break

    def send(mailInfo, pageContent, sliceName, receive_address, schedulerId, language):
        app.config.update(
            # EMAIL SETTINGS
            MAIL_SERVER=mailInfo.smtp_server,
            MAIL_PORT=mailInfo.port,
            MAIL_USE_TLS=False,
            MAIL_USE_SSL=mailInfo.ssl,
            MAIL_USE_SMTP=True,
            MAIL_USERNAME=mailInfo.email,
            MAIL_PASSWORD=base64.decodestring(mailInfo.password.encode(encoding="utf-8")).decode()
        )
        if language == 'en':
            subject = "Abnormal Slice ---" + sliceName
        else:
            subject = "异常切片——" + sliceName
        sender = mailInfo.email
        receiver = receive_address.split(',')
        mail = FMail(app)

        msg = Message(
            subject=subject,
            sender=sender,
            recipients=receiver
        )

        msg.html = pageContent
        print(pageContent)

        with app.app_context():
            try:
                mail.send(msg)
                log = models.MailLog(
                    warn_scheduler_id = schedulerId,
                    subject = subject,
                    sender = sender,
                    receiver = receiver,
                    status = True,
                )
                db.session.add(log)
            except Exception as e:
                log = models.MailLog(
                    warn_scheduler_id = schedulerId,
                    subject = subject,
                    sender = sender,
                    receiver = receiver,
                    status = False,
                    reason = str(e),
                )
                db.session.add(log)
            db.session.commit()
