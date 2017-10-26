from aiohttp import web

routes = [
    ('GET', '/v3/accounts'),
    ('GET', '/v3/accounts/TEST_ID'),
    ('GET', '/v3/accounts/TEST_ID/summary'),
    ('GET', '/v3/accounts/TEST_ID/instruments'),
    ('PATCH', '/v3/accounts/TEST_ID/configuration'),
    ('GET', '/v3/accounts/TEST_ID/changes'),
    ('GET', '/v3/instruments/0/candles'),
    ('POST', '/v3/accounts/TEST_ID/orders'),
    ('GET', '/v3/accounts/TEST_ID/orders'),
    ('GET', '/v3/accounts/TEST_ID/pendingOrders'),
    ('GET', '/v3/accounts/TEST_ID/orders/0'),
    ('PUT', '/v3/accounts/TEST_ID/orders/0'),
    ('PUT', '/v3/accounts/TEST_ID/orders/0/cancel'),
    ('PUT', '/v3/accounts/TEST_ID/orders/0/clientExtensions'),
    ('GET', '/v3/accounts/TEST_ID/positions'),
    ('GET', '/v3/accounts/TEST_ID/openPositions'),
    ('GET', '/v3/accounts/TEST_ID/positions/0'),
    ('PUT', '/v3/accounts/TEST_ID/positions/0/close'),
    ('GET', '/v3/accounts/TEST_ID/pricing'),
    ('GET', '/v3/accounts/TEST_ID/pricing/stream'),
    ('GET', '/v3/accounts/TEST_ID/trades'),
    ('GET', '/v3/accounts/TEST_ID/openTrades'),
    ('GET', '/v3/accounts/TEST_ID/trades/0'),
    ('PUT', '/v3/accounts/TEST_ID/trades/0/close'),
    ('PUT', '/v3/accounts/TEST_ID/trades/0/clientExtensions'),
    ('PUT', '/v3/accounts/TEST_ID/trades/0/orders'),
    ('GET', '/v3/accounts/TEST_ID/transactions'),
    ('GET', '/v3/accounts/TEST_ID/transactions/0'),
    ('GET', '/v3/accounts/TEST_ID/transactions/idrange'),
    ('GET', '/v3/accounts/TEST_ID/transactions/sinceid'),
    ('GET', '/v3/accounts/TEST_ID/transactions/stream'),
    ('GET', '/v3/users/0'),
    ('GET', '/v3/users/0/externalInfo')
]


def echo(request):
    print()
    return web.Response(body=request.body,
                        status=200,
                        reason='ECHO',
                        headers=request.headers,
                        content_type=request.content_type)


app = web.Application()

route_lookup = {'GET': app.router.add_get,
                'PUT': app.router.add_put,
                'PATCH': app.router.add_patch,
                'POST': app.router.add_post}

for route in routes:
    route_lookup[route[0]](route[1], echo)

web.run_app(app)