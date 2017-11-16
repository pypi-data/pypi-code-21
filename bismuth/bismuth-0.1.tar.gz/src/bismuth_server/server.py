# coding=utf-8
from asyncio import ensure_future, CancelledError
from base64 import b64encode, b64decode
import binascii

from sanic import Sanic
from sanic.exceptions import InvalidUsage, NotFound
from sanic.log import log
from sanic.response import json as json_response, text as text_response
import ujson as json
from websockets.exceptions import ConnectionClosed

from bismuth_server import premade
from bismuth_server.crypto import validate_signature
from bismuth_server.db import (
    initialize_db,
    cleanup_db,
    get_message_content,
    post_message,
    get_topic_keys,
    listen,
    unlisten,
    unlisten_all,
)
from bismuth_server.hotpatch import patch_all


# websocket status codes
WEBSOCKET_NORMAL_CLOSE = 1000
WEBSOCKET_GOING_AWAY = 1001
WEBSOCKET_CANNOT_ACCEPT = 1003
WEBSOCKET_GENERIC_VIOLATION = 1008
WEBSOCKET_TOO_LARGE = 1009
WEBSOCKET_UNEXPECTED_CONDITION = 1011


# hotpatch libraries
patch_all()


app = Sanic('bismuth')


app.listener('before_server_start')(initialize_db)
app.listener('after_server_stop')(cleanup_db)


if app.config.get('DEBUG'):
    app.static('/', './src/bismuth_jsclient/app.html')
    app.static('/static', './src/bismuth_jsclient/static')


# TODO: make websocket_max_size configurable
app.config.WEBSOCKET_MAX_SIZE = 2 ** 26  # 64 MB


def remote_address(request):
    """Return the remote address of the request in a (host, port) tuple"""
    if 'x-real-ip' in request.headers:
        ip = request.headers['x-real-ip']
        port = request.headers.get('x-real-port')
    else:
        ip, port = request.ip
    try:
        port = int(port, base=10)
    except (TypeError, ValueError):
        pass
    return ip, port


# noinspection PyUnusedLocal
@app.route('/tree/<message_id>', {'OPTIONS'}, strict_slashes=True)
async def http_get_message_options(_request, message_id):
    return premade.options_get


@app.route('/tree/<message_id>', {'GET'}, strict_slashes=True)
async def http_get_message(_request, message_id):
    try:
        message_id = bytes.fromhex(message_id)
    except ValueError:
        return text_response(
            f"Invalid message id hex: '{message_id}'",
            status=422,
        )
    message = await get_message_content(message_id)
    if message is None:
        return text_response(
            f"Message not found: {message_id.hex()}",
            status=404,
        )

    return json_response(
        {
            'topic': message['topic'].hex(),
            'topic_serial': message['topic_serial'],
            'signature': message['signature'] and b64encode(message['signature']),
            'message_body': b64encode(message['message_body']),
        },
        escape_forward_slashes=False,
        headers=premade.CACHE_FOREVER,
    )


@app.route('/tree', {'OPTIONS'}, strict_slashes=True)
async def http_post_message_options(_request):
    return premade.options_post


@app.route('/tree', {'POST'}, strict_slashes=True)
async def http_post_message(request):
    content_type = request.headers.get('content_type')
    if not content_type or (
        content_type != 'application/json' and
        not content_type.startswith('application/json;')  # in case encoding is specified
    ):
        return premade.http_post_responses['failure_not_json']
    try:
        message = request.json
    except InvalidUsage:
        return premade.http_post_responses['failure_invalid_json']

    result = await handle_json_post_message(message)
    return premade.http_post_responses.get(result) or json_response(
        {
            'success': False,
            'changed': False,
            'error': f"unexpected: {repr(result)}",
        },
        escape_forward_slashes=False,
        status=500,
    )


async def handle_json_post_message(message):
    try:
        topic = bytes.fromhex(message.pop('topic'))
    except (KeyError, ValueError):
        return 'failure_invalid_topic'

    try:
        data = b64decode(message.pop('data'), validate=True)
    except (KeyError, binascii.Error, ValueError):
        return 'failure_invalid_data'

    try:
        signature = b64decode(message.pop('signature', b''), validate=True)
    except (binascii.Error, ValueError):
        return 'failure_invalid_signature'

    choke = message.pop('choke', False)  # TODO: support with_metadata messages
    if type(choke) is not bool:
        return 'failure_invalid_choke'

    valid = await validate_signature(await get_topic_keys(topic), data, signature)
    if valid is None:
        return 'failure_nonexistent_topic'
    if not valid:
        return 'failure_unauthorized'

    # post the message
    return await post_message(topic, data, signature)


# noinspection PyUnusedLocal
@app.middleware('response')
async def cors(request, response):
    if response:
        response.headers.update(premade.CORS_ANYWHERE)


@app.exception(NotFound)
def not_found(request, **_):
    return text_response(
        f"Does not exist: {request.path}",
        status=404,
    )


@app.websocket('/ws')
async def accept(request, ws):
    log.debug(f"websocket {id(ws):x} accepted from {remote_address(request)}, security: {ws.secure}")
    try:
        msg = await ws.recv()
        if type(msg) is str:
            code, reason = await websocket_text(ws, msg) or (WEBSOCKET_NORMAL_CLOSE, 'bye')
        else:
            code, reason = await websocket_binary(ws, msg) or (WEBSOCKET_NORMAL_CLOSE, 'bye')
    except ConnectionClosed:
        log.debug(f"websocket {id(ws):x} closed remotely: code {repr(ws.close_code)}, reason {repr(ws.close_reason)}")
    except CancelledError:
        ensure_future(ws.close(WEBSOCKET_GOING_AWAY, 'shutting down'))
        log.debug(f"websocket {id(ws):x} closed, task cancelled")
    except Exception as ex:  # close websocket gracefully, then re-raise
        await ws.close(WEBSOCKET_UNEXPECTED_CONDITION, 'error')
        log.debug(f"websocket {id(ws):x} closed, task encountered error: {ex}")
        raise
    else:
        await ws.close(code, reason)
        log.debug(f"websocket {id(ws):x} closed locally:  code {repr(ws.close_code)}, reason {repr(ws.close_reason)}")


