import json
import requests
import gateway_client


def run():
    session = requests.session()
    with open('cloud_capture_order.json', 'rb') as f:
        setup = json.loads(f.read())
    gateway_client.process_response(setup, session)


if __name__ == "__main__":
    run()
