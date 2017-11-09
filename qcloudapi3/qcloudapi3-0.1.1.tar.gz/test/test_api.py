from qcloudapi3 import Api

def main():
    _module = 'wenzhi'
    action = 'TextSentiment'
    config = {
        'Region': 'gz',
        'secretId': 'AKIDPglgT5ZwBF7nHZLZJrDONAW2QcdSGZql',
        'secretKey': '0teEwZ3PZX6WkpjRBmCPQI1Ys10uZAdu',
        'method': 'post'
    }
    params = {
        "content": "所有人都很差劲。",
    }
    service = Api(_module, config)
    print('URL:\n' + service.generateUrl(action, params))
    print(service.call(action, params))


if __name__ == '__main__':
    main()