async def websocket_text(ws, first_message):
    async def receiver(channel, data):
        """redis receiver function; data is always bytes"""
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            text = repr(data)
        try:
            await ws.send(f"{channel} : {text}")
        except Exception as ex:
            log.debug(f"could not send message to websocket {id(ws):x}: {type(ex)} {ex}")
            raise

    state = None

    async def process_message(message):
        """process json message"""
        nonlocal state

        log.debug(f"websocket {id(ws):x} received message: {repr(message)}")

        try:
            msg = json.loads(message)
        except ValueError:
            await ws.close(WEBSOCKET_CANNOT_ACCEPT, 'invalid json')
            return False

        if not isinstance(msg, dict) or 'type' not in msg or 'serial' not in msg:
            await ws.close(WEBSOCKET_GENERIC_VIOLATION, 'invalid message')
            return False

        serial = msg['serial']
        if not isinstance(serial, int):
            await ws.close(WEBSOCKET_GENERIC_VIOLATION, 'invalid message serial')
            return False

        if state is None:
            if msg.get('type') == 'hello':
                state = 'greeted'
                ensure_future(ws.send(json.dumps({
                    'type': 'hello',
                    'serial': serial
                }, escape_forward_slashes=False)))
                return True
            else:
                await ws.close(WEBSOCKET_GENERIC_VIOLATION, 'unexpected message')
                return False
        elif state == 'greeted':
            if msg['type'] == 'post':
                msg_to_post = msg.get('message')
                if not isinstance(msg_to_post, dict):
                    await ws.close(WEBSOCKET_GENERIC_VIOLATION, 'invalid message')
                    return False

                result = await handle_json_post_message(msg_to_post)

                if result.startswith('failure_invalid_'):
                    await ws.close(WEBSOCKET_GENERIC_VIOLATION, 'invalid message')
                    return False

                elif result in premade.responses:
                    ensure_future(ws.send(json.dumps({
                        'type': 'status',
                        'serial': serial,
                        **premade.responses[result]['info'],
                    }, escape_forward_slashes=False)))
                else:
                    await ws.close(WEBSOCKET_UNEXPECTED_CONDITION, f"unexpected post result: {result}")
                    return False

            elif msg['type'] == 'get':
                try:
                    message_id = bytes.fromhex(msg['message_id'])
                except (KeyError, binascii.Error, ValueError, TypeError):
                    await ws.close(WEBSOCKET_GENERIC_VIOLATION, 'invalid or missing message_id')
                    return False
                fetched_message = await get_message_content(message_id)
                if fetched_message is None:
                    ensure_future(ws.send(json.dumps({
                        'type': 'message',
                        'from': 'get',
                        'serial': serial,
                        'success': False,
                        'error': 'message not found',
                    }, escape_forward_slashes=False)))
                else:
                    ensure_future(ws.send(json.dumps({
                        'type': 'message',
                        'from': 'get',
                        'serial': serial,
                        'success': True,
                        'error': None,
                        'topic': fetched_message['topic'].hex(),
                        'topic_serial': fetched_message['topic_serial'],
                        'signature': fetched_message['signature'] and b64encode(fetched_message['signature']),
                        'message_body': b64encode(fetched_message['message_body']),
                    }, escape_forward_slashes=False)))

            elif msg['type'] == 'subscribe':
                try:
                    topic = bytes.fromhex(msg['topic'])
                except (KeyError, ValueError, TypeError):
                    await ws.close(WEBSOCKET_GENERIC_VIOLATION, 'invalid or missing topic')
                    return False
                await listen(topic, receiver)
                ensure_future(ws.send(json.dumps({
                    'type': 'confirmation',
                    'serial': serial,
                }, escape_forward_slashes=False)))

            elif msg['type'] == 'unsubscribe':
                try:
                    topic = bytes.fromhex(msg['topic'])
                except (KeyError, ValueError, TypeError):
                    await ws.close(WEBSOCKET_GENERIC_VIOLATION, 'invalid or missing topic')
                    return False
                await unlisten(topic, receiver)
                ensure_future(ws.send(json.dumps({
                    'type': 'confirmation',
                    'serial': serial,
                }, escape_forward_slashes=False)))

            else:
                await ws.close(WEBSOCKET_GENERIC_VIOLATION, 'unexpected message')
        else:
            await ws.close(WEBSOCKET_UNEXPECTED_CONDITION, 'unexpected client state')
            return False

        return True

    try:
        if not await process_message(first_message):
            return
        while await process_message(await ws.recv()):
            pass
    finally:
        await unlisten_all(receiver)


async def websocket_binary(_ws, first_message):
    log.debug(f"received protobuf greeting: {repr(first_message)} length {len(first_message)}")
    return WEBSOCKET_CANNOT_ACCEPT, 'sorry'  # don't understand binary yet


def main():
    app.go_fast(
        host=app.config.get('HOST', '127.0.0.1'),
        port=int(app.config.get('PORT', 8000)),
        workers=int(app.config.get('WORKERS', 1)),
    )


if __name__ == '__main__':
    main()
