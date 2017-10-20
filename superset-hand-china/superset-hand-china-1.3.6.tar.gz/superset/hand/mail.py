from superset import app, db
from . import models
import superset.models.core as superset_models
from flask_mail import Mail as FMail, Message
from flask_babel import gettext as __
from flask_babel import lazy_gettext as _
import json, datetime, time, os
import logging


class Mail:

    "user to get slice content and send mail"

    def testConn(server, port, email, password):
        print("here")
        ssl = True
        if int(port) == 25:
            ssl = False
        app.config.update(
            # EMAIL SETTINGS
            MAIL_SERVER=server,
            MAIL_PORT=port,
            MAIL_USE_TLS=False,
            MAIL_USE_SSL=ssl,
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
        print(language)
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
                # pageContent = '<html><head><meta charset="utf-8"/></html><body><div style="margin-bottom: 20px;">仪表盘切片监控异常---' + sendSlc.slice_name+ ', <a target="_blank" href="' + (address + standalone_endpoint) + '">查看详情</a></div>'
                # send mail and write mail log
                print('======== send mail =======')
                f = open(app.config.get('SEND_MAIL_LOG'), 'a')
                timeStr = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                if language == 'en':
                    subject = "Abnormal monitoring of the Dashboard Slice ---" + sendSlc.slice_name
                else:
                    subject = "仪表盘切片监控异常——" + sendSlc.slice_name
                # subject = "仪表盘切片监控异常——" + sendSlc.slice_name
                sender = mail.email
                receiver = condition.receive_address
                f.writelines(timeStr + '    ' + '邮件主题：' + subject + '    ' + '由 ' + sender + ' 开始发送给 ' + receiver + '\n')
                f.close()
                Mail.send(mail, pageContent, sendSlc.slice_name, receiver, language)
                break

    def send(mailInfo, pageContent, sliceName, receive_address, language):
        if mailInfo.port == 25:
            ssl = False
        else:
            ssl = True
        app.config.update(
            # EMAIL SETTINGS
            MAIL_SERVER=mailInfo.smtp_server,
            MAIL_PORT=mailInfo.port,
            MAIL_USE_TLS=False,
            MAIL_USE_SSL=ssl,
            MAIL_USE_SMTP=True,
            MAIL_USERNAME=mailInfo.email,
            MAIL_PASSWORD=mailInfo.password
        )
        if language == 'en':
            subject = "Abnormal monitoring of the Dashboard Slice ---" + sliceName
        else:
            subject = "仪表盘切片监控异常——" + sliceName
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
            f = open(app.config.get('SEND_MAIL_LOG'), 'a')
            timeStr = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            try:
                mail.send(msg)
                print('====================== mail has sended ! ========================')
                f.writelines(timeStr + '    ' + '邮件发送成功\n\n')
            except Exception as e:
                f.writelines(timeStr + '    ' + '邮件发送失败, 原因：' + str(e) + '\n\n')
            f.close()
