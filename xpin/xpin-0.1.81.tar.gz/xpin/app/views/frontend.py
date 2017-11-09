#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import datetime
import json

from flask import Blueprint
from flask import jsonify
from flask import request, current_app, g

from ... import constants
from ...log import logger
from ..models import Pin, User, PinLog
from ..extensions import db

bp = Blueprint('frontend', __name__)


@bp.before_request
def unpack_input():
    for key in ('data', 'sign'):
        if key not in request.values:
            return jsonify(
                ret=constants.RET_PARAMS_INVALID
            )

    client_secret = current_app.config['CLIENT_SECRET']

    my_sign = hashlib.md5('|'.join(
        [client_secret, request.values['data']]
    )).hexdigest()

    if my_sign != request.values['sign']:
        return jsonify(
            ret=constants.RET_SIGN_INVALID
        )

    try:
        g.input = json.loads(request.values['data'])
    except:
        logger.error('json loads fail. request: %s', request)
        return jsonify(
            ret=constants.RET_PARAMS_INVALID
        )


@bp.before_request
def clear_expired_pins():
    """
    删除掉过期的pin
    :return:
    """
    Pin.query.filter(
        Pin.expire_time < datetime.datetime.now(),
        ).delete()


@bp.route(constants.URL_PIN_CREATE, methods=['POST'])
def create_pin():

    for key in ('username', 'source'):
        if key not in g.input:
            return jsonify(
                ret=constants.RET_PARAMS_INVALID
            )

    username = g.input['username']
    source = g.input['source']

    user = User.query.filter(User.username == username).first()

    if not user or not user.valid:
        logger.error('invalid user. request: %s', request)
        return jsonify(
            ret=constants.RET_USER_INVALID,
        )
    ding_user = g.ding.get_user(user.ding_id)
    # 判断是否是合法的企业内部用户
    if not ding_user:
        logger.error('invalid ding user. request: %s', request)
        return jsonify(
            ret=constants.RET_USER_INVALID,
        )

    # 删掉旧的
    Pin.query.filter(
        Pin.user_id == user.id,
        Pin.source == source,
    ).delete()

    db.session.commit()

    pin = Pin()
    pin.user_id = user.id
    pin.source = source
    pin.code = Pin.create_code(current_app.config['PIN_LENGTH'])
    # X_REAL_IP 是解决有nginx代理的情况
    # nginx 配置:
    # proxy_set_header X-Real-IP $remote_addr;
    # proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    pin.address = request.headers.get('X_REAL_IP') or request.remote_addr
    pin.remain_try_times = current_app.config['PIN_MAX_TRY_TIMES']

    if current_app.config['PIN_MAX_AGE']:
        pin.expire_time = datetime.datetime.now() + datetime.timedelta(seconds=current_app.config['PIN_MAX_AGE'])

    db.session.add(pin)
    db.session.commit()

    if current_app.config['PIN_LOG']:
        pin_log = PinLog()
        pin_log.username = pin.username
        pin_log.source = pin.source
        pin_log.code = pin.code
        pin_log.address = pin.address
        pin_log.create_time = pin.create_time
        pin_log.expire_time = pin.expire_time

        db.session.add(pin_log)
        db.session.commit()

    msg_title = current_app.config['MSG_TITLE']
    msg_content = current_app.config['MSG_CONTENT_TPL'].format(
        username=username,
        source=source,
        address=pin.address,
        pin=pin.code,
    )

    if not g.ding.emit(msg_title, msg_content, user_list=[user.ding_id]):
        logger.error('ding emit fail. request: %s', request)

    user_email = ding_user.get('email')
    if user_email:
        if g.send_cloud:
            if not g.send_cloud.emit(msg_title, msg_content, [user_email]):
                logger.error('send_cloud emit fail. request: %s', request)

        if g.mail:
            if not g.mail.emit(msg_title, msg_content, [user_email]):
                logger.error('mail emit fail. request: %s', request)

    return jsonify(
        ret=0
    )


@bp.route(constants.URL_PIN_VERIFY, methods=['POST'])
def verify_pin():
    """
    验证pin
    :return:
    """

    for key in ('username', 'source', 'pin'):
        if key not in g.input:
            return jsonify(
                ret=constants.RET_PARAMS_INVALID
            )

    username = g.input['username']
    source = g.input['source']
    pin_code = g.input['pin']

    user = User.query.filter(User.username == username).first()

    if not user or not user.valid:
        logger.error('invalid user. request: %s', request)
        return jsonify(
            ret=constants.RET_USER_INVALID,
        )

    pin = Pin.query.filter(
        Pin.user_id == user.id,
        Pin.source == source,
        ).first()

    if not pin:
        return jsonify(
            ret=constants.RET_PIN_INVALID
        )

    if pin.code != pin_code:
        if pin.remain_try_times is not None:
            pin.remain_try_times -= 1
            if pin.remain_try_times <= 0:
                # 超过次数，删掉pin
                db.session.delete(pin)
            else:
                db.session.add(pin)

            db.session.commit()

        return jsonify(
            ret=constants.RET_PIN_INVALID
        )

    if pin.expire_time and pin.expire_time < datetime.datetime.now():
        return jsonify(
            ret=constants.RET_PIN_EXPIRED,
        )

    # 删掉旧的
    Pin.query.filter(
        Pin.user_id == user.id,
        Pin.source == source,
        ).delete()

    db.session.commit()

    return jsonify(
        ret=0
    )
